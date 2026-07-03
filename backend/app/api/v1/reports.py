from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import ModuleRequired
from app.db.session import get_db
from app.models.user import Module, User
from app.schemas.reports import AdmissionReportRow, ConsultationReportRow, TreatmentProgressRow
from app.services.report_service import ReportService

router = APIRouter()
_role = ModuleRequired(Module.reports)


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("/admissions", response_model=List[AdmissionReportRow])
def report_admissions(
    service: ReportService = Depends(get_report_service),
    _: User = Depends(_role),
):
    return service.admissions_report()


@router.get("/consultations", response_model=List[ConsultationReportRow])
def report_consultations(
    service: ReportService = Depends(get_report_service),
    _: User = Depends(_role),
):
    return service.consultations_report()


@router.get("/treatment-progress", response_model=List[TreatmentProgressRow])
def report_treatment_progress(
    service: ReportService = Depends(get_report_service),
    _: User = Depends(_role),
):
    return service.treatment_progress_report()
