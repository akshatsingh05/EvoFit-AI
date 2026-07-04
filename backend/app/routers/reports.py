from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.reports import ReportSummary
from app.services import reports_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{period}", response_model=ReportSummary)
def get_report(
    period: Literal["weekly", "monthly"],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reports_service.get_report(db, current_user, period)
