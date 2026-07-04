from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.progress import ProgressResponse, WeightLogRequest, WeightLogEntry
from app.services import progress_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=ProgressResponse)
def get_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return progress_service.get_progress(db, current_user)


@router.post("/weight", response_model=WeightLogEntry)
def log_weight(
    payload: WeightLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = progress_service.log_weight(db, current_user, payload.log_date, payload.weight_kg)
    return WeightLogEntry.model_validate(entry)
