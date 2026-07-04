# EvoFit AI — Module 3: Workout • Nutrition • Progress

Built directly on the Module 1 + 2 codebase. Nothing in those modules was
regenerated — see the regression check below.

## NEW FILES

**Backend**
- `backend/app/models/workout.py` — `WorkoutPlan`, `WorkoutCompletion`
- `backend/app/models/nutrition.py` — `NutritionPlan`, `MealCompletion`
- `backend/app/models/progress.py` — `WeightLog`
- `backend/app/models/notification.py` — `Notification`
- `backend/app/data/exercise_library.py` — data pool the workout generator selects from
- `backend/app/data/meal_library.py` — data pool the nutrition generator selects from
- `backend/app/services/ai/provider.py` — AI provider abstraction (swap point for Claude/ChatGPT)
- `backend/app/services/ai/prompts.py` — prompt builders for future LLM calls
- `backend/app/services/ai/workout_generator.py` — deterministic plan builder from real profile data
- `backend/app/services/ai/nutrition_generator.py` — BMR/TDEE-based macro + meal calculator
- `backend/app/services/ai/workout_ai_service.py`
- `backend/app/services/ai/nutrition_ai_service.py`
- `backend/app/schemas/workout.py`, `nutrition.py`, `progress.py`, `reports.py`, `notifications.py`
- `backend/app/services/workout_service.py`, `nutrition_service.py`, `progress_service.py`, `reports_service.py`, `notification_service.py`
- `backend/app/routers/workout.py`, `nutrition.py`, `progress.py`, `reports.py`, `notifications.py`

**Frontend**
- `frontend/src/services/workoutService.js`, `nutritionService.js`, `progressService.js`, `reportsService.js`, `notificationService.js`
- `frontend/src/components/workout/ExerciseCard.jsx`, `WeekScheduleTabs.jsx`
- `frontend/src/components/nutrition/MealCard.jsx`
- `frontend/src/components/progress/ProgressChart.jsx`
- `frontend/src/components/layout/NotificationsPanel.jsx`
- `frontend/src/pages/Workout.jsx`, `Nutrition.jsx`, `Progress.jsx`
- `frontend/src/assets/logo.png`, `frontend/public/favicon.png`

## MODIFIED FILES

- `backend/app/main.py` — registered 4 new models + 5 new routers
- `backend/app/services/dashboard_service.py` — Today's Workout/Nutrition, streak, and weekly chart now pull from real Module 3 data instead of Module 2's "not_generated" placeholders
- `backend/app/services/profile_service.py` — fires a `profile_updated` notification on save
- `backend/app/services/workout_service.py` — fires `goal_achieved` at 7/30/100-day streak milestones
- `frontend/src/App.jsx` — added `/workout`, `/nutrition`, `/progress` routes
- `frontend/src/components/layout/Sidebar.jsx` — Workout/Nutrition/Progress now enabled (were "Soon"); uses the new logo + Lucide icons
- `frontend/src/components/layout/TopNav.jsx` — real `NotificationsPanel` replaces the placeholder bell
- `frontend/src/layouts/AuthLayout.jsx` — real logo image (covers Login/Signup/Forgot Password)
- `frontend/src/pages/Landing.jsx` — real logo image; feature cards use Lucide icons instead of colored circles
- `frontend/src/components/dashboard/TodayWorkoutCard.jsx`, `TodayNutritionCard.jsx` — link to the real Workout/Nutrition pages instead of disabled buttons
- `frontend/src/components/dashboard/QuickActions.jsx` — "View workout" / "View nutrition" replace the old disabled "coming soon" actions
- `frontend/index.html` — favicon points at the new logo
- `frontend/package.json` — added `lucide-react`

## The AI service layer (why it's structured this way)

`app/services/ai/provider.py` defines an `AIProvider` interface with one
method, `generate(prompt, context) -> dict`. Today the only implementation is
`RuleBasedProvider`, which ignores the prompt text and calls a deterministic
builder function instead — because there's no model to send the prompt to
yet. `app/services/ai/prompts.py` builds the *actual* prompt text a real
Claude call would use, and it's stored on every generated plan
(`generation_basis.prompt` in the DB) even though nothing consumes it today.

To wire in real Claude generation later:
1. Add a `ClaudeProvider(AIProvider)` that calls the Anthropic API with the prompt and parses the response into the same dict shape `RuleBasedProvider` returns.
2. Change `get_workout_provider()` / `get_nutrition_provider()` in `provider.py` to return it.

No changes needed anywhere else — routers, services, and the dashboard all depend on the interface, not the implementation.

## Honesty notes carried forward from Module 2

- **Recovery Score** and **Recovery Trend** are still `null` — they require
  daily check-ins, which are Module 4. Nothing fabricates them.
- **Fitness Score** is unchanged from Module 2's transparent onboarding-based formula.
- Everything else that was a placeholder in Module 2 — Today's Workout,
  Today's Nutrition, Workout Streak, Weekly Progress — is now backed by real
  generated plans and real completion records.

## New API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/workout` | Current week's plan (generates one if none exists) |
| POST | `/workout/regenerate` | Force a new plan for the current week |
| GET/POST | `/workout/completions` | Per-day completed/skipped status |
| GET | `/nutrition` | Today's plan (generates one if none exists) |
| POST | `/nutrition/regenerate` | Force a new plan for today |
| GET/POST | `/nutrition/completions` | Per-meal completed/skipped status |
| GET | `/progress` | Weight history, workout history, nutrition adherence, streak, fitness score |
| POST | `/progress/weight` | Log a weight entry |
| GET | `/reports/{weekly\|monthly}` | Aggregated summary + AI summary placeholder |
| GET | `/notifications` | List notifications |
| GET | `/notifications/unread-count` | Badge count |
| PUT | `/notifications/{id}/read`, `/notifications/read-all` | Mark read |

## Verified

- Fixed a real bug found during testing: the workout split used a focus tag
  (`upper_body`) that didn't exist in the exercise library, silently
  producing near-empty workout days. Confirmed the fix across two very
  different test profiles (intermediate/full-gym/build-muscle and
  beginner/no-equipment/vegan/yoga-preferring).
- Confirmed injury exclusion works: a user with a logged `left_knee` injury
  never receives squat/lunge/leg-press exercises.
- Confirmed diet-based meal filtering: a vegan profile only receives vegan meals.
- Confirmed nutrition macro math: protein×4 + fat×9 + carbs×4 reconciles with target calories.
- Confirmed dashboard integration: today's workout/nutrition reflect the
  actual generated plan and update correctly after marking completions;
  workout streak and weekly chart reflect real `WorkoutCompletion` rows.
- Confirmed notifications fire on real events (workout completed, streak
  milestone, profile updated) and are retrievable/markable via the API.
- **Regression check**: re-ran Module 1 (`/auth/me`, `/onboarding`,
  `/medical-history`) and Module 2 (`/profile`, `/settings`, `/dashboard`)
  against a live token — all still return 200.
- `npm run build` compiles clean; a full import-resolution scan found zero broken imports.
- Ran backend + frontend together and hit every Module 3 endpoint through
  the same origin the frontend actually calls.

## Running it

Same as before — no new setup steps:

```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## Next: Module 4

Daily check-ins, the adaptive AI engine, and full progress/recovery
tracking — this is what will finally populate Recovery Score and Recovery
Trend with real numbers instead of `null`.
