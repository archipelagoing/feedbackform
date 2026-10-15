# FeedbackForm TODO

Last updated: 2026-10-15.

Current state: Authenticated idea capture works. A one-time CLI provisions four
participants; the web app supports cookie login/logout, a shared workspace,
attributed ideas, author-only versioned editing, and history. Membership, Origin,
CSRF, session expiry, and stale edits are checked on the backend. The foundation
has 32 tables, strict schemas, migrations, and pinned dependencies. 31 backend
tests and five browser tests pass, as do typecheck, production build, and Ruff.
Annotations, AI runs, proposal reviews/decisions, and GitHub publication remain
unimplemented. The next milestone is a constrained,
four-participant workflow from ideas and feedback to reviewed proposals, with a
real ticketing integration. Course dates follow [project-requirements.pdf](project-requirements.pdf),
per the user's clarification: proposal November 12, final presentation December 3,
and final report December 17, 2026. The earlier November 22 deadline is superseded.
GitHub Issues creation from approved proposals is selected;
ticket imports and bidirectional status sync are deferred.

## Maintenance instructions

- Use this file as the authoritative project checklist. `todoSimple.md` is the
  reusable template; `SHOW_BIBLE.md` and `rubricatm.md` also contain templates.
  Product intent lives in `projBible.md`.
- Mark `[x]` only when the stated outcome has evidence. Leave unverified work
  unchecked and explain its status in the relevant progress note.
- After authorized work changes project state, update affected tasks, progress
  notes, next steps, and the date. Preserve unrelated tasks and user edits.
- Keep each task in one section. Next steps summarize priorities rather than
  duplicating checkboxes. Record reasons for scope changes or deferrals.
- Listing work here does not authorize executing the entire backlog, publishing,
  or deploying. Do not store credentials or personal feedback in this checklist.

## Next steps

1. Add whole-idea and anchored passage comments with author attribution and
   immutable source-version references in section 3.
2. Define the primary evaluation question and initial labeled cases in section 7
   before prompt tuning.
3. Verify comment anchoring after idea edits and keyboard-accessible commenting
   in section 3.
4. Connect extraction and human correction in section 4, then two-candidate
   synthesis in section 5.

The user accepted the MVP and pilot rules on 2026-10-15. Stack and versioned data
contracts are now defined in `docs/architecture.md` and `docs/data-model.md`.
Evaluation design and delivery environment remain open. Team registration is
expected to be handled by October 22 at 3pm but has not been verified; prepare
the November 12 proposal in parallel. Assemble evaluation examples alongside
the first implementation rather than at the end.

## 1. Define the pilot and freeze scope

- [x] Document the problem, initial users, and intended outcome in
  `projBible.md` §§1–5 and §14.
- [x] Document invariants covering original voice, explicit human support,
  unresolved disagreement, and source attribution in `projBible.md` §3.
- [x] Extract course dates and formats from `project-requirements.pdf`, page 1.
  The user instructed us to follow the PDF on 2026-10-15; this supersedes the
  earlier November 22 deadline. See the course milestones below. Timezone is
  not stated in the PDF.
- [x] Record the user's answer about required model training/fine-tuning: “no”
  (2026-10-15), interpreted as no mandatory training/fine-tuning. Plan for evaluated
  LLM orchestration; the answer does not establish all course grading criteria.
- [x] Record submission formats and listed points from the PDF: proposal writeup
  10, final presentation 10, report 20. Research and application avenues share
  the score breakdown; the PDF does not specify a separate proposal-presentation score.
- [x] Check explicit technical requirements: an open-access project GitHub
  repository link is required in the report. Model training/fine-tuning and a
  hosted deployment are not explicitly mandated by this PDF.
- [ ] Confirm submission timezone and check Canvas/instructor guidance for any
  additional grading, deployment, or submission requirements not stated in the PDF.
- [x] Establish real ticketing integration as a required first-release capability
  (user requirement, 2026-10-15). This confirms scope intent, not implementation.
- [x] Choose one initial ticketing provider and integration direction: approved
  proposal → reviewed implementation tickets → GitHub Issues (user selection,
  2026-10-15). Ticket import and bidirectional status sync are deferred.
