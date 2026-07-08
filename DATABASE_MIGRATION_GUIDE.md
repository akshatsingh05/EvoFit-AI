# Database Migration Guide

Schema is managed by **Alembic**, not `Base.metadata.create_all()`. This
lets schema changes be versioned, reviewed, and applied identically across
SQLite (dev) and PostgreSQL (production).

## How it's wired

- `backend/alembic.ini` — Alembic config. `sqlalchemy.url` is intentionally
  left blank here; `alembic/env.py` overrides it at runtime from
  `app.core.config.settings.DATABASE_URL`, so migrations always target
  whatever `.env` (or the deployment environment) points at — never a
  stale hardcoded URL.
- `backend/alembic/env.py` — imports `app.models` (registers every model on
  `Base.metadata`) so `--autogenerate` can diff the real model definitions
  against the database.
- `backend/alembic/versions/` — one file per migration, applied in order.
- The baseline migration (`baseline schema`) captures every table that
  existed at the start of this sprint plus the new `refresh_tokens` table.

## Startup schema verification

`app/database/verify.py` runs on every app startup and performs two
checks, in order:

1. The database's `alembic_version` matches the latest local migration
   file. Catches a database that was never migrated at all.
2. Every table the app's SQLAlchemy models expect to exist is actually
   present in the database. Catches a database whose version marker says
   "current" but whose tables don't actually match — most commonly from
   running `alembic stamp head` instead of a real `alembic upgrade head`
   (see the warning below), but also from a restored backup at a
   different revision or a migration that failed partway through.

If either check fails, the app refuses to start and logs exactly what's
wrong and what to run, instead of starting normally and only failing later
with a confusing runtime error the first time a request touches an
affected table.

**Never use `alembic stamp` to "fix" a database that's missing tables.**
`alembic stamp <revision>` marks a database as being at a given revision
*without running any migration DDL* — it's meant for bootstrapping Alembic
onto a database whose schema you've already verified matches that revision
by some other means (e.g. it was restored from a backup taken at exactly
that point), not as a shortcut past a failing or unwanted migration. If a
database is missing tables, run `alembic upgrade head` (or the specific
missing migration) instead so the tables actually get created.

## Day-to-day workflow

1. Change a model in `backend/app/models/`.
2. Generate a migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "add streak_count to daily_checkins"
   ```
3. **Open the generated file in `alembic/versions/` and read it.**
   Autogenerate is a diffing tool, not magic — it can miss things like
   column renames (which it sees as a drop + add, losing data) or
   server-side defaults. Edit the migration by hand if needed.
4. Apply it locally:
   ```bash
   alembic upgrade head
   ```
5. Commit the migration file alongside the model change in the same PR.
6. On deploy, the migration runs automatically before the app boots:
   - Docker: `Dockerfile`'s `CMD` runs `alembic upgrade head` before `gunicorn`.
   - Render: `render.yaml`'s `startCommand` does the same.
   - Any other host: run `alembic upgrade head` manually before starting the app.

## Useful commands

```bash
alembic current            # what revision is the DB currently at
alembic history --verbose  # full migration history
alembic downgrade -1       # roll back one migration
alembic upgrade head       # apply all pending migrations
```

## Switching between SQLite and PostgreSQL

No application code changes are needed — `DATABASE_URL`'s scheme
(`sqlite:///` vs `postgresql://`) is the only thing that changes, and
`app/database/session.py` branches on it purely for connection-pool
settings (SQLite doesn't support connection pooling the way Postgres does).
Alembic migrations run identically against either backend since the models
use SQLAlchemy's dialect-generic column types (`JSON`, `String`, `DateTime`,
etc.) rather than Postgres- or SQLite-specific types.

To test the Postgres path locally: `docker compose up db` (starts just
Postgres), point `DATABASE_URL` at it, then run `alembic upgrade head`.

## Why the old `database/migrations.py` script was removed

Sprint 3 included a one-off script that detected an outdated
`nutrition_plans` schema and dropped/recreated affected tables on startup.
That approach only works for a disposable local SQLite file — it has no
way to safely alter an existing production Postgres table without data
loss, and it wasn't versioned. Alembic replaces it entirely; if a similar
schema fix is ever needed again in production, write it as a proper
Alembic migration (with explicit `op.alter_column` / data-migration steps)
instead.
