# FeedbackForm versioned data contracts

Status: Foundational schemas implemented, 2026-10-15. SQLAlchemy records are in
`backend/app/db/models.py`; strict command and workflow boundaries are in
`backend/app/api/schemas.py`. The initial migration installs composite foreign
keys and immutable-history triggers. Authenticated workspace reads, idea
creation/versioned editing, and history are exposed; session and workspace-view
boundaries are in `backend/app/api/workspace_schemas.py`. Whole-idea and passage
annotation creation/listing are implemented in `backend/app/api/annotations.py`.
Comment edit/withdrawal and later feature transitions remain unimplemented.
Preference extraction/review routes now snapshot current inputs, validate original
evidence and participant attribution, and append inferred or human-authored
preference revisions. `backend/app/api/preferences.py` owns these transitions;
the OpenAI wire schema is in `backend/app/domain/extraction.py`. Subsequent runs
receive the latest correction/withdrawal heads. Invalid or stale results roll
back atomically; the snapshot and failed run remain available for audit.
The initial workspace and four identities can be provisioned through the frontend
using the validated `PilotSetup` command; this is disabled once any account or
workspace exists. It commits all records and the owner's session atomically.
See [architecture.md](architecture.md) for the selected stack and execution plan.

## Shared types and enforcement

IDs are server-generated UUID strings. Timestamps are UTC RFC 3339 strings.
Version/revision numbers are positive integers. Enum values below are exact
wire values. Every workspace-owned record carries `workspace_id`, even when not
repeated in the compact field lists below. Join tables enforce references within
the same workspace through composite foreign keys or equivalent checked writes.

Pydantic boundary models forbid unknown fields, validate enums and limits, and
distinguish omitted values from null. Relational checks verify source existence,
workspace, version, actor permissions, and current state before commit. JSON
syntax or a model's self-reported confidence cannot establish semantic correctness.
Text limits, collection limits, and schema versions are explicit in executable
boundary models. The frontend derives types from the API's OpenAPI
schema rather than maintaining a second set of independent contracts.

`EvidenceRef` is a discriminated union:

- `idea_span`: `idea_version_id`, optional `start_utf16`, `end_utf16`, `quote`,
  `prefix`, `suffix`. Without offsets it references the complete version.
- `annotation`: `annotation_version_id`; use the comment author's identity for
  attribution, not the author of the idea being discussed.
- `preference`: `preference_revision_id`; the revision links to original evidence.
- `constraint`: `constraint_revision_id`; this identifies an accepted or proposed
  constraint without treating the reference itself as proof of acceptance.

Span offsets use half-open UTF-16 code-unit positions in the exact stored text,
matching browser selection. The backend must convert before slicing Python text
and check that the slice equals `quote`, including emoji/multiline cases. Never
normalize line endings or Unicode after storing a referenced version.

## Identity, workspace, and policy

| Record | Fields beyond shared IDs/timestamps | Rules |
| --- | --- | --- |
| `users` | `display_name`, `login_name`, `password_hash` | Login names unique; secrets/hashes excluded from API responses and AI context. |
| `sessions` | `user_id`, `token_hash`, `expires_at`, `revoked_at?` | Server generated; never trust an actor ID in a request body. |
| `workspaces` | `title`, `goal`, `owner_id`, `input_revision`, `current_policy_id` | Owner must be a member; content/policy changes atomically advance input revision. |
| `memberships` | `user_id`, `role: owner\|participant`, `joined_at` | Unique workspace/user; exactly four required participants for this pilot, one owner. |
| `policy_versions` | `version`, `required_user_ids[4]`, `approval_rule: all_support_or_reservations`, `constraint_rule: all_accept`, `created_by` | Immutable roster/rule snapshot; only owner may start a policy change. No model can author human approvals. |

Workspace creation and its owner membership must commit together. Authorization
depends on the authenticated actor plus membership, not the presence of a UUID.
Policy changes invalidate active review rounds; required roster stays fixed in
the first pilot once reviewing starts.

