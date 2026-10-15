from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import (
    AnnotationEvidence,
    ConstraintEvidence,
    EvidenceRef,
    IdeaEvidence,
    PreferenceEvidence,
    Span,
)
from app.db import models as m


class DomainError(ValueError):
    """An input cannot be applied to the current domain state."""


def require_member(session: Session, workspace_id: str, actor_id: str) -> m.Membership:
    membership = session.scalar(
        select(m.Membership).where(
            m.Membership.workspace_id == workspace_id,
            m.Membership.user_id == actor_id,
        )
    )
    if membership is None:
        raise DomainError("Workspace membership required")
    return membership


def scoped_record(session: Session, model, workspace_id: str, record_id: str):
    record = session.scalar(
        select(model).where(
            model.workspace_id == workspace_id,
            model.id == str(record_id),
        )
    )
    if record is None:
        raise DomainError("Referenced source is unavailable in this workspace")
    return record


def validate_span(text: str, span: Span) -> None:
    encoded = text.encode("utf-16-le")
    if span.end_utf16 * 2 > len(encoded):
        raise DomainError("Passage is outside the source text")
    try:
        quote = encoded[span.start_utf16 * 2 : span.end_utf16 * 2].decode("utf-16-le")
    except UnicodeDecodeError as exc:
        raise DomainError("Passage splits a Unicode character") from exc
    if quote != span.quote:
        raise DomainError("Passage quote does not match the source version")
    before = encoded[: span.start_utf16 * 2].decode("utf-16-le")
    after = encoded[span.end_utf16 * 2 :].decode("utf-16-le")
    if not before.endswith(span.prefix) or not after.startswith(span.suffix):
        raise DomainError("Passage context does not match the source version")


def validate_evidence(
    session: Session,
    workspace_id: str,
    evidence: list[EvidenceRef],
    participant_id: str | None = None,
    snapshot: m.InputSnapshot | None = None,
) -> None:
    """Check original source/owner and manifest membership, never semantic entailment."""
    if snapshot is not None and snapshot.workspace_id != workspace_id:
        raise DomainError("Input snapshot belongs to another workspace")
    for ref in evidence:
        owner = None
        if isinstance(ref, IdeaEvidence):
            record = scoped_record(session, m.IdeaVersion, workspace_id, str(ref.idea_version_id))
            idea = scoped_record(session, m.Idea, workspace_id, record.idea_id)
            if idea.archived_at is not None:
                raise DomainError("Archived idea is unavailable for new analysis")
            if ref.span:
                validate_span(record.body, ref.span)
            owner = idea.author_id
            allowed = snapshot.idea_version_ids if snapshot else None
        elif isinstance(ref, AnnotationEvidence):
            record = scoped_record(
                session,
                m.AnnotationVersion,
                workspace_id,
                str(ref.annotation_version_id),
            )
            annotation = scoped_record(session, m.Annotation, workspace_id, record.annotation_id)
            current = scoped_record(
                session,
                m.AnnotationVersion,
                workspace_id,
                annotation.current_version_id,
            )
            if record.withdrawn or current.withdrawn:
                raise DomainError("Withdrawn annotation is unavailable for new analysis")
            owner = annotation.author_id
            allowed = snapshot.annotation_version_ids if snapshot else None
        elif isinstance(ref, PreferenceEvidence):
            record = scoped_record(
                session,
                m.PreferenceRevision,
                workspace_id,
                str(ref.preference_revision_id),
            )
            preference = scoped_record(session, m.Preference, workspace_id, record.preference_id)
            owner = preference.participant_id
            allowed = snapshot.preference_revision_ids if snapshot else None
        elif isinstance(ref, ConstraintEvidence):
            record = scoped_record(
                session,
                m.ConstraintRevision,
                workspace_id,
                str(ref.constraint_revision_id),
            )
            allowed = None
            if snapshot:
                allowed = list(
                    session.scalars(
                        select(m.ConstraintSetMember.constraint_revision_id).where(
                            m.ConstraintSetMember.constraint_set_id == snapshot.constraint_set_id,
                            m.ConstraintSetMember.workspace_id == workspace_id,
                        )
                    )
                )
        else:
            raise DomainError("Unknown evidence type")
        if allowed is not None and record.id not in allowed:
            raise DomainError("Evidence is not part of this run's input snapshot")
        if participant_id is not None and owner != participant_id:
            raise DomainError("Evidence cannot be attributed to this participant")
