from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from threading import Barrier
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models as m
from app.main import create_app
from tests.conftest import seed_workspace
from tests.test_auth_ideas import HEADERS, PASSWORD, sign_in
from tests.test_auth_ideas import client as client
from tests.test_auth_ideas import identities as identities
from tests.test_auth_ideas import password_hash as password_hash


def make_idea(client, identities, text="😀 repeat and repeat\nend"):
    sign_in(client, identities[2][0])
    root = f"/api/workspaces/{identities[0]}/ideas"
    idea = client.post(root, json={"body": text}).json()
    return root, idea, f"{root}/{idea['id']}/annotations"


def test_passage_and_whole_idea_comments_keep_original_context(client, identities, database):
    root, idea, path = make_idea(client, identities)
    text = idea["body"]
    start = len(text[: text.rfind("repeat")].encode("utf-16-le")) // 2
    sign_in(client, identities[2][1])
    result = client.post(
        path,
        json={
            "idea_version_id": idea["version_id"],
            "anchor": "passage",
            "span": {"start_utf16": start, "end_utf16": start + 6, "quote": "repeat"},
            "body": "Keep the second occurrence",
        },
    )
    assert result.status_code == 201, result.text
    comment = result.json()
    assert comment["author"]["id"] == identities[1][1]
    assert comment["span"]["start_utf16"] == start
    assert comment["source_body"] == text and not comment["historical"]
    assert (
        client.post(
            path,
            json={
                "idea_version_id": idea["version_id"],
                "anchor": "whole_idea",
                "body": "An overall concern",
            },
        ).status_code
        == 201
    )
    sign_in(client, identities[2][0])
    assert (
        client.patch(
            f"{root}/{idea['id']}",
            json={"body": "Entirely different text", "expected_version_id": idea["version_id"]},
        ).status_code
        == 200
    )
    rows = client.get(path).json()
    assert len(rows) == 2 and all(row["historical"] for row in rows)
    assert all(row["source_body"] == text and row["source_version"] == 1 for row in rows)
    with Session(database) as db:
        annotation = db.get(m.Annotation, comment["id"])
        assert (
            db.get(m.AnnotationVersion, annotation.current_version_id).body
            == "Keep the second occurrence"
        )


def test_all_four_can_comment_with_their_own_attribution(client, identities):
    _, idea, path = make_idea(client, identities)
    for i in range(4):
        sign_in(client, identities[2][i])
        response = client.post(
            path,
            json={
                "idea_version_id": idea["version_id"],
                "anchor": "whole_idea",
                "body": f"Person {i} feedback",
            },
        )
        assert response.status_code == 201
        assert response.json()["author"]["id"] == identities[1][i]
    assert len(client.get(path).json()) == 4


def test_invalid_quotes_bounds_and_surrogate_splits_are_rejected(client, identities):
    _, idea, path = make_idea(client, identities)
    for span in [
        {"start_utf16": 0, "end_utf16": 1, "quote": "😀"},
        {"start_utf16": 0, "end_utf16": 2, "quote": "wrong"},
        {"start_utf16": 0, "end_utf16": 999, "quote": "outside"},
        {"start_utf16": 0, "end_utf16": 2, "quote": "😀", "suffix": "wrong"},
    ]:
        response = client.post(
            path,
            json={
                "idea_version_id": idea["version_id"],
                "anchor": "passage",
                "span": span,
                "body": "Invalid anchor",
            },
        )
        assert response.status_code == 422, response.text
    assert client.get(path).json() == []


def test_wrong_idea_version_cannot_be_used_as_a_comment_source(client, identities):
    root, idea, path = make_idea(client, identities)
    other = client.post(root, json={"body": "Other idea"}).json()
    response = client.post(
        path,
        json={
            "idea_version_id": other["version_id"],
            "anchor": "whole_idea",
            "body": "Mismatched source",
        },
    )
    assert response.status_code == 404


def test_comment_permission_and_actor_spoofing_boundaries(client, identities, database):
    _, idea, path = make_idea(client, identities)
    payload = {"idea_version_id": idea["version_id"], "anchor": "whole_idea", "body": "Feedback"}
    assert client.post(path, json=payload, headers={"X-CSRF-Token": "bad"}).status_code == 403
    assert client.post(path, json={**payload, "author_id": identities[1][2]}).status_code == 422
    with Session(database) as db, db.begin():
        other, _ = seed_workspace(db)
        other_id = other.id
    hidden = f"/api/workspaces/{other_id}/ideas/{idea['id']}/annotations"
    assert client.get(hidden).status_code == 404
    assert client.post(hidden, json=payload).status_code == 404
    assert (
        client.get(f"/api/workspaces/{identities[0]}/ideas/{uuid4()}/annotations").status_code
        == 404
    )
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get(path).status_code == 401
    assert client.post(path, json=payload).status_code == 401


def test_comment_on_an_older_version_is_explicitly_historical(client, identities, database):
    root, idea, path = make_idea(client, identities)
    client.patch(
        f"{root}/{idea['id']}",
        json={"body": "New version", "expected_version_id": idea["version_id"]},
    )
    response = client.post(
        path,
        json={
            "idea_version_id": idea["version_id"],
            "anchor": "whole_idea",
            "body": "Feedback on the text I actually read",
        },
    )
    assert response.status_code == 201
    assert response.json()["historical"]
    with Session(database) as db:
        assert (
            db.scalar(select(m.Workspace).where(m.Workspace.id == identities[0])).input_revision
            == 4
        )


def test_simultaneous_signins_reserve_writes_without_lock_upgrade_failures(database, identities):
    gate = Barrier(2)
    with ExitStack() as stack:
        clients = [
            stack.enter_context(
                TestClient(
                    create_app(str(database.url), allowed_origins={"http://testserver"}),
                    headers=HEADERS,
                )
            )
            for _ in range(2)
        ]

        def login(index):
            gate.wait(timeout=5)
            return clients[index].post(
                "/api/auth/login",
                json={
                    "login_name": identities[2][index],
                    "password": PASSWORD,
                },
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(login, range(2)))
        assert [response.status_code for response in responses] == [200, 200]
        assert {response.json()["user"]["id"] for response in responses} == set(identities[1][:2])
