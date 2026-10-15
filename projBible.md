FeedbackForm — Product Show Bible
Status: Foundational product specification · v0.1 · October 2026
Product category: Idea-first collaborative workspace with agentic synthesis and consensus support
Working tagline: From scattered thoughts to shared direction.
Canonical product name: FeedbackForm
Initial pilot: Four graduate students collaboratively choosing and shaping an AI/ML project
Scope: Product vision plus a deliberately constrained academic MVP; proposed features are not claims of existing functionality.

0. How to use this document
This is the source of truth for product intent, not a claim that every feature has been built. It is written to guide product decisions, UX design, engineering, evaluation, and AI coding agents.
- MUST = core product invariant; do not silently violate.
- SHOULD = strong default; deviate only with a documented reason.
- COULD = later enhancement or experiment.
- MVP = required for the first demonstrable end-to-end release.
- Future = outside the first release unless time permits.
- Open question = a decision not yet made; do not invent an answer.
When implementing from this bible, preserve its user-centered intent, distinguish planned from implemented features, and surface conflicts rather than quietly choosing a direction.
1. One-sentence definition
FeedbackForm is an idea-first collaborative workspace where people capture rough thoughts, develop proposals together, annotate what resonates or concerns them, and use explainable AI to discover shared directions without erasing individual perspectives.
1.1 Short pitch
Most collaborative tools assume people already know what they want to create. FeedbackForm starts earlier: at the messy stage where everyone has fragments, intuitions, examples, doubts, and incompatible priorities. Participants contribute in natural language. They can respond to an idea as a whole or highlight an exact passage. FeedbackForm organizes these contributions, helps participants clarify what they mean, surfaces agreements and tensions, and suggests new directions that combine compatible priorities. People retain ownership of decisions.
1.2 The product is
- An idea-first workspace, not a document editor with AI bolted on.
- A collaborative sensemaking system, not a poll or popularity contest.
- A proposal-development environment, not just an idea generator.
- An evidence-linked AI collaborator, not an invisible decision maker.
- A place for productive disagreement, not manufactured unanimity.
1.3 The product is not
- A generic chatbot wrapped in a team dashboard.
- A voting app that selects the most popular idea.
- A system that merges every suggestion into an incoherent compromise.
- A project management suite, social network, or full office suite.
- A replacement for human consent, judgment, or accountability.
2. Problem and opportunity
2.1 The problem
Groups often begin with incomplete and differently expressed ideas. Existing workflows scatter the process across group chats, documents, comments, polls, and meetings. The group struggles to distinguish:
1. What people actually want from the proposed outcome.
2. Which aspects of an idea people like or dislike.
3. Which requirements are non-negotiable versus merely preferred.
4. Which apparent disagreements are differences in wording.
5. Which genuine conflicts need a human decision.
6. How a final proposal relates to the contributions that produced it.
As a result, teams may settle for the loudest voice, the easiest option, the first polished proposal, or an unsatisfying average.
2.2 Core opportunity
Make the evolution of an idea visible and navigable: from fragments to themes, from themes to candidate proposals, and from proposals to a group-endorsed direction.
2.3 Initial users
- Primary pilot: Four graduate students deciding on a technically substantial agentic AI course project.
- Later users: Research teams, hackathon teams, startup cofounders, design groups, writers' rooms, creative collectives, and community organizers.
- Common need: Arrive at a defensible shared direction while preserving the reasons behind individual contributions.
2.4 Jobs to be done
- When I have a vague thought, I want to capture it without writing a formal proposal.
- When someone shares an idea, I want to respond to the exact part I care about.
- When our discussion gets messy, I want to see what we agree on and what remains contested.
- When the AI suggests a combined idea, I want to know where it came from.
- When we choose a direction, I want to know whether my non-negotiables were respected.
- When we revisit a decision, I want to recover the reasoning and prior versions.
3. Product philosophy and invariants
3.1 Idea-first, not document-first
A participant can create an idea with a title and a single sentence, or even an untitled fragment. Polished documents are optional. Ideas may accumulate details, attachments, questions, and variants over time.
3.2 Preserve the original voice
AI-derived labels, summaries, and preferences must link back to original human-authored contributions. The AI may suggest interpretations, but must not silently rewrite the author's intent.
3.3 No forced consensus
The system must represent unresolved objections, abstentions, uncertainty, and minority viewpoints. A synthesis can be promising without being accepted. The system must never report unanimous agreement without explicit evidence from all required participants.
3.4 Do not confuse preferences with constraints
An enthusiastic reaction is not a hard requirement. A concern is not necessarily a veto. The AI can propose classifications, but the participant must be able to correct them.
3.5 Synthesis is accountable
Every material feature of an AI-generated proposal should be traceable to one or more source contributions, an explicitly labeled AI suggestion, or an externally cited source. Unsupported additions must be marked as suggestions rather than attributed to a person.
3.6 Keep humans in control
Only authorized humans may approve a final proposal, change group decision rules, or commit external actions. AI cannot vote on behalf of a participant or invent consent.
3.7 Preserve disagreement as information
A tension between two ideas is not automatically a defect. It may reveal an important design choice, a hidden assumption, or an opportunity to branch into multiple proposals.
3.8 Reversible and inspectable
Edits, syntheses, and decisions should be versioned. Participants must be able to inspect how a proposal changed and revert or fork where appropriate.
4. Conceptual model and vocabulary
Term	Meaning
Workspace	Shared context for a group, including members, ideas, discussions, and decisions.
Idea	A rough or developed concept; may start as one sentence.
Fragment	An incomplete thought, observation, question, or inspiration that may become an idea.
Proposal	A structured candidate direction with goals, scope, rationale, and trade-offs.
Annotation	Feedback anchored to a passage, section, idea, or attachment.
Reaction	A lightweight expression such as resonates, concern, question, or alternative.
Preference	Something a participant values or wants, with an optional strength.
Constraint	A requirement a proposal must meet if accepted as binding.
Objection	A reason a participant does not currently support a proposal.
Theme	A cluster of related ideas or preferences, with supporting evidence.
Tension	Two or more preferences that may be difficult to satisfy simultaneously.
Synthesis	A new candidate direction constructed from source ideas and feedback.
Lineage	Provenance links between source contributions and later proposal elements.
Consensus check	A structured request for participants to indicate support, reservations, or non-support.
Decision record	A durable summary of what was decided, by whom, under which rules, and why.


