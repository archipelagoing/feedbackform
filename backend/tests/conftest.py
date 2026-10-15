from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from app.db import models as m
from app.db.connection import build_engine


@pytest.fixture
def database(tmp_path):
    engine = build_engine(f"sqlite:///{tmp_path / 'test.db'}")
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    yield engine
    engine.dispose()


def seed_workspace(session: Session):
    users = [
        m.User(
            id=str(uuid4()),
            login_name=f"pilot-{uuid4()}",
            display_name=f"Person {i}",
            password_hash="test-only-hash",
        )
        for i in range(4)
    ]
    session.add_all(users)
    session.flush()
    workspace = m.Workspace(
        id=str(uuid4()), title="Pilot", goal="Choose a project", owner_id=users[0].id
    )
    session.add(workspace)
    session.add_all(
        [
            m.Membership(
                workspace_id=workspace.id,
                user_id=user.id,
                role="owner" if i == 0 else "participant",
            )
            for i, user in enumerate(users)
        ]
    )
    session.flush()
    policy = m.PolicyVersion(
        workspace_id=workspace.id,
        version=1,
        required_user_ids=[user.id for user in users],
        created_by=users[0].id,
    )
    session.add(policy)
    session.flush()
    workspace.current_policy_id = policy.id
    session.flush()
    return workspace, users


@pytest.fixture
def pilot(database):
    with Session(database) as session, session.begin():
        workspace, users = seed_workspace(session)
        result = workspace.id, [user.id for user in users]
    return result
