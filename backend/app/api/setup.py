from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api.routes import user_view
from app.api.workspace_schemas import AuthView, PilotSetup, SetupStatus
from app.auth import COOKIE_NAME, DB, csrf_token, require_browser_write, start_session
from app.db import models as m
from app.seed import provision_pilot

router = APIRouter(prefix="/api/setup")


def needs_setup(db) -> bool:
    return not db.scalar(select(m.User.id).limit(1)) and not db.scalar(
        select(m.Workspace.id).limit(1)
    )


@router.get("/status", response_model=SetupStatus)
def setup_status(db: DB):
    return SetupStatus(needed=needs_setup(db))


@router.post(
    "", response_model=AuthView, status_code=201, dependencies=[Depends(require_browser_write)]
)
def setup(body: PilotSetup, request: Request, response: Response, db: DB):
    # get_db reserves a SQLite writer before this check, serializing first-run attempts.
    if not needs_setup(db):
        raise HTTPException(
            409, "This workspace is already set up. Sign in with an existing account."
        )
    request.app.state.login_limiter.check(request.client.host if request.client else "local")
    try:
        workspace = provision_pilot(db, body)
        owner = db.get(m.User, workspace.owner_id)
        raw = start_session(db, owner.id, response, request.cookies.get(COOKIE_NAME))
        result = AuthView(user=user_view(owner), csrf_token=csrf_token(raw))
        db.commit()
        return result
    except (IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(409, "Setup could not be completed. Refresh and try again.") from exc
