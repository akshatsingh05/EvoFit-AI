# Deployment Checklist

## Before first deploy

- [ ] `backend/.env` and `frontend/.env` are in `.gitignore` (never commit real secrets)
- [ ] Generated unique `JWT_SECRET_KEY` and `SECRET_KEY` for production (see `ENVIRONMENT_VARIABLES.md`)
- [ ] `DATABASE_URL` points to a real PostgreSQL instance (Neon or Render Postgres), not SQLite
- [ ] `ENVIRONMENT=production` and `DEBUG=false` set on the backend
- [ ] `CORS_ORIGINS` set to the exact deployed frontend origin (no trailing slash)
- [ ] `TRUSTED_HOSTS` set to the real backend domain(s), not `*`
- [ ] `VITE_API_BASE_URL` set to the real backend URL before building the frontend
- [ ] Alembic migrations reviewed and applied (`alembic upgrade head`, or automatic via `startCommand`/Docker `CMD`)
- [ ] `/docs`, `/redoc`, `/openapi.json` confirmed disabled in production (`GET /docs` → 404)

## Auth & security

- [ ] Signup rejects weak passwords (missing letter or digit) — 422
- [ ] Login with wrong password — 401, no user enumeration detail
- [ ] `/auth/refresh` rotates tokens; reusing an old refresh token — 401
- [ ] `/auth/logout` revokes the refresh token; it can't be used afterward
- [ ] Rate limiting engages after `AUTH_RATE_LIMIT` requests/min on `/auth/login` — 429
- [ ] Security headers present on responses (`X-Frame-Options`, `X-Content-Type-Options`, and `Strict-Transport-Security` in production)

## Regression (no existing functionality broken)

- [ ] Signup / Login / Refresh / Logout
- [ ] Onboarding flow (all steps, medical history)
- [ ] Dashboard loads
- [ ] Workout: view + generate/regenerate
- [ ] Nutrition: view + generate/regenerate
- [ ] Adaptive AI insights
- [ ] Daily check-in submission
- [ ] Progress tracking + charts
- [ ] Reports
- [ ] Notifications
- [ ] Workout calendar / history, nutrition history, week navigation
- [ ] Profile editing (all sections)
- [ ] Settings, theme toggle persists across reload and across login sessions
- [ ] Delete account
- [ ] Smart regeneration
- [ ] Unknown route shows the custom 404 page (not a blank screen or the landing page)
- [ ] A thrown render error shows the custom error-boundary page, not a blank screen

## Infrastructure

- [ ] Backend `/health` returns 200 with the correct environment name
- [ ] Frontend loads over HTTPS with no mixed-content warnings
- [ ] Database connection pool settings (`DB_POOL_SIZE`/`DB_MAX_OVERFLOW`) appropriate for the hosting plan's connection limits
- [ ] Docker images build successfully (`docker compose build`) if self-hosting
- [ ] Logs are structured JSON in production (check Render's log stream)

## Post-deploy smoke test

- [ ] Full signup → onboarding → dashboard → logout → login flow on the live URL
- [ ] Confirm no console errors in the browser on each main page
- [ ] Confirm API calls go to the correct backend origin (not `localhost`)
