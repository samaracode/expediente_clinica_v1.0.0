from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.consent import ConsentRecord, ConsentType
from app.models.user import User
from app.schemas.consent import ConsentItem, ConsentSign

router = APIRouter()


@router.get("/{admission_id}/consents", response_model=List[ConsentItem])
def list_consents(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    existing = {
        r.consent_type: r
        for r in db.query(ConsentRecord)
        .filter(ConsentRecord.admission_id == admission_id)
        .all()
    }

    return [
        ConsentItem(
            consent_type=ct,
            is_signed=existing[ct].is_signed if ct in existing else False,
            signed_at=existing[ct].signed_at if ct in existing else None,
            verified_by_user_id=existing[ct].verified_by_user_id if ct in existing else None,
            notes=existing[ct].notes if ct in existing else None,
        )
        for ct in ConsentType
    ]


@router.post("/{admission_id}/consents/{consent_type}/sign", response_model=ConsentItem)
def sign_consent(
    admission_id: int,
    consent_type: ConsentType,
    data: ConsentSign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(ConsentRecord)
        .filter(
            ConsentRecord.admission_id == admission_id,
            ConsentRecord.consent_type == consent_type,
        )
        .first()
    )

    now = datetime.now(timezone.utc)

    if record:
        record.is_signed = True
        record.signed_at = now
        record.verified_by_user_id = current_user.id
        record.notes = data.notes
        record.authorized_persons = data.authorized_persons
    else:
        record = ConsentRecord(
            admission_id=admission_id,
            consent_type=consent_type,
            is_signed=True,
            signed_at=now,
            verified_by_user_id=current_user.id,
            notes=data.notes,
            authorized_persons=data.authorized_persons,
        )
        db.add(record)

    db.commit()
    db.refresh(record)

    return ConsentItem(
        consent_type=record.consent_type,
        is_signed=record.is_signed,
        signed_at=record.signed_at,
        verified_by_user_id=record.verified_by_user_id,
        notes=record.notes,
    )
