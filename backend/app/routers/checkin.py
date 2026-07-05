from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.daily_checkin import DailyCheckInRequest, DailyCheckInResponse
from app.services import daily_checkin_service

router = APIRouter(prefix="/checkin", tags=["checkin"])


@router.post("", response_model=DailyCheckInResponse)
def save_checkin(
    payload: DailyCheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = daily_checkin_service.upsert_checkin(db, current_user, payload)
    return DailyCheckInResponse.model_validate(record)


@router.get("/today", response_model=DailyCheckInResponse)
def get_today_checkin(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from datetime import date

    record = daily_checkin_service.get_checkin_for_date(db, current_user, date.today())
    if record is None:
        raise HTTPException(status_code=404, detail="No check-in recorded for today yet")
    return DailyCheckInResponse.model_validate(record)


@router.get("/history", response_model=list[DailyCheckInResponse])
def get_checkin_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = daily_checkin_service.get_history(db, current_user)
    return [DailyCheckInResponse.model_validate(r) for r in records]
