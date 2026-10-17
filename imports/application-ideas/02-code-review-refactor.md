# Agentic Code-Review & Auto-Refactor Swarm

## Context
- Decision: consider an application-style graduate AI/ML course project.
- Intended use: inspect repository changes and propose verified fixes or refactors.
- Source: Part A, Project 2 of `AIML_Project_Ideas.pdf` (page 3).
- This is an AI-generated candidate for discussion, not a participant endorsement or team approval.
- The source targets 80–90% of effort on AI/ML, with a minimal CLI rather than a substantial application interface. This is a proposed allocation, not a measured result.

## Proposed idea
- Build a multi-agent system that ingests a GitHub repository or pull-request diff, reviews changes for bugs, security issues, and style problems, writes and executes unit tests in a sandbox, and proposes/applies refactors while iterating until tests pass.
- Use a code-capable language model with Docker or restricted subprocess execution for tests.
- Expose static analysis tools such as pylint and bandit as agent tools.
- Use a ReAct-style propose-patch → run-tests → observe → retry loop.
- Consider tree-sitter for repository/AST parsing and structured code understanding.
- Bound execution with iteration limits and diff-size limits.
- Minimal demonstration: a CLI accepts a repository and pull request, displays execution progress, and produces a patch file plus a pass/fail test report.
- Source rationale: the project demonstrates code tool use, verification loops, and autonomous planning, resembling coding-agent products. The PDF's “industry-grade” framing is a proposal claim, not evidence of safe or successful fixes.

## Preferences
- Source proposal priorities: substantial agentic AI work, executable verification, iterative improvement, and a thin CLI.
- No participant's personal preferences or ranking of this candidate were supplied.

## Concerns
- The source explicitly calls for sandboxing, loop limits, diff limits, retry/rollback, and false-positive measurement.
- Passing the proposed tests is an evaluation signal; the source supplies no measured evidence that generated patches are correct or safe.
- No participant objections were supplied.

## Personal requirements
- Not specified. Suggested execution controls and project scope have not been personally confirmed or accepted as team constraints.

## Open questions
- Which repository language, coding model, and sandbox configuration should be selected?
- What proportion of seeded bugs can the system patch successfully?
- How often are review findings false positives?
- Does iterative verification improve results over a single-pass reviewer?

## Uncertainty
- The source does not supply implementation results, sandbox validation, model costs, or confirmed participant support.
- Its three-person, eight-week plan begins September 21, 2026, with a target around November 21. These are historical source assumptions, not the current project's agreed roster or course deadlines.

## Evaluation and demonstration
- Curate 15–20 repositories with seeded bugs for benchmarking.
- Measure patch success and review false-positive rates.
- Compare single-pass review with iterative agentic review/refactoring.
- Live demo: provide a seeded repository, show the execution trace, and inspect the resulting test report and before/after diff. A green suite is a proposed outcome, not an existing result.

## Suggested timeline
- Weeks 1–2: build the sandbox and static-analysis wrappers; implement a single-pass reviewer.
- Weeks 3–4: add test generation and execution; establish an end-to-end patch-and-verify loop.
- Weeks 5–6: add iterative refactoring with retry/rollback; curate the benchmark repositories.
- Week 7: evaluate patch success and false positives; tune loop limits.
- Week 8: finalize the CLI and report the single-pass versus iterative comparison.

## Suggested role split
- Member 1: sandbox execution and test-writing agent.
- Member 2: review/refactor agent and static-analysis integration.
- Member 3: benchmark curation, evaluation metrics, and CLI polish.

## References
- `AIML_Project_Ideas.pdf`, Part A, Project 2, page 3; shared scope assumptions on page 1.
- Converted to the FeedbackForm Markdown format; research-style projects are excluded.
