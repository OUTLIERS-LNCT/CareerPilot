# PrepPilot AI backend

This FastAPI service implements the backend workflow in the supplied PrepPilot project and technical blueprints. It uses SQLite by default for local development and supports PostgreSQL through `DATABASE_URL`, with SQLAlchemy 2, Pydantic, JWT bearer tokens and bcrypt.

## Scope and blueprint assumptions

The blueprints recommend a diagnostic-to-roadmap loop first, then resume/JD analysis and text interviews. This backend provides those flows, plus profile, resource catalogue, question authoring, and a dashboard. An idempotent seed command loads a starter set of skills, MCQs and curated resource links. JD matching uses exact skill-catalogue terms; the roadmap schedule remains deterministic while optional AI adds study guidance and interview follow-ups. These choices fill details the blueprints leave open. Voice, code execution, company scraping, refresh tokens, email verification, and frontend work are deferred. Readiness scores are study signals, not hiring predictions.

## Local setup (PowerShell)

Install Python 3.11 or newer, then run these commands from this folder. Docker is not required:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env`: set fresh `JWT_SECRET` and `ADMIN_BOOTSTRAP_SECRET`, and make sure `DATABASE_URL=sqlite:///./preppilot.db`. If `.env` already has a PostgreSQL URL, replace it with the SQLite URL for local use. Then create the schema and seed catalogue:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.seed_catalogue
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. Local data is stored in `preppilot.db` in the project folder. Resume files are private under `private_uploads/` and excluded from git. For Render, use its managed PostgreSQL database and set `DATABASE_URL` to the connection string in the service environment.

## Admin bootstrap and catalogue

Public signup always creates a student. Bootstrap the first admin only when no admin exists; it requires the server-side secret:

```powershell
$body = @{ email='admin@example.test'; password='change-this-long-password' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/v1/admin/bootstrap?secret=YOUR_SECRET' -ContentType 'application/json' -Body $body
```

For Swagger, click **Authorize** and enter your account email in `username` and your password. Swagger posts the form to `/api/v1/auth/token`. For frontend JSON login, use `/api/v1/auth/login`. Add content with `POST /api/v1/admin/skills`, `/admin/resources`, and `/admin/questions`. The private `answer_index` is never exposed as a question listing. Do not put real demo credentials in source control.

## API map

All application routes use `/api/v1` and protected calls require `Authorization: Bearer <token>`.

| Area | Routes | Access |
|---|---|---|
| Health | `GET /health/live`, `GET /health/ready` | Public |
| Auth | `POST /auth/signup`, `POST /auth/login` (JSON), `POST /auth/token` (Swagger OAuth form), `GET /auth/me` | Signup/login public; `me` authenticated |
| Admin bootstrap | `POST /admin/bootstrap?secret=...` | One-time secret gated |
| Profile | `GET/PUT /profile` | Own profile |
| Catalogue | `GET /catalogue/skills`, `GET /resources?skill_id=...` | Authenticated; verified resources |
| Assessments | `GET /assessments/questions`, `POST /assessments/submit`, `GET /assessments/attempts` | Own attempts; score computed server side |
| Roadmaps | `POST/GET /roadmaps`, `GET /roadmaps/{id}`, `PATCH /roadmaps/tasks/{id}` | Own roadmaps/tasks |
| Resume/JD | `POST/GET /resumes`, `DELETE /resumes/{id}`, `POST /analysis` | Own files/analyses |
| Interviews | `POST /interviews`, `POST /interviews/{id}/answers`, `POST /interviews/{id}/ai-answer`, `POST /interviews/{id}/complete` | Own sessions |
| Study tracking | `POST/GET /study-sessions` | Own study logs |
| Roadmap AI | `GET /roadmaps/{id}/study-guide` | Own roadmap, stores guidance |
| Resource recommendations | `GET /resources/recommendations?roadmap_id=...` | Own tasks; catalogue links only |
| AI status | `GET /ai/status` | Authenticated; no key returned |
| Dashboard | `GET /dashboard` | Own summary |
| Admin content | `POST /admin/skills`, `/admin/resources`, `/admin/questions`, `GET /admin/content` | Admin only |

## How requests work

FastAPI validates JSON and multipart data using Pydantic. The bearer dependency verifies the signed token, then loads an active user. Private queries include both record ID and the current user's ID. Assessment requests contain question IDs and selected option indexes; the trusted answer key remains in PostgreSQL and the server calculates the score. Roadmaps use score gap, estimated relevance and urgency weights, and reserve 22% of stated study time for revision and mocks. Prerequisite graphs aren't implemented because the source blueprint describes them as a future data input without defining their data model.

