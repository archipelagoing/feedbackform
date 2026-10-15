# FeedbackForm TODO

Last updated: 2026-10-15.

Current state: Planning only. [idea.md](idea.md) defines the concept and
[projBible.md](projBible.md) defines product intent. Repository inspection found
no application code, dependency manifests, tests, or deployment configuration.
No runtime behavior has been verified. The next milestone is a constrained,
four-participant workflow from ideas and feedback to reviewed proposals, with a
real ticketing integration. The course deadline is November 22, 2026, confirmed
by the user. GitHub Issues creation from approved proposals is selected;
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

1. Finalize pilot decision rules, remaining course requirements, and MVP boundaries
   in section 1. Deadline: November 22, 2026; outbound GitHub Issues is selected.
2. Define versioned data contracts and the primary evaluation question in sections
   2 and 7 before implementation or prompt tuning.
3. Set up the local application and controlled pilot access in section 2.
4. Complete persistent idea capture and passage comments in section 3.
5. Connect extraction, correction, and two-candidate synthesis in sections 4–5.

The product direction is documented. Decisions below remain open; suggested
defaults are proposals, not confirmed team agreements. Evaluation examples should
be assembled alongside the first implementation rather than at the end.

## 1. Define the pilot and freeze scope

- [x] Document the problem, initial users, and intended outcome in
  `projBible.md` §§1–5 and §14.
- [x] Document invariants covering original voice, explicit human support,
  unresolved disagreement, and source attribution in `projBible.md` §3.
- [x] Confirm the course deadline: November 22, 2026 (user confirmation,
  2026-10-15). Submission time and timezone have not been specified.
- [x] Record the user's answer about required model training/fine-tuning: “no”
  (2026-10-15), interpreted as no mandatory training/fine-tuning. Plan for evaluated
  LLM orchestration; the answer does not establish all course grading criteria.
- [ ] Confirm submission format, deployment needs, and any remaining course
  grading requirements; record the answers and their source.
- [x] Establish real ticketing integration as a required first-release capability
  (user requirement, 2026-10-15). This confirms scope intent, not implementation.
- [x] Choose one initial ticketing provider and integration direction: approved
  proposal → reviewed implementation tickets → GitHub Issues (user selection,
  2026-10-15). Ticket import and bidirectional status sync are deferred.
- [ ] Agree on the first-release contract: four controlled participant accounts,
  one workspace, plain-text ideas, passage comments, preference correction,
  two distinct candidate proposals, explicit reviews, a decision export, and one
  real ticketing integration.
  Reconcile any reductions with the bible's broader MVP list.
- [x] Choose the pilot approval rule: all four participants must explicitly
  support or support with reservations (user selection, 2026-10-15). Reservations
  remain visible. Missing responses, abstention, requests for changes, and
  opposition do not satisfy this rule.
- [ ] Finalize review-state labels and who may record a decision after the
  four-person approval rule passes.
- [ ] Define how a participant-confirmed requirement becomes a binding workspace
  constraint, who authorizes it, and how incompatible constraints are handled.
- [ ] Define correction and publication rules: material interpretations need
  confirmation before becoming binding; generated candidates remain drafts
  until a human chooses to share them for review.
- [ ] Agree on exclusions: PDF/OCR import, live collaborative editing, visual
  graphs, anonymous feedback, additional integrations, optimization of utilities,
  and full task management stay outside the first release. Ticket import and
  bidirectional sync are deferred under the selected outbound-only integration.

Progress: Product intent is documented, not validated with the pilot group.
The user confirmed the November 22 deadline and required real ticketing integration
on 2026-10-15, and selected outbound GitHub Issues creation from approved proposals.
The user also selected all-four support/support-with-reservations and answered
“no” to the course training/fine-tuning question. Other course requirements,
decision-recording authority, and the proposed scope reductions remain open.

### Pilot rules — confirmed approval rule and proposed defaults

The approval threshold is confirmed. The other defaults below remain proposals.

- Reviews (proposed labels): support, support with reservations, request changes,
  oppose, or abstain.
  All four participants review the exact proposal version. Approval requires all
  four to support or support with reservations; reservations stay visible.
  Missing responses, abstention, requests for changes, or opposition prevent
  approval under the confirmed rule. Reviews apply to the exact proposal version;
  implementing version binding remains unfinished work in section 2.
- Authority: a designated human facilitator records a decision only when the
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

### Proposed delivery checkpoints

Work backward from November 22; checkpoints are planning targets, not additional
confirmed course deadlines. Ownership and feasibility still need team review.

