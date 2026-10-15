# FeedbackForm

A collaborative workspace for turning ideas and feedback into evidence-linked
proposals, explicit group decisions, and reviewed GitHub implementation tickets.

Current stage: authenticated idea workspace. Four provisioned participants can
sign in, see their shared decision question and roster, post rough ideas, edit
their own ideas as new versions, and inspect history. Sessions survive reload and
are revoked on logout. The backend enforces membership and author-only edits.
Annotation UI, AI execution, proposal reviews/decisions, and GitHub publication
remain unimplemented. No model or GitHub credentials are needed for this milestone.

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
uv run python -m app.seed
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```sh
cd web
npm ci
npm run dev
```

Run `app.seed` once on an empty migrated database. It prompts for the workspace
question and four names/logins/passwords; passwords are entered without echo,
must be 12–256 characters, and are stored only as salted scrypt hashes.
The first participant owns the workspace. The command refuses to overwrite
existing accounts or workspaces; skip it on later starts. No default production
accounts or passwords are installed.

Open [the local app](http://127.0.0.1:3000), sign in with a provisioned account,
and share an idea. Reload to retrieve it, edit it to create a new version, and
use View history to inspect the original. [API documentation](http://127.0.0.1:8000/docs)
lists the available routes.
`GET /api/health` returns 503 until the expected database migration is installed.
Startup never creates tables implicitly; apply migrations explicitly.

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
ports 18080 and 3100. They migrate an isolated, ignored `backend/data/e2e.db` and
provision four test-only identities in that database. They verify real proxy
connectivity, four-person sign-in and sharing, reload persistence, author-only
edit controls, version history, logout, and simulated failure/session-expiry
states. Known browser-test credentials exist only in test code and the guarded
test seed; never use that seed against a real workspace. Backend tests use
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
auth, workspace reads, idea capture/editing, and history. Further command schemas
will appear in OpenAPI as their routes are implemented.

## Project references

- [Product bible](projBible.md): intent, invariants, and course deliverables.
- [Project checklist](todo.md): current state, next steps, and completion evidence.
- [Architecture](docs/architecture.md): selected stack and system boundaries.
- [Data contracts](docs/data-model.md): versioning, evidence, approvals, and ticket publication.
- [Course requirements](project-requirements.pdf): submission dates and formats.

Selected stack: Next.js/TypeScript, FastAPI/Pydantic, SQLite/SQLAlchemy/Alembic,
and a planned explicit Python AI workflow. Future GitHub integration runs on the backend.
