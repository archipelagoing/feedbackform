from datetime import UTC
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import inspect, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas import (
    AnnotationCreate,
    ConstraintCheck,
    FeatureDraft,
    IdeaCreate,
    IdeaEdit,
    IdeaEvidence,
    PolicyContract,
    PreferenceSuggestion,
    ReviewCreate,
    Span,
    WorkflowEnvelope,
)
from app.db import models as m
from app.domain.evidence import DomainError, validate_evidence, validate_span
from app.domain.versioning import create_idea, edit_idea
from app.main import create_app
from tests.conftest import seed_workspace


def test_migration_creates_complete_metadata_and_foreign_keys(database):
    assert set(inspect(database).get_table_names()) == set(m.Base.metadata.tables) | {
        "alembic_version"
    }
    with database.connect() as connection:
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1
        assert connection.execute(text("PRAGMA foreign_key_check")).all() == []
        triggers = (
            connection.execute(text("SELECT name FROM sqlite_master WHERE type='trigger'"))
            .scalars()
            .all()
        )
    assert len(triggers) == 2 * len(m.IMMUTABLE_TABLES)


def test_empty_database_migration_round_trip(database):
    config = Config("alembic.ini")
    with database.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
    assert inspect(database).get_table_names() == ["alembic_version"]
    with database.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    assert "idea_versions" in inspect(database).get_table_names()


def test_populated_database_downgrade(database, pilot):
    with Session(database) as session, session.begin():
        create_idea(session, pilot[0], pilot[1][0], IdeaCreate(body="Disposable test data"))
    config = Config("alembic.ini")
    with database.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
    assert inspect(database).get_table_names() == ["alembic_version"]


def test_migration_preserves_every_composite_reference(database):
    inspector = inspect(database)
    for name, table in m.Base.metadata.tables.items():
        actual = {
            (tuple(fk["constrained_columns"]), fk["referred_table"], tuple(fk["referred_columns"]))
            for fk in inspector.get_foreign_keys(name)
        }
        expected = {
            (
                tuple(fk.column_keys),
                fk.referred_table.name,
                tuple(element.column.name for element in fk.elements),
            )
            for fk in table.foreign_key_constraints
        }
        assert actual == expected, name


def test_idea_versions_survive_reopen_and_reject_stale_edit(database, pilot):
    workspace_id, actors = pilot
    with Session(database) as session, session.begin():
        idea = create_idea(session, workspace_id, actors[0], IdeaCreate(body="Original 😀 idea"))
        idea_id, previous_id = idea.id, idea.current_version_id
    with Session(database) as session, session.begin():
        latest = edit_idea(
            session,
            workspace_id,
            idea_id,
            actors[0],
            IdeaEdit(body="Revised idea", expected_version_id=previous_id),
        )
        latest_id = latest.id
    with Session(database) as session, session.begin():
        assert session.get(m.Idea, idea_id).current_version_id == latest_id
        assert session.get(m.IdeaVersion, previous_id).body == "Original 😀 idea"
        assert session.get(m.IdeaVersion, previous_id).created_at.tzinfo is UTC
        assert session.get(m.Workspace, workspace_id).input_revision == 3
        with pytest.raises(DomainError, match="changed"):
            edit_idea(
                session,
                workspace_id,
                idea_id,
                actors[0],
                IdeaEdit(body="Stale edit", expected_version_id=previous_id),
            )


def test_non_author_cannot_edit(database, pilot):
    workspace_id, actors = pilot
    with Session(database) as session, session.begin():
        idea = create_idea(session, workspace_id, actors[0], IdeaCreate(body="Owned idea"))
        with pytest.raises(DomainError, match="author"):
            edit_idea(
                session,
                workspace_id,
                idea.id,
                actors[1],
                IdeaEdit(body="Changed", expected_version_id=idea.current_version_id),
            )


def test_nonmember_cannot_create(database, pilot):
    with Session(database) as session, session.begin():
        with pytest.raises(DomainError, match="membership"):
            create_idea(session, pilot[0], str(uuid4()), IdeaCreate(body="Injected idea"))


def test_cross_workspace_and_wrong_author_evidence_rejected(database, pilot):
    workspace_id, actors = pilot
    with Session(database) as session, session.begin():
        other, _ = seed_workspace(session)
        idea = create_idea(session, workspace_id, actors[0], IdeaCreate(body="Human evidence"))
        refs = [IdeaEvidence(kind="idea_span", idea_version_id=idea.current_version_id)]
        validate_evidence(session, workspace_id, refs, participant_id=actors[0])
        with pytest.raises(DomainError, match="workspace"):
            validate_evidence(session, other.id, refs)
        with pytest.raises(DomainError, match="attributed"):
            validate_evidence(session, workspace_id, refs, participant_id=actors[1])


