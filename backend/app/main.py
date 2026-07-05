from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

# Import models so they're registered on Base.metadata before create_all runs
from app.models import (
    user,
    onboarding,
    medical_history,
    user_settings,
    workout,
    nutrition,
    progress,
    notification,
    daily_checkin,
    adaptive_insight,
)  # noqa: F401

from app.routers import (
    auth,
    onboarding as onboarding_router,
    medical_history as medical_history_router,
    dashboard,
    profile,
    settings as settings_router,
    workout as workout_router,
    nutrition as nutrition_router,
    progress as progress_router,
    reports,
    notifications,
    checkin,
    adaptive,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(onboarding_router.router)
app.include_router(medical_history_router.router)
app.include_router(dashboard.router)
app.include_router(profile.router)
app.include_router(settings_router.router)
app.include_router(workout_router.router)
app.include_router(nutrition_router.router)
app.include_router(progress_router.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(checkin.router)
app.include_router(adaptive.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