## Human-authored source records

| Record | Fields | Rules |
| --- | --- | --- |
| `ideas` | `author_id`, `current_version_id`, `archived_at?` | Stable identity; archiving changes active inputs without deleting evidence. |
| `idea_versions` | `idea_id`, `version`, `title?`, `body`, `editor_id`, `previous_version_id?` | Immutable; unique idea/version; pilot edits limited to author. |
| `annotations` | `author_id`, `idea_version_id`, `anchor: whole_idea\|passage`, `span?`, `current_version_id` | Always references an immutable idea version; passage spans require a verified quote. |
| `annotation_versions` | `annotation_id`, `version`, `body`, `previous_version_id?`, `withdrawn: boolean` | Immutable; only author edits/withdraws; retains original anchor. |

Implemented annotation behavior: do not auto-migrate annotations onto edited text. Show the source version and
an explicit historical-anchor label. An optional relocation is a new, verified
anchor and cannot rewrite old evidence. No threaded replies or reactions are
required by these contracts.

The annotation response returns the exact immutable `source_body`, numeric source
version, quote/span, author, timestamp, and whether the source differs from the
idea's current head. The UI highlights only spans whose source is the displayed
version. Mouse selection uses DOM ranges; the keyboard path finds exact matching
excerpts with surrounding context and maps normalized LF search offsets back to
source CRLF offsets without rewriting stored text. The complete
immutable body provides surrounding context even when prefix/suffix are empty.

## Preferences and binding constraints

| Record | Fields | Rules |
| --- | --- | --- |
| `preferences` | `participant_id`, `current_revision_id` | Stable participant-owned interpretation. |
| `preference_revisions` | `preference_id`, `revision`, `statement`, `kind: desire\|concern\|constraint\|question\|suggestion`, `strength?: nice_to_have\|important\|essential`, `status: inferred\|confirmed\|corrected\|withdrawn`, `evidence: EvidenceRef[]`, `uncertainty_note?`, `created_by_user_id?`, `run_id?`, `previous_revision_id?` | Inferred records come from runs; only the named participant can confirm, correct, set strength, or withdraw. At least one original idea/comment reference is required. |
| `constraints` | `proposed_by`, `current_revision_id` | Independent from the preference record; an essential preference is not automatically binding. |
| `constraint_revisions` | `constraint_id`, `revision`, `statement`, `evidence: EvidenceRef[]`, `previous_revision_id?` | Immutable wording; can be a group-authored requirement without an extracted preference. |
| `constraint_responses` | `constraint_revision_id`, `participant_id`, `response: accept\|reject\|withdraw_acceptance`, `supersedes_id?` | Append-only events; latest response per participant and exact revision counts. No response is not acceptance. |
| `constraint_sets` | `version`, `policy_version_id`, `previous_set_id?` | Immutable set of currently accepted constraint revisions. |
| `constraint_set_members` | `constraint_set_id`, `constraint_revision_id`, `acceptance_event_ids[4]` | Acceptances must be from all four required participants for that exact revision. |

Corrections append a revision and change the current pointer; previous text is
historical, not an additional active preference. Validate ownership through the
original sources rather than accepting model-supplied participant IDs unchecked.

A revised constraint requires four new acceptances. Any acceptance withdrawal
updates the current constraint set and invalidates active validation/review rounds.
Removing an accepted constraint requires all four to approve removal, except a
withdrawal immediately stops treating its unanimous acceptance as current. Record
the event and preserve older sets for historical decisions.

## Runs, snapshots, and analysis

