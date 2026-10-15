"""Known credentials for the isolated browser-test database only."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.workspace_schemas import PilotSetup
from app.config import database_url
from app.db import models as m
from app.db.connection import build_engine
from app.seed import provision_pilot


def main():
    url = database_url()
    if url != "sqlite:///./data/e2e.db":
        raise SystemExit("Refusing to seed test identities outside the browser-test database")
    engine = build_engine(url)
    try:
        with Session(engine) as db, db.begin():
            if db.scalar(select(m.Workspace.id).limit(1)) is None:
                provision_pilot(
                    db,
                    PilotSetup(
                        title="Our project",
                        goal="What should we build?",
                        members=[
                            {
                                "login_name": f"student{i}",
                                "display_name": f"Student {i}",
                                "password": f"browser-test-password-{i}",
                            }
                            for i in range(1, 5)
                        ],
                    ),
                )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
