from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

# Import models so they're registered on Base.metadata before create_all runs
from app.models import user, onboarding, medical_history  # noqa: F401

from app.routers import auth, onboarding as onboarding_router, medical_history as medical_history_router

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


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