| Record | Fields | Rules |
| --- | --- | --- |
| `input_snapshots` | `input_revision`, `policy_version_id`, `constraint_set_id`, `idea_version_ids`, `annotation_version_ids`, `preference_revision_ids`, `goal`, `manifest_hash` | Immutable manifest assembled from one consistent read; ordered canonical serialization for hashing. |
| `agent_runs` | `snapshot_id`, `requested_by`, `request_key`, `request_hash`, `workflow_type: analyze\|synthesize\|ticket_drafts`, `status: queued\|running\|succeeded\|failed\|cancelled`, `provider`, `model`, `prompt_versions`, `schema_version`, `generation_settings`, `retry_of?`, `token_usage?`, `cost_estimate?`, `duration_ms?`, `error_code?` | Unique workspace/request key; identical retry resolves to the same run, changed payload conflicts. A fresh run gets a fresh key. |
| `agent_events` | `run_id`, `sequence`, `stage`, `status`, `input_refs`, `output_json?`, `validation_errors?`, `duration_ms?`, `usage?` | Append-only, ordered per run; redact secrets and sensitive logs. |
| `analysis_items` | `run_id`, `kind: shared_priority\|distinctive_interest\|tension\|question`, `statement`, `evidence: EvidenceRef[]`, `uncertainty_note?` | Source-backed observations, not votes or confirmations; must reference the run's input manifest. |

Workflow envelope: `schema_version`, `run_id`, `snapshot_id`, `stage`, `payload`.
Envelope IDs are supplied/checked by the orchestrator, not trusted from generation.
Stage payloads are:

- Interpreter: `preferences[]` containing proposed participant, statement, kind,
  evidence, and uncertainty. The server assigns IDs and inferred status; the
  model cannot emit confirmations or group acceptance.
- Analyst: `items[]` with analysis-item kinds, statements, and evidence.
- Synthesis: exactly two `candidates[]`, each with title, summary, scope, assumptions,
  exclusions, unresolved concerns, and features using the origin rules below.
- Critic: `constraint_checks[]`, `attribution_findings[]`, `unresolved_concerns[]`,
  and `recommendation: ready_for_human_review\|revise\|infeasible\|needs_clarification`.
  Critic readiness is not participant approval.

Freshness is derived by comparing the snapshot revision and current inputs, not
by trusting a stored model assertion. A conservative stale flag does not delete
outputs. New runs use current corrected preferences; historical references remain
inspectable only to authorized users under the source's current visibility rules.

## Proposals, review rounds, and decisions

| Record | Fields | Rules |
| --- | --- | --- |
| `proposals` | `current_version_id`, `created_by_type: human\|ai`, `creator_user_id?`, `run_id?` | Stable candidate identity; generated drafts are distinct from shared candidates. |
| `proposal_versions` | `proposal_id`, `version`, `snapshot_id`, `title`, `summary`, `scope`, `assumptions[]`, `exclusions[]`, `unresolved_concerns[]`, `previous_version_id?`, `created_by_user_id?`, `run_id?` | Immutable content; edits create a version. |
| `proposal_features` | `proposal_version_id`, `text`, `origin: human_source\|combination\|ai_suggestion`, `evidence: EvidenceRef[]`, `rationale` | Human-source/combination origins need supporting human evidence; novel additions are explicitly AI suggestions, even if inspired by existing sources. |
| `proposal_validations` | `proposal_version_id`, `constraint_set_id`, `run_id?`, `checks[]`, `attribution_findings[]`, `created_by_user_id?` | Immutable result; each check identifies a constraint revision, status, method, evidence, and rationale. |
| `review_rounds` | `proposal_version_id`, `validation_id`, `policy_version_id`, `constraint_set_id`, `opened_by`, `opened_at`, `closed_at?` | Frozen review context; opened by owner after publication and validation. |
| `review_events` | `round_id`, `participant_id`, `stance: support\|support_with_reservations\|request_changes\|oppose\|abstain`, `reservations?`, `supersedes_id?` | Append-only; participant authors their own response. Latest event per required participant counts. Reservations required for support-with-reservations. |
| `decisions` | `round_id`, `proposal_version_id`, `policy_version_id`, `constraint_set_id`, `review_event_ids[4]`, `recorded_by`, `rationale`, `reservations_snapshot`, `decided_at` | Immutable; one accepted decision per round, recorded by workspace owner. Captures exact evidence, not mutable pointers. |

