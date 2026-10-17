# Agentic Customer-Support Resolution Engine with Memory

## Context
- Decision: consider an application-style graduate AI/ML course project.
- Intended use: resolve multi-turn customer-support tickets with knowledge retrieval, mock account/order tools, and cross-session memory.
- Source: Part A, Project 4 of `AIML_Project_Ideas.pdf` (page 5).
- This is an AI-generated candidate for discussion, not a participant endorsement or team approval.
- The source targets 80–90% of effort on AI/ML and keeps the demonstration to a terminal conversation. This is a proposed allocation, not a measured result.

## Proposed idea
- Build an agent that retrieves relevant knowledge-base articles, consults mock account/order APIs, decides whether to resolve or escalate a ticket, and remembers prior interactions with the same user across sessions.
- Use retrieval-augmented generation over synthetic FAQs and policies.
- Implement mock order-lookup and refund tools as Python functions without needing a real account/order database.
- Use a vector memory store keyed by user ID for cross-session recall.
- Track multi-turn dialogue state.
- Implement a confidence/uncertainty-based escalation policy for handing off to a human.
- Minimal demonstration: a terminal chat with a user identifier that shows memory persisting across separate sessions.
- Source rationale: the project combines retrieval, tools, memory, and escalation policies, resembling customer-support agents. The PDF's “industry-grade” framing is a proposal claim, not evidence of production readiness.

## Preferences
- Source proposal priorities: multi-turn support resolution, persistent memory, explicit escalation, and a minimal chat interface.
- No participant's personal preferences or ranking of this candidate were supplied.

## Concerns
- The source identifies uncertainty and the need for escalation as design concerns and proposes measuring memory-recall accuracy.
- No participant objections or observed system failures were supplied.

## Personal requirements
- Not specified. Mock APIs, memory mechanisms, and escalation behavior are project suggestions, not personally confirmed requirements or accepted team constraints.

## Open questions
- How should confidence or uncertainty be estimated and the escalation policy selected?
- What are the resolution rate, escalation precision/recall, and cross-session memory-recall accuracy?
- Which knowledge-base examples, ticket labels, and memory store should be used?

## Uncertainty
- No implementation, labeled ticket set, measured results, or confirmed participant support are provided.
- The source assumes a three-person team and eight weeks starting September 21, 2026, targeting around November 21. These are historical source assumptions, not the current project's agreed roster or course deadlines.

## Evaluation and demonstration
- Build a labeled support-ticket set.
- Measure resolution rate, escalation precision/recall, and memory-recall accuracy.
- Live demo: resolve an issue in one session, open another with the same user ID to demonstrate retained context, and include a ticket that intentionally triggers escalation.

## Suggested timeline
- Weeks 1–2: build the synthetic knowledge base, mock APIs, and single-turn retrieval agent.
- Weeks 3–4: add multi-turn state and cross-session memory.
- Weeks 5–6: add escalation policy and confidence estimation; create labeled test tickets.
- Week 7: evaluate resolution, escalation, and memory recall.
- Week 8: polish the CLI chat and write an error-analysis report.

## Suggested role split
- Member 1: retrieval, knowledge base, and mock APIs.
- Member 2: memory architecture and multi-turn state.
- Member 3: escalation policy, evaluation dataset/metrics, and demo CLI.

## References
- `AIML_Project_Ideas.pdf`, Part A, Project 4, page 5; shared scope assumptions on page 1.
- Converted to the FeedbackForm Markdown format; research-style projects are excluded.
