import io
import json
from urllib.error import HTTPError, URLError
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models as m
from app.domain.extraction import ExtractionError, ExtractionOutput, OpenAIExtractor
from tests.test_auth_ideas import client as client  # noqa: F401
from tests.test_auth_ideas import identities as identities  # noqa: F401
from tests.test_auth_ideas import password_hash as password_hash  # noqa: F401
from tests.test_auth_ideas import sign_in


class FakeExtractor:
    """Explicit test double, never available through production configuration."""

    provider = "test"
    model = "fixture"
    configured = True

    def __init__(self):
        self.inputs = []
        self.transform = lambda rows: rows
        self.during_call = lambda: None

    def extract(self, payload):
        self.inputs.append(payload)
        self.during_call()
        rows = [
            {
                "source_id": source["source_id"],
                "participant_id": source["participant_id"],
                "statement": "Intentionally imperfect interpretation",
                "kind": "desire",
                "quote": source["text"],
                "uncertainty_note": None,
            }
            for source in payload["new_sources"]
        ]
        return ExtractionOutput(preferences=self.transform(rows)), {"total_tokens": 12}


@pytest.fixture
def extractor(client, database, identities):
    fake = FakeExtractor()
    client.app.state.extractor = fake
    with Session(database) as db, db.begin():
        workspace = db.get(m.Workspace, identities[0])
        db.add(
            m.ConstraintSet(
                workspace_id=workspace.id, version=1, policy_version_id=workspace.current_policy_id
            )
        )
    return fake


def idea(client, identities, body="I prefer a web app, not a mobile app."):
    sign_in(client, identities[2][0])
    response = client.post(f"/api/workspaces/{identities[0]}/ideas", json={"body": body})
    assert response.status_code == 201
    return response.json()


def start(client, identities, key=None):
    return client.post(
        f"/api/workspaces/{identities[0]}/preference-extractions",
        json={"request_key": key or str(uuid4())},
    )


def board(client, identities):
    response = client.get(f"/api/workspaces/{identities[0]}/preferences")
    assert response.status_code == 200, response.text
    return response.json()


def test_extract_original_owners_and_review_history(client, identities, extractor, database):
    original = idea(client, identities, "🦊 I prefer a web app.")
    sign_in(client, identities[2][1])
    response = client.post(
        f"/api/workspaces/{identities[0]}/ideas/{original['id']}/annotations",
        json={
            "idea_version_id": original["version_id"],
            "anchor": "whole_idea",
            "body": "Only if it works offline.",
        },
    )
    assert response.status_code == 201
    key = str(uuid4())
    assert start(client, identities, key).status_code == 202
    data = board(client, identities)
    assert data["latest_run"]["status"] == "succeeded"
    assert {p["participant"]["id"] for p in data["preferences"]} == set(identities[1][:2])
    own = next(p for p in data["preferences"] if p["participant"]["id"] == identities[1][1])
    other = next(p for p in data["preferences"] if p["id"] != own["id"])
    assert own["status"] == "inferred" and own["strength"] is None
    assert own["sources"][0]["text"] == "Only if it works offline."
    review_path = f"/api/workspaces/{identities[0]}/preferences/"
    command = {
        "expected_revision_id": own["revision_id"],
        "statement": "Offline support is required",
        "kind": "constraint",
        "strength": "essential",
        "action": "correct",
    }
    assert client.patch(review_path + other["id"], json=command).status_code == 403
    revised = client.patch(review_path + own["id"], json=command)
    assert revised.status_code == 200, revised.text
    assert revised.json()["status"] == "corrected" and revised.json()["version"] == 2
    assert client.patch(review_path + own["id"], json=command).status_code == 409
    history = client.get(review_path + own["id"] + "/history").json()
    assert [r["status"] for r in history] == ["inferred", "corrected"]
    assert start(client, identities, key).json()["id"] == data["latest_run"]["id"]
    assert len(extractor.inputs) == 1  # Idempotent request did not make a second paid call.
    assert start(client, identities).status_code == 409  # No new sources.
    # A new contribution triggers incremental extraction with corrected heads as context.
    idea(client, identities, "I want a simple deployment.")
    assert start(client, identities).status_code == 202
    context = extractor.inputs[-1]["existing_interpretations"]
    assert any(
        p["statement"] == command["statement"] and p["status"] == "corrected" for p in context
    )
    assert len(extractor.inputs[-1]["new_sources"]) == 1
    with Session(database) as db:
        assert db.get(m.IdeaVersion, original["version_id"]).body == "🦊 I prefer a web app."
        assert not db.scalar(
            select(m.Constraint)
        )  # Personal essential != binding group constraint.
        assert db.scalar(select(m.AgentRun)).token_usage == {"total_tokens": 12}