## Database and migrations

`app/main.py` contains routes and SQLAlchemy models in this teaching scaffold. Tables cover users, profiles, skills, resources, questions, attempts, roadmaps/tasks, resumes, analyses, interview sessions, study sessions and study guidance snapshots. Foreign keys tie private rows to their owners. To add future schema changes:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Review autogenerated migrations before deployment. The initial migration creates the current metadata. Local runs use SQLite; Render can use PostgreSQL by setting `DATABASE_URL`. Split routes into `app/api/v1/` modules and business logic into services as the project grows.

## Security and privacy

Passwords are bcrypt hashes and JWT access tokens expire after 30 minutes. Role comes from the server. The bootstrap secret is passed as a query parameter, so only use it locally or over HTTPS and remove/rotate it after creating the admin. Uploads accept PDF, DOCX and TXT with a 5 MB default cap; files are named randomly, stored under a per-user directory, and never served publicly. Ownership is checked for listing, analysis and deletion. Parser failures don't return private document text.

Before a public deployment, add HTTPS, strict CORS, rate limits, malware scanning and parser isolation, secret management, database backups and a documented data retention/deletion policy. Never log tokens, passwords, API keys or resume/JD contents. Keep OpenRouter credentials server side if you add the client.

## Verification

```powershell
pytest
python -m compileall app tests
```

The included test checks roadmap task estimates against the supplied time budget. Add PostgreSQL-backed API tests for cross-student access, bootstrap behavior, token expiry, upload failures, repeated assessment policy and migration rollback before production use.

## Deployment

Use Render PostgreSQL with TLS/backups, a least-privilege database account, HTTPS, and a Python host running Uvicorn. Set `DATABASE_URL`, `JWT_SECRET`, `FRONTEND_ORIGIN` and upload settings in the host secret store. Run Alembic migrations during release. `/health/ready` checks database connectivity; `/health/live` checks process liveness. This repository contains the backend only.


## Build and seed the database

For local use, SQLite is created as a file automatically when the migration runs. No Docker or separate database install is needed. Set DATABASE_URL=sqlite:///./preppilot.db in .env, then run:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.seed_catalogue
```

The seed command is idempotent: it adds missing skills, questions and curated learning resources without deleting admin content. It includes starter content for DSA, SQL, DBMS, OOP, OS and other placement topics. For Render, create a managed PostgreSQL database, set the service DATABASE_URL from Render, and run the same migration and seed commands during deployment. The database engine is selected from the URL.

## Progress tracking and AI features

`POST /api/v1/study-sessions` records a student's planned and actual study time, optional roadmap task and a short reflection. `GET /api/v1/study-sessions` returns that student's own history. Existing attempts and task status form additional progress evidence. `GET /api/v1/resources/recommendations` returns only verified resources already attached to incomplete, high-priority roadmap tasks.

To enable AI guidance, put an OpenRouter API key and a model slug supported by your OpenRouter account into backend `.env` as `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`. Keep the key server-side. `GET /api/v1/ai/status` reports whether it is configured. `GET /api/v1/roadmaps/{id}/study-guide` asks the model for a study focus and resource IDs drawn from the existing catalogue, stores the guidance snapshot, and falls back to a deterministic study checklist if the provider is unset, times out, or returns invalid JSON. `POST /api/v1/interviews/{id}/ai-answer` evaluates an answer with a four-part coaching rubric and asks a follow-up; it has a fixed local fallback. The LLM cannot set assessment scores or change roadmap deadlines.

Calling an AI endpoint can send the interview answer or roadmap task metadata to the configured OpenRouter model provider. Resume/JD text is not sent by these features. Tell students which features use an external provider and obtain any consent required for your deployment. Provider/model availability and costs depend on the account and selected model.

The route modules and schemas remain centralized in `app/main.py` for this beginner scaffold; the `app/models`, `app/schemas`, and `app/services` packages re-export stable symbols while the code can be split into domain routers later.







## Frontend

The `frontend/` folder contains the Vite/React student experience. Start the backend first, then in a second PowerShell terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. It calls the API at `http://127.0.0.1:8000/api/v1` by default. The backend `.env` should allow `FRONTEND_ORIGIN=http://localhost:5173`. See `frontend/README.md` for Vercel build settings.
