import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.exceptions import register_exception_handlers
from app.core.rate_limit import limiter
from app.database.session import engine
from app.database.verify import verify_database_schema
from app.middleware.security_headers import SecurityHeadersMiddleware

# Import models so they're registered on Base.metadata. create_all() is no
# longer called here -- schema is managed entirely by Alembic migrations
# (see backend/alembic/ and DATABASE_MIGRATION_GUIDE.md). This import is
# still required so SQLAlchemy relationships resolve and so Alembic's
# autogenerate (env.py) sees every model.
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
    workout_preferences,
    nutrition_preferences,
    plan_import,
)

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
    preferences as preferences_router,
    plan_import as plan_import_router,
)

configure_logging()
logger = logging.getLogger("evofit.startup")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered adaptive fitness and nutrition coaching API.",
    version="3.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
register_exception_handlers(app)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_hosts_list,
)

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
app.include_router(preferences_router.router)
app.include_router(plan_import_router.router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info(
        "EvoFit AI backend starting | environment=%s debug=%s db=%s",
        settings.ENVIRONMENT,
        settings.DEBUG,
        "postgresql" if not settings.DATABASE_URL.startswith("sqlite") else "sqlite",
    )
    # Fail fast and loudly if migrations haven't been applied, instead of
    # letting the app "start successfully" and only discover missing tables
    # when a real request (e.g. login) hits them. See app/database/verify.py.
    verify_database_schema(engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME, "environment": settings.ENVIRONMENT}