Important: Idea, proposal, and synthesis are related but not interchangeable. An idea need not be evaluated; a synthesis is a generated candidate; a proposal is a candidate the group can explicitly assess.
5. Core user experience
5.1 Workspace entry
A user creates or joins a workspace. The landing view answers:
- What are we trying to decide or create?
- What ideas have been shared?
- What is new since I last visited?
- What needs my feedback?
- Where are we in the process?
The workspace's decision question might be: “What agentic AI application should our four-person graduate team build?”
5.2 Capture without friction
Entry points include:
- Quick thought: A sentence, question, or fragment.
- New idea: Title, short description, optional details.
- Paste or import: Text, markdown, and later PDFs.
- Respond to idea: Comment on the entire idea.
- Highlight and comment: Select an exact passage and react in natural language.
- Build on this: Suggest an extension, alternative, or combination.
The interface must not require choosing an AI-defined category before posting.
5.3 Review and discussion
Each idea has a readable main body, contextual annotations, discussion threads, linked ideas, revisions, and provenance. People can respond with their own words; quick reaction labels are optional shortcuts, not replacements for explanation.
Suggested reactions: I like this, I have a concern, I'd change this, I have a question, This is essential, This reminds me of, Combine with…
5.4 Sensemaking
An optional AI-assisted view groups contributions into:
- Shared priorities.
- Distinctive interests.
- Unresolved questions.
- Hard constraints awaiting confirmation.
- Conflicts and trade-offs.
- Possible combinations.
Every displayed inference should offer View source and Correct interpretation.
5.5 Synthesis
A participant requests synthesis with a stated objective, for example:
Generate three feasible agentic AI project directions that preserve our interest in autonomous planning, measurable evaluation, actual ML components, and multi-agent coordination. Respect our deadline and avoid heavy frontend work.

