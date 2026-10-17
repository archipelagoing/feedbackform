# Autonomous Data-Pipeline Anomaly & Root-Cause Agent

## Context
- Decision: consider an application-style graduate AI/ML course project.
- Intended use: investigate anomalies in a simulated data pipeline and propose remediation.
- Source: Part A, Project 3 of `AIML_Project_Ideas.pdf` (page 4).
- This is an AI-generated candidate for discussion, not a participant endorsement or team approval.
- The source targets 80–90% of effort on AI/ML with only a small terminal interface. This is a proposed allocation, not a measured result.

## Proposed idea
- Build an agent that monitors structured logs and metrics, detects anomalies, investigates through log/schema/metric tools, ranks root-cause hypotheses, and proposes or executes a remediation script.
- Use synthetic pipeline metrics with a statistical/ML detector such as Isolation Forest, Prophet, or a simple autoencoder.
- Expose log-query, schema-lookup, and metric-query tools to an LLM agent.
- Rank candidate causes and compare them with injected ground truth.
- Simulate failure modes such as schema drift, null spikes, and latency spikes.
- Optionally use a LangGraph state machine for a diagnose → hypothesize → verify loop.
- Minimal demonstration: a rich/textual terminal dashboard streams simulated events and shows the investigation trace and root-cause report.
- Source rationale: the project combines anomaly detection and agentic reasoning over structured and unstructured signals, resembling AIOps/observability systems. The PDF's “industry-grade” framing is a proposal claim, not validated production readiness.

## Preferences
- Source proposal priorities: agentic diagnosis, realistic injected incidents, ground-truth evaluation, and minimal supporting UI.
- No participant's personal preferences or ranking of this candidate were supplied.

## Concerns
- The source proposes hypothesis verification and incident-based evaluation but reports no demonstrated diagnosis or remediation reliability.
- No participant objections were supplied.

## Personal requirements
- Not specified. The proposed failure modes, tools, and simulation are project suggestions, not personally confirmed requirements or accepted team constraints.

## Open questions
- Which anomaly detector and pipeline simulation should be selected?
- How accurate are root-cause diagnoses, and how long does diagnosis take?
- Should the demonstration stop at a proposed remediation or execute it in the simulation? The source mentions both without specifying an approval policy.

## Uncertainty
- No implementation, incident results, remediation success measurements, or confirmed participant support are provided.
- The source assumes three members and eight weeks starting September 21, 2026, targeting around November 21. These are historical source assumptions, not the current project's agreed roster or course deadlines.

## Evaluation and demonstration
- Evaluate root-cause accuracy and time-to-diagnosis over at least 20 injected incidents.
- Expand the failure-mode library to exercise varied conditions.
- Live demo: inject an incident, show the investigation as it runs, and inspect the resulting root-cause hypothesis and remediation diff.

## Suggested timeline
- Weeks 1–2: build the synthetic pipeline, failure-injection framework, and baseline anomaly detector.
- Weeks 3–4: implement log/schema/metric tools and connect the diagnostic loop.
- Weeks 5–6: add hypothesis ranking and remediation-script generation; expand failure modes.
- Week 7: evaluate accuracy and diagnosis time across injected incidents.
- Week 8: polish the terminal dashboard and prepare the report and incident-replay demo.

## Suggested role split
- Member 1: synthetic pipeline, failure injection, and anomaly detector.
- Member 2: agentic diagnosis loop and tool design.
- Member 3: incident evaluation, root-cause metrics, and terminal UI.

## References
- `AIML_Project_Ideas.pdf`, Part A, Project 3, page 4; shared scope assumptions on page 1.
- Converted to the FeedbackForm Markdown format; research-style projects are excluded.