- [x] Agree on the first-release contract: four controlled participant accounts,
  one workspace, plain-text ideas, passage comments, preference correction,
  two distinct candidate proposals, explicit reviews, a decision export, and one
  real ticketing integration.
  Accepted by the user on 2026-10-15; the bible's MVP list is reconciled.
- [x] Choose the pilot approval rule: all four participants must explicitly
  support or support with reservations (user selection, 2026-10-15). Reservations
  remain visible. Missing responses, abstention, requests for changes, and
  opposition do not satisfy this rule.
- [x] Finalize review states: support, support with reservations, request changes,
  oppose, abstain. The workspace owner records a decision after the four-person
  approval rule passes (user acceptance, 2026-10-15).
- [x] Define binding constraints: all four explicitly accept a requirement before
  it binds the group. Incompatible constraints require human revision; AI cannot
  silently relax them (user acceptance, 2026-10-15).
- [x] Define correction and publication rules: material interpretations need
  confirmation before becoming binding; generated candidates remain drafts
  until a human chooses to share them for review.
- [x] Agree on exclusions: PDF/OCR import, live collaborative editing, visual
  graphs, anonymous feedback, additional integrations, optimization of utilities,
  and full task management stay outside the first release. Ticket import and
  bidirectional sync are deferred under the selected outbound-only integration.

Progress: Product intent is documented, not validated with the pilot group.
The user selected the PDF as the schedule authority, superseding November 22,
and required outbound GitHub Issues creation from approved proposals.
The user also selected all-four support/support-with-reservations and answered
“no” to the course training/fine-tuning question. The PDF does not explicitly
require training or deployment. On 2026-10-15 the user accepted the MVP, owner
decision authority, all-four constraint acceptance, and human correction and
ticket review rules. Course clarifications remain open; registration and other
future actions have not been marked completed.

### Pilot rules — agreed 2026-10-15

These rules define intended behavior; implementation is still outstanding.

- Reviews: support, support with reservations, request changes,
  oppose, or abstain.
  All four participants review the exact proposal version. Approval requires all
  four to support or support with reservations; reservations stay visible.
  Missing responses, abstention, requests for changes, or opposition prevent
  approval under the confirmed rule. Reviews apply to the exact proposal version;
  implementing version binding remains unfinished work in section 2.
- Authority: the workspace owner records a decision only when the
  rule passes. AI cannot submit reviews, adopt constraints, or finalize decisions.
- Constraints: personal confirmation establishes what someone means; all four
  must explicitly accept a requirement before it becomes binding on the workspace.
  Incompatible accepted constraints halt approval until people revise them.
- Corrections: participants control their own preference interpretations.
  Corrections create history and invalidate affected analysis. Source edits and
  changed constraints require fresh validation and review before finalization.
- Publication: generated proposals and ticket breakdowns begin as drafts. A human
  reviews the exact content and destination before any external ticket creation.
  No ticketing credentials or live destination are needed to settle these rules.

### Course milestones — PDF requirements

Source: `project-requirements.pdf`, page 1, CS541A Fall 2026. Times are reproduced
as written; timezone is unspecified. These tasks are tracked in section 8.

| Milestone | Due / event | Required format |
| --- | --- | --- |
| Team formation | October 22, 3pm | One teammate fills in team information on Canvas. |
| Proposal presentation | November 12 in lecture; upload by 3pm | At most 5 minutes: problem, existing solutions, proposed solution. |
| Proposal writeup — 10 points | November 12, 3pm | PDF, at most 2 pages; essentially the presentation's content. |
| Final presentation — 10 points | December 3 in lecture; upload by 3pm | At most 5 minutes: problem, solution, and how well it addresses the problem. |
| Final report — 20 points | December 17, 23:59 | Official ACL format, PDF, at most 4 main pages plus unlimited references and appendix; include an open-access project GitHub repository link. |

### Proposed delivery checkpoints

These are internal planning targets, not additional course deadlines. Ownership
and feasibility still need team review. November 22 is no longer a course deadline.

- October 18: resolve section 1 policies, provider, scope, and evaluation target.
- October 25: working persistent workspace, comments, and preference correction.
- November 1: two-candidate synthesis, lineage, and constraint critique.
- November 8: versioned human review, decision recording, and ticket integration
  working against a real provider in a controlled test destination.