def test_cross_workspace_database_reference_rejected(database, pilot):
    workspace_id, actors = pilot
    with pytest.raises(IntegrityError):
        with Session(database) as session, session.begin():
            other, _ = seed_workspace(session)
            session.add(m.Idea(workspace_id=other.id, author_id=actors[0]))


def test_evidence_must_belong_to_the_runs_snapshot(database, pilot):
    workspace_id, actors = pilot
    with Session(database) as session, session.begin():
        idea = create_idea(session, workspace_id, actors[0], IdeaCreate(body="New evidence"))
        refs = [IdeaEvidence(kind="idea_span", idea_version_id=idea.current_version_id)]
        snapshot = m.InputSnapshot(workspace_id=workspace_id, idea_version_ids=[])
        with pytest.raises(DomainError, match="snapshot"):
            validate_evidence(session, workspace_id, refs, snapshot=snapshot)
        snapshot.workspace_id = str(uuid4())
        with pytest.raises(DomainError, match="another workspace"):
            validate_evidence(session, workspace_id, refs, snapshot=snapshot)


def test_head_cannot_point_to_another_ideas_version(database, pilot):
    workspace_id, actors = pilot
    with pytest.raises(IntegrityError):
        with Session(database) as session, session.begin():
            first = create_idea(session, workspace_id, actors[0], IdeaCreate(body="First"))
            second = create_idea(session, workspace_id, actors[0], IdeaCreate(body="Second"))
            first.current_version_id = second.current_version_id


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_historical_rows_are_immutable(database, pilot, operation):
    with Session(database) as session, session.begin():
        idea = create_idea(session, pilot[0], pilot[1][0], IdeaCreate(body="Preserve this"))
        version_id = idea.current_version_id
    with pytest.raises(IntegrityError, match="immutable"):
        with database.begin() as connection:
            if operation == "update":
                connection.execute(
                    update(m.IdeaVersion)
                    .where(m.IdeaVersion.id == version_id)
                    .values(body="Rewritten")
                )
            else:
                connection.execute(
                    text("DELETE FROM idea_versions WHERE id=:id"), {"id": version_id}
                )


def test_utf16_anchor_preserves_emoji_and_line_endings():
    validate_span(
        "A😀\r\nB", Span(start_utf16=1, end_utf16=5, quote="😀\r\n", prefix="A", suffix="B")
    )
    for span in [
        Span(start_utf16=1, end_utf16=2, quote="😀"),
        Span(start_utf16=1, end_utf16=3, quote="wrong"),
        Span(start_utf16=0, end_utf16=100, quote="too long"),
    ]:
        with pytest.raises(DomainError):
            validate_span("A😀\r\nB", span)


def test_strict_boundary_rejects_impersonation_and_blank_content():
    with pytest.raises(ValidationError):
        IdeaCreate(body="idea", author_id=str(uuid4()))
    with pytest.raises(ValidationError):
        IdeaCreate(body=" \n\t")
    with pytest.raises(ValidationError):
        AnnotationCreate(idea_version_id=uuid4(), anchor="passage", body="Concern")
    with pytest.raises(ValidationError):
        ReviewCreate(round_id=uuid4(), stance="support_with_reservations", expected_sequence=0)


def test_model_cannot_invent_confirmation_or_verified_satisfaction():
    evidence = [{"kind": "idea_span", "idea_version_id": str(uuid4())}]
    with pytest.raises(ValidationError):
        PreferenceSuggestion(
            participant_id=uuid4(),
            statement="Use Python",
            kind="desire",
            evidence=evidence,
            status="confirmed",
        )
    with pytest.raises(ValidationError):
        ConstraintCheck(
            constraint_revision_id=uuid4(),
            status="verified",
            method="model",
            evidence=evidence,
            rationale="Looks feasible",
        )
    with pytest.raises(ValidationError):
        FeatureDraft(text="Feature", origin="human_source", evidence=[], rationale="No source")


def test_policy_requires_four_distinct_people():
    user = uuid4()
    with pytest.raises(ValidationError):
        PolicyContract(required_user_ids=[user] * 4)


def test_workflow_discriminator_cannot_mix_stage_payloads():
    with pytest.raises(ValidationError):
        TypeAdapter(WorkflowEnvelope).validate_python(
            {
                "schema_version": "1",
                "run_id": str(uuid4()),
                "snapshot_id": str(uuid4()),
                "stage": "synthesize",
                "payload": {"preferences": []},
            }
        )


def test_ready_health_and_no_unauthenticated_write_routes(database):
    with TestClient(create_app(str(database.url))) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["schema_revision"] == "0001_foundation"
        assert client.get("/api/workspaces").status_code == 401
        assert client.post("/api/workspaces", json={"owner_id": "spoof"}).status_code == 405


def test_unmigrated_health_does_not_claim_ready(tmp_path):
    with TestClient(create_app(f"sqlite:///{tmp_path / 'empty.db'}")) as client:
        response = client.get("/api/health")
        assert response.status_code == 503
        assert response.json()["database"] == "migration_required"
