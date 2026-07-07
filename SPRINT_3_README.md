# Sprint 3 — Production Readiness & Final Polish

Sprint 3 builds on the same Sprint 1 + Sprint 2 codebase (no modules rebuilt,
no architecture redesigned). Summary of each area below.

## 1. Fully functional dark mode
The entire UI was already built on a token system (`bg-primary`,
`text-on-surface-variant`, etc. — no hardcoded hex/gray/slate colors anywhere
in `src/`), so implementing real dark mode was a matter of making those
tokens swap rather than rewriting every page:

- `tailwind.config.js`: `darkMode: 'class'`; every color token now resolves
  through `rgb(var(--color-x) / <alpha>)`, so existing opacity modifiers
  (`bg-primary/10`, etc.) keep working.
- `index.css`: `:root { --color-x: R G B; }` (light) and `.dark { ... }`
  (dark) for all ~40 tokens — a full M3-style dark palette derived from the
  same brand hues (green primary, blue secondary, amber tertiary).
- `context/ThemeContext.jsx` (new): applies/removes the `.dark` class,
  persists to `localStorage` (survives refresh/logout/browser restart), and
  syncs with the existing per-user `settings.theme` backend field so the
  choice follows the user across devices too.
- `index.html`: a tiny inline pre-paint script reads `localStorage` and
  applies `.dark` before React even mounts, so there's no flash of the wrong
  theme on load.
- `pages/Settings.jsx`: the theme picker (previously a placeholder that only
  saved a preference no CSS ever read) now actually flips the theme
  instantly.
- Charts (`ProgressChart.jsx`, `WeeklyProgressChart.jsx`) already used
  `fill-primary` / `stroke-primary` token classes, so they adapt automatically
  — no chart-specific changes needed.
- Every existing page (Landing, Auth, Dashboard, Sidebar, Nav, Workout,
  Nutrition, Progress, Reports, Check-in, Profile, Settings, Calendar,
  History, Notifications, cards/tables/forms/dialogs) inherits this
  automatically since none of them bypassed the token system.

## 2. Better Adaptive AI
`services/ai/adaptive_engine.py` (rewritten, same RuleBasedProvider pattern
so a real Claude/ChatGPT call can replace it later without touching any
caller):
- Added **nutrition adherence** (real `MealCompletion` data) and **workout
  streak** as first-class signals feeding recommendations.
- Extracted `compute_weight_trend()` as a shared, pure function so the coach
  tip and the adaptive analysis agree on the same weight-trend signal instead
  of computing it differently in two places.
- Recommendation phrasing now rotates through 2-3 variants per situation
  (seeded by day-of-year) so repeated regenerations don't read identically.

## 3. AI Coach
New `services/ai/coach_engine.py` + `coach_ai_service.py` (same
provider/prompt pattern as workout/nutrition/adaptive generation).
`adaptive_service.generate_coach_tip()` combines: latest recovery score,
consistency, fatigue flag, nutrition adherence, workout streak, and weight
trend vs. goal — prioritized (acute recovery > streak momentum > adherence >
weight trend > goal default) — into one short, varying sentence.

This **replaces** `dashboard_service._generate_coach_tip()`, which was a
placeholder that only ever looked at static onboarding fields and returned the
exact same sentence every single day regardless of how the user was actually
doing.

## 4. Performance
- **Route-level code splitting**: `App.jsx` now lazy-loads every
  authenticated page (`React.lazy` + `Suspense`). Main bundle dropped from
  ~355 KB to ~265 KB (gzip ~108 KB → ~90 KB); each page is its own small chunk
  fetched on navigation.
- **Backend**: added composite indexes `(user_id, week_start_date)` on both
  `workout_plans` and `nutrition_plans` — the single most frequent query
  pattern in the app (every Workout/Nutrition page load).
- `components/workout/ExerciseCard.jsx` memoized (`React.memo`) — rendered
  many times per page, purely presentational.