- November 10: proposal slides and two-page writeup ready for review ahead of
  the November 12 submissions.
- November 22: proposed internal target for the four-person pilot and initial
  held-out evaluation, leaving time to fix failures before the final presentation.
- December 1: final slides, results, and clean-environment demo rehearsal ready.
- December 15: ACL report and public-repository checks ready for final review.

## 2. Establish data contracts and a runnable foundation

- [x] Select and record the pilot stack and supported environment in
  [architecture.md](docs/architecture.md): Next.js/TypeScript, FastAPI/Pydantic,
  SQLite/SQLAlchemy/Alembic, and explicit Python workflow stages. Start with a
  local desktop Chromium pilot; hosting remains open.
- [x] Define record contracts for source references, preferences, constraints,
  themes/tensions, proposal features, reviews, decisions, and workflow events.
  Distinguish inferred preferences, participant confirmation, and group acceptance.
  See [data-model.md](docs/data-model.md) and the corresponding backend models/schemas.
- [x] Implement Pydantic boundary schemas, relational models, and the initial
  migration. Verify same-workspace foreign keys, immutable history, source
  attribution, UTF-16 anchors, and idea edit ownership/stale-version checks.
  Feature-specific decision, constraint, and ticket transitions remain in sections 4–6.
- [x] Define immutable idea and proposal versions. Anchor comments and feature
  evidence to exact source versions; attach each review to the proposal version
  reviewed. A later edit must not inherit approval automatically.
- [x] Define analysis snapshots: record input versions, preference/constraint
  revisions, model and prompt versions, and run IDs. Mark results stale when
  their inputs change rather than presenting them as current.
- [x] Scaffold frontend, backend, persistence, migrations, environment examples,
  and documented local startup commands without committed secrets.
- [x] Implement controlled pilot identities and workspace membership checks on
  available reads/writes. Reject client-supplied actor IDs and cross-workspace
  access. Review-specific impersonation checks remain part of section 6.
- [x] Verify a local round trip: a participant creates an idea, reloads the page,
  and retrieves the same attributed content from persistent storage.

Progress (2026-10-15): `backend/app/db/models.py` defines 32 tables;
`backend/app/api/schemas.py` defines strict commands and stage outputs. Migration
`0001_foundation` installs composite foreign keys and immutable-history triggers.
`backend/app/domain/` implements foundational version/evidence validation, not
the complete product services. API returns readiness only after migration.
Generated OpenAPI/boundary JSON and frontend types are source artifacts ready for version control.
`uv.lock` and `package-lock.json` pin installed dependencies on Python 3.14.7/Node 24.10.0.
Verified: 31 backend tests passed, including empty/populated migration rollback,
every migrated foreign key, historical edit/delete rejection, stale edits,
source ownership/manifest checks, and Unicode anchors. Ruff lint/format,
`alembic check`, TypeScript checking, and Next.js production build passed.
All five Playwright checks passed against real local servers, including four
independent participant sessions, attributed sharing, reload persistence, version
history, author-only edit controls, logout, failed-save draft preservation, and
simulated session expiry/API failure. Visually inspected the desktop Chromium
workspace screenshot. Real pilot accounts are not provisioned automatically:
run `uv run python -m app.seed` from `backend/` once; no default real credentials
are shipped. Known test credentials are restricted to the isolated e2e seed.
Documentation links resolve and `git diff --check` passes. Local runtime data,
dependencies, screenshots, and credentials remain ignored.
Known tooling warnings: Alembic's table-sort warning for intentional version/head
cycles and Starlette's httpx test-client deprecation. Model calls, proposal reviews,
and external GitHub actions remain unverified/unbuilt. No new migration was needed
for login/idea routes; the existing schema supports this milestone.

## 3. Capture ideas and contextual feedback

- [x] Build one workspace view showing its decision question, participants,
  ideas, and next action; avoid requiring separate full-featured screens.
- [x] Support one-sentence ideas with optional titles and attribution. Editing
  creates a version while retaining the original contribution.
