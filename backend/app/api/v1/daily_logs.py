from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.follow_up import DailyLog
from app.models.user import User
from app.schemas.daily_logs import DailyLogCreate, DailyLogOut, DailyLogUpdate

router = APIRouter()


def _build_out(log: DailyLog) -> DailyLogOut:
    return DailyLogOut(
        id=log.id,
        admission_id=log.admission_id,
        logged_by_id=log.logged_by_id,
        log_date=str(log.log_date),
        intervention_type=log.intervention_type,
        notes=log.notes,
        recommendations=log.recommendations,
    )


@router.get("/{admission_id}/daily-logs", response_model=List[DailyLogOut])
def list_daily_logs(
    admission_id: int,
    from_date: Optional[str] = Query(None, description="Fecha inicio YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="Fecha fin YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    q = db.query(DailyLog).filter(DailyLog.admission_id == admission_id, DailyLog.is_deleted == False)  # noqa: E712
    if from_date:
        q = q.filter(DailyLog.log_date >= date.fromisoformat(from_date))
    if to_date:
        q = q.filter(DailyLog.log_date <= date.fromisoformat(to_date))
    return [_build_out(log) for log in q.order_by(DailyLog.log_date.desc()).all()]


@router.delete("/{admission_id}/daily-logs/{log_id}", status_code=204)
def delete_daily_log(
    admission_id: int,
    log_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    log = (
        db.query(DailyLog)
        .filter(DailyLog.id == log_id, DailyLog.admission_id == admission_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    log.is_deleted = True
    log.deleted_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/{admission_id}/daily-logs", response_model=DailyLogOut, status_code=201)
def create_daily_log(
    admission_id: int,
    data: DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    log = DailyLog(
        admission_id=admission_id,
        logged_by_id=current_user.id,
        log_date=date.fromisoformat(data.log_date),
        intervention_type=data.intervention_type,
        notes=data.notes,
        recommendations=data.recommendations,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _build_out(log)


@router.put("/{admission_id}/daily-logs/{log_id}", response_model=DailyLogOut)
def update_daily_log(
    admission_id: int,
    log_id: int,
    data: DailyLogUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    log = (
        db.query(DailyLog)
        .filter(DailyLog.id == log_id, DailyLog.admission_id == admission_id)
        .first()
    )
    if not log:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if data.intervention_type is not None:
        log.intervention_type = data.intervention_type
    if data.notes is not None:
        log.notes = data.notes
    if data.recommendations is not None:
        log.recommendations = data.recommendations
    db.commit()
    db.refresh(log)
    return _build_out(log)
