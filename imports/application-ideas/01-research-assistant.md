# Autonomous Multi-Agent Research Assistant (Agentic AI)

## Context
- Decision: consider an application-style graduate AI/ML course project.
- Intended use: answer research questions with a grounded, cited report.
- Source: Part A, Project 1 of `AIML_Project_Ideas.pdf` (page 2).
- This is an AI-generated candidate for discussion, not a participant endorsement or team approval.
- The source prioritizes AI/ML development, targeting 80–90% of effort on the AI core with a minimal supporting interface. This is a proposed allocation, not a measured result.

## Proposed idea
- Build cooperating Planner, Researcher, Critic, and Writer agents. Given a research question, they decompose it into subtasks, search and read sources through tools, cross-check claims, critique drafts, and produce a cited report.
- The source proposes autonomous execution after the initial question, without further human input.
- Suggested orchestration options: LangGraph, CrewAI, or AutoGen.
- Tools: web search API, PDF/HTML parsers, and calculator/code execution tools.
- Add a Reflexion-style critique loop to detect unsupported claims.
- Use retrieval-augmented generation with FAISS or Chroma for grounding and citation tracking.
- Minimal demonstration: a terminal CLI or single notebook accepts a question, displays agent progress/tool calls, and ends with a Markdown report containing citations.
- Source rationale: the project demonstrates orchestration, tool use, reflection, and grounded retrieval, resembling deep-research products. The PDF's “industry-grade” framing is a proposal claim, not validated performance.

## Preferences
- Source proposal priorities: agentic AI, grounded reports, citation tracking, and low interface overhead.
- No participant's personal preferences or ranking of this candidate were supplied.

## Concerns
- The source identifies hallucinated or unsupported claims as a failure mode the critique loop should address.
- No participant objections were supplied; the effectiveness of reflection and retrieval remains to be measured.

## Personal requirements
- Not specified. The source's project scope and techniques are suggestions, not personally confirmed requirements or accepted team constraints.

## Open questions
- Which orchestration framework, model, and search service should be selected? The source offers options without choosing them.
- How faithful are the reports and how accurate are the citations on held-out questions?
- How do results change when reflection or retrieval is removed?

## Uncertainty
- No implementation, benchmark results, cost estimates, or confirmed participant support are provided.
- The source assumes three team members and eight weeks, starting September 21, 2026, with a target around November 21. These are historical source assumptions, not the current project's agreed roster or course deadlines.

## Evaluation and demonstration
- Build a held-out set of 20–30 questions and score report faithfulness and citation accuracy.
- Compare runs with and without reflection, and with and without retrieval grounding.
- Live demo: enter a fresh research question, show the multi-agent execution trace and final cited report, and present measured before/after evaluation results if available.

## Suggested timeline
- Weeks 1–2: define agent roles, set up orchestration, and integrate search.
- Weeks 3–4: add retrieval grounding and citation tracking; complete an initial end-to-end pipeline.
- Weeks 5–6: add the Critic/reflection loop and the evaluation questions and metrics.
- Week 7: run reflection/retrieval ablations and tune prompts.
- Week 8: polish the CLI, write the report, and analyze failure cases.

## Suggested role split
- Member 1: Planner/Researcher logic and tool integration.
- Member 2: Critic/reflection loop and retrieval/citation grounding.
- Member 3: evaluation harness, metrics, ablations, and demo CLI.

## References
- `AIML_Project_Ideas.pdf`, Part A, Project 1, page 2; shared scope assumptions on page 1.
- Converted to the FeedbackForm Markdown format; research-style projects are excluded.
