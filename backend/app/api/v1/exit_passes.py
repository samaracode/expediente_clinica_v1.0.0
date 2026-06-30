from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.follow_up import ExitPass, PassStatus, PassType
from app.models.user import User
from app.schemas.exit_passes import ExitPassCreate, ExitPassOut, ExitPassUpdate

router = APIRouter()


def _parse_dt(dt_str: str | None) -> datetime | None:
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _build_out(p: ExitPass) -> ExitPassOut:
    pt = p.pass_type.value if isinstance(p.pass_type, PassType) else p.pass_type
    st = p.status.value if isinstance(p.status, PassStatus) else p.status
    return ExitPassOut(
        id=p.id,
        admission_id=p.admission_id,
        requested_at=p.requested_at.isoformat() if p.requested_at else None,
        approved_by_id=p.approved_by_id,
        departure_date=p.departure_date.isoformat() if p.departure_date else None,
        return_date_expected=p.return_date_expected.isoformat() if p.return_date_expected else None,
        return_date_actual=p.return_date_actual.isoformat() if p.return_date_actual else None,
        reason=p.reason,
        narrative=p.narrative,
        companion=p.companion,
        pass_type=pt,
        status=st,
    )


@router.get("/{admission_id}/exit-passes", response_model=List[ExitPassOut])
def list_exit_passes(
    admission_id: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    q = db.query(ExitPass).filter(ExitPass.admission_id == admission_id)
    if status_filter:
        try:
            q = q.filter(ExitPass.status == PassStatus(status_filter))
        except ValueError:
            pass
    return [_build_out(p) for p in q.order_by(ExitPass.requested_at.desc()).all()]


@router.post("/{admission_id}/exit-passes", response_model=ExitPassOut, status_code=201)
def create_exit_pass(
    admission_id: int,
    data: ExitPassCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    try:
        pass_type = PassType(data.pass_type)
    except ValueError:
        pass_type = PassType.regular

    p = ExitPass(
        admission_id=admission_id,
        departure_date=_parse_dt(data.departure_date),
        return_date_expected=_parse_dt(data.return_date_expected),
        reason=data.reason,
        narrative=data.narrative,
        companion=data.companion,
        pass_type=pass_type,
        status=PassStatus.pending,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _build_out(p)


@router.put("/{admission_id}/exit-passes/{pass_id}", response_model=ExitPassOut)
def update_exit_pass(
    admission_id: int,
    pass_id: int,
    data: ExitPassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = (
        db.query(ExitPass)
        .filter(ExitPass.id == pass_id, ExitPass.admission_id == admission_id)
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    if data.status is not None:
        try:
            new_status = PassStatus(data.status)
        except ValueError:
            raise HTTPException(status_code=422, detail="Estado inválido")
        p.status = new_status
        if new_status == PassStatus.approved:
            p.approved_by_id = current_user.id

    if data.return_date_actual is not None:
        p.return_date_actual = _parse_dt(data.return_date_actual)
    if data.narrative is not None:
        p.narrative = data.narrative
    if data.companion is not None:
        p.companion = data.companion

    db.commit()
    db.refresh(p)
    return _build_out(p)
