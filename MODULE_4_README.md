# EvoFit AI — Module 4: Adaptive AI + Daily Check-In + Final Integration

Built directly on the Module 1–3 codebase. Nothing in those modules was
regenerated — see the regression check below.

## FIRST TASK: Toggle switch bug — fixed

**Root cause**: the thumb (`<span>`) was absolutely positioned with `top-1`
but no explicit `left` offset, so its resting position depended on browser
default behavior instead of being pinned — that's what produced the
"thumb pushed to the edge" look.

**Fix**: rebuilt `Toggle.jsx` using the standard accessible switch pattern —
the track is `inline-flex items-center` and the thumb is a normal (not
absolutely positioned) flex child shifted with `translate-x-1` (off) /
`translate-x-6` (on). This is deterministic across browsers because the
thumb's resting position is defined by flexbox, not by an unset offset.
Also added a `disabled` state and a `focus-visible` ring. `Toggle` is only
used in Settings (3 instances), so fixing the component fixed all of them —
no other switch-style control exists elsewhere in the app.

## NEW FILES

**Backend**
- `backend/app/models/daily_checkin.py` — `DailyCheckIn`
- `backend/app/models/adaptive_insight.py` — `AdaptiveInsight` (history table, not overwritten)
- `backend/app/services/fitness_score.py` — shared utility extracted from `dashboard_service` to avoid a circular import once `adaptive_service` existed
- `backend/app/services/ai/adaptive_engine.py` — deterministic recovery/consistency/fatigue analysis from real data
- `backend/app/services/ai/adaptive_ai_service.py` — prompt + provider orchestration (same pattern as Module 3)
- `backend/app/services/daily_checkin_service.py`
- `backend/app/services/adaptive_service.py`
- `backend/app/schemas/daily_checkin.py`, `adaptive.py`
- `backend/app/routers/checkin.py`, `adaptive.py`

**Frontend**
- `frontend/src/services/checkinService.js`, `adaptiveService.js`
- `frontend/src/components/checkin/ScaleSelector.jsx`
- `frontend/src/components/dashboard/AICoachRecommendations.jsx`, `CheckInStatusBanner.jsx`
- `frontend/src/pages/DailyCheckIn.jsx`

## MODIFIED FILES

- `backend/app/services/ai/provider.py` — added `get_adaptive_provider` factory
- `backend/app/services/ai/prompts.py` — added `build_adaptive_prompt`
- `backend/app/services/ai/workout_generator.py` — accepts `intensity_modifier` from the adaptive engine (adjusts sets and training-day count)
- `backend/app/services/ai/nutrition_generator.py` — accepts `adaptive_calorie_adjustment` from the adaptive engine
- `backend/app/services/workout_service.py` — `_build_context` now looks up the latest `AdaptiveInsight` automatically so regenerated plans reflect it with no caller changes needed
- `backend/app/services/nutrition_service.py` — same, for calorie adjustment
- `backend/app/services/profile_service.py` — unchanged from Module 3 (no further changes needed)
- `backend/app/services/progress_service.py` — added recovery history, AI recommendation history, check-in history, workout/nutrition consistency percentages; fixed the circular-import risk by importing `compute_fitness_score` from the new shared module
- `backend/app/services/dashboard_service.py` — recovery score, AI recommendations, check-in status, and unread notification count now come from real Module 4 data
- `backend/app/schemas/dashboard.py` — added `ai_recommendations`, `has_checked_in_today`, `unread_notifications_count`
- `backend/app/schemas/progress.py` — added `recovery_history`, `ai_recommendation_history`, `checkin_history`, `workout_consistency_pct`, `nutrition_consistency_pct`
- `backend/app/main.py` — registered 2 new models + 2 new routers
- `frontend/src/components/ui/Toggle.jsx` — bug fix (see above)
- `frontend/src/components/ui/Button.jsx`, `OptionCard.jsx`, `MultiChipToggle.jsx` — added `focus-visible` rings (Button/OptionCard/MultiChipToggle had none); OptionCard/MultiChipToggle also gained `aria-pressed` so screen readers announce selection state
- `frontend/src/components/dashboard/RecoveryScoreCard.jsx` — links to `/checkin` when empty instead of a static "Module 4" placeholder message
- `frontend/src/components/dashboard/QuickActions.jsx` — added the `daily_checkin` action (primary-styled to draw attention)
- `frontend/src/pages/Dashboard.jsx` — added `CheckInStatusBanner` and `AICoachRecommendations`
- `frontend/src/pages/Progress.jsx` — added recovery history chart, consistency percentages, check-in history, AI recommendation history
- `frontend/src/pages/DailyCheckIn.jsx` — mood grid made responsive (`grid-cols-2 sm:grid-cols-5`) so it doesn't cramp on mobile
- `frontend/src/App.jsx` — added `/checkin` route
- `frontend/src/components/layout/Sidebar.jsx` — added "Daily Check-In" nav item

