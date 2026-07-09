from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.plan_import import (
    ManualImportRequest,
    ImportedPlanResponse,
    ImportHistoryResponse,
    PlanAnalysisResponse,
    ApplyDecisionRequest,
    ApplyDecisionResponse,
)
from app.services import file_parsing_service, plan_import_service, plan_export_service

router = APIRouter(prefix="/plan-import", tags=["plan-import"])


def _validate_plan_type(plan_type: str) -> None:
    if plan_type not in ("workout", "nutrition"):
        raise HTTPException(status_code=400, detail="plan_type must be 'workout' or 'nutrition'")


@router.post("/{plan_type}/manual", response_model=ImportedPlanResponse)
def import_manual(
    plan_type: str,
    payload: ManualImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_plan_type(plan_type)
    record = plan_import_service.create_imported_plan(
        db, current_user, plan_type, payload.plan_name, "manual", payload.raw_text
    )
    return ImportedPlanResponse.model_validate(record)


@router.post("/{plan_type}/file", response_model=ImportedPlanResponse)
async def import_file(
    plan_type: str,
    plan_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_plan_type(plan_type)
    data = await file.read()
    raw_text, source_type = file_parsing_service.extract_text(file, data)
    record = plan_import_service.create_imported_plan(db, current_user, plan_type, plan_name, source_type, raw_text)
    return ImportedPlanResponse.model_validate(record)


@router.get("/history", response_model=ImportHistoryResponse)
def get_history(
    plan_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if plan_type is not None:
        _validate_plan_type(plan_type)
    entries = plan_import_service.list_imported_plans(db, current_user, plan_type)
    return ImportHistoryResponse(entries=entries)


@router.get("/{imported_plan_id}", response_model=ImportedPlanResponse)
def get_imported_plan(
    imported_plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    record = plan_import_service.get_imported_plan(db, current_user, imported_plan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Imported plan not found")
    return ImportedPlanResponse.model_validate(record)


@router.delete("/{imported_plan_id}")
def delete_imported_plan(
    imported_plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    deleted = plan_import_service.delete_imported_plan(db, current_user, imported_plan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Imported plan not found")
    return {"deleted": True}


@router.post("/{imported_plan_id}/compare", response_model=PlanAnalysisResponse)
def compare_plan(
    imported_plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    record = plan_import_service.get_imported_plan(db, current_user, imported_plan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Imported plan not found")
    analysis = plan_import_service.run_comparison(db, current_user, record)
    return PlanAnalysisResponse.model_validate(analysis)


@router.get("/{imported_plan_id}/analysis", response_model=PlanAnalysisResponse)
def get_analysis(
    imported_plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    record = plan_import_service.get_imported_plan(db, current_user, imported_plan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Imported plan not found")
    analysis = plan_import_service.get_latest_analysis(db, current_user, imported_plan_id)
    if analysis is None:
        analysis = plan_import_service.run_comparison(db, current_user, record)
    return PlanAnalysisResponse.model_validate(analysis)


@router.post("/{imported_plan_id}/apply", response_model=ApplyDecisionResponse)
def apply_decision(
    imported_plan_id: str,
    payload: ApplyDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = plan_import_service.get_imported_plan(db, current_user, imported_plan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Imported plan not found")
    try:
        result = plan_import_service.apply_decision(db, current_user, record, payload.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ApplyDecisionResponse(**result)


@router.get("/{imported_plan_id}/export")
def export_report(
    imported_plan_id: str,
    format: str = Query(default="pdf", pattern="^(pdf|docx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = plan_import_service.get_imported_plan(db, current_user, imported_plan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Imported plan not found")
    analysis = plan_import_service.get_latest_analysis(db, current_user, imported_plan_id)
    if analysis is None:
        analysis = plan_import_service.run_comparison(db, current_user, record)

    section = {
        "scope": record.plan_type,
        "plan_name": record.plan_name,
        "comparison": analysis.comparison,
        "observations": analysis.observations,
        "suggestions": analysis.suggestions,
    }

    if format == "pdf":
        content = plan_export_service.build_pdf_report([section])
        media_type = "application/pdf"
        filename = f"{record.plan_name.replace(' ', '_')}_report.pdf"
    else:
        content = plan_export_service.build_docx_report([section])
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{record.plan_name.replace(' ', '_')}_report.docx"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/combined")
def export_combined_report(
    format: str = Query(default="pdf", pattern="^(pdf|docx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Feature 8 - combined report across the most recent workout + nutrition import."""
    sections = []
    for plan_type in ("workout", "nutrition"):
        plans = plan_import_service.list_imported_plans(db, current_user, plan_type)
        if not plans:
            continue
        latest = plans[0]
        analysis = plan_import_service.get_latest_analysis(db, current_user, latest.id)
        if analysis is None:
            analysis = plan_import_service.run_comparison(db, current_user, latest)
        sections.append({
            "scope": plan_type,
            "plan_name": latest.plan_name,
            "comparison": analysis.comparison,
            "observations": analysis.observations,
            "suggestions": analysis.suggestions,
        })

    if not sections:
        raise HTTPException(status_code=404, detail="No imported plans to export yet")

    if format == "pdf":
        content = plan_export_service.build_pdf_report(sections)
        media_type = "application/pdf"
        filename = "EvoFit_Combined_Report.pdf"
    else:
        content = plan_export_service.build_docx_report(sections)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "EvoFit_Combined_Report.docx"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
