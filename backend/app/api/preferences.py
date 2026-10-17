"""Snapshot extraction jobs and participant-owned, append-only preference review."""

import hashlib
import json
import time
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.routes import user_view
from app.api.schemas import Contract, PreferenceCorrection, Span
from app.api.workspace_schemas import UserView
from app.auth import AUTH, DB, member_or_404, require_csrf
from app.db import models as m
from app.domain.evidence import DomainError, validate_evidence
from app.domain.extraction import PROMPT_VERSION, ExtractionError, ExtractionOutput

router = APIRouter(prefix="/api/workspaces/{workspace_id}")


class ExtractionRequest(Contract):
    request_key: UUID


class ExtractionRunView(Contract):
    id: UUID
    status: str
    error_code: str | None


class PreferenceSourceView(Contract):
    version_id: UUID
    kind: str
    text: str
    quote: str | None
    historical: bool


class PreferenceView(Contract):
    id: UUID
    revision_id: UUID
    version: int
    participant: UserView
    statement: str
    kind: str
    strength: str | None
    status: str
    uncertainty_note: str | None
    sources: list[PreferenceSourceView]


class PreferenceBoard(Contract):
    configured: bool
    latest_run: ExtractionRunView | None
    preferences: list[PreferenceView]


def run_view(run):
    return ExtractionRunView(id=run.id, status=run.status, error_code=run.error_code)


def preference_view(db, preference, revision=None):
    revision = revision or db.get(m.PreferenceRevision, preference.current_version_id)
    sources = []
    for ref in revision.evidence:
        if ref["kind"] == "idea_span":
            source = db.get(m.IdeaVersion, ref["idea_version_id"])
            parent = db.get(m.Idea, source.idea_id)
            historical = parent.current_version_id != source.id or parent.archived_at is not None
            quote = ref.get("span", {}).get("quote") if ref.get("span") else None
        else:
            source = db.get(m.AnnotationVersion, ref["annotation_version_id"])
            parent = db.get(m.Annotation, source.annotation_id)
            idea_version = db.get(m.IdeaVersion, parent.idea_version_id)
            idea = db.get(m.Idea, idea_version.idea_id)
            historical = (
                parent.current_version_id != source.id
                or source.withdrawn
                or idea.current_version_id != idea_version.id
                or idea.archived_at is not None
            )
            quote = None
        sources.append(
            PreferenceSourceView(
                version_id=source.id,
                kind=ref["kind"],
                text=source.body,
                quote=quote,
                historical=historical,
            )
        )
    return PreferenceView(
        id=preference.id,
        revision_id=revision.id,
        version=revision.version,
        participant=user_view(db.get(m.User, preference.participant_id)),
        statement=revision.statement,
        kind=revision.kind,
        strength=revision.strength,
        status=revision.status,
        uncertainty_note=revision.uncertainty_note,
        sources=sources,
    )


def current_preferences(db, workspace):
    return db.scalars(
        select(m.Preference)
        .where(m.Preference.workspace_id == workspace)
        .order_by(m.Preference.created_at, m.Preference.id)
    ).all()