- [ ] Support whole-idea comments and passage comments. For passages, persist
  the quote, source version, offsets, and surrounding context; reload must show
  the correct source. After an edit, preserve the old-version anchor and clearly
  flag any unverified relocation to the current text.
- [ ] Provide a keyboard-accessible way to comment on a passage or selected
  section; commenting must not depend exclusively on mouse selection.
- [ ] Verify with four pilot identities that comments remain attributed and
  readable after reload and that an edit does not silently move feedback.

Progress (2026-10-15): Authenticated capture/edit/history UI and API are implemented
in `web/src/app/page.tsx` and `backend/app/api/routes.py`. Four-session browser
checks verify sharing and persistence; API checks reject non-author edits, stale
versions, cross-workspace IDs, actor spoofing, and invalid CSRF/Origin headers.
Comments and annotation UI remain unbuilt. Use immutable source versions before
attempting automatic re-anchoring across arbitrary edits.
Threaded replies, quick reactions, and richer navigation are deferred below
under the agreed scope decision in section 1.

## 4. Extract preferences and support correction

- [ ] Implement structured extraction with source spans and participant IDs;
  preserve negation, conditions, uncertainty, and multiple signals in a comment.
- [ ] Build a review view where each participant can confirm, correct, or
  withdraw their own inferred preferences without rewriting the original comment.
- [ ] Ensure corrected and withdrawn interpretations supersede earlier versions
  in subsequent runs; unconfirmed inferences must not become binding constraints.
- [ ] Generate an evidence-linked summary of shared priorities, distinctive
  interests, tensions, and unanswered questions. Do not infer human endorsement
  from semantic overlap.
- [ ] Validate structured outputs and references before persistence. Invalid
  IDs, absent sources, and attribution to the wrong participant must be rejected
  or flagged rather than displayed as verified facts.
- [ ] Verify correction behavior with a fixture: correct an intentionally wrong
  extraction and demonstrate that the next analysis uses the correction.

Progress: No extraction or correction workflow exists. Section 2's source and
preference contracts and section 3's persisted feedback are prerequisites.

## 5. Generate alternatives with accountable critique

- [ ] Implement an explicit workflow that snapshots inputs, analyzes tensions,
  generates two meaningfully different candidates, and critiques them. Use
  specialized stages first; add autonomous tools only for a demonstrated need.
- [ ] Include goals, scope, rationale, assumptions, exclusions, unresolved
  objections, and feature-level lineage in each candidate. Label novel AI
  additions as suggestions rather than attributing them to participants.
- [ ] Check accepted constraints and attribution. Separate verified checks from
  estimates, violations, and unknowns; judgment-based feasibility claims must
  state their assumptions.
- [ ] Represent an infeasible constraint set explicitly. Surface the conflict
  and request human trade-offs instead of quietly relaxing a requirement.
- [ ] Bound retries, critique revisions, and run cost. Record run status, prompt
  versions, timing, token usage, validation failures, and revision reasons.
- [ ] Preserve human-authored work on model failure and allow a retry without
  duplicate published candidates. Treat workspace content as untrusted input
  and prevent it from granting agent permissions or fabricating reviews.
- [ ] Verify that every attributed feature references an existing source and
  inspect whether that source actually supports the claim. Report semantic
  attribution errors separately from broken-reference errors.

Progress: No AI workflow exists. A critic is an additional check, not proof of
feasibility. The primary demonstration should include a visible failure and
recovery, as described in `projBible.md` §20.

## 6. Review candidates and record decisions

- [ ] Present both candidates with source inspection, unresolved concerns,
  per-participant preference coverage, and explicit uncertainty; avoid an opaque
  consensus percentage.
- [ ] Implement one review per participant per proposal version under the
  agreed rule. Show who responded, who has not, and outstanding reservations.
- [ ] Support a bounded revision cycle: human feedback creates a new proposal
  version and requires fresh review; retain prior versions and stances as history.
- [ ] Enforce the approval rule in application logic before an authorized human
  records a decision. Store the exact proposal version, rule, required reviewers,
  supporting reviews, rationale, and outstanding reservations.
- [ ] Export a readable Markdown decision record with provenance and unresolved
  reservations. Do not silently mark objections resolved when a decision passes.