Constraint-check status is `verified`, `estimated`, `violated`, or `unknown`.
Method is `deterministic`, `model`, or `human`. Model-only findings cannot claim
deterministic verification. `estimated` and `unknown` require an explicit owner
assessment with rationale before finalization; the assessment is stored as human
evidence, not a rewrite of the model result. Known violations and incompatible
binding constraints block acceptance until people revise the proposal or constraints.

Before recording a decision in one short transaction, verify:

1. Authenticated actor is the owner; proposal is published and the reviewed version
   is still its current head.
2. Round policy/roster and constraint set still match current values; source input
   freshness and validation remain valid. Changed context requires a new round.
3. Exactly four distinct required participants have current review events for this
   round, each `support` or `support_with_reservations`.
4. Constraint checks cover the complete accepted set and there is no unresolved
   violation or unsupported attribution; uncertain checks have recorded human assessment.
5. Store the decision with exact review-event IDs and reservations atomically.

A revised proposal, policy, or constraint set cannot inherit votes. A changed
review after a recorded decision does not rewrite that historical decision;
show subsequent withdrawal/dissent and require a new decision for a new endorsement.
Ticket publication rechecks current support and context, so an old decision alone
cannot authorize new external work after withdrawal.

## Ticket drafts, authorization, and external results

| Record | Fields | Rules |
| --- | --- | --- |
| `ticket_drafts` | `decision_id`, `current_revision_id` | Only accepted proposals can supply implementation tickets. |
| `ticket_draft_revisions` | `ticket_draft_id`, `revision`, `title`, `description`, `acceptance_criteria[]`, `proposal_feature_ids[]`, `edited_by?`, `run_id?` | Immutable preview content; no automatic assignment or private feedback export. |
| `ticket_batches` | `decision_id`, `repository_owner`, `repository_name`, `request_key`, `payload_hash`, `authorized_by`, `authorized_at` | Owner authorizes exact content/destination; key reuse with a different payload is rejected. No credentials in this record. |
| `ticket_batch_items` | `batch_id`, `ticket_draft_revision_id`, `export_marker`, `state: pending\|sending\|published\|failed\|unknown`, `github_issue_id?`, `github_issue_number?`, `github_issue_url?`, `last_error?` | Unique draft revision per repository; marker unique; external IDs required when published. |
| `ticket_attempts` | `item_id`, `attempt`, `started_at`, `finished_at?`, `outcome?`, `http_status?`, `error_code?` | Preserve network history; tokens and authorization headers are never logged. |

The server snapshots a complete payload before authorization. A draft revision or
repository change cannot mutate an authorized batch. A repeated click reuses its
request key and published items; `sending` at process interruption becomes `unknown`.
Do not create a new issue until ambiguous outcomes have been reconciled as described
in [architecture.md](architecture.md). Exported artifacts reference exact decision
and proposal IDs; their existence does not mean later proposal versions are approved.

## Verification obligations for implementation

SQLAlchemy storage uses `version` and `current_version_id` consistently, including
records called revisions above. The common UTC `created_at` field represents
joined/opened/authorized/decided/start times; mutable terminal timestamps retain
their own fields. Review and constraint events include an explicit sequence to
order a participant's responses without relying on timestamp ties. Ticket batch
items also retain their repository to enforce draft/destination uniqueness.

Executable schemas and migrations cover the records above. SQL checks enforce
scoped foreign keys, uniqueness, enums, and append-only historical records, not
the meaning of JSON evidence or permission to approve a decision. The initial
domain helpers check idea edit ownership, stale edits, source existence/scope,
participant attribution, snapshot evidence membership, and UTF-16 anchors.
Tests cover those foundation paths. Complete request-time validation and tests
for confirmation, snapshots, constraint withdrawal, review revision, decision
races, and partial/ambiguous ticket publication as each feature service is added.
Do not expose write routes before their authentication and domain checks exist.
