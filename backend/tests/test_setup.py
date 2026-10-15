from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import models as m
from app.main import create_app
from tests.test_auth_ideas import HEADERS


def payload():
    return {
        "title": "Our course project",
        "goal": "What will our final project be?",
        "members": [
            {
                "login_name": f"dev{i}",
                "display_name": f"Developer {i}",
                "password": f"setup-test-password-{i}",
            }
            for i in range(1, 5)
        ],
    }


def test_setup_status_creation_owner_session_and_other_logins(database):
    with TestClient(
        create_app(str(database.url), allowed_origins={"http://testserver"}), headers=HEADERS
    ) as client:
        assert client.get("/api/setup/status").json() == {"needed": True}
        response = client.post("/api/setup", json=payload())
        assert response.status_code == 201, response.text
        assert response.json()["user"]["login_name"] == "dev1"
        assert "password" not in response.text
        assert client.get("/api/auth/me").status_code == 200
        assert client.get("/api/setup/status").json() == {"needed": False}
        assert len(client.get("/api/workspaces").json()[0]["members"]) == 4
        original = client.get("/api/workspaces").json()
        assert client.post("/api/setup", json=payload()).status_code == 409
        assert client.get("/api/workspaces").json() == original
        for i in range(2, 5):
            assert (
                client.post(
                    "/api/auth/login",
                    json={"login_name": f"dev{i}", "password": f"setup-test-password-{i}"},
                ).status_code
                == 200
            )


def test_invalid_setup_is_atomic_and_does_not_echo_passwords(database):
    with TestClient(
        create_app(str(database.url), allowed_origins={"http://testserver"}), headers=HEADERS
    ) as client:
        bad = payload()
        bad["members"][0]["password"] = "private"
        response = client.post("/api/setup", json=bad)
        assert response.status_code == 422 and "private" not in response.text
        duplicate = payload()
        duplicate["members"][1]["login_name"] = "dev1"
        response = client.post("/api/setup", json=duplicate)
        assert response.status_code == 422
        assert "setup-test-password" not in response.text
        assert client.get("/api/setup/status").json() == {"needed": True}
    with Session(database) as db:
        assert db.scalar(select(func.count()).select_from(m.User)) == 0
        assert db.scalar(select(func.count()).select_from(m.Workspace)) == 0


def test_setup_requires_origin_and_custom_header(database):
    with TestClient(create_app(str(database.url), allowed_origins={"http://testserver"})) as client:
        assert client.post("/api/setup", json=payload()).status_code == 403
        assert (
            client.post(
                "/api/setup",
                json=payload(),
                headers={**HEADERS, "Origin": "https://elsewhere.example"},
            ).status_code
            == 403
        )
        assert client.get("/api/setup/status").json() == {"needed": True}


def test_two_setup_requests_cannot_create_or_overwrite_two_workspaces(database):
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

        def setup(index):
            gate.wait(timeout=5)
            body = payload()
            body["title"] = f"Attempt {index}"
            return clients[index].post("/api/setup", json=body)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(setup, range(2)))
        assert sorted(response.status_code for response in results) == [201, 409]
    with Session(database) as db:
        assert db.scalar(select(func.count()).select_from(m.User)) == 4
        assert db.scalar(select(func.count()).select_from(m.Workspace)) == 1