- October 18: resolve section 1 policies, provider, scope, and evaluation target.
- October 25: working persistent workspace, comments, and preference correction.
- November 1: two-candidate synthesis, lineage, and constraint critique.
- November 8: versioned human review, decision recording, and ticket integration
  working against a real provider in a controlled test destination.
- November 15: four-person pilot and held-out evaluation complete; remaining work
  focuses on defects, analysis, and demonstration.
- November 20: clean-environment rehearsal and submission artifacts ready.
- November 22: course deadline; verify submission time and timezone separately.

## 2. Establish data contracts and a runnable foundation

- [ ] Select and record the pilot stack and supported environment. Starting
  proposal from the bible: React/Next.js, FastAPI, SQLite, and an explicit Python
  workflow; confirm before scaffolding.
- [ ] Define validated schemas for source references, preferences, constraints,
  themes/tensions, proposal features, reviews, decisions, and workflow events.
  Distinguish inferred preferences, participant confirmation, and group acceptance.
- [ ] Define immutable idea and proposal versions. Anchor comments and feature
  evidence to exact source versions; attach each review to the proposal version
  reviewed. A later edit must not inherit approval automatically.
- [ ] Define analysis snapshots: record input versions, preference/constraint
  revisions, model and prompt versions, and run IDs. Mark results stale when
  their inputs change rather than presenting them as current.
- [ ] Scaffold frontend, backend, persistence, migrations, environment examples,
  and documented local startup commands without committed secrets.
- [ ] Implement controlled pilot identities and workspace membership checks on
  reads and writes. Verify that another identity cannot impersonate a reviewer
  or access a workspace without membership.
- [ ] Verify a local round trip: a participant creates an idea, reloads the page,
  and retrieves the same attributed content from persistent storage.

Progress: No stack has been selected or scaffolded. Versioning and permission
contracts should precede feature work because later evidence and decisions depend
on them. Section 1's core rules are prerequisites for finalizing these contracts.

## 3. Capture ideas and contextual feedback

- [ ] Build one workspace view showing its decision question, participants,
  ideas, and next action; avoid requiring separate full-featured screens.
- [ ] Support one-sentence ideas with optional titles and attribution. Editing
  creates a version while retaining the original contribution.
- [ ] Support whole-idea comments and passage comments. For passages, persist
  the quote, source version, offsets, and surrounding context; reload must show
  the correct source. After an edit, preserve the old-version anchor and clearly
  flag any unverified relocation to the current text.
- [ ] Provide a keyboard-accessible way to comment on a passage or selected
  section; commenting must not depend exclusively on mouse selection.
- [ ] Verify with four pilot identities that comments remain attributed and
  readable after reload and that an edit does not silently move feedback.

Progress: No capture or annotation UI exists. Start with immutable source
versions rather than promising automatic re-anchoring across arbitrary edits.
Threaded replies, quick reactions, and richer navigation are deferred below
pending the scope decision in section 1.

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
rule. Final state labels and decision-recording authority remain open. Final
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
- [ ] Prepare the course report and required submission artifacts with measured
  results, trade-offs, and limitations. Verify setup from a clean environment.
- [ ] Complete the agreed handoff and verify it in the intended setting; any
  public deployment or external publication requires separate authorization.

Progress: Deadline confirmed as November 22, 2026. Other delivery requirements and
environment are unconfirmed. Local demo
readiness and a verified deployment are separate outcomes.

## Future priorities

These items remain outside the proposed first-release contract. Move them into
the active sections only after the core flow works and scope is explicitly expanded.

- [ ] Add threaded replies and optional reaction shortcuts (deferred from the
  bible's broader MVP to prioritize the complete AI and review workflow).
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
- **Confirmed requirements — 2026-10-15:** Course deadline November 22, 2026;
  real ticketing integration is required, using GitHub Issues to create implementation
  tickets from approved proposals. Source: user instructions in this session.
- **Confirmed approval rule — 2026-10-15:** All four participants must support or
  support with reservations; retain reservations in the decision record.
- **Course-answer interpretation — 2026-10-15:** The user's “no” is read as no
  mandatory model training/fine-tuning, not as confirmation of submission or
  deployment requirements.
- **Open decisions:** Remaining course requirements, test repository/access,
  exact first-release scope,
  review and constraint authority, stack, evaluation target, and delivery setting
  are tracked in the relevant sections above.
- **Planning decision — 2026-10-15:** Create this checklist from the product bible
  using the simple template. No separate FAQ is needed for the current milestone.
- **Dependency:** Later implementation depends on the contracts and policy
  decisions above; organizing the backlog does not resolve those decisions.
