from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api.routes import user_view
from app.api.schemas import AnnotationCreate
from app.api.workspace_schemas import AnnotationView
from app.auth import AUTH, DB, member_or_404, require_csrf
from app.db import models as m
from app.domain.evidence import DomainError, validate_span

router = APIRouter(prefix="/api/workspaces/{workspace_id}/ideas/{idea_id}/annotations")


def get_idea(db, workspace: str, idea_id: str):
    idea = db.scalar(
        select(m.Idea).where(
            m.Idea.workspace_id == workspace,
            m.Idea.id == idea_id,
            m.Idea.archived_at.is_(None),
        )
    )
    if idea is None:
        raise HTTPException(404, "Idea not found")
    return idea


def annotation_view(db, annotation: m.Annotation, idea: m.Idea):
    content = db.get(m.AnnotationVersion, annotation.current_version_id)
    source = db.get(m.IdeaVersion, annotation.idea_version_id)
    return AnnotationView(
        id=annotation.id,
        version_id=content.id,
        idea_id=idea.id,
        idea_version_id=source.id,
        source_version=source.version,
        source_body=source.body,
        historical=source.id != idea.current_version_id,
        anchor=annotation.anchor,
        span=annotation.span,
        body=content.body,
        author=user_view(db.get(m.User, annotation.author_id)),
        created_at=annotation.created_at,
    )


@router.get("", response_model=list[AnnotationView])
def list_annotations(
    workspace_id: UUID,
    idea_id: UUID,
    auth: AUTH,
    db: DB,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    idea = get_idea(db, workspace, str(idea_id))
    rows = db.scalars(
        select(m.Annotation)
        .join(m.IdeaVersion, m.Annotation.idea_version_id == m.IdeaVersion.id)
        .where(
            m.Annotation.workspace_id == workspace,
            m.IdeaVersion.idea_id == idea.id,
        )
        .order_by(m.Annotation.created_at, m.Annotation.id)
        .offset(offset)
        .limit(limit)
    ).all()
    return [annotation_view(db, row, idea) for row in rows]


@router.post(
    "", response_model=AnnotationView, status_code=201, dependencies=[Depends(require_csrf)]
)
def post_annotation(workspace_id: UUID, idea_id: UUID, body: AnnotationCreate, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    idea = get_idea(db, workspace, str(idea_id))
    source = db.scalar(
        select(m.IdeaVersion).where(
            m.IdeaVersion.workspace_id == workspace,
            m.IdeaVersion.idea_id == idea.id,
            m.IdeaVersion.id == str(body.idea_version_id),
        )
    )
    if source is None:
        raise HTTPException(404, "Source version not found for this idea")
    if body.span:
        try:
            validate_span(source.body, body.span)
        except DomainError as exc:
            raise HTTPException(422, str(exc)) from exc
    try:
        annotation = m.Annotation(
            workspace_id=workspace,
            author_id=auth.user_id,
            idea_version_id=source.id,
            anchor=body.anchor,
            span=body.span.model_dump() if body.span else None,
        )
        db.add(annotation)
        db.flush()
        content = m.AnnotationVersion(
            workspace_id=workspace,
            annotation_id=annotation.id,
            version=1,
            body=body.body,
            withdrawn=False,
        )
        db.add(content)
        db.flush()
        annotation.current_version_id = content.id
        db.execute(
            update(m.Workspace)
            .where(m.Workspace.id == workspace)
            .values(input_revision=m.Workspace.input_revision + 1)
        )
        db.flush()
        result = annotation_view(db, annotation, idea)
        db.commit()
        return result
    except (IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(
            409, "The workspace is busy. Your comment was not confirmed saved."
        ) from exc
