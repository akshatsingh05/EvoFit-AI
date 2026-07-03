# ARCHITECTURE.md

## Frontend
React, React Router, Tailwind CSS, Axios, React Hook Form

```
src/
  assets/
  components/
  context/
  hooks/
  layouts/
  pages/
  routes/
  services/
  utils/
```

## Backend
FastAPI, SQLAlchemy, SQLite, JWT

```
backend/
  app/
    core/
    database/
    dependencies/
    models/
    routers/
    schemas/
    services/
```

## Rules
- Reusable components
- Thin routers
- Business logic in services
- API layer only through services
- JSON responses
- No hardcoded data

## Routes
Public:
- /
- /login
- /signup

Protected:
- /onboarding
- /dashboard
- /workout
- /nutrition
- /checkin
- /progress
- /profile
