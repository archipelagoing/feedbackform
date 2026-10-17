# Adapting FeedbackForm for the AWS/OpenCV hackathon

Assessment date: October 15, 2026. Target confirmed by the user:
[OpenCV AI Competition 2026, powered by AWS](https://opencv26.devpost.com/).

## Assessment

This is a **moderate-to-large adaptation**, rather than an AWS hosting change.
FeedbackForm currently collects text ideas and comments. Its planned preference
extraction, proposal review, and ticket creation provide a useful collaboration
layer, but the repository has no image-analysis pipeline or AWS deployment.
The AI preference workflow itself is still being implemented.

Handwriting recognition is not required. The competition calls for substantive
OpenCV 5 image/video analysis and a meaningful component running on AWS.
Simply hosting the existing text app on AWS, importing OpenCV without using it,
or sending an image directly to a multimodal model would leave the required
OpenCV contribution unproven. [Official overview](https://opencv26.devpost.com/)

## Best fit without handwriting: collaborative visual design review

Extend the existing idea workflow to accept exported mockups or screenshots.
Participants discuss particular regions, compare alternatives, and approve
implementation work with visual evidence attached.

An example demonstration:

1. Upload two versions of a team's interface mockup.
2. Use OpenCV to align the images, identify changed regions, and flag alignment
   failures instead of generating misleading differences.
3. Show the regions and overlays next to the original images. Participants can
   attach feedback to a region and correct suggested interpretations.
4. Use the detected changes to ask targeted review questions: for example,
   whether an enlarged control addresses someone's stated accessibility concern.
5. After human review, retain the image region and comment as evidence for a
   proposed implementation task. Ticket publication still needs human approval.

This avoids handwriting entirely. OpenCV supplies measurable visual evidence;
the language model connects that evidence to the team's discussion. Pixel
differences alone cannot establish accessibility, usability, intent, or approval.
Limit the first version to comparable desktop screenshots with similar viewport
sizes. Arbitrary photography, handwriting, and video would expand the scope.

## What can be reused, and what must be added

| Area | Current position | Adaptation |
| --- | --- | --- |
| Participants and permissions | Four-person setup, login, membership checks | Reuse access control for image uploads and reads. |
| Feedback and history | Text ideas, comments, exact text versions | Add immutable image versions and region anchors. |
| Evidence and correction | Contracts exist; AI workflow in progress | Add image evidence references and visible overlays; preserve human correction. |
| Vision | No pipeline | Implement and evaluate actual OpenCV 5 alignment and region detection. |
| Storage and execution | Local SQLite, API, frontend | Add an AWS-hosted processing component and private image storage; choose deployment after a small feasibility spike. |
| Proposals and tickets | Planned | Finish only the narrow path needed for the demonstration; do not present planned behavior as working. |
| Evaluation | No measured AI/vision results | Label screenshot pairs and compare region detection with a simple difference baseline. |

New image records should preserve dimensions, content hash, processing version,
coordinate system, and source image IDs. Resizing a displayed image must not
silently move its feedback regions. The existing UTF-16 text offsets cannot serve
as image coordinates.

## Effort estimate

These are engineering estimates, not measured delivery promises. They assume a
developer comfortable with the current stack, access to AWS, and a usable
OpenCV 5 build for the selected environment.

| Deliverable | Estimated focused effort |
| --- | --- |
| OpenCV 5 compatibility spike and controlled image comparison | 1–2 developer-days |
| Uploads, immutable image versions, region display and feedback | 2–3 developer-days |
| Integration with the preference/review workflow | 2–4 developer-days |
| AWS deployment, private storage, reproducible configuration | 1–3 developer-days |
| Evaluation, failures, documentation, demo video | 2–3 developer-days |
| **Total incremental effort** | **8–15 developer-days**, plus unfinished core features |

A narrow local proof of concept could take roughly 2–4 days; that is not a
complete competition submission. Parallel work may shorten calendar time, but
integration, unfamiliar tooling, and OpenCV version availability can lengthen it.
No dependency installation, AWS access, deployment, or vision quality has been
verified for this adaptation.

## Competition constraints and timing

The official overview requires a technical report, judge-accessible code,
reproducible dependencies/instructions, an architecture diagram, a working
endpoint or arranged live demonstration, a video of at most five minutes, and
evaluation evidence. Its deadline text says October 26 at 11:59pm Pacific, while
the page header shows 11:45pm PDT. Use **October 26 before 11:45pm PDT** as a
conservative planning cutoff and confirm the discrepancy with the organizer.
That leaves about eleven calendar days from this assessment.
[Official submission requirements and dates](https://opencv26.devpost.com/)

The optional Agentic Vision path requires visual results to change a later
decision, action, or tool call. The proposed review workflow could fit if the
running system actually uses detected regions to choose subsequent review
steps. An image explanation alone would not demonstrate that requirement.
[Official Agentic Vision requirements](https://opencv26.devpost.com/)

Technical execution accounts for 30% of judging and includes OpenCV implementation
depth, reliability, and evaluation. A superficial vision add-on would therefore
be a weak competitive strategy. [Official judging rules](https://opencv26.devpost.com/rules)

## Recommendation

Keep the course project's text-first workflow as the main milestone. If entering
the hackathon is a priority, first spend one day proving OpenCV 5 can run a useful
screenshot comparison in the intended AWS environment. Continue only if it
detects meaningful changes and exposes failure cases on a small labeled set.

Then build a separate, tightly scoped visual-review demonstration with the same
participant and evidence model. Do not pivot to handwriting just to match the
event: the hard part is adding a useful, evaluated vision capability and deploying
it, regardless of whether the inputs contain handwriting.

This file assesses a possible adaptation; it does not change the approved course
scope or authorize AWS spending, deployment, or competition submission.