- [ ] Verify missing responses, opposition, changed rules, and edits after
  endorsement cannot produce a false claim of unanimous or current approval.

Progress: All-four support or support-with-reservations is the confirmed approval
rule. State labels and owner decision authority are also agreed in section 1. Final
authorization must depend on persisted human actions, not model-generated assessments.

### 6.1 Real ticketing integration

- [ ] Record a controlled GitHub test repository, access requirements, and
  definition of a successful handoff for outbound issue creation.
  Scope one provider first; a mocked response or Markdown download is insufficient.
- [ ] Implement the agreed provider connection with server-side credentials,
  destination access checks, and actionable authentication/permission errors.
- [ ] Implement outbound GitHub Issues creation end to end. Generate editable
  ticket drafts from the approved proposal version with titles,
  descriptions, acceptance criteria, and source/decision references; require a
  human preview and explicit publish action for the selected destination.
- [ ] Persist external ticket IDs/URLs and their source versions. Handle partial
  success and ambiguous timeouts without blindly recreating tickets on retry;
  report per-ticket outcomes and preserve drafts when the provider is unavailable.
- [ ] Verify against a real controlled GitHub repository that issue creation
  succeeds and links return to the correct records. Verify
  preview/cancel, successful creation, safe retries, and permission failures.

Progress: The user selected GitHub Issues and outbound implementation tickets from
approved proposals on 2026-10-15. No account has been connected and no external
tickets have been created. The tasks describe
product behavior; they do not authorize posting to an unspecified destination.

## 7. Evaluate the AI and the complete workflow

- [ ] Choose a primary research question and minimum course metrics before
  prompt tuning. Proposed question: does confirmed preference extraction plus
  evidence-linked critique reduce unsupported attributions and constraint
  violations compared with direct synthesis?
- [ ] Assemble labeled development and held-out cases covering ordinary feedback,
  negation, conditional preferences, conflicting requirements, corrections,
  minority objections, infeasibility, and unsupported attribution. Define scoring
  units and adjudicate ambiguous labels with human reviewers.
- [ ] Implement a reproducible evaluation harness. Keep model settings and input
  evidence comparable; log prompt versions, latency, tokens/cost, and failures.
- [ ] Compare a direct-synthesis baseline, a single structured call, and the
  staged workflow. Include a no-critic ablation; add further ablations only if
  time and sample size support useful conclusions.
- [ ] Report extraction accuracy, unsupported attribution, accepted-constraint
  violations, and lowest-participant preference coverage. Distinguish estimated
  coverage from actual human support; report sample counts and uncertainty.
- [ ] Collect participant judgments on faithful representation, usefulness,
  alternative diversity, and clarity; blind system identity where practical.
  Do not reuse prompt-tuning examples as held-out evidence.
- [ ] Run the complete four-person flow from contribution through correction,
  synthesis, review, revision, and export. Include access isolation, stale inputs,
  model failure, and fabricated-consent attempts in the relevant checks.
- [ ] Record reproducible commands, results, limitations, and failure examples.
  Resolve defects that lose work, misattribute feedback, or fabricate approval,
  and rerun affected checks before declaring the pilot ready.

Progress: No dataset, benchmark, tests, or pilot results exist. Start dataset
design alongside section 2; do not wait until the UI is complete. Four-person
pilot feedback alone will not establish broad effectiveness.

## 8. Prepare the demonstration and handoff

- [ ] Have one teammate register the team on Canvas by October 22 at 3pm and
  record confirmation. The PDF's requirement does not establish that this is done.
- [ ] Prepare and upload proposal slides by November 12 at 3pm; rehearse a talk
  of at most five minutes for that day's lecture covering the problem, existing
  solutions, and proposed solution.
- [ ] Prepare and submit the proposal PDF by November 12 at 3pm: at most two
  pages, covering essentially the same content as the proposal presentation.
- [ ] Review empty, loading, error, stale-analysis, and no-feasible-candidate
  states; verify readable labels, focus behavior, and keyboard operation on the
  chosen browser and device scope.
- [ ] Update README with actual setup, model configuration, commands, data flow,
  privacy implications of external model processing, and known limitations.