The system returns multiple differentiated candidates, not one supposedly optimal answer. Each candidate includes rationale, preserved preferences, excluded preferences, uncertainties, and provenance.
5.6 Review and decision
Participants independently review candidate proposals. They may support, support with reservations, request changes, oppose, or abstain. The group can revise, branch, or decide to discuss unresolved conflicts. A human-authorized decision is recorded with its supporting evidence and outstanding reservations.
5.7 Continue after selection
The selected proposal can become a living project brief, but full task management is out of scope for the MVP. FeedbackForm should retain the original brainstorming history so later decisions remain understandable.
6. Information architecture
6.1 Main workspace navigation
1. Overview — purpose, activity, pending decisions.
2. Ideas — rough thoughts and developed ideas; list or board view.
3. Discussion — conversations and annotations in context.
4. Patterns — AI-assisted agreements, differences, constraints, open questions.
5. Proposals — generated or human-written candidate directions.
6. Decisions — reviews, approvals, rationale, and history.
For the MVP, these may be tabs on one page rather than separate full-featured routes.
6.2 Idea detail layout
- Header: title, author, created/updated time, status.
- Main canvas: rich text or markdown body.
- Inline highlights: anchored annotations with participant attribution.
- Right rail or bottom drawer: comments on the selected passage.
- Related ideas: links and proposed combinations.
- History: prior revisions and linked syntheses.
- Actions: comment, annotate, build on, fork, include in synthesis.
6.3 Proposal detail layout
- Summary and intended outcome.
- Core features and rationale.
- Explicit constraints and assumptions.
- Preference coverage by participant.
- Trade-offs and unresolved concerns.
- Source lineage for each major feature.
- Revision history and consensus state.
- Actions: annotate, revise, fork, request consensus check.
7. Interaction details and edge cases
7.1 Highlighting
Users select a passage and attach feedback. Store the quoted text plus a robust text anchor, not just start/end offsets; edits can invalidate offsets. For the MVP, support plain text/markdown annotations reliably before advanced PDF anchoring.
7.2 Annotation types
- Positive signal: what resonates and why.
- Concern: what seems risky, undesirable, or unclear.
- Suggestion: proposed modification.
- Question: information needed to decide.
- Requirement: something the person considers essential.
- Connection: related idea or source.
A comment may contain multiple types. The AI must not force one label if multiple interpretations are plausible.
7.3 Replies and conversations
Comments can have replies. Thread state: open, resolved, or archived. Resolving a thread does not imply agreement or that an objection has been withdrawn.
7.4 Forking versus editing
A participant can create an alternative version of an idea without overwriting the original. Preserve author attribution and link the fork to its source.
7.5 Deletion and privacy
Deleted or private contributions must not be resurfaced through AI summaries to unauthorized users. Provenance and caches must honor access controls and deletion policies.
7.6 Missing participation
Do not treat silence as agreement. A proposal cannot be called unanimously supported if someone has not responded.
7.7 Misinterpretation
Participants must be able to say: “That's not what I meant.” Corrections should supersede the faulty interpretation in subsequent syntheses while preserving an auditable history.
7.8 Contradictory statements
A person can change their mind. Prefer the latest explicit, context-relevant preference but retain earlier statements as historical context; ask for clarification when the conflict matters.
8. AI architecture
8.1 Guiding principle
Use multiple agents only where separation improves reliability, evaluation, or maintainability. The MVP may implement specialized stages within one orchestrated workflow rather than running many LLMs concurrently.
8.2 Proposed agents
A. Preference Interpreter
Input: Human-authored text, annotations, context, optional reaction label.
Output: Candidate preference records with category, polarity, strength, source references, and uncertainty.
Responsibilities:
- Extract what is valued, rejected, questioned, or required.
- Distinguish a feature preference from a hard constraint.
- Preserve negation, conditionals, and nuance.
- Identify ambiguous feedback requiring clarification.
- Never infer consent or silently promote a soft preference into a veto.
B. Theme and Tension Analyst
Input: Confirmed and provisional preferences, idea links, constraints.
Output: Themes, overlaps, conflicts, missing information, and evidence references.
Responsibilities:
- Cluster semantically similar preferences without flattening differences.
- Distinguish genuine contradiction from complementary interests.
- Track minority priorities as first-class inputs.
- Surface conflicts requiring trade-offs or clarification.
C. Synthesis Planner
Input: Workspace goal, ideas, themes, confirmed constraints, feedback.
Output: Multiple candidate proposals with feature-level lineage and trade-offs.
Responsibilities:
- Generate diverse, coherent alternatives.
- Combine compatible elements where useful.
- Reject combinations that violate confirmed hard constraints.
- Mark novel AI-originated additions clearly.
- Explain what each candidate preserves and what it sacrifices.
D. Critic and Consensus Evaluator
Input: Candidate proposals, participant preferences, source evidence.
Output: Coverage report, constraint violations, contradictions, unsupported attributions, unresolved concerns.
Responsibilities:
- Check each proposal against stated constraints.
- Challenge claims of group agreement.
- Identify overlooked participants or objections.
- Recommend clarification questions and revision targets.
- Evaluate, but never fabricate or cast participant votes.
8.3 Workflow
Human ideas, fragments, comments, imports
                   |
                   v
         Normalize + store originals
                   |
                   v
          Preference Interpreter
                   |
          Human correction (optional)
                   |
                   v
          Theme & Tension Analyst
                   |
                   v
             Synthesis Planner
                   |
                   v
       Critic / Constraint Validator
             |              |
       pass + cite       revise / flag
             |              |
             +-------<------+
                   |
                   v
        Candidate proposals + lineage
                   |
                   v
           Human review and votes
                   |
                   v
       Revise, branch, or record decision
