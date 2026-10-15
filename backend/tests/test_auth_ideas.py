from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.workspace_schemas import PilotSetup
from app.auth import COOKIE_NAME, hash_password, token_hash, verify_password
from app.db import models as m
from app.main import create_app
from app.seed import provision_pilot
from tests.conftest import seed_workspace

PASSWORD = "test-only-password-1234"
HEADERS = {"Origin": "http://testserver", "X-FeedbackForm-Request": "1"}


@pytest.fixture(scope="session")
def password_hash():
    return hash_password(PASSWORD)


@pytest.fixture
def identities(database, pilot, password_hash):
    with Session(database) as db, db.begin():
        db.execute(update(m.User).values(password_hash=password_hash))
        users = [db.get(m.User, actor) for actor in pilot[1]]
        logins = [user.login_name for user in users]
    return pilot[0], pilot[1], logins


@pytest.fixture
def client(database):
    with TestClient(
        create_app(str(database.url), allowed_origins={"http://testserver"}), headers=HEADERS
    ) as client:
        yield client


def sign_in(client, login):
    response = client.post("/api/auth/login", json={"login_name": login, "password": PASSWORD})
    assert response.status_code == 200, response.text
    client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    return response


def test_provisioning_builds_four_accounts_policy_and_constraint_set(database):
    setup = PilotSetup(
        title="Team project",
        goal="Choose our direction",
        members=[
            {
                "login_name": f"student{i}",
                "display_name": f"Student {i}",
                "password": f"different-test-password-{i}",
            }
            for i in range(4)
        ],
    )
    with Session(database) as db, db.begin():
        workspace = provision_pilot(db, setup)
        workspace_id = workspace.id
    with Session(database) as db:
        workspace = db.get(m.Workspace, workspace_id)
        memberships = db.scalars(select(m.Membership)).all()
        assert len(memberships) == 4
        assert sum(member.role == "owner" for member in memberships) == 1
        policy = db.get(m.PolicyVersion, workspace.current_policy_id)
        assert len(set(policy.required_user_ids)) == 4
        assert db.scalar(select(m.ConstraintSet)).policy_version_id == policy.id
        hashes = db.scalars(select(m.User.password_hash)).all()
        assert len(set(hashes)) == 4
        assert verify_password(
            "different-test-password-0",
            db.scalar(select(m.User).where(m.User.login_name == "student0")).password_hash,
        )
        with pytest.raises(ValueError, match="preserved"):
            provision_pilot(db, setup)


