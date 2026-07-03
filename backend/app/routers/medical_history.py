from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.medical_history import MedicalHistoryRequest, MedicalHistoryResponse
from app.services import medical_history_service

router = APIRouter(prefix="/medical-history", tags=["medical-history"])


@router.get("", response_model=MedicalHistoryResponse)
def get_medical_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = medical_history_service.get_medical_history(db, current_user)
    if record is None:
        raise HTTPException(status_code=404, detail="No medical history recorded yet")
    return MedicalHistoryResponse.model_validate(record)


@router.post("", response_model=MedicalHistoryResponse)
def save_medical_history(
    payload: MedicalHistoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = medical_history_service.upsert_medical_history(db, current_user, payload)
    return MedicalHistoryResponse.model_validate(record)