- Existing `useMemo` usage in Workout/Nutrition (schedule-with-dates,
  day-dot-status derivation) was already in place from Sprint 2 and is
  unchanged.

## 5. Accessibility
- Fixed `Button.jsx` and `Card.jsx` to actually forward extra props
  (`aria-label`, `role`, etc.) — previously they silently dropped anything
  not explicitly destructured, which is exactly the kind of gap that adding
  `aria-label="Previous week"` etc. would have hit invisibly.
- Icon-only buttons (week/month navigation, calendar cells) now have
  `aria-label`s; decorative icons/dots marked `aria-hidden`.
- `Calendar.jsx` day cells: `aria-label` (full date + status), `aria-current`
  for today, `aria-pressed` for the selected day — all native `<button>`
  elements, so keyboard navigation (Tab/Enter/Space) already works.
- `Input.jsx`: `aria-invalid` + `aria-describedby` wired to the error message
  (`role="alert"`) when a field errors.
- `RegeneratePromptModal.jsx`: `role="dialog"`, `aria-modal`,
  `aria-labelledby`, focuses the heading on open, closes on Escape.
- New Toast system: `role="status"`/`aria-live="polite"` region.

## 6. Responsiveness
Verified against the existing responsive conventions already established in
Sprint 1/2 (`AppLayout`'s `md:flex` sidebar + mobile drawer, `flex-wrap` on
control rows, responsive `grid-cols-2 sm:grid-cols-3` on info cards). All new
Sprint 2/3 surfaces (week navigator, calendar, plan info card, history list,
toasts) follow the same patterns and were checked at mobile/tablet/desktop
widths.

## 7. UI Polish
- New reusable **Toast notification system**
  (`context/ToastContext.jsx`) — wired into Profile save, Settings
  (preferences/password/delete-account), Profile section editing, and
  Workout/Nutrition regenerate, so real actions now get real feedback instead
  of only inline text.
- Smooth theme-switch transition (`transition-colors duration-200` on
  `<body>`) so toggling dark mode doesn't hard-cut.
- Modal focus/entry animation (`toast-in` keyframe) for the new toasts.

## 8. Code cleanup
- Removed `dashboard_service._generate_coach_tip()`, a placeholder function
  fully superseded by `adaptive_service.generate_coach_tip()`.
- Extracted `compute_weight_trend()` instead of leaving duplicated trend math
  in two engines.
- No other dead code found — `get_current_plan_if_exists` /
  `get_today_plan_if_exists` remain as intentional, documented public API
  parity from Sprint 2 (not unused duplicates).

## 9. Final QA
Full regression pass (39 `TestClient`-driven checks spanning every Sprint 1,
2, and 3 endpoint) — all passed. Frontend production build is clean with no
errors, dark mode CSS variables and lazy-loaded chunks verified in the build
output.

## New files
**Backend:** `services/ai/coach_engine.py`, `services/ai/coach_ai_service.py`
**Frontend:** `context/ThemeContext.jsx`, `context/ToastContext.jsx`

## Modified files
**Backend:** `services/ai/adaptive_engine.py`, `services/ai/provider.py`,
`services/ai/prompts.py`, `services/adaptive_service.py`,
`services/dashboard_service.py`, `models/workout.py`, `models/nutrition.py`
(composite indexes)
**Frontend:** `tailwind.config.js`, `index.css`, `index.html`, `main.jsx`,
`App.jsx`, `context/AuthContext.jsx`, `pages/Settings.jsx`, `pages/Profile.jsx`,
`pages/Workout.jsx`, `pages/Nutrition.jsx`, `components/ui/Button.jsx`,
`components/ui/Card.jsx`, `components/ui/Input.jsx`,
`components/shared/RegeneratePromptModal.jsx`, `components/shared/Calendar.jsx`,
`components/workout/WorkoutCalendarView.jsx`, `components/workout/ExerciseCard.jsx`,
`components/shared/WeekNavigator.jsx`
