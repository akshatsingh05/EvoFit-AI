# MODULES.md

# EvoFit AI Development Modules

This document divides the project into four implementation modules. Each module should be completed, tested, and integrated before moving to the next.

---

# MODULE 1 — Authentication & User Setup

## Objective
Build the complete user entry flow.

## Frontend
- Landing Page
- Login
- Signup
- Forgot Password (optional)
- Onboarding
  - Goals
  - Body Metrics
  - Fitness Experience
  - Lifestyle & Diet
  - Medical History
  - Review

## Backend
- JWT Authentication
- User Management
- Onboarding APIs
- Medical History APIs

## APIs
- POST /auth/signup
- POST /auth/login
- GET /auth/me
- POST /onboarding
- GET /onboarding
- POST /medical-history
- GET /medical-history

## Definition of Done
- User can register
- User can log in
- JWT works
- Onboarding saved
- Medical history saved
- Redirect to dashboard

---

# MODULE 2 — Dashboard & Core Experience

## Objective
Create the primary user experience after onboarding.

## Frontend
- Dashboard
- Sidebar
- Top Navigation
- Workout Overview
- Nutrition Overview
- Profile
- Settings

## Backend
- Dashboard aggregation
- Profile APIs
- Initial statistics

## APIs
- GET /dashboard
- GET /profile
- PUT /profile

## Dashboard Widgets
- Today's Workout
- Today's Nutrition
- Recovery Score
- Workout Streak
- Fitness Score
- AI Coach Tip

## Definition of Done
- Dashboard loads real data
- Navigation works
- Profile updates correctly

---

# MODULE 3 — AI Workout & Nutrition

## Objective
Deliver personalized fitness and nutrition plans.

## Frontend
- Workout Page
- Workout Details
- Nutrition Page
- Meal Details
- Exercise Library

## Backend
- Workout Generation Service
- Nutrition Generation Service
- AI Prompt Services
- Plan Storage

## APIs
- POST /generate-workout
- GET /workout
- POST /generate-nutrition
- GET /nutrition

## Features
- Dynamic workout plans
- Personalized meal plans
- Calories
- Macronutrients
- Exercise substitutions
- Meal substitutions

## Definition of Done
- AI generates plans
- Plans persist in database
- Plans displayed correctly

---

# MODULE 4 — Adaptive AI, Progress & Finalization

## Objective
Complete the adaptive coaching system and prepare the MVP.

## Frontend
- Daily Check-In
- Progress
- Charts
- AI Analysis
- History

## Backend
- Daily Check-In Service
- Adaptive AI Service
- Progress APIs
- Recommendation Engine

## APIs
- POST /daily-checkin
- POST /analyze-progress
- GET /progress

## Features
- Recovery analysis
- Updated workout
- Updated nutrition
- Coaching advice
- Weight trend
- Recovery trend
- Workout streak
- Fitness score history

## Final Tasks
- API testing
- Frontend testing
- Integration testing
- Responsive fixes
- Error handling
- Tableau dashboard
- Deployment

## Definition of Done
- Complete end-to-end user flow
- Adaptive recommendations working
- Analytics complete
- MVP ready for demonstration
