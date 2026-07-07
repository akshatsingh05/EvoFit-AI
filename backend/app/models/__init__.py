"""
Importing this package registers every model on Base.metadata. Used by
Alembic's env.py (autogenerate needs every model imported) and by main.py at
startup.
"""
from app.models import (  # noqa: F401
    user,
    refresh_token,
    onboarding,
    medical_history,
    user_settings,
    workout,
    nutrition,
    progress,
    notification,
    daily_checkin,
    adaptive_insight,
)
