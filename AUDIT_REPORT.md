# Production Audit — Bugs Found and Fixed

Performed a full audit in response to a reported `500 Internal Server Error`
on login. Root cause found and fixed, plus four related issues surfaced by
the same investigation.

## 0. (Follow-up) Schema-version check could still be bypassed

**Reported again after the fixes above were delivered:** login still
returned 500 with the same generic frontend message.

**Re-investigation:** Extracted the actual delivered ZIP into a clean
environment (not my working directory) and rebuilt from scratch — fresh
venv, `pip install -r requirements.txt`, `alembic upgrade head`, real
`uvicorn` server, real HTTP requests — on **both SQLite and a real local
PostgreSQL instance**. Could not reproduce with a normally-migrated
database on either backend.

The reported bug only reproduces under one specific condition: a database
where `alembic_version` says the schema is current, but the actual tables
don't match — most commonly caused by running `alembic stamp head`
instead of `alembic upgrade head` (a common shortcut when adopting Alembic
against a database that already has *some* tables from an older,
pre-Alembic version of the app), but also reachable via a restored backup
from a different revision or a migration that failed partway through.
Reproduced exactly: built a Postgres database with every table except
`refresh_tokens`, stamped it as `head` without actually running the
migration, and got the identical error — `relation "refresh_tokens" does
not exist` — despite the previous startup check reporting the schema as
current, because that check only compared the version *string*, not
whether the tables it implies actually exist.

**Root cause:** the original startup schema check (see item #1 in the
original audit below) verified `alembic_version` matched the latest local
migration, but never verified the tables that revision implies were
actually present. A correct version marker on an incomplete/drifted schema
passed the check and let the app start normally, deferring the failure
to the first login exactly as before.

**Fix:** `app/database/verify.py` now performs a second, independent
check after the version-string check passes: it compares every table
`Base.metadata` expects (i.e. every SQLAlchemy model in the app) against
what the inspector reports actually exists in the database, and refuses
to start listing any missing table by name if there's a mismatch. This
catches drift the version marker alone cannot detect, regardless of how it
was introduced (bad stamp, partial migration, manual DDL, restored
backup).

**Verified:**
- The stamped-but-incomplete Postgres database now fails at startup with
  a clear, specific error naming the missing table, instead of starting
  and failing on first login.
- A properly `alembic upgrade head`-migrated database still boots
  normally on both SQLite and PostgreSQL.
- Full signup → login → protected routes → refresh (with rotation) →
  logout flow verified end-to-end against a real local PostgreSQL 16
  instance and against SQLite, both via a real running `uvicorn` server
  hit with real HTTP requests (not just the test client).
- Full application regression sweep (onboarding, dashboard, workout,
  nutrition, progress, reports, notifications, adaptive insights,
  settings, profile, password change with token revocation, delete
  account) re-run against both databases after the fix.

## 1. Login/signup crash: `no such table: refresh_tokens` (originally reported bug)

**Symptom:** Login reaches the backend successfully but returns 500; the
frontend shows only a generic error.

**Root cause:** Both `login` and `signup` call `_issue_tokens()`, which
inserts a row into the `refresh_tokens` table. If the database hasn't had
Alembic migrations applied — a pre-existing/legacy DB file from before this
table existed, or any deploy path that starts the app without first running
`alembic upgrade head` — that table doesn't exist, and the insert throws an
unhandled `OperationalError`. Reproduced directly: built a DB with every
table except `refresh_tokens` (simulating an un-migrated database) and
confirmed login crashes with exactly this error.

**Fix:** Added `app/database/verify.py`, run from `main.py`'s startup
event. It compares the database's `alembic_version` against the latest
local migration and **refuses to start** with a clear, actionable error
(`"Run alembic upgrade head..."`) if they don't match — instead of starting
"successfully" and failing later, confusingly, on the first login attempt.
Verified both directions: a properly-migrated DB boots normally; an
un-migrated one now fails immediately at startup with a clear message
instead of a cryptic runtime 500.

