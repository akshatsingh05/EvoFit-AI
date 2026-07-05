# EvoFit AI — Sprint 1: AI Personalization & Plan Generation

Backend-only sprint, as instructed — no UI redesign, no new frontend files.
The existing Workout/Nutrition pages and their "Regenerate" buttons already
called the right endpoints (built in Module 3); the bug was entirely in what
those endpoints computed.

## NEW FILES

None. Every requirement in this sprint was addressable by fixing existing
generation logic and expanding existing data files — no new tables, models,
services, or frontend components were needed.

## MODIFIED FILES

- `backend/app/data/exercise_library.py` — expanded from 30 to 62 exercises; added `level`, `impact_level`, `order_priority`, and `contraindications` fields; fixed a real gap where "none equipment" had zero push-focused exercises
- `backend/app/data/meal_library.py` — expanded from 27 to 38 meals; added `low_glycemic` tag for diabetes-aware soft filtering
- `backend/app/services/ai/workout_generator.py` — rewritten (see below)
- `backend/app/services/ai/nutrition_generator.py` — rewritten (see below)
- `backend/app/services/workout_service.py` — context now includes `body_metrics`, `cleared_for_exercise`, a variation seed, and the previous plan's exercise names
- `backend/app/services/nutrition_service.py` — same, for nutrition (variation seed, previous plan's meal names, `conditions`)

## FEATURE 1 — Personalized workout generation

**What was actually wrong**: exercise selection was `pool[:5]` — the first five
matches in a fixed-order list. Every user with the same equipment/injury
profile got byte-for-byte the same exercises, in the same order, forever.

**Fix**:
- **BMI** is calculated from real height/weight and used as a soft preference for lower-impact exercises (BMI ≥ 30, or doctor-not-cleared, both trigger this)
- **Medical conditions** (not just injuries) now exclude contraindicated exercises — e.g. `heart_condition` excludes Burpees, Jump Squats, high-intensity cardio
- **Doctor restrictions**: `cleared_for_exercise = false` caps the plan to ≤3 days, ≤2 sets, ≤3 exercises/day, low-impact only
- **Per-user variety**: selection is seeded from `user_id + week`, so two users with identical onboarding answers get different plans (verified below) — proven, not assumed
- **Exercise ordering**: compound movements are sorted before isolation/accessory work

## FEATURE 2 — Workout days matching onboarding exactly

**Root cause found**: `training_day_count = round((base_days_by_experience +
max(current_freq, base_days)) / 2)` — this *averaged* the user's selected
frequency with an experience-based default. A beginner who selected 5
days/week got `round((3+5)/2) = 4`, not 5. On top of that, adaptive fatigue
was silently removing an entire day rather than just reducing volume.

**Fix**: training day count is now `fitness_experience.workouts_per_week_current`,
directly, clamped to a valid 1–7 range (expanded from the old 2–6-only layout
table). Adaptive fatigue now only reduces `sets`, never the day count.
Verified for 3/4/5/6 below — all exact.

## FEATURE 3 — Personalized nutrition generation

BMR/TDEE calculation was already real (Module 3). What was hardcoded was meal
selection: `chosen = pool[0]` — always the first match. Fixed the same way as
workouts: seeded selection per user/regeneration, with a soft preference for
lower-glycemic meals when the user has a logged diabetes-related condition,
which also nudges the fat/protein-vs-carb macro split.

## FEATURE 4 & 5 — Regeneration actually regenerates

Root cause: regeneration called the exact same deterministic function with
the exact same inputs, so of course it produced the same plan — that's not a
bug in the "regenerate" wiring (Module 3 already called the right endpoint),
it's that the generator itself had no source of variation to draw on.

Fix: every regenerate call now includes a fresh random nonce in its
variation seed, and explicitly avoids repeating whatever's in the plan being
replaced when the exercise/meal pool has alternatives. Verified below that
two regenerate calls in a row produce two different plans, not just one
different pair.

## What was reused unchanged

- The AI service layer's structure (`provider.py`, prompt builders) — untouched, still the same swap-point pattern for a future Claude/ChatGPT integration
- `WorkoutPlan`/`NutritionPlan`/`WorkoutCompletion`/`MealCompletion` models — no schema changes
- All routers, all other services, the entire frontend
- The adaptive engine (Module 4) — its `intensity_modifier` and
  `nutrition_calorie_adjustment` outputs are consumed exactly as before, just
  no longer able to silently violate Feature 2's day-count guarantee

## Verified

- **Feature 2**: created 4 users requesting 3/4/5/6 workout days respectively — each got exactly that many training days, confirmed by counting non-rest, non-yoga days in the raw schedule
- **Feature 1 & personalization**: two users with byte-for-byte identical onboarding answers received different exercise selections and different meal selections — confirmed by diffing the actual exercise/meal name lists, not just trusting the code path
- **Medical safety**: a user with `cleared_for_exercise: false` and `heart_condition` got capped to 3 days / 2 sets / 3 exercises per day, with zero high-intensity or contraindicated exercises (Burpee, Jump Squat) anywhere in the plan
- **Feature 4**: original plan → regenerate → regenerate again — all three exercise lists differ from each other (not just the first two), while day count stayed correct after regeneration
- **Feature 5**: nutrition regenerate produced a different meal list while calorie targets stayed consistent (target isn't randomized, only meal choice)
- **Full regression across Modules 1–4** on a live token: all 14 endpoints returned 200, plus workout completion, workout regenerate, and nutrition regenerate all still functional, unauthorized requests still 401
- `npm run build` still compiles clean (frontend untouched, verified anyway since it consumes these same endpoints)

## Honesty note

"Doctor Restrictions" and "Previous Workout Completion" were both interpreted
concretely: doctor restrictions = the existing `cleared_for_exercise` flag
from Module 1's medical history (there wasn't a separate field for this, and
adding one would have meant a schema change the brief said to avoid unless
"absolutely necessary" — reusing the existing flag was sufficient). Previous
workout completion currently informs variety (avoiding repeat exercises
across regenerations) rather than adjusting volume based on completion rate
directly — that signal already flows into the plan via Module 4's adaptive
`intensity_modifier`, which is itself derived partly from completion
consistency, so it wasn't duplicated here.

## Running it

No new setup steps:

```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```