8.4 Agent state and tool boundaries
Each stage receives structured input and returns validated JSON. Agents should have access only to the tools necessary for their role. Tools may include read workspace, retrieve annotations, find similar ideas, inspect source spans, write draft proposal, and validate constraints. Publishing proposals, changing permissions, and recording final decisions require authorized human actions.
8.5 Confidence and abstention
Model confidence scores are not inherently calibrated. Treat them as provisional heuristics. When interpretation is ambiguous or materially consequential, ask a participant rather than guessing. Record uncertainty and evaluate it empirically.
8.6 Reflection and stopping
A bounded critique-and-revise loop may improve proposals. Set a maximum number of revisions, cost budget, and explicit stopping conditions. Do not assume more reflection always means higher quality.
8.7 Why this is agentic
The system performs multi-step, stateful work: interpreting feedback, retrieving evidence, detecting tensions, planning combinations, checking constraints, and iterating on human feedback. It is not agentic merely because it calls an LLM or assigns multiple personas.
9. Consensus and preference modeling
9.1 Preference schema
Each preference should include:
- Participant ID.
- Source annotation or idea reference.
- Human-readable preference statement.
- Category: desire, concern, constraint, question, suggestion.
- Strength: optional, user-confirmed (e.g. nice-to-have / important / essential).
- Status: inferred, confirmed, corrected, withdrawn.
- Relevant context and timestamp.
9.2 Consensus is multidimensional
A proposal's review should show:
1. Coverage: Which stated preferences it addresses.
2. Constraint satisfaction: Whether confirmed hard constraints are met.
3. Fairness: Whether any participant's priorities are consistently neglected.
4. Objections: Which concerns remain unresolved.
5. Confidence: Whether the AI's interpretation is supported by evidence.
6. Explicit human support: Who has actually endorsed it.
Do not compress these into one opaque “consensus percentage.”
9.3 Optional scoring model
For analysis, an illustrative objective is:
\[
\max_{x\in\mathcal{F}} \sum_{i=1}^{n} w_i U_i(x),
\]
where \(\mathcal{F}\) is the set of proposals satisfying confirmed hard constraints, \(U_i(x)\) is participant \(i\)'s explicitly elicited or cautiously estimated utility, and \(w_i\) is an agreed weight (equal by default). Consider also maximizing the minimum participant satisfaction to avoid sacrificing one member for the group average.
Warning: Utilities are not directly observable from arbitrary comments. Any inferred score must be labeled as an estimate and must not replace participant review.
9.4 Consensus states
- Exploring: Ideas and preferences still being gathered.
- Synthesizing: Candidate proposals being constructed.
- Reviewing: Participants evaluating candidates.
- Needs revision: Material objections or unmet constraints remain.
- Accepted: Human-defined decision rule satisfied.
- Deferred: No acceptable proposal yet; questions remain.
9.5 Decision rules
Confirmed pilot rule (user selection, October 15, 2026): all four participants
must explicitly support or support with reservations. Reservations remain visible.
Missing responses, abstention, requests for changes, and opposition do not satisfy
the rule. Reviews must apply to the exact proposal version being accepted.
The user accepted the following pilot defaults on October 15, 2026: review states
are support, support with reservations, request changes, oppose, and abstain.
The workspace owner records a decision only after the approval rule passes.
All four must explicitly accept a requirement before it becomes binding on the
group; incompatible constraints require human revision rather than silent relaxation.
Participants correct their own preference interpretations; generated proposals and
ticket breakdowns remain drafts until a human reviews and authorizes publication.
This pilot choice is not a claim that every team should use the same rule.
10. Traceability and explainability
Every synthesis should include a Why this feature? view with:
- Source idea(s) and exact passage(s).
- Relevant human comments and authors.
- The interpreted preference(s).
- Whether the feature is directly requested, a combination, or an AI suggestion.
- Any unresolved objections.
Example:
Feature: Executable experiments with automated verification
Supported by: Student A's interest in autonomous planning; Student B's preference for measurable code-based results; Student C's requirement for actual ML.
Status: Proposed synthesis; not yet approved by all participants.

The explanation must be generated from stored references, not fabricated after the fact.
11. Suggested data model
Implementation contracts selected October 15, 2026 are in
[docs/data-model.md](docs/data-model.md), superseding the initial illustrative table.
The relational model uses immutable source/proposal versions, append-only
preference and review history, explicit four-person constraint acceptance,
frozen analysis manifests, and decision records tied to exact review events.
GitHub publication uses immutable authorized ticket batches and per-item outcomes.
Foundation status, October 15, 2026: executable SQLAlchemy records and Pydantic
boundary schemas exist in `backend/app/`, with migration `0001_foundation` and
tests for database integrity and version/evidence helpers. Four-account local
provisioning (now available through the frontend wizard), cookie login/logout,
member-scoped workspace/idea HTTP routes, and
idea capture/edit/history UI are implemented. Whole-idea and passage comments,
current-version highlights, original-context inspection, and keyboard passage
selection are implemented. Annotation edits/withdrawal, AI execution, proposal
review/decision transitions, and GitHub publishing remain unimplemented. See README
for setup and verification commands.