- [ ] Assign the four ownership areas from `projBible.md` §18 to actual teammates,
  with shared integration checkpoints and a schedule based on the confirmed deadline.
- [ ] Adapt the project target and criteria in `rubricatm.md` to the agreed MVP,
  then assess actual implementation with evidence; do not grade planned features.
- [ ] Prepare a repeatable demo dataset and reset procedure. Rehearse the complete
  flow, including one correction, one unresolved objection, failure recovery,
  source inspection, and the baseline comparison.
- [ ] Prepare and upload final slides by December 3 at 3pm; rehearse a talk of
  at most five minutes for that day's lecture covering the problem, solution,
  and evidence of effectiveness. Verify demo setup from a clean environment.
- [ ] Prepare and submit the final report PDF by December 17 at 23:59 in official
  ACL format: at most four main pages, unlimited references and appendix. Include
  measured results, trade-offs, limitations, and an open-access project GitHub link.
- [ ] Prepare a repository suitable for public access, checking setup instructions,
  reproducibility, and absence of secrets or private participant data. Verify the
  report's repository link is accessible without sign-in before submission;
  any visibility change still needs authorization.
- [ ] Complete the agreed handoff and verify it in the intended setting; any
  public deployment or external publication requires separate authorization.

Progress: Dates and artifact formats were extracted from `project-requirements.pdf`
on 2026-10-15. No registration, upload, or submission has been performed or verified.
Timezone and any additional Canvas guidance remain unconfirmed. A hosted deployment
is not explicitly required by the PDF; public repository access is required.

## Future priorities

These items remain outside the agreed first-release contract. Move them into
the active sections only after the core flow works and scope is explicitly expanded.

- [ ] Add threaded replies and optional reaction shortcuts (deferred from the
  bible's original broader MVP to prioritize the complete AI and review workflow;
  scope reduction accepted on 2026-10-15).
- [ ] Add richer proposal comparison, forks, and history navigation once the
  basic versioned revision loop is usable.
- [ ] Add PDF import and robust passage anchoring with supported-format tests.
- [ ] Add rich-text and live collaborative editing with reliable annotation behavior.
- [ ] Add visual idea graphs and duplicate/merge suggestions if pilot evidence
  shows they improve navigation.
- [ ] Explore clarification queues, anonymous feedback, additional integrations, semantic
  retrieval, or utility optimization only with a specific evaluated need and
  appropriate privacy and decision rules.
- [ ] Consider ticket imports or bidirectional status sync after outbound GitHub
  Issues creation is verified and the core milestone is complete.

## Blockers and decisions

- **Observed starting point:** Documentation only, verified by repository file
  inspection on 2026-10-15. No runtime checks were available to run.
- **Schedule authority — 2026-10-15:** The user instructed us to follow
  `project-requirements.pdf`; its dates supersede the earlier November 22 deadline.
- **Confirmed requirements — 2026-10-15:** Real ticketing integration is required,
  using GitHub Issues to create implementation
  tickets from approved proposals. Source: user instructions in this session.
- **Confirmed approval rule — 2026-10-15:** All four participants must support or
  support with reservations; retain reservations in the decision record.
- **Course-answer interpretation — 2026-10-15:** The user's “no” is read as no
  mandatory model training/fine-tuning, not as confirmation of submission or
  deployment requirements.
- **Open decisions:** Remaining course requirements, test repository/access,
  model provider/access, evaluation target, and delivery setting
  are tracked in the relevant sections above.
- **MVP and policy acceptance — 2026-10-15:** The user accepted the proposed
  first-release boundaries, workspace-owner decision recording, all-four binding
  constraint acceptance, and human correction and ticket review rules.
- **Technical selection — 2026-10-15:** Next.js/TypeScript UI, FastAPI/Pydantic API,
  SQLite with SQLAlchemy and Alembic, explicit Python orchestration, server-side
  GitHub REST integration. See `docs/architecture.md` and `docs/data-model.md`.
- **Planning decision — 2026-10-15:** Create this checklist from the product bible
  using the simple template. No separate FAQ is needed for the current milestone.
- **Dependency:** Later implementation depends on the contracts and policy
  decisions above; organizing the backlog does not resolve those decisions.
