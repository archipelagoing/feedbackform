from sqlalchemy import update
from sqlalchemy.orm import Session

from app.api.schemas import IdeaCreate, IdeaEdit
from app.db import models as m
from app.domain.evidence import DomainError, require_member, scoped_record


def create_idea(session: Session, workspace_id: str, actor_id: str, body: IdeaCreate) -> m.Idea:
    require_member(session, workspace_id, actor_id)
    idea = m.Idea(workspace_id=workspace_id, author_id=actor_id)
    session.add(idea)
    session.flush()
    version = m.IdeaVersion(
        workspace_id=workspace_id,
        idea_id=idea.id,
        version=1,
        title=body.title,
        body=body.body,
        editor_id=actor_id,
    )
    session.add(version)
    session.flush()
    idea.current_version_id = version.id
    session.execute(
        update(m.Workspace)
        .where(m.Workspace.id == workspace_id)
        .values(input_revision=m.Workspace.input_revision + 1)
    )
    session.flush()
    return idea


def edit_idea(
    session: Session,
    workspace_id: str,
    idea_id: str,
    actor_id: str,
    body: IdeaEdit,
) -> m.IdeaVersion:
    require_member(session, workspace_id, actor_id)
    idea = scoped_record(session, m.Idea, workspace_id, idea_id)
    if idea.author_id != actor_id:
        raise DomainError("Only the author may edit an idea")
    previous = scoped_record(session, m.IdeaVersion, workspace_id, idea.current_version_id)
    if previous.id != str(body.expected_version_id):
        raise DomainError("Idea has changed; reload before editing")
    version = m.IdeaVersion(
        workspace_id=workspace_id,
        idea_id=idea.id,
        version=previous.version + 1,
        title=body.title,
        body=body.body,
        editor_id=actor_id,
        previous_version_id=previous.id,
    )
    session.add(version)
    session.flush()
    result = session.execute(
        update(m.Idea)
        .where(
            m.Idea.id == idea_id,
            m.Idea.workspace_id == workspace_id,
            m.Idea.current_version_id == previous.id,
        )
        .values(current_version_id=version.id)
    )
    if result.rowcount != 1:
        raise DomainError("Idea has changed; reload before editing")
    session.execute(
        update(m.Workspace)
        .where(m.Workspace.id == workspace_id)
        .values(input_revision=m.Workspace.input_revision + 1)
    )
    return version
