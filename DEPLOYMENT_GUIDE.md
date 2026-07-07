# Deployment Guide

Target topology: **Vercel** (frontend) + **Render** (backend) + **Neon or
Render Postgres** (database). Docker Compose is provided for local
staging/testing of the same topology, not as the production deploy method.

## 1. Database (Neon)

1. Create a project at [neon.tech](https://neon.tech).
2. Copy the connection string it gives you (starts with `postgresql://`).
   Neon connection strings usually already include `?sslmode=require` —
   keep that; SQLAlchemy/psycopg2 respect it automatically.
3. That's it for now — `alembic upgrade head` (run automatically by the
   backend on deploy, see below) creates the schema.

_Using Render's managed Postgres instead of Neon:_ `render.yaml` already
provisions one (`evofit-ai-db`) and wires `DATABASE_URL` to it
automatically — skip straight to step 2 and ignore the Neon-specific
`DATABASE_URL` value.

## 2. Backend (Render)

1. Push this repo to GitHub/GitLab.
2. In the Render dashboard: **New +** → **Blueprint**, select the repo.
   Render reads `render.yaml` from the repo root and provisions the web
   service (+ database, if you're using Render Postgres instead of Neon).
3. `JWT_SECRET_KEY` and `SECRET_KEY` are generated automatically
   (`generateValue: true`). If you're using Neon instead of Render Postgres,
   manually set `DATABASE_URL` to your Neon connection string in the
   service's Environment tab instead of relying on `fromDatabase`.
4. After the first deploy, note the backend's `*.onrender.com` URL. Go back
   into the service's Environment tab and fill in the `sync: false`
   variables that couldn't be known ahead of time:
   - `TRUSTED_HOSTS` → your `*.onrender.com` hostname (and custom domain, if any)
   - `FRONTEND_URL` / `BACKEND_URL` → your Vercel URL / this Render URL
   - `CORS_ORIGINS` → your Vercel URL (set this *after* step 3 below)
5. Redeploy after changing env vars (Render does this automatically on save).
6. Verify: `curl https://<your-service>.onrender.com/health` → `{"status":"ok",...}`.

The `startCommand` (`alembic upgrade head && gunicorn ...`) means every
deploy automatically brings the database schema up to date before serving
traffic — no manual migration step required post-deploy.

## 3. Frontend (Vercel)

1. Import the repo in Vercel. It reads `vercel.json` from the repo root
   (build command, output directory, and SPA rewrite rule are all
   pre-configured there).
2. In Project Settings → Environment Variables, set `VITE_API_BASE_URL` to
   your Render backend URL from step 2 (e.g. `https://evofit-ai-backend.onrender.com`).
   This is a **build-time** variable — redeploy after setting/changing it.
3. Deploy. Note the resulting Vercel URL.
4. Go back to Render and set `CORS_ORIGINS` (backend) to this Vercel URL,
   then let Render redeploy.

## 4. Verify end-to-end

- Visit the Vercel URL, sign up for an account, complete onboarding, and
  confirm the dashboard loads.
- Check the browser network tab: API calls should hit the Render URL with
  no CORS errors.
- Log out and back in; confirm a stale/invalid refresh token redirects to
  `/login` instead of showing a blank page (open dev tools → Application →
  Local Storage → manually corrupt `evofit_refresh_token` → refresh the
  page → should redirect to login).

## Docker Compose (local staging, not production)

```bash
docker compose up --build
```

Starts Postgres + backend (migrated automatically) + frontend (built and
served via nginx) at `http://localhost:8080`. Useful for testing the
Postgres code path and the production Docker images before deploying, or
as a self-hosting option if you're not using Render/Vercel.

## Rolling back a bad deploy

- **Render**: use the "Rollback" action on a previous successful deploy in
  the dashboard. If the bad deploy included a migration, also run
  `alembic downgrade -1` (via a Render shell) before rolling back the code,
  or the old code may not match the new schema.
- **Vercel**: "Promote to Production" on a previous deployment from the
  Deployments tab — instant, since it's just a static build swap.

See `DEPLOYMENT_CHECKLIST.md` for a step-by-step pre-launch checklist and
`DATABASE_MIGRATION_GUIDE.md` for the migration workflow in detail.
