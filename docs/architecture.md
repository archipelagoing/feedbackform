# FeedbackForm implementation architecture

Status: Selected implementation direction, 2026-10-15. No application is
scaffolded yet. Product intent is in [projBible.md](../projBible.md); the concrete
record contracts are in [data-model.md](data-model.md).

## Stack decision

| Area | Selection | Purpose |
| --- | --- | --- |
| Web | Next.js App Router, React, TypeScript, plain CSS | Idea capture, passage selection, correction, and versioned review in one small workspace UI. |
| API | Python FastAPI with Pydantic v2 | Validate requests and model outputs; own authorization and domain transitions. |
| Persistence | SQLite, SQLAlchemy 2, Alembic migrations | Local persistent pilot with explicit transactions and a migration history. |
| AI orchestration | Explicit Python stages and a provider adapter | Interpret → analyze → synthesize → critique, with bounded revisions and recorded evidence. |
| External tickets | GitHub REST API via a backend HTTP client | Publish reviewed drafts as issues and store the returned IDs and URLs. |
| Verification | pytest and Playwright | Domain/API checks, reproducible AI evaluation, and essential browser flows. |
| Package tools | npm with lockfile; Python virtual environment with pinned dependencies | Reproduce the frontend and backend installations. |

This adopts the bible's primary frontend/backend proposal. SQLAlchemy provides
explicit relational constraints; Pydantic handles boundary validation. SQLite is
the pilot store; revisit PostgreSQL if the team needs multiple API/worker instances
or sustained concurrent writers. No vector database, agent framework, message
broker, or separate integration platform is needed for the initial workflow.

Target the existing Node 24 environment and Python 3.13+; the current local Python
is 3.14.7, so scaffolding must verify dependency compatibility before pinning a
supported interpreter. Resolve exact library versions and commit lockfiles during
scaffolding, rather than claiming uninstalled dependencies are tested.

Initial verified-browser target will be desktop Chrome/Chromium on macOS, with
keyboard operation. Mobile and other browsers remain unverified until checked.
Run locally first. Hosting and public deployment are separate later decisions.

## Application boundaries

The browser calls a same-origin `/api` path proxied to FastAPI during development.
FastAPI is the single authority for reads, writes, sessions, access checks, and
workflow state; Next.js does not implement a second copy of the business rules.
No database file or model/GitHub credential is available to browser code.

Proposed source layout for the next scaffolding task:

```text
web/                         Next.js UI and generated API types
backend/app/api/             Routes, session handling, request/response schemas
backend/app/domain/          Versioning, review, constraints, decision rules
backend/app/db/              SQLAlchemy models and transaction helpers
backend/app/workflows/       Structured stages, validation, bounded execution
backend/app/integrations/    Model-provider and GitHub adapters
backend/migrations/         Alembic revisions
backend/tests/              Domain and API tests
evaluation/                 Labeled cases, baseline runners, reports
web/e2e/                    Essential Playwright flows
```

For the pilot, provision four participant identities through a local admin/seed
command. Give each an independent login secret, store only password hashes, and
use opaque server-side sessions with HttpOnly cookies. Do not use a browser-supplied
`user_id` as authentication. The authenticated identity supplies actors for all
commands. Credentials and session rows stay outside exports and model inputs.
Authentication, CSRF protection, and authorization still require implementation
and verification before the pilot can be called multi-user ready.

## Run execution and freshness

A request creates a persisted run and an immutable input manifest, then returns
its ID. The UI polls run status. Initially execute one run at a time in the API
process, without holding a database transaction open during a model call. On
startup, mark interrupted running jobs as failed and offer a fresh retry; do not
claim durable job resumption. A separate worker can follow if needed.

All human source, preference, constraint, goal, and policy writes increment a
workspace input revision. Persisting AI outputs, reviews, and ticket records does
not itself change that revision. A run reads
and records its manifest in a short consistent transaction. Before draft publication
or decision recording, compare the captured revision against current relevant
inputs and revalidate. Conservatively flag any content/policy revision mismatch
as stale in the first release. Reviews do not change synthesis inputs; they have
their own history and are checked transactionally at decision time.

Store model/provider identifiers, prompt versions, generation settings, input
references, schema version, latency, usage, and stage outcomes. Do not put secrets
in traces. The model provider and model are still open selections dependent on
available team access; configure them behind one adapter, without building a
general multi-provider platform. Evaluation uses recorded settings and held-out
cases; the primary question is still tracked in `todo.md` §7.

## Persistence and authorization rules

Enable SQLite foreign keys on every connection, use short transactions and a
busy timeout, and serialize conflicting writes. Treat migration scripts as the
authority for database evolution. Application role checks supplement database
foreign keys: a valid user reference does not establish permission to act.

Immutable versions are never updated to implement editing. Stable parent records
point to the current version; editing uses an expected-version/revision check and
returns a conflict when another writer got there first. Version creation and the
head-pointer update occur in one transaction.

Changing binding constraints requires a new proposal validation/review round.
Decision recording checks the current proposal version, constraint-set revision,
required roster, and latest review events atomically. A historical decision keeps
its snapshots even after later revisions; it does not endorse the newer content.

For the first pilot, keep the four-person roster and owner fixed once reviews
start. A future membership change must invalidate active approval rounds and
re-establish required reviewers. Withdrawal/redaction must prevent source text
from resurfacing through old runs or exports; do not offer hard deletion until a
consistent retention/redaction path exists. Access checks apply to every source
inspection and export, including historical ones.

## GitHub Issues handoff

Use one configured repository and a server-side fine-grained personal access
token limited to that repository with Issues write permission. This is a
controlled-pilot connection, not OAuth onboarding for arbitrary organizations.
Read the credential from the environment; it is never part of a workspace record.
GitHub authentication does not replace FeedbackForm participant authentication.

After an accepted decision, generate editable ticket drafts. Each ticket includes
a title, description, acceptance criteria, decision/proposal version references,
and a stable export marker. Do not include private comments or participant details
by default. For a local-only app, include stable textual IDs and a source excerpt;
add app links only when a reachable base URL exists.

A human reviews the exact payload and repository and explicitly publishes. Store
that authorization against an immutable batch. A subsequent edit or destination
change needs a new preview and authorization. A client-provided idempotency key
resolves to the same batch; the backend rejects reuse with different content.

Publish items sequentially. Persist intent before each network call and record
the returned issue ID/number/URL before continuing. GitHub issue creation is an
external side effect; a local database transaction cannot make it exactly-once.
If a timeout or process crash makes the outcome uncertain, mark the item unknown
and reconcile its export marker against repository issues before retrying. If
absence cannot be established, require human inspection instead of blind retry.
Successfully published items are not resent when another item fails.

Decision approval and ticket publication are distinct human actions. The approval
of a proposal does not authorize sending arbitrary ticket content to GitHub.

## Implementation references

Consulted official documentation on 2026-10-15:

- [Next.js installation and App Router](https://nextjs.org/docs/app/getting-started/installation)
- [FastAPI relational databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy SQLite connection and foreign-key behavior](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)
- [GitHub issue creation and permission requirements](https://docs.github.com/en/rest/issues/issues#create-an-issue)

These sources inform the selection; compatibility, authentication, concurrency,
and real GitHub publication have not yet been tested in this repository.