11.1 Data integrity
- Every record is scoped to a workspace with enforced access control.
- All annotations and synthesized features have stable source identifiers.
- Use versioning rather than overwriting meaningful historical states.
- A review belongs to a real user, never to an AI agent impersonating one.
- Agent outputs are validated before persistence.
11.2 Minimal API outline
POST   /workspaces
GET    /workspaces/{id}
POST   /workspaces/{id}/ideas
GET    /workspaces/{id}/ideas
POST   /ideas/{id}/annotations
GET    /ideas/{id}/annotations
POST   /workspaces/{id}/analyze
GET    /workspaces/{id}/patterns
POST   /workspaces/{id}/synthesize
GET    /workspaces/{id}/proposals
POST   /proposals/{id}/reviews
POST   /workspaces/{id}/decisions
GET    /agent-runs/{id}
The endpoint names are illustrative; authentication, validation, permissions, and idempotency are required before production deployment.
12. UI and design language
12.1 Desired feeling
Thoughtful, welcoming, intelligent, editorial, collaborative, and calm. The interface should encourage exploration rather than competition.
12.2 Design principles
- Put ideas and human words at the center.
- Make writing and commenting frictionless.
- Keep AI available but not constantly interrupting.
- Display annotations in context rather than hiding them in a generic chat log.
- Use visual structure to clarify relationships and revisions.
- Avoid leaderboards, popularity-first ranking, and gamified pressure.
- Make source provenance visible without cluttering the main canvas.
12.3 Primary screens
Workspace overview: Goal, idea feed, recent activity, unresolved questions, next step.
Idea composer: Quick capture, optional title, expandable details.
Idea detail: Read, select, highlight, annotate, reply, fork.
Patterns: Shared priorities, tensions, unanswered questions, source links.
Synthesis studio: User sets goals/constraints; AI produces multiple candidate proposals.
Proposal review: Compare alternatives, inspect lineage, record stance.
Decision history: What was chosen, under which rule, and why.
12.4 Accessibility
Keyboard-accessible selection and commenting; adequate contrast; screen-reader labels; alternatives to color-only reaction distinctions; clear focus indicators; understandable AI explanations.
13. Core user stories and acceptance criteria
Story 1 — Capture a fragment
As a participant, I can post a one-sentence thought without completing a formal template.
Accept when: The fragment appears in the shared workspace, retains attribution, and can be edited or developed later.
Story 2 — Annotate a specific passage
As a participant, I can highlight a passage and explain what I like or would change.
Accept when: The annotation remains linked to the correct passage, displays author and timestamp, and survives a normal page reload.
Story 3 — Correct AI interpretation
As a participant, I can correct an extracted preference.
Accept when: The corrected interpretation is used in the next synthesis, and the original source remains accessible.
Story 4 — Discover shared interests
As a team member, I can see patterns across all members' feedback.
Accept when: Every reported agreement links to supporting evidence; uncertain overlaps are not presented as confirmed consensus.
Story 5 — Generate proposals
As a team member, I can request multiple new directions from our ideas and feedback.
Accept when: At least two meaningfully different candidates appear with constraints, trade-offs, and feature-level sources.
Story 6 — Preserve an objection
As a participant, I can object to a proposal without my objection disappearing in the synthesis.
Accept when: The objection remains visible in review and is not marked resolved without explicit action.
Story 7 — Record a decision
As a workspace member, I can review and endorse a candidate.
Accept when: The system accurately shows who responded, who has not, and whether the workspace's stated decision rule was met.
14. Initial pilot: four-student agentic AI project selection
14.1 Scenario
Four graduate students have a document containing ten possible AI/ML course projects (five application-oriented and five research-oriented). They prefer an application-focused agentic AI system with substantial AI/ML engineering, minimal conventional app overhead, a live demo, and a limited project timeline. They want to identify what each person values rather than choose only by popularity.
14.2 Pilot workflow
1. Create workspace: Choose our agentic AI project.
2. Add each project as an idea; preserve the source document and page references.
3. Each member highlights features they like, dislike, or question.
4. Extract and confirm preferences; ask about ambiguous comments.
5. Display common priorities and incompatible requirements.
6. Generate three distinct application proposals with evidence-linked features.
7. Have all four members review and annotate the new proposals.
8. Revise once or twice, then conduct an explicit consensus check.
9. Export the selected proposal and decision rationale.
14.3 Example (hypothetical)
- Member A values autonomous research planning.
- Member B wants executable code and objective test results.
- Member C wants substantive ML beyond prompting.
- Member D wants multi-agent coordination and a strong live demonstration.
Possible synthesis: an autonomous experimentation agent that plans investigations, runs ML analyses, validates results, and coordinates specialized agents. This is a candidate, not evidence that these are the real members' preferences.
14.4 Pilot success criteria
- All four participants can contribute and annotate.
- The system identifies shared priorities with linked evidence.
- It generates multiple distinct proposals satisfying the confirmed course constraints.
- Participants can correct AI misinterpretations.
- It never attributes preferences or votes to the wrong participant.
- A final decision can be exported with provenance and unresolved reservations.
15. Evaluation and experimental design
This project should demonstrate AI engineering, not merely a working interface.
Course clarification, October 15, 2026: the user's “no” to the training/fine-tuning
question is interpreted as no mandatory training or fine-tuning. Plan around
evaluated LLM orchestration; remaining grading, submission, and deployment
requirements are not established by that answer.
The subsequently supplied `project-requirements.pdf` (page 1) offers research and
application avenues with the same score breakdown. It does not explicitly require
model training/fine-tuning or a hosted deployment. It requires an open-access
project GitHub repository link in the report. Additional Canvas/instructor guidance
has not been reviewed; do not infer that this PDF establishes every grading criterion.
15.1 Evaluation datasets
- Synthetic controlled cases: Known preferences, hard constraints, contradictory statements, missing votes, and feasible/infeasible combinations.
- Human-annotated cases: Real team comments with independently confirmed preference labels.
- Adversarial cases: Sarcasm, negation, ambiguous pronouns, conflicting revisions, one dissenting member, unsupported synthesis features.
Avoid using only self-generated examples that mirror the prompts.
15.2 Metrics
Capability	Suggested measure
Preference extraction	Precision, recall, F1 against human-verified labels
Constraint detection	Recall of true hard constraints; false promotion rate
Agreement detection	Precision of supported agreement claims
Conflict detection	Precision/recall on labeled incompatible requirements
Attribution	Fraction of claims linked to correct human/source records
Synthesis validity	Percentage satisfying all confirmed hard constraints
Coverage	Proportion of important confirmed preferences addressed
Fairness	Lowest participant coverage and coverage disparity
Diversity	Distinctness of generated candidate proposals
Hallucination	Unsupported feature-attribution rate
Human usefulness	Blind participant ratings of relevance and clarity
Efficiency	Latency, tokens/cost per synthesis, number of clarification turns


