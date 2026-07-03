# EvoFit AI — Module 2: Dashboard & Core Experience

Built directly on top of the Module 1 codebase. Nothing in Module 1 was
regenerated — see the verification section below for the regression check.

## NEW FILES

**Backend**
- `backend/app/models/user_settings.py`
- `backend/app/schemas/dashboard.py`
- `backend/app/schemas/profile.py`
- `backend/app/schemas/settings.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/services/profile_service.py`
- `backend/app/services/settings_service.py`
- `backend/app/routers/dashboard.py`
- `backend/app/routers/profile.py`
- `backend/app/routers/settings.py`

**Frontend**
- `frontend/src/services/dashboardService.js`
- `frontend/src/services/profileService.js`
- `frontend/src/services/settingsService.js`
- `frontend/src/components/layout/Sidebar.jsx`
- `frontend/src/components/layout/TopNav.jsx`
- `frontend/src/components/layout/ProfileDropdown.jsx`
- `frontend/src/layouts/AppLayout.jsx`
- `frontend/src/components/dashboard/WelcomeHeader.jsx`
- `frontend/src/components/dashboard/TodayWorkoutCard.jsx`
- `frontend/src/components/dashboard/TodayNutritionCard.jsx`
- `frontend/src/components/dashboard/RecoveryScoreCard.jsx`
- `frontend/src/components/dashboard/WorkoutStreakCard.jsx`
- `frontend/src/components/dashboard/FitnessScoreCard.jsx`
- `frontend/src/components/dashboard/WeeklyProgressChart.jsx`
- `frontend/src/components/dashboard/AICoachTipCard.jsx`
- `frontend/src/components/dashboard/QuickActions.jsx`
- `frontend/src/components/ui/Toggle.jsx`
- `frontend/src/pages/Profile.jsx`
- `frontend/src/pages/Settings.jsx`

## MODIFIED FILES

- `backend/app/models/user.py` — added the `settings` relationship (one new line + import; auth fields untouched)
- `backend/app/main.py` — registered the 3 new routers and the new model import
- `frontend/src/pages/Dashboard.jsx` — replaced the Module 1 placeholder shell with the real widget grid wired to `GET /dashboard`
- `frontend/src/App.jsx` — added `/profile` and `/settings` routes inside the existing `ProtectedRoute` group

Nothing else was touched. Auth, JWT handling, onboarding, medical history, and
the design tokens are byte-for-byte what they were in Module 1.

## An honesty note on dashboard data

Modules 3 (AI workout/nutrition generation) and 4 (daily check-ins, adaptive
AI, progress) don't exist yet. Rather than fabricate numbers for widgets that
depend on them, the dashboard shows real, honest states:

- **Today's Workout / Today's Nutrition** — "not generated yet" until Module 3 ships plan generation
- **Recovery Score** — `null` / "—" until Module 4 ships daily check-ins
- **Workout Streak** — a real `0`, not a placeholder number
- **Weekly Progress chart** — real zeros across all 7 days
- **Fitness Score** — the one number that *is* populated now, but it's a transparent, deterministic formula from actual onboarding answers (experience level + current training frequency + equipment access), explicitly labeled as a baseline the adaptive engine will recalculate in Module 4
- **AI Coach Tip** — rule-based text generated from real profile fields (sleep, stress, goal) — not an LLM call yet; that's Module 3

## New API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/dashboard` | Aggregated dashboard data |
| GET | `/profile` | Full profile: user + onboarding + medical history |
| PUT | `/profile` | Update `full_name` |
| GET | `/settings` | Theme + notification preferences (auto-creates defaults) |
| PUT | `/settings` | Update any subset of preferences |
| PUT | `/settings/password` | Change password (verifies current password) |

## Verified

Ran the full stack together (backend + frontend) and confirmed, in order:
- Fresh signup → dashboard returns honest empty states, fitness score `0`
- Complete onboarding + medical history → dashboard recalculates: fitness
  score computed correctly (72 for an intermediate/4x-week/full-gym profile),
  AI coach tip correctly picks up on low sleep before other rules
- Profile GET/PUT reflect real onboarding + medical data and persist name changes
- Settings GET auto-creates defaults, PUT persists theme + notification toggles
- Password change: wrong current password → 401; correct → 200, and a
  follow-up login with the new password succeeds
- **Regression check**: `/auth/me`, `/onboarding`, `/medical-history` all still
  return 200 with a valid Module 1 token — nothing broke
- `npm run build` compiles clean; a full import-resolution scan across every
  `.jsx`/`.js` file in `src/` found zero broken imports
- CORS from the frontend origin to the backend confirmed working

## Running it

Same as Module 1 — no new setup steps:

```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Next: Module 3

AI workout and nutrition generation — this is what will replace the
"not_generated" empty states with real plans, and give the AI Coach Tip
access to actual generated content.
