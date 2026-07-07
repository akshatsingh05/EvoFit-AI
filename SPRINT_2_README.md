# Sprint 2 — EvoFit AI

Sprint 2 extends the existing EvoFit AI codebase (Sprint 1 + Modules 1–4 preserved
and unmodified in behavior) with the following features, built per the agreed
architecture.

## What changed and why

### 1. Nutrition is now weekly (mirrors Workout)
`NutritionPlan` was a daily model; it's now weekly (`week_start_date` + `days`
JSON, one row per week), exactly mirroring `WorkoutPlan`. The Sprint 1 AI
generator (`services/ai/nutrition_generator.py` / `nutrition_ai_service.py`)
was **not modified** — `nutrition_service.py` simply calls it once per day (7
times) with an accumulating "avoid" list for variety, the same trick
`workout_service.py` already used week-to-week.

Because this project has no migration framework (no Alembic, just
`Base.metadata.create_all`), `backend/app/database/migrations.py` adds a
dev-only guard: if it detects the old daily `nutrition_plans` table shape, it
drops just that table (and `meal_completions`) so they're recreated in the new
shape. This only matters if you're running against an old Sprint-1 SQLite
file; a fresh database is unaffected.

### 2. Shared week/registration-date logic
`services/week_utils.py` is the single source of truth for week-boundary math
and the "don't generate before registration" rule, used by both
`workout_service.py` and `nutrition_service.py`.

### 3. Week Navigation (Workout + Nutrition)
`GET /workout/week?offset=N` / `GET /nutrition/week?offset=N` (0 = current,
negative = past, positive = future). Current/future weeks generate on first
visit; weeks before the user registered return `plan: null` with
`is_before_registration: true` instead of fabricating history.

### 4. Workout Calendar
`GET /workout/calendar?start=&end=` returns a per-day status
(completed/skipped/rest/upcoming/missed/no_plan) plus the existing streak
calculation. The frontend's `components/shared/Calendar.jsx` is a **generic**
month-grid component with no workout-specific knowledge — `WorkoutCalendarView.jsx`
is the thin domain wrapper — so Daily Check-in / Recovery can reuse the same
calendar later.

### 5. Unified History
`schemas/history.py` defines a single `HistoryEntry` shape. `GET
/workout/history` and `GET /nutrition/history` both return
`{kind, entries: [...]}` using that shape, and the frontend's
`HistoryList.jsx` renders either one identically. A future Daily Check-in or
Recovery history just needs an adapter function that returns
`list[HistoryEntry]`.

### 6. Plan Information card
`build_plan_info()` in both services computes generated-on / goal / difficulty
/ plan version / last-regenerated from data that already existed (no schema
change) — plan versioning is simply "how many rows exist for this week,"
since regenerating already created a new row rather than mutating history.
`components/shared/PlanInfoCard.jsx` renders it for both pages.

### 7. Complete Profile Editing
No onboarding logic was duplicated. `pages/ProfileEditSection.jsx` reuses the
exact onboarding step components (`GoalsStep`, `BodyMetricsStep`,
`FitnessExperienceStep`, `LifestyleDietStep`, `MedicalHistoryStep`) and the
exact `/onboarding` and `/medical-history` endpoints — only `onNext`/`onBack`
now point back to `/profile` instead of the next wizard step. Only Name/Email
go through the (extended) `/profile` endpoint.

*(One-line, backward-compatible tweak: `GoalsStep.jsx`'s `showBack` condition
was widened so it also shows Back when reused with `stepCount === 1`; the real
6-step onboarding wizard is unaffected.)*

### 8. Smart Regeneration Prompt
`hooks/useSmartRegeneration.js` + `components/shared/RegeneratePromptModal.jsx`.
After saving a profile section, if the before/after values differ, the modal
offers "Regenerate Now" (regenerates both current-week plans) or "Later".

### 9. Delete Account
`profile_service.USER_OWNED_MODELS` is a registry of every model keyed by
`user_id`. `delete_account()` iterates it (plus the ORM cascades already in
place for onboarding/medical history/settings) — and a future "Export My
Data" feature can reuse the same registry to serialize instead of delete.
Settings → Danger Zone requires typing `DELETE` to confirm.

## Verification

A full regression pass (`TestClient`-driven, 39 checks) confirms Sprint 1 and
Module 1–4 endpoints are unaffected and every Sprint 2 endpoint behaves
correctly, including the registration-date edge cases. See conversation
history for the full pass/fail log; every check passed.

## New backend files
`services/week_utils.py`, `database/migrations.py`, `schemas/plan_info.py`, `schemas/history.py`

## New frontend files
`pages/ProfileEditSection.jsx`, `hooks/useSmartRegeneration.js`,
`components/shared/{Calendar,HistoryList,PlanInfoCard,WeekNavigator,RegeneratePromptModal}.jsx`,
`components/workout/WorkoutCalendarView.jsx`, `utils/dateUtils.js`