15.3 Baselines and ablations
Compare:
1. Simple summary baseline: Summarize comments and propose one idea.
2. Single-agent structured baseline: One LLM extracts preferences and generates proposals.
3. Full pipeline: Interpreter + theme analysis + synthesis + critic.
4. Without critique: Remove verification stage.
5. Without provenance: Remove evidence-aware generation (for experimental comparison only; not product default).
6. Without clarification: Do not request human corrections.
Test whether added agent complexity materially improves quality relative to latency and cost. Do not assume it does.
15.4 Evaluation protocol
- Predefine a small, labeled benchmark before tuning prompts.
- Separate development examples from held-out evaluation cases.
- Use multiple seeds or repeated runs where stochasticity matters.
- Report uncertainty and qualitative failures, not just mean scores.
- Conduct human review without telling raters which system generated which proposal where practical.
- Never claim “consensus achieved” based solely on AI-estimated utilities.
16. MVP versus later releases
16.1 MVP — build this first
Scope accepted by the user on October 15, 2026; this supersedes the broader
initial MVP where noted. Implementation remains outstanding.
- One four-person workspace with controlled participant accounts.
- Quick thought and idea submission.
- Plain-text idea detail pages.
- Highlight-to-comment annotation with stable anchoring.
- Whole-idea and passage comments; threaded replies and quick reactions are deferred.
- Structured preference extraction with source references.
- Human correction of extracted preferences.
- Agreement/tension summary with citations to comments.
- Generation of two distinct alternative proposals.
- Proposal review with explicit per-person stance.
- Simple decision record and markdown export.
- Real ticketing-system integration (required by the user on October 15, 2026).
  The user selected GitHub Issues and outbound implementation tickets from approved
  proposals. Generate editable ticket drafts, then support human-authorized issue
  creation with stored external links. Ticket import and bidirectional status sync
  are deferred. See `todo.md` §§1 and 6.1.
- Logging and an evaluation harness.
16.2 Phase 2 — only after the MVP works
- Threaded replies and optional quick reactions.
- PDF import with robust passage anchoring.
- Rich-text editor and collaborative live editing.
- Visual idea graph and relationship exploration.
- Automatic duplicate detection and idea merging suggestions.
- Rich proposal comparison matrices.
- Additional integrations beyond the required initial ticketing provider, such
  as Drive and messaging platforms.