## 2. Orphaned `refresh_tokens` rows on account deletion

**Found while verifying fix #1.** `RefreshToken.user_id` has `ON DELETE
CASCADE` at the database level, but SQLite doesn't enforce foreign keys by
default, and there was no ORM-level cascade either. Deleting an account
left orphaned refresh-token rows behind on SQLite (confirmed: 1 orphaned
row after a delete-account call). This wouldn't happen on PostgreSQL
(which enforces FKs by default), meaning dev and prod behaved differently.

**Fix:**
- Added an explicit `cascade="all, delete-orphan"` relationship from
  `User` to `RefreshToken` in `app/models/user.py`, so cleanup happens at
  the ORM level regardless of database backend.
- Enabled `PRAGMA foreign_keys=ON` for SQLite connections in
  `app/database/session.py`, so local development enforces the same FK
  behavior as production instead of silently ignoring it.

Verified: 0 orphaned rows after account deletion, on both a fresh
signup/delete cycle and one with an extra outstanding refresh token.

## 3. Stolen refresh tokens survived a password change

**Found during the audit, not previously reported.** `change_password()`
updated the password hash but never touched existing refresh tokens. If an
attacker had captured a refresh token, changing your password would **not**
stop them — they could keep minting new access tokens indefinitely.

**Fix:** `change_password()` now revokes every outstanding, non-revoked
refresh token for that user in the same transaction as the password
update. Verified: after a password change, the previously-issued refresh
token returns 401 on `/auth/refresh`, while login with the new password
still works normally.

## 4. Password-complexity rule wasn't applied to password changes

**Found during the audit.** The signup form's password field required a
letter and a number (added as part of the earlier deployment-readiness
work), but `ChangePasswordRequest.new_password` only checked length — so
weaker passwords were allowed for password changes than for signup.

**Fix:** Extracted the rule into a single shared
`validate_password_complexity()` in `app/core/security.py`, used by both
`SignupRequest` and `ChangePasswordRequest`, so the two can no longer drift
apart the way they just had.

## 5. Frontend crash risk on validation errors (Signup, Login, Settings, Profile, Progress, Daily Check-In)

**Found while verifying fix #4.** FastAPI returns `detail` as a plain
string for most errors, but as a **list** of validation-error objects for
422s. Six pages read `err.response?.data?.detail` and rendered it directly
as a React child (e.g. `<p>{passwordError}</p>`). A string renders fine; an
array of objects makes React throw `"Objects are not valid as a React
child"` and crash the page. Fix #4 made this materially more likely to
happen in practice (an 8-character all-letter password now fails
server-side even where old client-side checks didn't catch it).

**Fix:**
- Added `frontend/src/utils/errorMessage.js` — a `getErrorMessage(err,
  fallback)` helper that normalizes both shapes (string or validation-error
  array) into a plain, safe-to-render string.
- Replaced every direct `err.response?.data?.detail` usage with this
  helper in `Login.jsx`, `Signup.jsx`, `Settings.jsx`, `Profile.jsx`,
  `Progress.jsx`, and `DailyCheckIn.jsx`.
- Added matching client-side password-complexity validation to the Signup
  and change-password forms, so most users never trigger the 422 at all.

Verified the helper against all three real error shapes the backend
actually returns (validation array, plain-string detail, and a raw network
error with no `response`) — all three now resolve to plain strings.

## 6. Hardening: `SecurityHeadersMiddleware` rewritten as pure ASGI middleware

While investigating fix #1, the same request's server log showed the
exception logged twice (once via the app's own exception handler, once via
uvicorn's top-level ASGI error logging). Further testing showed this
duplicate logging is actually standard Starlette/uvicorn instrumentation
present regardless of middleware choice — not a bug caused by
`SecurityHeadersMiddleware`. It was still rewritten from
`BaseHTTPMiddleware` to a plain ASGI middleware, since `BaseHTTPMiddleware`
has known edge cases under real (non-localhost) network conditions around
streaming responses and task-group exception propagation; the rewrite
removes that class of risk even though it wasn't the cause of the reported
bug. Behavior (headers added to every response) is unchanged and verified
identical.

## 7. CRITICAL: `passlib` + modern `bcrypt` incompatibility crashes login/signup with 500

**Symptom (reported):** Login reaches the backend successfully but returns
500; frontend shows only the generic fallback message.

**Root cause:** `passlib` 1.7.4 (last released 2020) detects its bcrypt
backend by reading `bcrypt.__about__.__version__`. That submodule was
removed in `bcrypt` 4.1+. Pinning `bcrypt==4.0.1` in `requirements.txt`
worked around this in a clean install, but the pin isn't bulletproof — any
environment where bcrypt ends up newer (a pre-existing/global install, a
transitive dependency's constraint, a later `pip install --upgrade`) hits
`AttributeError: module 'bcrypt' has no attribute '__about__'`, which
passlib "traps" and then fails a different way inside its own internal
self-test (`ValueError: password cannot be longer than 72 bytes`) —
crashing `hash_password`/`verify_password`, and therefore signup and login,
with an unhandled 500.

**Reproduced exactly as reported:** installed `bcrypt` 5.0.0 over a clean
`pip install -r requirements.txt`, pre-created a user with a correctly
hashed password, then attempted login — confirmed 500 with the traceback
above, isolated to `verify_password` inside `auth_service.login`.

**Fix:** Removed `passlib` entirely and call `bcrypt` directly in
`app/core/security.py` (`bcrypt.hashpw` / `bcrypt.checkpw`), which has no
version-detection shim to break and works correctly with any current
`bcrypt` release. Also handled bcrypt's 72-*byte* input limit explicitly
(truncating on a UTF-8 character boundary) since the raw `bcrypt` library
raises rather than silently truncating like passlib used to. Updated
`requirements.txt` to drop `passlib[bcrypt]` and bump `bcrypt` to `5.0.0`.

**Verified:**
- Fresh install of the corrected `requirements.txt` (bcrypt 5.0.0, no
  passlib) — signup and login both succeed with no errors.
- The exact failing scenario (existing user, login) now returns 200.
- Edge cases: passwords >72 bytes, multi-byte Unicode passwords, and a
  malformed/foreign hash value all handled without crashing.
- Full regression suite (auth lifecycle + every module + protected-route
  rejection + password change + delete account) passes end-to-end.
- `alembic check` confirms zero drift between models and the migration
  history (no missing or inconsistent tables).



Re-ran the full auth lifecycle plus every module endpoint after each fix
and once more at the end with all fixes applied together: signup, login,
refresh (including rotation), logout, password change (including token
revocation and the new complexity rule), onboarding, dashboard, workout
(get/regenerate/week/history), nutrition (get/regenerate/week/history),
progress, reports, notifications, daily check-in, adaptive insights,
settings, profile, and delete-account. All passed. Frontend rebuilds
cleanly (`npm run build`) with no errors.

## Files changed in this audit

**New:**
- `backend/app/database/verify.py`
- `frontend/src/utils/errorMessage.js`

**Modified:**
- `backend/app/main.py` (startup schema verification)
- `backend/app/database/session.py` (SQLite FK enforcement)
- `backend/app/models/user.py` (refresh_tokens cascade relationship)
- `backend/app/core/security.py` (shared password complexity validator; password hashing rewritten to use `bcrypt` directly instead of `passlib`)
- `backend/app/schemas/auth.py`, `backend/app/schemas/settings.py` (use shared validator)
- `backend/app/services/settings_service.py` (revoke tokens on password change)
- `backend/app/middleware/security_headers.py` (pure ASGI middleware)
- `backend/requirements.txt` (removed `passlib[bcrypt]`, bumped `bcrypt` to `5.0.0`)
- `frontend/src/pages/Login.jsx`, `Signup.jsx`, `Settings.jsx`, `Profile.jsx`, `Progress.jsx`, `DailyCheckIn.jsx` (safe error rendering; Signup/Settings also get matching client-side password validation)
