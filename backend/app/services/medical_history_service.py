from sqlalchemy.orm import Session

from app.models.medical_history import MedicalHistory
from app.models.user import User
from app.schemas.medical_history import MedicalHistoryRequest


def get_medical_history(db: Session, user: User) -> MedicalHistory | None:
    return db.query(MedicalHistory).filter(MedicalHistory.user_id == user.id).first()


def upsert_medical_history(db: Session, user: User, payload: MedicalHistoryRequest) -> MedicalHistory:
    record = get_medical_history(db, user)
    if record is None:
        record = MedicalHistory(user_id=user.id)
        db.add(record)

    record.conditions = payload.conditions
    record.injuries = payload.injuries
    record.medications = payload.medications
    record.allergies = payload.allergies
    record.additional_notes = payload.additional_notes
    record.cleared_for_exercise = payload.cleared_for_exercise

    db.commit()
    db.refresh(record)
    return record