- Cross-workspace templates and organization controls.
16.3 Future explorations
- Facilitator agent that asks well-timed clarification questions.
- Dynamic negotiation and trade-off exploration.
- Privacy-preserving preference aggregation.
- Multi-modal image/audio feedback.
- Long-term workspace memory across projects.
- Learning which syntheses teams actually adopt, with opt-in consent.
16.4 Explicit non-goals for MVP
- Production-scale social network.
- Full Google Docs replacement.
- Autonomous posting to external services.
- Real-time collaborative cursor editing.
- Arbitrary PDF fidelity and OCR across all layouts.
- Fully automated consensus decisions.
- Training a foundation model from scratch.
17. Technical implementation proposal
17.1 Pragmatic stack
Selected October 15, 2026; see [docs/architecture.md](docs/architecture.md) for
boundaries, environment, run execution, and implementation references.
- Frontend: Next.js App Router, React, TypeScript, and plain CSS.
- Backend: Python FastAPI with Pydantic v2 boundary validation.
- Database: SQLite with SQLAlchemy 2 and Alembic migrations for the controlled
  pilot; revisit PostgreSQL for multi-instance or sustained concurrent writes.
- AI: LLM API with structured JSON outputs and schema validation.
- Orchestration: Explicit Python workflow stages; no agent framework initially.
- Ticketing: Server-side GitHub REST adapter, one configured repository, reviewed
  ticket drafts, immutable publication authorization, and retry reconciliation.
- Retrieval: Start with SQL/source-linked text retrieval; add embeddings/vector search only if semantic retrieval measurably helps.
- Testing: pytest for backend and agent stages; Playwright for essential UI flows.
- Observability: Prompt versions, agent runs, structured events, tool results, token/cost logging.
17.2 Security and privacy
- Enforce workspace membership on every read and write.
- Treat imported documents, comments, and tool outputs as untrusted data, never instructions to agents.
- Use structured output validation and bounded tool permissions.
- Protect secrets and avoid logging credentials or unnecessary personal data.
- Clearly identify when third-party model APIs process workspace content.
- Provide deletion and retention controls appropriate to the deployment.
- Require approval for any external publication or integration action.
17.3 Reliability
- Idempotent synthesis requests where practical.
- Timeouts and bounded retries.
- Clear error states when model calls fail.
- Preserve user-authored work independently of AI availability.
- Never overwrite original ideas with AI rewrites.
- Cache or snapshot analysis by workspace version to prevent stale consensus reports.
18. Four-person team ownership
Member	Primary responsibility	Deliverables
1 — Product & interaction	Idea workspace, annotation UX, API integration	Usable idea capture, contextual comments, proposal review
2 — Language understanding	Preference extraction, classification, correction loop	Structured outputs, labeled dataset, extraction evaluation
3 — Synthesis & orchestration	Theme analysis, candidate generation, critique loop	Agent workflow, constraint-aware proposals, provenance
4 — Evaluation & platform	Data model, test harness, observability, robustness	Reproducible benchmark, ablations, logging, deployment


Shared responsibility: Integration, testing, prompt review, academic write-up, and demo. No one should be relegated to presentation-only work. If the course strongly prioritizes AI work over UI, keep frontend scope extremely small and redistribute effort toward benchmarking and agent reliability.
19. Delivery plan
Schedule authority: `project-requirements.pdf`, page 1, supplied October 15, 2026.
The user instructed us to follow the PDF, superseding the earlier November 22
deadline and November 21 planning target. All dates below are in 2026; the PDF
does not specify a timezone.
- October 22, 3pm: one teammate registers the team on Canvas.
- November 12, in lecture: proposal presentation, at most five minutes. Upload
  slides by 3pm; cover the problem, existing solutions, and proposed solution.
- November 12, 3pm: proposal PDF, at most two pages, essentially the same content
  as the presentation; worth 10 points.
- December 3, in lecture: final presentation, at most five minutes. Upload slides
  by 3pm; cover the problem, solution, and how well it addresses the problem;
  worth 10 points.
- December 17, 23:59: final report PDF in official ACL format, at most four main
  pages plus unlimited references and appendix, including an open-access project
  GitHub repository link; worth 20 points.
