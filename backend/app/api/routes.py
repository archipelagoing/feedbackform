from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api.schemas import IdeaCreate, IdeaEdit
from app.api.workspace_schemas import (
    AuthView,
    IdeaHistoryView,
    IdeaView,
    LoginRequest,
    MemberView,
    UserView,
    WorkspaceView,
)
from app.auth import (
    AUTH,
    COOKIE_NAME,
    DB,
    csrf_token,
    member_or_404,
    require_browser_write,
    require_csrf,
    secure_cookies,
    start_session,
    verify_password,
)
from app.db import models as m
from app.domain.evidence import DomainError
from app.domain.versioning import create_idea, edit_idea

router = APIRouter(prefix="/api")


def user_view(user: m.User) -> UserView:
    return UserView(id=user.id, display_name=user.display_name, login_name=user.login_name)


def idea_view(db, idea: m.Idea) -> IdeaView:
    version = db.get(m.IdeaVersion, idea.current_version_id)
    return IdeaView(
        id=idea.id,
        workspace_id=idea.workspace_id,
        version_id=version.id,
        version=version.version,
        title=version.title,
        body=version.body,
        author=user_view(db.get(m.User, idea.author_id)),
        created_at=idea.created_at,
        updated_at=version.created_at,
    )


@router.post("/auth/login", response_model=AuthView, dependencies=[Depends(require_browser_write)])
def login(body: LoginRequest, request: Request, response: Response, db: DB):
    # A bounded in-process limiter is sufficient for the single-process local pilot.
    # The key is the direct peer address; forwarded client IP headers are not trusted.
    request.app.state.login_limiter.check(request.client.host if request.client else "local")
    user = db.scalar(select(m.User).where(m.User.login_name == body.login_name))
    encoded = user.password_hash if user else request.app.state.dummy_password_hash
    valid = verify_password(body.password.get_secret_value(), encoded)
    if not valid or user is None:
        raise HTTPException(401, "Login name or password is incorrect")
    raw = start_session(db, user.id, response, request.cookies.get(COOKIE_NAME))
    db.commit()
    return AuthView(user=user_view(user), csrf_token=csrf_token(raw))


@router.get("/auth/me", response_model=AuthView)
def me(request: Request, auth: AUTH, db: DB):
    return AuthView(
        user=user_view(db.get(m.User, auth.user_id)),
        csrf_token=csrf_token(request.cookies[COOKIE_NAME]),
    )


@router.post("/auth/logout", status_code=204, dependencies=[Depends(require_csrf)])
def logout(response: Response, auth: AUTH, db: DB):
    auth.revoked_at = datetime.now(UTC)
    db.commit()
    response.delete_cookie(
        COOKIE_NAME, path="/api", httponly=True, secure=secure_cookies(), samesite="strict"
    )


@router.get("/workspaces", response_model=list[WorkspaceView])
def workspaces(auth: AUTH, db: DB):
    rows = db.scalars(
        select(m.Workspace)
        .join(m.Membership, m.Membership.workspace_id == m.Workspace.id)
        .where(m.Membership.user_id == auth.user_id)
        .order_by(m.Workspace.created_at, m.Workspace.id)
    ).all()
    result = []
    for row in rows:
        pairs = db.execute(
            select(m.User, m.Membership.role)
            .join(m.Membership, m.Membership.user_id == m.User.id)
            .where(m.Membership.workspace_id == row.id)
            .order_by(m.User.created_at, m.User.id)
        ).all()
        result.append(
            WorkspaceView(
                id=row.id,
                title=row.title,
                goal=row.goal,
                input_revision=row.input_revision,
                members=[MemberView(user=user_view(user), role=role) for user, role in pairs],
            )
        )
    return result


@router.get("/workspaces/{workspace_id}/ideas", response_model=list[IdeaView])
def ideas(
    workspace_id: UUID,
    auth: AUTH,
    db: DB,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    rows = db.scalars(
        select(m.Idea)
        .where(m.Idea.workspace_id == workspace, m.Idea.archived_at.is_(None))
        .order_by(m.Idea.created_at.desc(), m.Idea.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [idea_view(db, idea) for idea in rows]


@router.post(
    "/workspaces/{workspace_id}/ideas",
    response_model=IdeaView,
    status_code=201,
    dependencies=[Depends(require_csrf)],
)
def post_idea(workspace_id: UUID, body: IdeaCreate, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    try:
        idea = create_idea(db, workspace, auth.user_id, body)
        result = idea_view(db, idea)
        db.commit()
        return result
    except (IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(409, "The workspace is busy. Refresh and try again.") from exc


@router.patch(
    "/workspaces/{workspace_id}/ideas/{idea_id}",
    response_model=IdeaView,
    dependencies=[Depends(require_csrf)],
)
def patch_idea(workspace_id: UUID, idea_id: UUID, body: IdeaEdit, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    idea = db.scalar(
        select(m.Idea).where(
            m.Idea.id == str(idea_id),
            m.Idea.workspace_id == workspace,
            m.Idea.archived_at.is_(None),
        )
    )
    if idea is None:
        raise HTTPException(404, "Idea not found")
    if idea.author_id != auth.user_id:
        raise HTTPException(403, "Only the author may edit an idea")
    try:
        edit_idea(db, workspace, idea.id, auth.user_id, body)
        db.flush()
        db.refresh(idea)
        result = idea_view(db, idea)
        db.commit()
        return result
    except (DomainError, IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(409, "This idea changed. Reload before editing again.") from exc


@router.get(
    "/workspaces/{workspace_id}/ideas/{idea_id}/history", response_model=list[IdeaHistoryView]
)
def history(workspace_id: UUID, idea_id: UUID, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    idea = db.scalar(
        select(m.Idea).where(m.Idea.workspace_id == workspace, m.Idea.id == str(idea_id))
    )
    if idea is None:
        raise HTTPException(404, "Idea not found")
    versions = db.scalars(
        select(m.IdeaVersion)
        .where(m.IdeaVersion.workspace_id == workspace, m.IdeaVersion.idea_id == idea.id)
        .order_by(m.IdeaVersion.version.desc())
    ).all()
    return [
        IdeaHistoryView(
            version_id=v.id, version=v.version, title=v.title, body=v.body, created_at=v.created_at
        )
        for v in versions
    ]
