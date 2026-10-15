"""Strict human-command and model-output boundaries; actors come from sessions."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

ShortText = Annotated[str, StringConstraints(min_length=1, max_length=200, pattern=r"\S")]
Body = Annotated[str, StringConstraints(min_length=1, max_length=20_000, pattern=r"\S")]
Note = Annotated[str, StringConstraints(min_length=1, max_length=2_000, pattern=r"\S")]
Positive = Annotated[int, Field(strict=True, gt=0)]
Stance = Literal["support", "support_with_reservations", "request_changes", "oppose", "abstain"]
PreferenceKind = Literal["desire", "concern", "constraint", "question", "suggestion"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Span(Contract):
    start_utf16: Annotated[int, Field(strict=True, ge=0)]
    end_utf16: Annotated[int, Field(strict=True, gt=0)]
    quote: Body
    prefix: Annotated[str, Field(max_length=200)] = ""
    suffix: Annotated[str, Field(max_length=200)] = ""

    @model_validator(mode="after")
    def ordered(self):
        if self.end_utf16 <= self.start_utf16:
            raise ValueError("Span end must follow start")
        return self


class IdeaEvidence(Contract):
    kind: Literal["idea_span"]
    idea_version_id: UUID
    span: Span | None = None


class AnnotationEvidence(Contract):
    kind: Literal["annotation"]
    annotation_version_id: UUID


class PreferenceEvidence(Contract):
    kind: Literal["preference"]
    preference_revision_id: UUID


class ConstraintEvidence(Contract):
    kind: Literal["constraint"]
    constraint_revision_id: UUID


EvidenceRef = Annotated[
    IdeaEvidence | AnnotationEvidence | PreferenceEvidence | ConstraintEvidence,
    Field(discriminator="kind"),
]
Evidence = Annotated[list[EvidenceRef], Field(min_length=1, max_length=100)]


class IdeaCreate(Contract):
    title: ShortText | None = None
    body: Body


class IdeaEdit(IdeaCreate):
    expected_version_id: UUID


class AnnotationCreate(Contract):
    idea_version_id: UUID
    anchor: Literal["whole_idea", "passage"]
    span: Span | None = None
    body: Body

    @model_validator(mode="after")
    def anchor_shape(self):
        if (self.anchor == "passage") != (self.span is not None):
            raise ValueError("Only passage annotations require a span")
        return self


class PreferenceSuggestion(Contract):
    participant_id: UUID
    statement: Note
    kind: PreferenceKind
    evidence: Evidence
    uncertainty_note: Note | None = None

    @model_validator(mode="after")
    def original_source(self):
        if not any(isinstance(ref, (IdeaEvidence, AnnotationEvidence)) for ref in self.evidence):
            raise ValueError("Preference extraction requires original human evidence")
        return self


class PreferenceCorrection(Contract):
    expected_revision_id: UUID
    statement: Note
    kind: PreferenceKind
    strength: Literal["nice_to_have", "important", "essential"] | None = None
    action: Literal["confirm", "correct", "withdraw"]


class ConstraintDraft(Contract):
    statement: Note
    evidence: Annotated[list[EvidenceRef], Field(max_length=100)] = Field(default_factory=list)


class ConstraintResponseCreate(Contract):
    constraint_revision_id: UUID
    response: Literal["accept", "reject", "withdraw_acceptance"]
    expected_sequence: Annotated[int, Field(strict=True, ge=0)]


class PolicyContract(Contract):
    required_user_ids: Annotated[list[UUID], Field(min_length=4, max_length=4)]
    approval_rule: Literal["all_support_or_reservations"] = "all_support_or_reservations"
    constraint_rule: Literal["all_accept"] = "all_accept"

    @model_validator(mode="after")
    def distinct_roster(self):
        if len(set(self.required_user_ids)) != 4:
            raise ValueError("Exactly four distinct participants are required")
        return self


class AnalysisSuggestion(Contract):
    kind: Literal["shared_priority", "distinctive_interest", "tension", "question"]
    statement: Note
    evidence: Evidence
    uncertainty_note: Note | None = None


class FeatureDraft(Contract):
    text: Note
    origin: Literal["human_source", "combination", "ai_suggestion"]
    evidence: Annotated[list[EvidenceRef], Field(max_length=100)] = Field(default_factory=list)
    rationale: Note

    @model_validator(mode="after")
    def attributed_source(self):
        if self.origin != "ai_suggestion" and not any(
            isinstance(ref, (IdeaEvidence, AnnotationEvidence, PreferenceEvidence))
            for ref in self.evidence
        ):
            raise ValueError("Attributed features require human-source evidence")
        return self


class CandidateDraft(Contract):
    title: ShortText
    summary: Note
    scope: Body
    assumptions: Annotated[list[Note], Field(max_length=30)]
    exclusions: Annotated[list[Note], Field(max_length=30)]
    unresolved_concerns: Annotated[list[Note], Field(max_length=100)]
    features: Annotated[list[FeatureDraft], Field(min_length=1, max_length=30)]


class ConstraintCheck(Contract):
    constraint_revision_id: UUID
    status: Literal["verified", "estimated", "violated", "unknown"]
    method: Literal["deterministic", "model", "human"]
    evidence: Annotated[list[EvidenceRef], Field(max_length=100)]
    rationale: Note

    @model_validator(mode="after")
    def model_cannot_verify(self):
        if self.method == "model" and self.status == "verified":
            raise ValueError("Model judgment cannot claim verified constraint satisfaction")
        return self


class AttributionFinding(Contract):
    feature_index: Annotated[int, Field(strict=True, ge=0, lt=30)]
    candidate_index: Literal[0, 1]
    explanation: Note
    evidence: Annotated[list[EvidenceRef], Field(max_length=100)]


class InterpretOutput(Contract):
    preferences: Annotated[list[PreferenceSuggestion], Field(max_length=200)]


class AnalyzeOutput(Contract):
    items: Annotated[list[AnalysisSuggestion], Field(max_length=100)]


class SynthesizeOutput(Contract):
    candidates: Annotated[list[CandidateDraft], Field(min_length=2, max_length=2)]


class CritiqueOutput(Contract):
    constraint_checks: Annotated[list[ConstraintCheck], Field(max_length=200)]
    attribution_findings: Annotated[list[AttributionFinding], Field(max_length=100)]
    unresolved_concerns: Annotated[list[Note], Field(max_length=100)]
    recommendation: Literal["ready_for_human_review", "revise", "infeasible", "needs_clarification"]


class ReviewCreate(Contract):
    round_id: UUID
    stance: Stance
    reservations: Note | None = None
    expected_sequence: Annotated[int, Field(strict=True, ge=0)]

    @model_validator(mode="after")
    def reservation_required(self):
        if self.stance == "support_with_reservations" and (
            self.reservations is None or not self.reservations.strip()
        ):
            raise ValueError("Support with reservations requires an explanation")
        return self


class DecisionCreate(Contract):
    round_id: UUID
    expected_input_revision: Positive
    rationale: Note


class TicketDraftContent(Contract):
    title: ShortText
    description: Body
    acceptance_criteria: Annotated[list[Note], Field(min_length=1, max_length=30)]
    proposal_feature_ids: Annotated[list[UUID], Field(max_length=30)]


class TicketPublish(Contract):
    decision_id: UUID
    ticket_draft_revision_ids: Annotated[list[UUID], Field(min_length=1, max_length=30)]
    repository_owner: Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}$")]
    repository_name: Annotated[str, Field(pattern=r"^[A-Za-z0-9_.-]{1,100}$")]
    request_key: UUID
    payload_hash: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

    @model_validator(mode="after")
    def distinct_drafts(self):
        if len(set(self.ticket_draft_revision_ids)) != len(self.ticket_draft_revision_ids):
            raise ValueError("Duplicate draft revisions are not allowed")
        return self


class SnapshotContract(Contract):
    input_revision: Positive
    policy_version_id: UUID
    constraint_set_id: UUID
    idea_version_ids: Annotated[list[UUID], Field(max_length=200)]
    annotation_version_ids: Annotated[list[UUID], Field(max_length=1000)]
    preference_revision_ids: Annotated[list[UUID], Field(max_length=1000)]
    goal: Note


class InterpretEnvelope(Contract):
    schema_version: Literal["1"]
    run_id: UUID
    snapshot_id: UUID
    stage: Literal["interpret"]
    payload: InterpretOutput


class AnalyzeEnvelope(Contract):
    schema_version: Literal["1"]
    run_id: UUID
    snapshot_id: UUID
    stage: Literal["analyze"]
    payload: AnalyzeOutput


class SynthesizeEnvelope(Contract):
    schema_version: Literal["1"]
    run_id: UUID
    snapshot_id: UUID
    stage: Literal["synthesize"]
    payload: SynthesizeOutput


class CritiqueEnvelope(Contract):
    schema_version: Literal["1"]
    run_id: UUID
    snapshot_id: UUID
    stage: Literal["critique"]
    payload: CritiqueOutput


WorkflowEnvelope = Annotated[
    InterpretEnvelope | AnalyzeEnvelope | SynthesizeEnvelope | CritiqueEnvelope,
    Field(discriminator="stage"),
]