The PDF does not separately assign points to the proposal presentation. See
`todo.md` §§1 and 8 for checkpoints and deliverable tasks. November 22 is only a
proposed internal pilot/evaluation target, not a course deadline. Deployment needs
and any additional course guidance remain open.
Initial five-week build allocation — proposed internal plan
Week 1 — Foundation
Define user stories and schemas; build idea creation, comments, workspace persistence; assemble first labeled examples.
Week 2 — Preference intelligence
Implement structured extraction, source references, correction UI, and initial evaluation.
Week 3 — Synthesis
Implement theme/conflict analysis, constraint-aware candidate generation, and provenance validation.
Week 4 — Group review
Add proposal comparison, participant stances, revision workflow, and decision records; run end-to-end pilot.
Week 5 — Evaluation and demonstration
Run baselines and ablations, fix failure cases, rehearse live demo, and complete report.
Scope-cut order if behind: Defer PDF import, visual graph, real-time editing,
additional integrations, and sophisticated optimization before cutting preference
correction, provenance, human review, or evaluation. Preserve the required outbound
GitHub Issues integration; reduce optional ticket metadata and workflow features first.
20. Live demo script
1. Open a workspace with several rough project ideas.
2. Have four participant profiles contribute distinct natural-language feedback.
3. Highlight an exact passage and add a concern or requirement.
4. Show the AI extracting a preference, then correct one intentional misinterpretation.
5. Display a shared-interest cluster and a genuine unresolved conflict.
6. Request three proposals under explicit time and technical constraints.
7. Open one proposal's lineage to show which comments inspired each feature.
8. Show the critic flagging a violated constraint or unsupported attribution.
9. Have members review, including one reservation or objection.
10. Revise and record the final decision only after the chosen human approval rule is satisfied.
11. Show quantitative comparison against a simple summarization baseline.
The demo must not depend on perfect model behavior. Include at least one honest failure-and-recovery example.
21. Success criteria
Product success
- Participants feel accurately represented.
- They can contribute without first writing polished proposals.
- The system reveals useful common ground and real disagreements.
- Generated proposals are understandable, differentiated, and traceable.
- A decision can be explained afterward using the original contributions.
Technical success
- A complete input-to-synthesis-to-review workflow works reliably.
- Preference extraction and source attribution are evaluated on held-out cases.
- Hard-constraint violations and fabricated agreement claims are measured.
- The multi-stage pipeline is compared with simpler baselines.
- Agent logs support reproducible debugging and analysis.
Failure conditions
- The system invents participant preferences or votes.
- A proposal silently violates confirmed hard constraints.
- AI summaries erase a minority objection.
- Users cannot recover the sources of an AI-generated claim.
- The team spends most of its time on generic app infrastructure rather than AI behavior and evaluation.
22. Open product decisions
These questions are intentionally unresolved:
1. Should a workspace default to open discussion or independent feedback before others' reactions become visible?
2. Resolved October 15, 2026: all four must support or support with reservations;
   review states and workspace-owner decision recording are defined in §9.5.
3. All four must accept a requirement before it becomes binding (§9.5). How much
   structure should be required when someone marks a personal preference “essential”?
4. Should the AI ask clarifying questions immediately or collect them into a review queue?
5. Should participants be able to submit anonymous feedback? If so, how is provenance protected?
6. Which PDF formats must the first release support, if any?
7. Should generated proposals be editable directly, fork-only, or both?
8. What is the minimum useful set of metrics for the course rubric?
9. Course dates and required artifacts follow `project-requirements.pdf` and §19.
   What timezone applies, is there additional Canvas/instructor guidance, and
   what environment should the team use for its demonstration?
10. How will the team collect genuine participant judgments for evaluation without contaminating the test set?
11. Which controlled GitHub repository and authentication setup will the pilot use?
    GitHub Issues with outbound implementation tickets from approved proposals is
    confirmed; import and bidirectional status sync are deferred.
23. Product voice and writing guidance
FeedbackForm should sound like a thoughtful collaborator, not a facilitator forcing agreement.
Prefer:
- “Three people mentioned wanting measurable outcomes. One person has not weighed in yet.”
- “These two ideas seem compatible, but the timeline requirement may rule out their combination.”
- “This proposal preserves A and B's priorities; C's concern remains unresolved.”
- “I may have interpreted your comment as a hard requirement. Is that right?”
Avoid:
- “Everyone agrees!” without explicit evidence.
- “The AI has selected the best idea.”
- “Your concerns have been resolved” when no participant confirmed that.
- Unexplained percentages such as “94% consensus.”
- Invented motivations, false certainty, and bland summaries that erase differences.
24. Final north star
FeedbackForm exists to make collaborative thinking cumulative. A fragment can become a discussion, a discussion can become a shared insight, and shared insights can become proposals. At every stage, participants should be able to see how the work evolved, what was preserved, what was sacrificed, and who still needs to be heard.
The best outcome is not necessarily a compromise or a unanimous vote. It is a well-understood, collectively owned direction that people can support for reasons they recognize as their own.