@router.get("/preferences", response_model=PreferenceBoard)
def board(workspace_id: UUID, request: Request, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    latest = db.scalar(
        select(m.AgentRun)
        .where(
            m.AgentRun.workspace_id == workspace,
            m.AgentRun.prompt_versions["interpret"].as_string() == PROMPT_VERSION,
        )
        .order_by(m.AgentRun.created_at.desc(), m.AgentRun.id.desc())
    )
    return PreferenceBoard(
        configured=request.app.state.extractor.configured,
        latest_run=run_view(latest) if latest else None,
        preferences=[preference_view(db, row) for row in current_preferences(db, workspace)],
    )


@router.get("/preferences/{preference_id}/history", response_model=list[PreferenceView])
def history(workspace_id: UUID, preference_id: UUID, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    preference = db.get(m.Preference, str(preference_id))
    if preference is None or preference.workspace_id != workspace:
        raise HTTPException(404, "Preference not found")
    revisions = db.scalars(
        select(m.PreferenceRevision)
        .where(
            m.PreferenceRevision.preference_id == preference.id,
            m.PreferenceRevision.workspace_id == workspace,
        )
        .order_by(m.PreferenceRevision.version)
    ).all()
    return [preference_view(db, preference, revision) for revision in revisions]


@router.patch(
    "/preferences/{preference_id}",
    response_model=PreferenceView,
    dependencies=[Depends(require_csrf)],
)
def review(workspace_id: UUID, preference_id: UUID, body: PreferenceCorrection, auth: AUTH, db: DB):
    workspace = str(workspace_id)
    member_or_404(db, workspace, auth.user_id)
    preference = db.get(m.Preference, str(preference_id))
    if preference is None or preference.workspace_id != workspace:
        raise HTTPException(404, "Preference not found")
    if preference.participant_id != auth.user_id:
        raise HTTPException(403, "Only the participant can review their interpretation")
    previous = db.get(m.PreferenceRevision, preference.current_version_id)
    if previous.id != str(body.expected_revision_id):
        raise HTTPException(409, "This interpretation changed. Refresh before reviewing it.")
    if previous.status == "withdrawn":
        raise HTTPException(409, "This interpretation has been withdrawn")
    if body.action in {"confirm", "withdraw"} and (
        body.statement != previous.statement or body.kind != previous.kind
    ):
        raise HTTPException(422, "Use correction to change the statement or kind")
    revision = m.PreferenceRevision(
        workspace_id=workspace,
        preference_id=preference.id,
        version=previous.version + 1,
        statement=body.statement,
        kind=body.kind,
        strength=previous.strength if body.action == "withdraw" else body.strength,
        status={"confirm": "confirmed", "correct": "corrected", "withdraw": "withdrawn"}[
            body.action
        ],
        evidence=previous.evidence,
        uncertainty_note=previous.uncertainty_note,
        previous_version_id=previous.id,
        created_by_user_id=auth.user_id,
    )
    db.add(revision)
    db.flush()
    preference.current_version_id = revision.id
    db.execute(
        update(m.Workspace)
        .where(m.Workspace.id == workspace)
        .values(input_revision=m.Workspace.input_revision + 1)
    )
    db.flush()
    result = preference_view(db, preference, revision)
    db.commit()
    return result


def prepare_input(db, workspace):
    sources = []
    for idea in db.scalars(
        select(m.Idea)
        .where(m.Idea.workspace_id == workspace.id, m.Idea.archived_at.is_(None))
        .order_by(m.Idea.id)
    ):
        version = db.get(m.IdeaVersion, idea.current_version_id)
        sources.append(
            {
                "source_id": version.id,
                "participant_id": idea.author_id,
                "kind": "idea_span",
                "text": version.body,
                "title": version.title,
            }
        )
    for annotation in db.scalars(
        select(m.Annotation)
        .join(m.IdeaVersion, m.Annotation.idea_version_id == m.IdeaVersion.id)
        .join(m.Idea, m.IdeaVersion.idea_id == m.Idea.id)
        .where(m.Annotation.workspace_id == workspace.id, m.Idea.archived_at.is_(None))
        .order_by(m.Annotation.id)
    ):
        version = db.get(m.AnnotationVersion, annotation.current_version_id)
        if not version.withdrawn:
            context = db.get(m.IdeaVersion, annotation.idea_version_id)
            sources.append(
                {
                    "source_id": version.id,
                    "participant_id": annotation.author_id,
                    "kind": "annotation",
                    "text": version.body,
                    "idea_context": context.body,
                    "passage": annotation.span,
                }
            )
    preferences = current_preferences(db, workspace.id)
    heads = [db.get(m.PreferenceRevision, row.current_version_id) for row in preferences]
    existing = [
        {
            "participant_id": row.participant_id,
            "statement": head.statement,
            "status": head.status,
            "kind": head.kind,
            "strength": head.strength,
            "evidence": head.evidence,
        }
        for row, head in zip(preferences, heads, strict=True)
    ]
    processed = set()
    for event in db.scalars(
        select(m.AgentEvent)
        .join(m.AgentRun, m.AgentEvent.run_id == m.AgentRun.id)
        .where(
            m.AgentRun.workspace_id == workspace.id,
            m.AgentRun.status == "succeeded",
            m.AgentEvent.stage == "interpret",
        )
    ):
        processed.update(event.input_refs)
    new_sources = [source for source in sources if source["source_id"] not in processed]
    payload = {
        "goal": workspace.goal,
        "new_sources": new_sources,
        "existing_interpretations": existing,
    }
    if len(sources) > 200 or len(heads) > 1000 or len(json.dumps(payload)) > 100_000:
        raise HTTPException(422, "This workspace exceeds the pilot extraction limit")
    return sources, heads, payload


@router.post(
    "/preference-extractions",
    status_code=202,
    response_model=ExtractionRunView,
    dependencies=[Depends(require_csrf)],
)
def extract(
    workspace_id: UUID,
    body: ExtractionRequest,
    request: Request,
    background: BackgroundTasks,
    auth: AUTH,
    db: DB,
):
    workspace_id = str(workspace_id)
    member_or_404(db, workspace_id, auth.user_id)
    existing = db.scalar(
        select(m.AgentRun).where(
            m.AgentRun.workspace_id == workspace_id, m.AgentRun.request_key == str(body.request_key)
        )
    )
    if existing:
        return run_view(existing)
    extractor = request.app.state.extractor
    if not extractor.configured:
        raise HTTPException(503, "OpenAI is not configured. Ask the app operator to connect it.")
    active = db.scalar(select(m.AgentRun.id).where(m.AgentRun.status.in_(["queued", "running"])))
    if active:
        raise HTTPException(409, "An extraction is already running. Wait and refresh.")
    workspace = db.get(m.Workspace, workspace_id)
    sources, heads, payload = prepare_input(db, workspace)
    if not payload["new_sources"]:
        raise HTTPException(
            409, "No new ideas or comments to interpret. Existing reviews are kept."
        )
    constraint_set = db.scalar(
        select(m.ConstraintSet)
        .where(m.ConstraintSet.workspace_id == workspace_id)
        .order_by(m.ConstraintSet.version.desc())
    )
    if constraint_set is None:
        raise HTTPException(409, "Workspace policy setup is incomplete")
    manifest = {
        "input_revision": workspace.input_revision,
        "policy_version_id": workspace.current_policy_id,
        "constraint_set_id": constraint_set.id,
        "goal": workspace.goal,
        "idea_version_ids": [s["source_id"] for s in sources if s["kind"] == "idea_span"],
        "annotation_version_ids": [s["source_id"] for s in sources if s["kind"] == "annotation"],
        "preference_revision_ids": [head.id for head in heads],
    }
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    snapshot = m.InputSnapshot(workspace_id=workspace_id, manifest_hash=digest, **manifest)
    db.add(snapshot)
    db.flush()
    run = m.AgentRun(
        workspace_id=workspace_id,
        snapshot_id=snapshot.id,
        requested_by=auth.user_id,
        request_key=str(body.request_key),
        request_hash=digest,
        workflow_type="analyze",
        status="queued",
        provider=extractor.provider,
        model=extractor.model,
        prompt_versions={"interpret": PROMPT_VERSION},
        schema_version="1",
        generation_settings={"max_output_tokens": 6000, "timeout_seconds": 45, "retries": 0},
    )
    db.add(run)
    db.flush()
    result = run_view(run)
    run_id = run.id
    db.commit()  # Release the SQLite writer before any network operation.
    background.add_task(execute_extraction, request.app.state.engine, extractor, run_id, payload)
    return result


def execute_extraction(engine, extractor, run_id, payload):
    started = time.monotonic()
    writer = engine.execution_options(sqlite_write=True)
    try:
        with Session(writer) as db, db.begin():
            run = db.get(m.AgentRun, run_id)
            run.status = "running"
        output, usage = extractor.extract(payload)
        output = ExtractionOutput.model_validate(output)
        with Session(writer) as db, db.begin():
            run = db.get(m.AgentRun, run_id)
            snapshot = db.get(m.InputSnapshot, run.snapshot_id)
            workspace = db.get(m.Workspace, run.workspace_id)
            if workspace.input_revision != snapshot.input_revision:
                raise ExtractionError("stale_inputs")
            sources = {source["source_id"]: source for source in payload["new_sources"]}
            seen = set()
            for signal in output.preferences:
                source = sources.get(signal.source_id)
                if source is None or signal.participant_id != source["participant_id"]:
                    raise ExtractionError("invalid_attribution")
                position = source["text"].find(signal.quote)
                if position < 0:
                    raise ExtractionError("invalid_evidence")
                key = (signal.source_id, signal.statement, signal.kind)
                if key in seen:
                    raise ExtractionError("duplicate_output")
                seen.add(key)
                if source["kind"] == "idea_span":
                    start = len(source["text"][:position].encode("utf-16-le")) // 2
                    span = Span(
                        start_utf16=start,
                        end_utf16=start + len(signal.quote.encode("utf-16-le")) // 2,
                        quote=signal.quote,
                    )
                    from app.api.schemas import IdeaEvidence

                    evidence = [
                        IdeaEvidence(kind="idea_span", idea_version_id=signal.source_id, span=span)
                    ]
                else:
                    from app.api.schemas import AnnotationEvidence

                    evidence = [
                        AnnotationEvidence(
                            kind="annotation", annotation_version_id=signal.source_id
                        )
                    ]
                validate_evidence(db, run.workspace_id, evidence, signal.participant_id, snapshot)
                preference = m.Preference(
                    workspace_id=run.workspace_id, participant_id=signal.participant_id
                )
                db.add(preference)
                db.flush()
                revision = m.PreferenceRevision(
                    workspace_id=run.workspace_id,
                    preference_id=preference.id,
                    version=1,
                    statement=signal.statement,
                    kind=signal.kind,
                    status="inferred",
                    evidence=[ref.model_dump(mode="json") for ref in evidence],
                    uncertainty_note=signal.uncertainty_note,
                    run_id=run.id,
                )
                db.add(revision)
                db.flush()
                preference.current_version_id = revision.id
            if output.preferences:
                workspace.input_revision += 1
            run.status = "succeeded"
            run.token_usage = usage
            run.duration_ms = int((time.monotonic() - started) * 1000)
            db.add(
                m.AgentEvent(
                    workspace_id=run.workspace_id,
                    run_id=run.id,
                    sequence=1,
                    stage="interpret",
                    status="succeeded",
                    input_refs=list(sources),
                    output_json=output.model_dump(mode="json"),
                    duration_ms=run.duration_ms,
                    usage=usage,
                )
            )
    except Exception as exc:
        # Roll back the entire result, including valid rows preceding an invalid one.
        code = (
            str(exc)
            if isinstance(exc, ExtractionError)
            else ("invalid_evidence" if isinstance(exc, DomainError) else "extraction_failed")
        )
        with Session(writer) as db, db.begin():
            run = db.get(m.AgentRun, run_id)
            run.status = "failed"
            run.error_code = code
            run.duration_ms = int((time.monotonic() - started) * 1000)
            db.add(
                m.AgentEvent(
                    workspace_id=run.workspace_id,
                    run_id=run.id,
                    sequence=1,
                    stage="interpret",
                    status="failed",
                    input_refs=[s["source_id"] for s in payload["new_sources"]],
                    validation_errors=[{"code": code}],
                    duration_ms=run.duration_ms,
                )
            )
