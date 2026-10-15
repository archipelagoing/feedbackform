"""Relational foundation. Domain transitions are separate from raw persistence."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    MetaData,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamps must be timezone aware")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=UTC) if value is not None else None


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Record:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=lambda: datetime.now(UTC))


class Scoped(Record):
    workspace_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workspaces.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )


def ref(field: str, table: str, target: str = "id") -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["workspace_id", field],
        [f"{table}.workspace_id", f"{table}.{target}"],
        deferrable=True,
        initially="DEFERRED",
    )


def member(field: str) -> ForeignKeyConstraint:
    return ref(field, "memberships", "user_id")


def scoped(*constraints):
    return (UniqueConstraint("workspace_id", "id"), *constraints)


def enum_check(field: str, values: str):
    choices = ", ".join(repr(value) for value in values.split())
    return CheckConstraint(f"{field} IN ({choices})", name=f"{field}_values")


def head(parent_table: str, versions: str, parent_field: str):
    return ForeignKeyConstraint(
        ["workspace_id", "id", "current_version_id"],
        [f"{versions}.workspace_id", f"{versions}.{parent_field}", f"{versions}.id"],
        name=f"fk_{parent_table}_current_version",
        deferrable=True,
        initially="DEFERRED",
    )


def versioned(parent_field: str, parent_table: str, *extra):
    return scoped(
        ref(parent_field, parent_table),
        UniqueConstraint("workspace_id", parent_field, "version"),
        UniqueConstraint("workspace_id", parent_field, "id"),
        CheckConstraint("version > 0", name="positive_version"),
        *extra,
    )


class User(Record, Base):
    __tablename__ = "users"
    display_name: Mapped[str] = mapped_column(String(120))
    login_name: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)


class Session(Record, Base):
    __tablename__ = "sessions"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime())


class Workspace(Record, Base):
    __tablename__ = "workspaces"
    title: Mapped[str] = mapped_column(String(200))
    goal: Mapped[str] = mapped_column(Text)
    owner_id: Mapped[str] = mapped_column(String(36))
    input_revision: Mapped[int] = mapped_column(default=1)
    current_policy_id: Mapped[str | None] = mapped_column(String(36))
    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "owner_id"],
            ["memberships.workspace_id", "memberships.user_id"],
            deferrable=True,
            initially="DEFERRED",
        ),
        ForeignKeyConstraint(
            ["id", "current_policy_id"],
            ["policy_versions.workspace_id", "policy_versions.id"],
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint("input_revision > 0", name="positive_input_revision"),
    )


class Membership(Scoped, Base):
    __tablename__ = "memberships"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(String(20))
    __table_args__ = scoped(
        UniqueConstraint("workspace_id", "user_id"), enum_check("role", "owner participant")
    )


class PolicyVersion(Scoped, Base):
    __tablename__ = "policy_versions"
    version: Mapped[int]
    required_user_ids: Mapped[list] = mapped_column(JSON)
    approval_rule: Mapped[str] = mapped_column(default="all_support_or_reservations")
    constraint_rule: Mapped[str] = mapped_column(default="all_accept")
    created_by: Mapped[str]
    __table_args__ = scoped(
        UniqueConstraint("workspace_id", "version"),
        member("created_by"),
        CheckConstraint("version > 0", name="positive_version"),
        enum_check("approval_rule", "all_support_or_reservations"),
        enum_check("constraint_rule", "all_accept"),
    )


class Idea(Scoped, Base):
    __tablename__ = "ideas"
    author_id: Mapped[str]
    current_version_id: Mapped[str | None]
    archived_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    __table_args__ = scoped(member("author_id"), head("ideas", "idea_versions", "idea_id"))


class IdeaVersion(Scoped, Base):
    __tablename__ = "idea_versions"
    idea_id: Mapped[str]
    version: Mapped[int]
    title: Mapped[str | None] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    editor_id: Mapped[str]
    previous_version_id: Mapped[str | None]
    __table_args__ = versioned(
        "idea_id",
        "ideas",
        member("editor_id"),
        ForeignKeyConstraint(
            ["workspace_id", "idea_id", "previous_version_id"],
            ["idea_versions.workspace_id", "idea_versions.idea_id", "idea_versions.id"],
            deferrable=True,
            initially="DEFERRED",
        ),
    )


class Annotation(Scoped, Base):
    __tablename__ = "annotations"
    author_id: Mapped[str]
    idea_version_id: Mapped[str]
    anchor: Mapped[str]
    span: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    current_version_id: Mapped[str | None]
    __table_args__ = scoped(
        member("author_id"),
        ref("idea_version_id", "idea_versions"),
        head("annotations", "annotation_versions", "annotation_id"),
        enum_check("anchor", "whole_idea passage"),
        CheckConstraint(
            "(anchor = 'whole_idea' AND span IS NULL) OR (anchor = 'passage' AND span IS NOT NULL)",
            name="span_matches_anchor",
        ),
    )


class AnnotationVersion(Scoped, Base):
    __tablename__ = "annotation_versions"
    annotation_id: Mapped[str]
    version: Mapped[int]
    body: Mapped[str] = mapped_column(Text)
    previous_version_id: Mapped[str | None]
    withdrawn: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = versioned(
        "annotation_id",
        "annotations",
        ForeignKeyConstraint(
            ["workspace_id", "annotation_id", "previous_version_id"],
            [
                "annotation_versions.workspace_id",
                "annotation_versions.annotation_id",
                "annotation_versions.id",
            ],
            deferrable=True,
            initially="DEFERRED",
        ),
    )


class Preference(Scoped, Base):
    __tablename__ = "preferences"
    participant_id: Mapped[str]
    current_version_id: Mapped[str | None]
    __table_args__ = scoped(
        member("participant_id"), head("preferences", "preference_revisions", "preference_id")
    )


class PreferenceRevision(Scoped, Base):
    __tablename__ = "preference_revisions"
    preference_id: Mapped[str]
    version: Mapped[int]
    statement: Mapped[str] = mapped_column(Text)
    kind: Mapped[str]
    strength: Mapped[str | None]
    status: Mapped[str]
    evidence: Mapped[list] = mapped_column(JSON)
    uncertainty_note: Mapped[str | None] = mapped_column(Text)
    created_by_user_id: Mapped[str | None]
    run_id: Mapped[str | None]
    previous_version_id: Mapped[str | None]
    __table_args__ = versioned(
        "preference_id",
        "preferences",
        member("created_by_user_id"),
        ref("run_id", "agent_runs"),
        enum_check("kind", "desire concern constraint question suggestion"),
        enum_check("strength", "nice_to_have important essential"),
        enum_check("status", "inferred confirmed corrected withdrawn"),
        ref("previous_version_id", "preference_revisions"),
    )


class Constraint(Scoped, Base):
    __tablename__ = "constraints"
    proposed_by: Mapped[str]
    current_version_id: Mapped[str | None]
    __table_args__ = scoped(
        member("proposed_by"), head("constraints", "constraint_revisions", "constraint_id")
    )


class ConstraintRevision(Scoped, Base):
    __tablename__ = "constraint_revisions"
    constraint_id: Mapped[str]
    version: Mapped[int]
    statement: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list] = mapped_column(JSON)
    previous_version_id: Mapped[str | None]
    __table_args__ = versioned(
        "constraint_id", "constraints", ref("previous_version_id", "constraint_revisions")
    )


class ConstraintResponse(Scoped, Base):
    __tablename__ = "constraint_responses"
    constraint_revision_id: Mapped[str]
    participant_id: Mapped[str]
    response: Mapped[str]
    sequence: Mapped[int]
    supersedes_id: Mapped[str | None]
    __table_args__ = scoped(
        ref("constraint_revision_id", "constraint_revisions"),
        member("participant_id"),
        ref("supersedes_id", "constraint_responses"),
        enum_check("response", "accept reject withdraw_acceptance"),
        UniqueConstraint("workspace_id", "constraint_revision_id", "participant_id", "sequence"),
        CheckConstraint("sequence > 0", name="positive_sequence"),
    )


class ConstraintSet(Scoped, Base):
    __tablename__ = "constraint_sets"
    version: Mapped[int]
    policy_version_id: Mapped[str]
    previous_set_id: Mapped[str | None]
    __table_args__ = scoped(
        ref("policy_version_id", "policy_versions"),
        ref("previous_set_id", "constraint_sets"),
        UniqueConstraint("workspace_id", "version"),
        CheckConstraint("version > 0", name="positive_version"),
    )


class ConstraintSetMember(Scoped, Base):
    __tablename__ = "constraint_set_members"
    constraint_set_id: Mapped[str]
    constraint_revision_id: Mapped[str]
    acceptance_event_ids: Mapped[list] = mapped_column(JSON)
    __table_args__ = scoped(
        ref("constraint_set_id", "constraint_sets"),
        ref("constraint_revision_id", "constraint_revisions"),
        UniqueConstraint("workspace_id", "constraint_set_id", "constraint_revision_id"),
    )


class InputSnapshot(Scoped, Base):
    __tablename__ = "input_snapshots"
    input_revision: Mapped[int]
    policy_version_id: Mapped[str]
    constraint_set_id: Mapped[str]
    idea_version_ids: Mapped[list] = mapped_column(JSON)
    annotation_version_ids: Mapped[list] = mapped_column(JSON)
    preference_revision_ids: Mapped[list] = mapped_column(JSON)
    goal: Mapped[str] = mapped_column(Text)
    manifest_hash: Mapped[str] = mapped_column(String(64))
    __table_args__ = scoped(
        ref("policy_version_id", "policy_versions"),
        ref("constraint_set_id", "constraint_sets"),
        CheckConstraint("input_revision > 0", name="positive_input_revision"),
    )


class AgentRun(Scoped, Base):
    __tablename__ = "agent_runs"
    snapshot_id: Mapped[str]
    requested_by: Mapped[str]
    request_key: Mapped[str]
    request_hash: Mapped[str] = mapped_column(String(64))
    workflow_type: Mapped[str]
    status: Mapped[str] = mapped_column(default="queued")
    provider: Mapped[str]
    model: Mapped[str]
    prompt_versions: Mapped[dict] = mapped_column(JSON)
    schema_version: Mapped[str]
    generation_settings: Mapped[dict] = mapped_column(JSON)
    retry_of: Mapped[str | None]
    token_usage: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    cost_estimate: Mapped[str | None]
    duration_ms: Mapped[int | None]
    error_code: Mapped[str | None]
    __table_args__ = scoped(
        ref("snapshot_id", "input_snapshots"),
        member("requested_by"),
        ref("retry_of", "agent_runs"),
        UniqueConstraint("workspace_id", "request_key"),
        enum_check("workflow_type", "analyze synthesize ticket_drafts"),
        enum_check("status", "queued running succeeded failed cancelled"),
    )


class AgentEvent(Scoped, Base):
    __tablename__ = "agent_events"
    run_id: Mapped[str]
    sequence: Mapped[int]
    stage: Mapped[str]
    status: Mapped[str]
    input_refs: Mapped[list] = mapped_column(JSON)
    output_json: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    validation_errors: Mapped[list | None] = mapped_column(JSON(none_as_null=True))
    duration_ms: Mapped[int | None]
    usage: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    __table_args__ = scoped(
        ref("run_id", "agent_runs"),
        UniqueConstraint("workspace_id", "run_id", "sequence"),
        CheckConstraint("sequence > 0", name="positive_sequence"),
    )


class AnalysisItem(Scoped, Base):
    __tablename__ = "analysis_items"
    run_id: Mapped[str]
    kind: Mapped[str]
    statement: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list] = mapped_column(JSON)
    uncertainty_note: Mapped[str | None] = mapped_column(Text)
    __table_args__ = scoped(
        ref("run_id", "agent_runs"),
        enum_check("kind", "shared_priority distinctive_interest tension question"),
    )


class Proposal(Scoped, Base):
    __tablename__ = "proposals"
    current_version_id: Mapped[str | None]
    created_by_type: Mapped[str]
    creator_user_id: Mapped[str | None]
    run_id: Mapped[str | None]
    published_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    __table_args__ = scoped(
        head("proposals", "proposal_versions", "proposal_id"),
        member("creator_user_id"),
        ref("run_id", "agent_runs"),
        enum_check("created_by_type", "human ai"),
    )


class ProposalVersion(Scoped, Base):
    __tablename__ = "proposal_versions"
    proposal_id: Mapped[str]
    version: Mapped[int]
    snapshot_id: Mapped[str]
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(Text)
    assumptions: Mapped[list] = mapped_column(JSON)
    exclusions: Mapped[list] = mapped_column(JSON)
    unresolved_concerns: Mapped[list] = mapped_column(JSON)
    previous_version_id: Mapped[str | None]
    created_by_user_id: Mapped[str | None]
    run_id: Mapped[str | None]
    __table_args__ = versioned(
        "proposal_id",
        "proposals",
        ref("snapshot_id", "input_snapshots"),
        ref("previous_version_id", "proposal_versions"),
        member("created_by_user_id"),
        ref("run_id", "agent_runs"),
    )


class ProposalFeature(Scoped, Base):
    __tablename__ = "proposal_features"
    proposal_version_id: Mapped[str]
    text: Mapped[str] = mapped_column(Text)
    origin: Mapped[str]
    evidence: Mapped[list] = mapped_column(JSON)
    rationale: Mapped[str] = mapped_column(Text)
    __table_args__ = scoped(
        ref("proposal_version_id", "proposal_versions"),
        enum_check("origin", "human_source combination ai_suggestion"),
    )


class ProposalValidation(Scoped, Base):
    __tablename__ = "proposal_validations"
    proposal_version_id: Mapped[str]
    constraint_set_id: Mapped[str]
    run_id: Mapped[str | None]
    checks: Mapped[list] = mapped_column(JSON)
    attribution_findings: Mapped[list] = mapped_column(JSON)
    created_by_user_id: Mapped[str | None]
    __table_args__ = scoped(
        ref("proposal_version_id", "proposal_versions"),
        ref("constraint_set_id", "constraint_sets"),
        ref("run_id", "agent_runs"),
        member("created_by_user_id"),
    )


class ReviewRound(Scoped, Base):
    __tablename__ = "review_rounds"
    proposal_version_id: Mapped[str]
    validation_id: Mapped[str]
    policy_version_id: Mapped[str]
    constraint_set_id: Mapped[str]
    opened_by: Mapped[str]
    closed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    __table_args__ = scoped(
        ref("proposal_version_id", "proposal_versions"),
        ref("validation_id", "proposal_validations"),
        ref("policy_version_id", "policy_versions"),
        ref("constraint_set_id", "constraint_sets"),
        member("opened_by"),
    )


class ReviewEvent(Scoped, Base):
    __tablename__ = "review_events"
    round_id: Mapped[str]
    participant_id: Mapped[str]
    stance: Mapped[str]
    reservations: Mapped[str | None] = mapped_column(Text)
    supersedes_id: Mapped[str | None]
    sequence: Mapped[int]
    __table_args__ = scoped(
        ref("round_id", "review_rounds"),
        member("participant_id"),
        ref("supersedes_id", "review_events"),
        UniqueConstraint("workspace_id", "round_id", "participant_id", "sequence"),
        CheckConstraint("sequence > 0", name="positive_sequence"),
        enum_check("stance", "support support_with_reservations request_changes oppose abstain"),
        CheckConstraint(
            "stance != 'support_with_reservations' OR "
            "(reservations IS NOT NULL AND length(trim(reservations)) > 0)",
            name="reservation_required",
        ),
    )


class Decision(Scoped, Base):
    __tablename__ = "decisions"
    round_id: Mapped[str]
    proposal_version_id: Mapped[str]
    policy_version_id: Mapped[str]
    constraint_set_id: Mapped[str]
    review_event_ids: Mapped[list] = mapped_column(JSON)
    recorded_by: Mapped[str]
    rationale: Mapped[str] = mapped_column(Text)
    reservations_snapshot: Mapped[list] = mapped_column(JSON)
    __table_args__ = scoped(
        ref("round_id", "review_rounds"),
        ref("proposal_version_id", "proposal_versions"),
        ref("policy_version_id", "policy_versions"),
        ref("constraint_set_id", "constraint_sets"),
        member("recorded_by"),
        UniqueConstraint("workspace_id", "round_id"),
    )


class TicketDraft(Scoped, Base):
    __tablename__ = "ticket_drafts"
    decision_id: Mapped[str]
    current_version_id: Mapped[str | None]
    __table_args__ = scoped(
        ref("decision_id", "decisions"),
        head("ticket_drafts", "ticket_draft_revisions", "ticket_draft_id"),
    )


class TicketDraftRevision(Scoped, Base):
    __tablename__ = "ticket_draft_revisions"
    ticket_draft_id: Mapped[str]
    version: Mapped[int]
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    acceptance_criteria: Mapped[list] = mapped_column(JSON)
    proposal_feature_ids: Mapped[list] = mapped_column(JSON)
    edited_by: Mapped[str | None]
    run_id: Mapped[str | None]
    __table_args__ = versioned(
        "ticket_draft_id", "ticket_drafts", member("edited_by"), ref("run_id", "agent_runs")
    )


class TicketBatch(Scoped, Base):
    __tablename__ = "ticket_batches"
    decision_id: Mapped[str]
    repository_owner: Mapped[str]
    repository_name: Mapped[str]
    request_key: Mapped[str]
    payload_hash: Mapped[str] = mapped_column(String(64))
    authorized_by: Mapped[str]
    __table_args__ = scoped(
        ref("decision_id", "decisions"),
        member("authorized_by"),
        UniqueConstraint("workspace_id", "request_key"),
    )


class TicketBatchItem(Scoped, Base):
    __tablename__ = "ticket_batch_items"
    batch_id: Mapped[str]
    ticket_draft_revision_id: Mapped[str]
    repository_owner: Mapped[str]
    repository_name: Mapped[str]
    export_marker: Mapped[str] = mapped_column(unique=True)
    state: Mapped[str] = mapped_column(default="pending")
    github_issue_id: Mapped[int | None]
    github_issue_number: Mapped[int | None]
    github_issue_url: Mapped[str | None]
    last_error: Mapped[str | None] = mapped_column(Text)
    __table_args__ = scoped(
        ref("batch_id", "ticket_batches"),
        ref("ticket_draft_revision_id", "ticket_draft_revisions"),
        UniqueConstraint("ticket_draft_revision_id", "repository_owner", "repository_name"),
        enum_check("state", "pending sending published failed unknown"),
        CheckConstraint(
            "state != 'published' OR (github_issue_id IS NOT NULL AND "
            "github_issue_number IS NOT NULL AND github_issue_url IS NOT NULL)",
            name="published_issue_required",
        ),
    )


class TicketAttempt(Scoped, Base):
    __tablename__ = "ticket_attempts"
    item_id: Mapped[str]
    attempt: Mapped[int]
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    outcome: Mapped[str | None]
    http_status: Mapped[int | None]
    error_code: Mapped[str | None]
    __table_args__ = scoped(
        ref("item_id", "ticket_batch_items"),
        UniqueConstraint("workspace_id", "item_id", "attempt"),
        CheckConstraint("attempt > 0", name="positive_attempt"),
    )


# Migration installs UPDATE/DELETE guards for historical rows. Mutable heads,
# run status, closed_at, and external attempt outcomes remain separately writable.
IMMUTABLE_TABLES = (
    "policy_versions",
    "idea_versions",
    "annotation_versions",
    "preference_revisions",
    "constraint_revisions",
    "constraint_responses",
    "constraint_sets",
    "constraint_set_members",
    "input_snapshots",
    "agent_events",
    "analysis_items",
    "proposal_versions",
    "proposal_features",
    "proposal_validations",
    "review_events",
    "decisions",
    "ticket_draft_revisions",
    "ticket_batches",
)
