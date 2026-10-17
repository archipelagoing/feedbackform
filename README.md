# FeedbackForm

A collaborative workspace for turning ideas and feedback into evidence-linked
proposals, explicit group decisions, and reviewed GitHub implementation tickets.

Current stage: authenticated idea workspace with preference extraction and review.
On an empty database, the frontend collects the workspace question and four
participant accounts, then signs in the first participant as owner. Participants can
sign in, see their shared decision question and roster, post rough ideas, edit
their own ideas as new versions, inspect history, and comment on complete ideas
or exact passages. Sessions survive reload and are revoked on logout. The backend
enforces membership, author-only edits, and exact source-version anchors.
OpenAI extraction produces evidence-linked drafts that each participant can
confirm, correct, or withdraw with retained history. Proposal generation,
group reviews/decisions, and GitHub publication remain unimplemented.
Idea capture and review work without model credentials; extraction needs the
server-side OpenAI configuration described below.

## Local setup

Requirements: Node 24, npm, Python 3.13 or 3.14, and
[uv](https://docs.astral.sh/uv/getting-started/installation/). Verified locally with
Node 24.10.0, npm 11.6.0, and Python 3.14.7. Dependency resolutions are recorded
in `web/package-lock.json` and `backend/uv.lock`.

Start the backend in one terminal:

```sh
cd backend
uv sync --frozen
uv run alembic upgrade head
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```sh
cd web
npm ci
npm run dev
```

Open [the local app](http://127.0.0.1:3000). On the first visit, follow the setup
wizard: enter the workspace name and decision question, then four display names,
login names, passwords, and password confirmations. Passwords must be 12–256
characters; duplicate logins and mismatched confirmations are rejected. Setup
creates all four accounts atomically and signs you in as participant 1, the owner.
On later visits, sign in normally. Setup cannot overwrite existing accounts or
workspaces, and no default production credentials are installed. Passwords stay
in form memory until submission and are stored only as salted scrypt hashes.
There is no terminal account-setup step. The optional `app.seed` command remains
available for headless local provisioning; it uses the same empty-database guard.

After signing in, share an idea. Reload to retrieve it, edit it to create a new version, and
use View history to inspect the original. [API documentation](http://127.0.0.1:8000/docs)
lists the available routes.
To discuss an idea, use Comment on idea, or select text in its body and choose
Comment on selected passage. The keyboard alternative opens a passage search
field: type the exact passage, Tab to the matching excerpt's comment button, and
Enter to open the comment form. Repeated matches show surrounding text so you can
choose the occurrence you mean. Saved passages are highlighted on their source
version. Comments include author/time, quoted text, and an expandable original
context. After an idea edit, earlier comments stay labeled with their original
version and are not relocated onto the new text. Use Refresh comments to fetch
other participants' feedback; live synchronization is not implemented.
`GET /api/health` returns 503 until the expected database migration is installed.
Startup never creates tables implicitly; apply migrations explicitly.

For an AI-generated project brief, use **Import a Markdown document** beneath
Share an idea. Download the template, choose a UTF-8 `.md` or `.markdown` file,
review/edit its plain-text preview, confirm it as your contribution, and import
it. The document becomes a versioned idea eligible for normal preference
extraction; importing alone does not call OpenAI. See the
[Markdown format and suggested AI prompt](docs/markdown-import.md) and
[downloadable template](web/public/templates/idea-template.md).
Idea cards render Markdown headings, lists, emphasis, code, and tables. Use
**Show Markdown source** to inspect the original. Passage comments remain anchored
to source offsets; HTML is escaped and embedded images are not fetched.

The default database is `backend/data/feedbackform.db` when commands run from
`backend/`. To override it, export `FEEDBACKFORM_DATABASE_URL` in that shell before
both Alembic and Uvicorn. Backend `.env` files are not loaded automatically.
See [backend/.env.example](backend/.env.example). For the web proxy, copy
[web/.env.example](web/.env.example) to `web/.env.local` if you need a different
backend origin. Rebuild the web app after changing the proxy for production mode.
Local databases, credentials, dependency folders, and build outputs are ignored.

Sessions last eight hours. Cookies are HttpOnly and SameSite=Strict; only token
hashes are stored. Authenticated writes require a session-bound CSRF header and
an explicit allowed Origin. Login also requires the allowed Origin and custom
browser header. `FEEDBACKFORM_ALLOWED_ORIGINS` defaults to the two localhost
frontend origins on port 3000; update it when changing the frontend address.
Set `FEEDBACKFORM_SECURE_COOKIES=1` when using HTTPS. The local HTTP default is 0.
API responses use `Cache-Control: no-store`. Sign-in attempts are limited per
direct peer in the single API process; proxy/multi-instance hosting needs its own
configuration. This milestone does not include signup, password reset, or hosted auth.

## OpenAI extraction and participant review

The workspace now includes **Understand everyone’s priorities**, above Shared
ideas. If an older backend is running, restart it to load the new routes, then
refresh the browser. A production web server also needs a fresh build and restart.
Without model configuration, this panel visibly explains that a connection is
needed and disables extraction; it never substitutes fake AI results.

The app operator must export `OPENAI_API_KEY` and `OPENAI_MODEL` in the backend
server's environment before starting it. Use a model available to your OpenAI
project that supports the Responses API and strict Structured Outputs. The model
is deliberately explicit; no paid default is selected. Backend `.env` files are
not automatically loaded. Keep credentials server-side and out of chat, source
control, browser storage, and `NEXT_PUBLIC_*` variables.

Select **Extract preferences from new feedback** after sharing ideas or comments.
The backend records an immutable input snapshot and starts a background job; the
UI polls for completion. Only one extraction runs at a time in this local pilot.
The job sends the decision question, new source text, comment context, opaque
participant/source IDs, and the latest interpretation revisions to OpenAI.
Passwords and login names are not included. External model processing is therefore
part of the data flow; use feedback your team is comfortable sending to OpenAI.

The server uses the [Responses API structured-output format](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)
through Python's standard HTTP library, with no additional dependency. Requests
set `store: false`; this is not a claim of zero provider-side retention. Calls have
a 45-second socket timeout, a 6,000-output-token cap, and no automatic retries.
The pilot caps inputs at 200 sources, 1,000 interpretation heads, and 100,000
serialized characters. Usage and duration are recorded when available; pricing
and cost estimates are not calculated.

Output must pass schema, exact-quote, source-manifest, and participant-ownership
checks before any interpretation is saved. Idea quotes receive server-calculated
UTF-16 spans. Comment evidence retains the exact annotation version. These checks
establish provenance, not semantic correctness. Refusals, incomplete responses,
invalid references, and discussion changes during a call produce failed runs with
no partial interpretations. A retry uses a new request key; resending the same key
returns the original run without another model call.

Expand **Inspect original evidence** and review your own draft. Confirmation,
correction, and withdrawal append immutable revisions and reject stale edits.
All participants can see interpretations; only the attributed participant can
change one. Corrections and withdrawals become context for subsequent extraction,
and already processed source versions are not interpreted again. Changed source
versions are eligible as new feedback. Historical evidence is labeled. Confirming
an essential personal requirement does not create a binding group constraint.

Run one backend process only: restart recovery marks interrupted jobs as failed;
there is no durable queue or multi-worker coordination. Refresh interpretations
to fetch other people's reviews. Evidence-linked group summaries, synthesis,
constraint acceptance, and proposal review are subsequent milestones.

See [the evaluation plan and cases](backend/evaluation/README.md). Live OpenAI calls
and semantic quality have not been verified with this team's credentials.

## Verification

From `backend/`:

```sh
uv run pytest -q
uv run ruff check app migrations scripts tests
uv run ruff format --check app migrations scripts tests
uv run alembic check
```

From `web/`:

```sh
npm run typecheck
npm run build
npx playwright install chromium
npm run test:e2e
```

The browser tests start and stop their own API and production web servers on
ports 18080 and 3100. Each run migrates a fresh, ignored `backend/data/e2e-<id>.db`.
A dependency test provisions four test-only identities through the actual browser
wizard before the remaining checks run. They verify real proxy
connectivity, four-person sign-in and sharing, reload persistence, author-only
edit controls, version history, logout, and simulated failure/session-expiry
states. Annotation checks additionally cover mouse/keyboard selection, repeated
phrases, emoji/CRLF offsets, persistence, and earlier-version context after edits.
Preference checks run against the real API/database using the explicit provider
double in `backend/tests/e2e_app.py`: extraction, evidence inspection, correction,
reload/history, participant-only controls, withdrawal, and missing connection UI.
The production entry point never loads this double. These are workflow tests,
not measurements of OpenAI extraction quality.
Known browser-test credentials exist only in test code and the isolated test
database; never use them for a real workspace. Backend tests use
temporary databases and check password/session behavior, Origin/CSRF protection,
membership isolation, stale edits, migrations, history, and input boundaries.

The initial migration has a downgrade for disposable databases; returning to
`base` destroys all application data. Back up real data before any destructive
migration. Alembic autogeneration currently warns about intentional cycles between
parent records and their current versions; tests compare every migrated foreign
key against the ORM metadata. The current Starlette test client also emits an
httpx deprecation warning; tests still pass.

## Generated contracts

From `backend/`, run `uv run python -m scripts.export_contracts` to regenerate
`openapi.json` and `contracts.json`. The latter is a map of named boundary JSON
schemas, including the discriminated workflow envelope. From `web/`, run
`npm run generate:api` to regenerate frontend API types. These commands require
no running server, database, or external account. Generated types cover health,
setup, auth, workspace reads, idea capture/editing, history, annotation create/list,
preference review/history, and extraction routes. Further command schemas
will appear in OpenAPI as their routes are implemented.

## Project references

- [Product bible](projBible.md): intent, invariants, and course deliverables.
- [Project checklist](todo.md): current state, next steps, and completion evidence.
- [Architecture](docs/architecture.md): selected stack and system boundaries.
- [Data contracts](docs/data-model.md): versioning, evidence, approvals, and ticket publication.
- [Markdown import format](docs/markdown-import.md): AI-generated briefs, template, review, and extraction.
- [Course requirements](project-requirements.pdf): submission dates and formats.
- [AWS/OpenCV adaptation assessment](aws-opencv-adaptation.md): vision scope and estimated effort without handwriting recognition.

Selected stack: Next.js/TypeScript, FastAPI/Pydantic, SQLite/SQLAlchemy/Alembic,
and an explicit Python AI workflow. Future GitHub integration runs on the backend.
