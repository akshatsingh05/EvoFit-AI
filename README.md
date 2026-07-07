# EvoFit AI

AI-powered adaptive fitness and nutrition coaching web application. This
README covers the production-ready build produced during the Deployment
Readiness sprint (Sprint 4). For a history of what each feature sprint
built, see `SPRINT_1_README.md` / `SPRINT_2_README.md` / `SPRINT_3_README.md`
and `MODULES.md` / `ARCHITECTURE.md` / `DESIGN.md` / `PRODUCT.md`.

## Project Overview

EvoFit AI is a full-stack coaching app that onboards a user's goals, body
metrics, fitness experience, and medical history, then generates and
adapts personalized workout and nutrition plans over time based on daily
check-ins and logged progress.

Core modules: Authentication (JWT + refresh tokens), Onboarding, Medical
History, Dashboard, Workout, Nutrition, Adaptive AI, Daily Check-In,
Progress Tracking, Reports, Notifications, Workout Calendar/History,
Nutrition History, Profile Editing, Settings/Dark Mode, Delete Account,
Smart Regeneration.

## Technology Stack

**Frontend**: React, Vite, Tailwind CSS, React Router, Axios, React Hook Form
**Backend**: FastAPI, Python, SQLAlchemy 2.0, Pydantic v2, JWT auth (access + refresh)
**Database**: SQLite (development) / PostgreSQL (production), versioned via Alembic
**Deployment**: Docker, Render (backend + Postgres), Vercel (frontend), or Neon (Postgres)

## Folder Structure

```
evofit-ai/
├── backend/
│   ├── app/
│   │   ├── core/          # config, security, logging, exceptions, rate limiting
│   │   ├── middleware/     # security headers
│   │   ├── database/       # engine/session setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # FastAPI route handlers, one per module
│   │   ├── services/        # business logic (incl. services/ai/ provider layer)
│   │   ├── dependencies/    # shared FastAPI dependencies (e.g. get_current_user)
│   │   └── main.py
│   ├── alembic/              # migration environment + versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Procfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/, components/, context/, routes/, services/
│   │   └── main.jsx, App.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── docker-compose.yml
├── render.yaml
├── vercel.json
├── DEPLOYMENT_GUIDE.md
├── ENVIRONMENT_VARIABLES.md
├── DATABASE_MIGRATION_GUIDE.md
└── DEPLOYMENT_CHECKLIST.md
```

## Installation

Prerequisites: Python 3.12+, Node.js 20+, (optionally) Docker.

```bash
git clone <repo-url>
cd evofit-ai
```

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # defaults work as-is for local SQLite development
alembic upgrade head        # creates evofit.db with the full schema
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`; interactive API docs at
`http://localhost:8000/docs` (disabled automatically when `ENVIRONMENT=production`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env         # VITE_API_BASE_URL defaults to http://localhost:8000
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Environment Variables

See `ENVIRONMENT_VARIABLES.md` for the full reference. Quick summary:
`backend/.env.example` and `frontend/.env.example` list every variable the
app reads; copy each to `.env` and fill in real values for anything beyond
local development. **Never commit `.env` files** — only the `.env.example`
templates are tracked.

## Running Locally

Backend: `uvicorn app.main:app --reload` (from `backend/`)
Frontend: `npm run dev` (from `frontend/`)

## Docker

```bash
docker compose up --build
```

This starts Postgres, the backend (migrated automatically on boot), and the
built frontend served via nginx, at `http://localhost:8080` (frontend) and
`http://localhost:8000` (backend API). See `DEPLOYMENT_GUIDE.md` for details.

## Database Migrations

Schema changes are managed by Alembic, not `Base.metadata.create_all()`.
See `DATABASE_MIGRATION_GUIDE.md` for the full workflow. Quick reference:

```bash
# after changing a model in app/models/
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## Deployment Instructions

Full walkthrough in `DEPLOYMENT_GUIDE.md`. Summary: backend + Postgres on
Render (`render.yaml`), frontend on Vercel (`vercel.json`), database
optionally on Neon instead of Render's managed Postgres.

## API Documentation

Interactive Swagger UI is available at `/docs` (and ReDoc at `/redoc`) on
any non-production deployment. In production these are disabled by default
(`ENVIRONMENT=production` sets `docs_url`/`redoc_url`/`openapi_url` to
`None` in `app/main.py`) since the API is only consumed by the first-party
frontend; re-enable by adjusting that check if a public API is desired
later.

## Screenshots

_Add screenshots of the Dashboard, Workout, Nutrition, and Progress screens
here before publishing._

| Screen | Screenshot |
|---|---|
| Dashboard | _placeholder_ |
| Workout | _placeholder_ |
| Nutrition | _placeholder_ |
| Progress | _placeholder_ |

## Future Enhancements

- Wire a real `ClaudeProvider` / `ChatGPTProvider` into the existing
  `AIProvider` interface (`app/services/ai/provider.py`) once external AI
  calls are approved — the abstraction is already in place, only the
  concrete provider classes and `AI_PROVIDER` switch need to be added.
- Redis-backed rate limiting if the backend scales beyond a single instance.
- Transactional email delivery for password-reset tokens (currently logged
  server-side rather than emailed).
- CI pipeline (lint + test + build) gating deploys.
