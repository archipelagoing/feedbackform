# Multi-Agent Task-Allocation Marketplace (Agentic Coordination)

## Context
- Decision: consider an application-style graduate AI/ML course project.
- Intended use: simulate agent negotiation over constrained task assignments, such as delivery or compute scheduling.
- Source: Part A, Project 5 of `AIML_Project_Ideas.pdf` (page 6).
- This is an AI-generated candidate for discussion, not a participant endorsement or team approval.
- The source targets 80–90% of effort on AI/ML with only a terminal simulation and simple assignment visualization. This is a proposed allocation, not a measured result.

## Proposed idea
- Build a simulated marketplace of self-interested LLM agents that bid and negotiate over task allocations under time, capacity, and cost constraints.
- Use a coordinator agent to resolve conflicts and renegotiate assignments, aiming to produce allocation behavior without centrally hard-coded allocation rules.
- Consider AutoGen or a custom message-passing loop.
- Choose an auction/negotiation mechanism such as English auctions, Vickrey auctions, or a contract-net protocol driven by LLM bids.
- Use a configurable grid-world or task-graph simulation.
- Compare the agent approach with an appropriate classical baseline, such as greedy allocation or the Hungarian algorithm.
- Minimal demonstration: print negotiation rounds in a terminal and render final assignments using ASCII or matplotlib.
- Source rationale: the project demonstrates coordination, negotiation, and game-theoretic evaluation for scheduling/logistics scenarios. The PDF's “industry-grade” framing and emergent-coordination goal are proposal claims, not established results.

## Preferences
- Source proposal priorities: multi-agent coordination, constrained allocation, comparison with classical methods, and a lightweight interface.
- No participant's personal preferences or ranking of this candidate were supplied.

## Concerns
- The source explicitly proposes evaluating allocation efficiency, convergence time, and robustness; it supplies no evidence that the agent approach outperforms a classical baseline.
- No participant objections were supplied.

## Personal requirements
- Not specified. Simulation constraints and negotiation protocols are suggested experiment settings, not personally confirmed requirements or accepted team constraints.

## Open questions
- Which task environment, negotiation protocol, and agent framework should be selected?
- How efficiently do agents allocate tasks compared with an appropriate classical baseline?
- How quickly does negotiation converge, and how robust is it under different constraints?

## Uncertainty
- No implementation, allocation results, convergence measurements, or confirmed participant support are provided.
- The source assumes three members and eight weeks starting September 21, 2026, targeting around November 21. These are historical source assumptions, not the current project's agreed roster or course deadlines.
- The proposed 10–20-agent scale and emergent allocation behavior are targets requiring verification.

## Evaluation and demonstration
- Compare allocation efficiency against the classical baseline.
- Measure negotiation convergence time and robustness across varied constraints.
- Live demo: run more than ten simulated agents, show their negotiation rounds, render the assignment map, and present a measured efficiency comparison if available.

## Suggested timeline
- Weeks 1–2: build the simulation, task/agent generator, and classical-solver baseline.
- Weeks 3–4: implement LLM bidding and contract-net negotiation.
- Weeks 5–6: add coordinator/re-negotiation logic and scale to 10–20 agents with varied constraints.
- Week 7: evaluate efficiency, convergence, and robustness.
- Week 8: polish the visualization and report the efficiency gap relative to the baseline.

## Suggested role split
- Member 1: simulation environment and classical baseline solver.
- Member 2: LLM negotiation/bidding protocol.
- Member 3: coordinator logic, evaluation metrics, and visualization.

## References
- `AIML_Project_Ideas.pdf`, Part A, Project 5, page 6; shared scope assumptions on page 1.
- Converted to the FeedbackForm Markdown format; research-style projects are excluded.
