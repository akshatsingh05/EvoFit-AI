from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.adaptive import AdaptiveInsightResponse
from app.services import adaptive_service

router = APIRouter(prefix="/adaptive", tags=["adaptive"])


@router.post("/generate", response_model=AdaptiveInsightResponse)
def generate_insight(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insight = adaptive_service.generate_insight(db, current_user)
    return AdaptiveInsightResponse.model_validate(insight)


@router.get("/latest", response_model=AdaptiveInsightResponse)
def get_latest_insight(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insight = adaptive_service.get_or_create_latest_insight(db, current_user)
    return AdaptiveInsightResponse.model_validate(insight)


@router.get("/history", response_model=list[AdaptiveInsightResponse])
def get_insight_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insights = adaptive_service.get_insight_history(db, current_user)
    return [AdaptiveInsightResponse.model_validate(i) for i in insights]
