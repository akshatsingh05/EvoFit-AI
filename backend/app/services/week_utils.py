"""
Shared week-boundary helpers used by both workout_service and nutrition_service
so week navigation, registration-date guarding, and offset math live in exactly
one place (Sprint 2: "Nutrition should follow the same architecture as Workout").
"""
from datetime import date, timedelta

from app.models.user import User


def week_start(for_date: date) -> date:
    return for_date - timedelta(days=for_date.weekday())


def week_start_for_offset(offset: int) -> date:
    """offset=0 is the current week, negative is past, positive is future."""
    return week_start(date.today()) + timedelta(weeks=offset)


def get_registration_week_start(user: User) -> date:
    """The Monday of the week the user signed up — the earliest week we'll ever generate for."""
    return week_start(user.created_at.date())


def is_week_before_registration(week_start_date: date, user: User) -> bool:
    return week_start_date < get_registration_week_start(user)
