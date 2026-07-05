"""
Dashboard aggregation service.

Module 4 update: Recovery Score and AI Recommendations now come from a real
AdaptiveInsight when one exists (generated from actual check-ins, workout
completions, and weight history — see app/services/adaptive_service.py).
Before any check-in/insight exists, these stay honest empty states rather
than fabricated numbers.
"""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout import WorkoutCompletion
from app.schemas.dashboard import DashboardResponse, WorkoutSummary, NutritionSummary, WeeklyProgressPoint
from app.services import (
    onboarding_service,
    workout_service,
    nutrition_service,
    daily_checkin_service,
    adaptive_service,
    notification_service,
)
from app.services.fitness_score import compute_fitness_score

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _generate_coach_tip(onboarding) -> str:
    """
    Rule-based tip generated from the user's actual profile fields.
    This is deterministic backend logic, not an LLM call — real AI-generated
    coaching tips are a future enhancement once a live model is wired in
    (see app/services/ai/provider.py).
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

    return "Check today's workout and nutrition plan to keep your streak going."


def _today_workout_summary(db: Session, user: User) -> WorkoutSummary:
    plan = workout_service.get_or_create_current_plan(db, user)
    today = date.today()
    today_index = today.weekday()  # 0 = Monday
    day = plan.schedule[today_index]

    if day["is_rest_day"]:
        return WorkoutSummary(status="rest_day", title="Rest day", exercise_count=0)

    completions = workout_service.get_completions_for_plan(db, user, plan)
    status = completions.get(today.isoformat())

    return WorkoutSummary(
        status="completed" if status == "completed" else "scheduled",
        title=day["focus"].replace("_", " ").title(),
        exercise_count=len(day["exercises"]),
    )


def _today_nutrition_summary(db: Session, user: User) -> NutritionSummary:
    plan = nutrition_service.get_or_create_today_plan(db, user)
    completions = nutrition_service.get_completions_for_date(db, user, date.today())
    logged_calories = sum(
        meal["calories"] for meal in plan.meals if completions.get(meal["meal_type"]) == "completed"
    )
    status = "logged" if completions else "on_track"
    return NutritionSummary(status=status, target_calories=plan.target_calories, logged_calories=logged_calories)


def _weekly_progress(db: Session, user: User) -> list[WeeklyProgressPoint]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    completions = (
        db.query(WorkoutCompletion)
        .filter(
            WorkoutCompletion.user_id == user.id,
            WorkoutCompletion.workout_date.between(week_start, week_start + timedelta(days=6)),
        )
        .all()
    )
    completed_dates = {c.workout_date for c in completions if c.status == "completed"}

    checkins = daily_checkin_service.get_recent_checkins(db, user, days=7)
    checkin_dates = {c.checkin_date for c in checkins}

    return [
        WeeklyProgressPoint(
            day_label=DAY_LABELS[i],
            workouts_completed=1 if (week_start + timedelta(days=i)) in completed_dates else 0,
            has_checkin=(week_start + timedelta(days=i)) in checkin_dates,
        )
        for i in range(7)
    ]


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    onboarding = onboarding_service.get_onboarding(db, user)
    fitness_score, fitness_score_basis = compute_fitness_score(onboarding)

    if user.has_completed_onboarding:
        today_workout = _today_workout_summary(db, user)
        today_nutrition = _today_nutrition_summary(db, user)
        workout_streak_days = workout_service.compute_workout_streak(db, user)
        weekly_progress = _weekly_progress(db, user)
    else:
        today_workout = WorkoutSummary(status="not_generated")
        today_nutrition = NutritionSummary(status="not_generated")
        workout_streak_days = 0
        weekly_progress = [
            WeeklyProgressPoint(day_label=label, workouts_completed=0, has_checkin=False) for label in DAY_LABELS
        ]

    # Recovery score + recommendations come from the latest adaptive insight,
    # which itself requires at least one check-in to be meaningful. Before
    # that exists, this stays an honest null/empty list rather than a guess.
    has_checked_in_today = daily_checkin_service.has_checked_in_today(db, user) if user.has_completed_onboarding else False
    latest_insight = adaptive_service.get_latest_insight(db, user) if user.has_completed_onboarding else None
    recovery_score = latest_insight.recovery_score if latest_insight else None
    ai_recommendations = latest_insight.recommendations if latest_insight else []

    ai_coach_tip = _generate_coach_tip(onboarding)
    unread_notifications_count = notification_service.unread_count(db, user)

    quick_actions = ["view_profile", "edit_settings"]
    if user.has_completed_onboarding:
        quick_actions = ["view_workout", "view_nutrition"] + quick_actions
        if not has_checked_in_today:
            quick_actions.insert(0, "daily_checkin")
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
        ai_recommendations=ai_recommendations,
        has_checked_in_today=has_checked_in_today,
        unread_notifications_count=unread_notifications_count,
        quick_actions_available=quick_actions,
    )