## How the adaptive engine actually works

`app/services/ai/adaptive_engine.py` computes, from real rows only:
- **Recovery score** (0–100): weighted blend of the last 7 days of check-ins — sleep (30%), energy (25%), soreness (20%), pain (15%), mood (10%)
- **Consistency %**: actual completed vs. scheduled training days
- **Fatigue flag**: true if recovery < 40 or recent average pain ≥ 3
- **Intensity modifier** (-1/0/+1): fed into the workout generator's `sets` and training-day count
- **Nutrition calorie adjustment**: triggered specifically when logged weight trend contradicts the stated goal (e.g., goal is `lose_weight` but weight hasn't gone down)
- **Recommendations**: each one is a plain-English sentence built from the actual numbers above — nothing is templated boilerplate unless every input is neutral

Same swap-point pattern as Module 3: `build_adaptive_prompt()` constructs the
exact prompt a real Claude call would use; `RuleBasedProvider` runs the
deterministic engine instead. Swapping in a real model later means adding a
`ClaudeProvider` and pointing `get_adaptive_provider()` at it — nothing else changes.

## A note on the circular imports

Wiring the adaptive engine into the dashboard and progress pages created two
real circular-import risks (`dashboard_service ↔ progress_service` via a
shared fitness-score function, and `daily_checkin_service ↔ progress_service`
via weight logging). Both were fixed by extracting the shared logic
(`fitness_score.py`) or by having the lower-level service touch the
`WeightLog` model directly instead of calling back up through another
service. I caught these by actually running `python -c "from app.main import
app"` and reading the traceback, not by inspecting the code by eye.

## Verified

- Fresh signup → dashboard shows `recovery_score: null`, empty `ai_recommendations`, per Module 4's own honesty standard
- Submitted a deliberately poor check-in (4.5h sleep, pain 4/5, soreness 5/5, mood "low") → generated insight correctly returned `recovery_score: 33`, `fatigue_flag: true`, `intensity_modifier: -1`, with recommendations that named the actual sleep/pain numbers
- Confirmed the regenerated workout plan's `sets` actually dropped from 4 → 3 (build_muscle base minus the -1 modifier) — verified in the raw API response, not just assumed from code
- Confirmed `/checkin` is idempotent (resubmitting the same date updates rather than duplicates)
- Confirmed validation: an out-of-range check-in (sleep=30, energy=10) correctly returns 422
- **Full regression across Modules 1–4** on a live token: `auth/me`, `onboarding`, `medical-history`, `profile`, `settings`, `dashboard`, `workout`, `nutrition`, `progress`, `reports/weekly`, `reports/monthly`, `notifications`, `checkin/history`, `adaptive/latest`, `adaptive/history` — all 200
- `npm run build` compiles clean; a full import-resolution scan found zero broken imports
- Ran backend + frontend together (backend live, frontend served from its production build) and drove a full signup → onboarding → dashboard flow through the real origin

## Honesty notes

- `checkin_history`/`recovery_history` are genuinely empty for a user who
  hasn't checked in — `adaptive/latest` will auto-generate one neutral
  insight (recovery defaults to 60) rather than 404, since the dashboard
  needs *something* to render, but it's clearly not treated as a real score
  until check-ins exist to back it up.
- The "final polish" pass was scoped to concrete, verifiable fixes (the
  Toggle bug, missing focus-visible states on Button/OptionCard/
  MultiChipToggle, missing `aria-pressed` on selection controls, and two
  mobile grid layouts that would have cramped on narrow screens) rather than
  a blanket claim of an exhaustive accessibility audit.

## Running it

Same as before — no new setup steps:

```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## What's left for a true production launch

- Swap `RuleBasedProvider` for a real Claude-backed provider (the prompts and swap points are ready — see `app/services/ai/provider.py`)
- Password reset emails (currently logged server-side, not sent)
- Rate limiting / abuse protection on the public auth endpoints
- A production Postgres database in place of SQLite
