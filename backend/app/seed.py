"""Interactive, one-time local provisioning. Never installs default credentials."""

from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.workspace_schemas import PilotMember, PilotSetup
from app.auth import hash_password
from app.config import database_url
from app.db import models as m
from app.db.connection import build_engine


def provision_pilot(db: Session, setup: PilotSetup) -> m.Workspace:
    if db.scalar(select(m.Workspace.id).limit(1)) or db.scalar(select(m.User.id).limit(1)):
        raise ValueError(
            "Pilot setup requires an empty migrated database; existing data was preserved"
        )
    names = [member.login_name for member in setup.members]
    if len(set(names)) != 4:
        raise ValueError("Each participant needs a distinct login name")
    users = [
        m.User(
            login_name=member.login_name,
            display_name=member.display_name,
            password_hash=hash_password(member.password.get_secret_value()),
        )
        for member in setup.members
    ]
    db.add_all(users)
    db.flush()
    workspace = m.Workspace(title=setup.title, goal=setup.goal, owner_id=users[0].id)
    db.add(workspace)
    db.flush()
    db.add_all(
        [
            m.Membership(
                workspace_id=workspace.id,
                user_id=user.id,
                role="owner" if i == 0 else "participant",
            )
            for i, user in enumerate(users)
        ]
    )
    db.flush()
    policy = m.PolicyVersion(
        workspace_id=workspace.id,
        version=1,
        required_user_ids=[user.id for user in users],
        created_by=users[0].id,
    )
    db.add(policy)
    db.flush()
    workspace.current_policy_id = policy.id
    constraints = m.ConstraintSet(workspace_id=workspace.id, version=1, policy_version_id=policy.id)
    db.add(constraints)
    db.flush()
    return workspace


def main():
    print("Set up four participants. Participant 1 will own the workspace.")
    title = input("Workspace title [Our project]: ").strip() or "Our project"
    goal = input("Decision question: ").strip()
    members = []
    for i in range(4):
        print(f"Participant {i + 1}")
        login = input("Login name (lowercase letters/numbers/._-): ").strip()
        display = input("Display name: ").strip()
        password = getpass("Password (12–256 characters): ")
        if password != getpass("Repeat password: "):
            raise SystemExit("Passwords did not match. Nothing was saved.")
        try:
            members.append(PilotMember(login_name=login, display_name=display, password=password))
        except ValidationError:
            raise SystemExit(
                "Invalid participant details. Use a lowercase login, a display name, and a "
                "12–256 character password. Nothing was saved."
            ) from None
    try:
        setup = PilotSetup(title=title, goal=goal, members=members)
    except ValidationError:
        raise SystemExit(
            "Enter a nonempty title and decision question. Nothing was saved."
        ) from None
    engine = build_engine(database_url())
    try:
        with Session(engine) as db, db.begin():
            provision_pilot(db, setup)
        print("Pilot created. All four participants can now sign in with their own credentials.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