def test_confirm_withdraw_and_no_resurrection(client, identities, extractor):
    idea(client, identities)
    start(client, identities)
    preference = board(client, identities)["preferences"][0]
    path = f"/api/workspaces/{identities[0]}/preferences/{preference['id']}"
    command = {
        "expected_revision_id": preference["revision_id"],
        "statement": "Silently rewritten",
        "kind": preference["kind"],
        "action": "confirm",
    }
    assert client.patch(path, json=command).status_code == 422
    command["statement"] = preference["statement"]
    confirmed = client.patch(path, json=command)
    assert confirmed.status_code == 200 and confirmed.json()["status"] == "confirmed"
    command.update(expected_revision_id=confirmed.json()["revision_id"], action="withdraw")
    withdrawn = client.patch(path, json=command)
    assert withdrawn.status_code == 200 and withdrawn.json()["status"] == "withdrawn"
    command["expected_revision_id"] = withdrawn.json()["revision_id"]
    assert client.patch(path, json=command).status_code == 409
    idea(client, identities, "How will we evaluate it?")
    start(client, identities)
    assert extractor.inputs[-1]["existing_interpretations"][0]["status"] == "withdrawn"
    assert len(extractor.inputs[-1]["new_sources"]) == 1
    assert len(board(client, identities)["preferences"]) == 2


@pytest.mark.parametrize("failure", ["participant", "source", "quote", "duplicate", "schema"])
def test_invalid_results_are_atomic(client, identities, extractor, database, failure):
    idea(client, identities)
    idea(client, identities, "We need offline support.")

    def corrupt(rows):
        if failure == "participant":
            rows[-1]["participant_id"] = identities[1][1]
        elif failure == "source":
            rows[-1]["source_id"] = str(uuid4())
        elif failure == "quote":
            rows[-1]["quote"] = "fabricated source quote"
        elif failure == "schema":
            rows[-1]["kind"] = "approved"
        else:
            rows.append(rows[0])
        return rows

    extractor.transform = corrupt
    assert start(client, identities).status_code == 202
    data = board(client, identities)
    assert data["latest_run"]["status"] == "failed"
    assert data["preferences"] == []
    with Session(database) as db:
        assert not db.scalar(select(m.Preference))
        assert not db.scalar(select(m.PreferenceRevision))
        assert db.scalar(select(m.AgentEvent)).status == "failed"


def test_edit_during_network_call_discards_result_without_holding_writer(
    client, identities, extractor, database
):
    idea(client, identities)

    def edit():
        with Session(database.execution_options(sqlite_write=True)) as db, db.begin():
            workspace = db.get(m.Workspace, identities[0])
            workspace.input_revision += 1

    extractor.during_call = edit
    start(client, identities)
    data = board(client, identities)
    assert data["latest_run"]["error_code"] == "stale_inputs"
    assert data["preferences"] == []


def test_unconfigured_access_and_csrf(client, identities):
    idea(client, identities)
    client.app.state.extractor = OpenAIExtractor()
    client.app.state.extractor._key = ""
    assert board(client, identities)["configured"] is False
    assert start(client, identities).status_code == 503
    response = client.post(
        f"/api/workspaces/{uuid4()}/preference-extractions", json={"request_key": str(uuid4())}
    )
    assert response.status_code == 404
    del client.headers["X-CSRF-Token"]
    assert start(client, identities).status_code == 403
    client.post("/api/auth/logout")
    client.cookies.clear()
    assert client.get(f"/api/workspaces/{identities[0]}/preferences").status_code == 401


def test_openai_wire_contract_and_secret_handling(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-never-expose")
    monkeypatch.setenv("OPENAI_MODEL", "configured-test-model")
    calls = []

    def send(request, timeout):
        calls.append((request, timeout))
        return io.BytesIO(
            json.dumps(
                {
                    "status": "completed",
                    "usage": {"total_tokens": 9},
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": '{"preferences": []}'}],
                        }
                    ],
                }
            ).encode()
        )

    monkeypatch.setattr("app.domain.extraction.urlopen", send)
    output, usage = OpenAIExtractor().extract({"new_sources": []})
    assert output.preferences == [] and usage == {"total_tokens": 9}
    request, timeout = calls[0]
    assert request.full_url == "https://api.openai.com/v1/responses" and timeout == 45
    body = json.loads(request.data)
    assert body["store"] is False and body["max_output_tokens"] == 6000
    assert body["text"]["format"]["strict"] is True
    assert body["text"]["format"]["schema"]["additionalProperties"] is False
    assert "test-secret" not in str(body)


@pytest.mark.parametrize(
    "result,code",
    [
        ({"status": "incomplete"}, "incomplete_output"),
        (
            {
                "status": "completed",
                "output": [
                    {"type": "message", "content": [{"type": "refusal", "refusal": "private text"}]}
                ],
            },
            "provider_refused",
        ),
        ({"status": "completed", "output": []}, "invalid_output"),
        (HTTPError("url", 401, "secret provider detail", {}, None), "provider_auth"),
        (HTTPError("url", 429, "secret provider detail", {}, None), "provider_rate_limit"),
        (URLError("secret network detail"), "provider_unavailable"),
        (TimeoutError("secret timeout detail"), "provider_timeout"),
    ],
)
def test_provider_failure_codes(monkeypatch, result, code):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    monkeypatch.setenv("OPENAI_MODEL", "fixture")

    def send(*args, **kwargs):
        if isinstance(result, Exception):
            raise result
        return io.BytesIO(json.dumps(result).encode())

    monkeypatch.setattr("app.domain.extraction.urlopen", send)
    with pytest.raises(ExtractionError) as error:
        OpenAIExtractor().extract({})
    assert str(error.value) == code
