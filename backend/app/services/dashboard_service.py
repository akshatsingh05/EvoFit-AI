"""
Dashboard aggregation service.

Design note: Modules 3 (AI workout/nutrition generation) and 4 (daily check-ins,
adaptive AI, progress tracking) haven't been built yet. Rather than fabricate
plausible-looking numbers for widgets that depend on them, this service returns
honest empty/zero states with a `status` field the frontend uses to render an
appropriate empty state. The one derived number here — fitness_score — is a
transparent, deterministic function of the user's actual onboarding answers,
not a random or hardcoded figure, and is clearly labeled as a baseline.
"""
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.dashboard import DashboardResponse, WorkoutSummary, NutritionSummary, WeeklyProgressPoint
from app.services import onboarding_service

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

EXPERIENCE_POINTS = {"beginner": 20, "intermediate": 45, "advanced": 70}
EQUIPMENT_POINTS = {"none": 5, "home_basic": 10, "full_gym": 15}


def _compute_fitness_score(onboarding) -> tuple[int, str]:
    """
    Baseline fitness score (0-100) derived purely from onboarding answers:
    experience level, current weekly training frequency, and equipment access.
    This is a starting point only — Module 4's adaptive engine will recompute
    it from real check-in and workout-completion data.
    """
    fitness_experience = onboarding.fitness_experience
    if not fitness_experience:
        return 0, "Complete onboarding to calculate your baseline score"

    experience_score = EXPERIENCE_POINTS.get(fitness_experience.get("experience_level"), 0)
    frequency_score = min(int(fitness_experience.get("workouts_per_week_current", 0)) * 3, 15)
    equipment_score = EQUIPMENT_POINTS.get(fitness_experience.get("equipment_access"), 0)

    score = min(experience_score + frequency_score + equipment_score, 100)
    return score, "Baseline score from your experience level, current training frequency, and equipment access"


def _generate_coach_tip(onboarding) -> str:
    """
    Rule-based tip generated from the user's actual profile fields.
    This is deterministic backend logic, not an LLM call — real AI-generated
    coaching tips arrive in Module 3 once plan generation is wired up.
    """
    lifestyle = onboarding.lifestyle_diet
    goals = onboarding.goals

    if not goals:
        return "Finish onboarding so your AI coach can start building your first plan."

    if lifestyle and lifestyle.get("sleep_hours_avg", 8) < 6:
        return "Your sleep has been on the lower side — aim for at least 7 hours tonight to support recovery."

    if lifestyle and lifestyle.get("stress_level") == "high":
        return "Stress levels look high. Consider a lighter session today and prioritize a wind-down routine."

    primary_goal = goals.get("primary_goal")
    if primary_goal == "build_muscle":
        return "Consistency beats intensity for muscle growth — focus on hitting every planned session this week."
    if primary_goal == "lose_weight":
        return "Small, sustainable calorie deficits work best — pair your workouts with consistent meal timing."
    if primary_goal == "improve_endurance":
        return "Keep most of your cardio easy and reserve hard efforts for 1-2 sessions a week."

    return "Generate your first workout and nutrition plan to get personalized daily coaching."


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    onboarding = onboarding_service.get_onboarding(db, user)

    fitness_score, fitness_score_basis = _compute_fitness_score(onboarding)

    # No workout/nutrition generation exists yet (Module 3) — honest empty state.
    today_workout = WorkoutSummary(status="not_generated")
    today_nutrition = NutritionSummary(status="not_generated")

    # No daily check-in system exists yet (Module 4) — recovery/streak are real zeros, not fabricated.
    recovery_score = None
    workout_streak_days = 0
    weekly_progress = [
        WeeklyProgressPoint(day_label=label, workouts_completed=0, has_checkin=False) for label in DAY_LABELS
    ]

    ai_coach_tip = _generate_coach_tip(onboarding)

    quick_actions = ["view_profile", "edit_settings"]
    if user.has_completed_onboarding:
        quick_actions.insert(0, "generate_workout_plan")
        quick_actions.insert(1, "generate_nutrition_plan")
    else:
        quick_actions.insert(0, "complete_onboarding")

    return DashboardResponse(
        full_name=user.full_name,
        has_completed_onboarding=user.has_completed_onboarding,
        today_workout=today_workout,
        today_nutrition=today_nutrition,
        recovery_score=recovery_score,
        workout_streak_days=workout_streak_days,
        fitness_score=fitness_score,
        fitness_score_basis=fitness_score_basis,
        weekly_progress=weekly_progress,
        ai_coach_tip=ai_coach_tip,
        quick_actions_available=quick_actions,
    )
