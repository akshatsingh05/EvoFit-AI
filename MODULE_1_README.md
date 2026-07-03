# EvoFit AI — Module 1: Authentication & User Setup

This is Module 1 of 4 (see MODULES.md). It implements the complete user entry
flow end to end, backed by a real database — no mock data.

## What's included

**Backend** (`backend/`) — FastAPI + SQLAlchemy + SQLite + JWT
- `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`, `POST /auth/forgot-password`
- `GET /onboarding`, `POST /onboarding` (incremental step saves; auto-marks complete)
- `GET /medical-history`, `POST /medical-history`
- Password hashing (bcrypt), JWT bearer auth, Pydantic validation on every input
- Thin routers → services (business logic) → SQLAlchemy models, per ARCHITECTURE.md

**Frontend** (`frontend/`) — React + Vite + Tailwind + React Router + Axios + React Hook Form
- Landing, Login, Signup, Forgot Password
- 6-step Onboarding wizard: Goals → Body Metrics → Fitness Experience → Lifestyle & Diet
  → Medical History → Review. Saves to the backend after each step and **resumes where
  you left off** if you reload mid-flow.
- Auth context + protected routes (redirects to `/login` if unauthenticated, to
  `/onboarding` if onboarding is incomplete)
- All colors, type scale, spacing, radii, and shadows pulled directly from DESIGN.md's
  token block into `tailwind.config.js` — no invented design system

## Verified working (see smoke test output from build)

- Signup → JWT issued → login works → `/auth/me` returns the real user
- Onboarding: partial save (goals only) persists and reloads correctly; saving all
  4 steps flips `has_completed_onboarding` to `true` automatically
- Medical history saves and is retrievable
- Duplicate signup → 409, wrong password → 401, missing token → 401
- `npm run build` compiles cleanly with no errors

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit JWT_SECRET_KEY for anything beyond local dev
uvicorn app.main:app --reload --port 8000
```

API docs (Swagger UI) will be at `http://localhost:8000/docs`.
The SQLite database file is created automatically on first run.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env            # points VITE_API_BASE_URL at your backend
npm run dev
```

Visit `http://localhost:5173`.

### 3. Try the full flow

1. Go to `/signup`, create an account
2. You'll land in the onboarding wizard — fill in each step
3. On the final Review step, click "Finish & go to dashboard"
4. Reload the page — you should stay logged in and land on `/dashboard`
5. Log out and log back in with the same credentials to confirm persistence

## Environment variables

**Backend** (`.env`)
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLite connection string |
| `JWT_SECRET_KEY` | Signing key for JWTs — change for anything beyond local dev |
| `JWT_ALGORITHM` | Defaults to HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |

**Frontend** (`.env`)
| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Base URL of the backend API |

## Next: Module 2

Dashboard, sidebar, top navigation, profile/settings screens, and the dashboard
aggregation API — building on this same project, no regeneration.