def test_cookie_session_is_hashed_private_and_revocable(client, identities, database):
    response = sign_in(client, identities[2][0])
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie and "path=/api" in cookie
    assert "no-store" in response.headers["cache-control"]
    assert response.json()["user"]["id"] == identities[1][0]
    assert "password" not in response.text
    raw = client.cookies.get(COOKIE_NAME)
    with Session(database) as db:
        stored = db.scalar(select(m.Session))
        assert stored.token_hash == token_hash(raw)
        assert stored.token_hash != raw
    assert client.get("/api/auth/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    client.cookies.set(COOKIE_NAME, raw, path="/api")
    assert client.get("/api/auth/me").status_code == 401


def test_wrong_password_and_unknown_account_have_same_error(client, identities):
    wrong = client.post(
        "/api/auth/login",
        json={
            "login_name": identities[2][0],
            "password": "wrong-long-password",
        },
    )
    unknown = client.post(
        "/api/auth/login",
        json={
            "login_name": "unknown-account",
            "password": PASSWORD,
        },
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_mutations_require_origin_custom_header_and_session_csrf(client, identities):
    login_body = {"login_name": identities[2][0], "password": PASSWORD}
    assert (
        client.post(
            "/api/auth/login", json=login_body, headers={"Origin": "https://attacker.example"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/auth/login", json=login_body, headers={"X-FeedbackForm-Request": ""}
        ).status_code
        == 403
    )
    sign_in(client, identities[2][0])
    path = f"/api/workspaces/{identities[0]}/ideas"
    assert (
        client.post(path, json={"body": "Forged"}, headers={"X-CSRF-Token": "wrong"}).status_code
        == 403
    )
    assert client.post(path, json={"body": "Forged"}, headers={"Origin": "null"}).status_code == 403


def test_expired_session_cannot_read_or_write(client, identities, database):
    sign_in(client, identities[2][0])
    with Session(database) as db, db.begin():
        db.execute(update(m.Session).values(expires_at=datetime.now(UTC) - timedelta(seconds=1)))
    assert client.get("/api/workspaces").status_code == 401
    assert (
        client.post(f"/api/workspaces/{identities[0]}/ideas", json={"body": "Expired"}).status_code
        == 401
    )


def test_authenticated_capture_edit_and_history_preserve_authorship(client, identities, database):
    workspace_id, actors, logins = identities
    sign_in(client, logins[0])
    workspace = client.get("/api/workspaces").json()[0]
    assert len(workspace["members"]) == 4
    path = f"/api/workspaces/{workspace_id}/ideas"
    created = client.post(path, json={"body": "A rough thought 😀"})
    assert created.status_code == 201, created.text
    idea = created.json()
    assert idea["author"]["id"] == actors[0] and idea["title"] is None
    edited = client.patch(
        f"{path}/{idea['id']}",
        json={
            "body": "A developed thought",
            "title": "Direction",
            "expected_version_id": idea["version_id"],
        },
    )
    assert edited.status_code == 200, edited.text
    assert edited.json()["version"] == 2
    history = client.get(f"{path}/{idea['id']}/history").json()
    assert [version["body"] for version in history] == ["A developed thought", "A rough thought 😀"]
    assert client.get(path).json()[0]["body"] == "A developed thought"
    with Session(database) as db:
        assert db.get(m.IdeaVersion, idea["version_id"]).body == "A rough thought 😀"
    sign_in(client, logins[1])
    assert client.get(path).json()[0]["author"]["id"] == actors[0]
    denied = client.patch(
        f"{path}/{idea['id']}",
        json={
            "body": "Impersonation",
            "expected_version_id": edited.json()["version_id"],
        },
    )
    assert denied.status_code == 403


def test_stale_edit_rolls_back_without_extra_version(client, identities, database):
    sign_in(client, identities[2][0])
    path = f"/api/workspaces/{identities[0]}/ideas"
    idea = client.post(path, json={"body": "Original"}).json()
    edit = {"body": "Latest", "expected_version_id": idea["version_id"]}
    assert client.patch(f"{path}/{idea['id']}", json=edit).status_code == 200
    assert client.patch(f"{path}/{idea['id']}", json=edit).status_code == 409
    assert len(client.get(f"{path}/{idea['id']}/history").json()) == 2
    with Session(database) as db:
        assert db.get(m.Workspace, identities[0]).input_revision == 3


def test_workspace_nonmember_cannot_discover_read_or_write(client, identities, database):
    with Session(database) as db, db.begin():
        other, actors = seed_workspace(db)
        other_id = other.id
        other_idea = m.Idea(workspace_id=other_id, author_id=actors[0].id)
        db.add(other_idea)
        db.flush()
        other_idea_id = other_idea.id
    sign_in(client, identities[2][0])
    assert len(client.get("/api/workspaces").json()) == 1
    path = f"/api/workspaces/{other_id}/ideas"
    assert client.get(path).status_code == 404
    assert client.post(path, json={"body": "Unauthorized"}).status_code == 404
    assert client.get(f"{path}/{other_idea_id}/history").status_code == 404
    own_path = f"/api/workspaces/{identities[0]}/ideas/{other_idea_id}"
    assert client.get(f"{own_path}/history").status_code == 404
    assert (
        client.patch(
            own_path, json={"body": "Cross-workspace", "expected_version_id": str(uuid4())}
        ).status_code
        == 404
    )


def test_unauthenticated_and_spoofed_input_rejected(client, identities):
    path = f"/api/workspaces/{identities[0]}/ideas"
    assert client.get(path).status_code == 401
    assert client.post(path, json={"body": "No session"}).status_code == 401
    sign_in(client, identities[2][0])
    response = client.post(path, json={"body": "Spoof", "author_id": identities[1][1]})
    assert response.status_code == 422
    assert client.get(path).json() == []


def test_validation_errors_do_not_echo_passwords(client):
    response = client.post("/api/auth/login", json={"login_name": "person", "password": "private"})
    assert response.status_code == 422
    assert "private" not in response.text
    assert "input" not in response.json()["detail"][0]


def test_login_rate_limit(client, identities):
    client.app.state.login_limiter.attempts = 1
    payload = {"login_name": identities[2][0], "password": "wrong-long-password"}
    assert client.post("/api/auth/login", json=payload).status_code == 401
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
