from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.medical import DrugTest, MedicationLog, MedicalRecord
from app.models.user import User
from app.schemas.medical import (
    DrugTestItem,
    MedicationLogItem,
    MedicalRecordOut,
    MedicalRecordUpsert,
)

router = APIRouter()


def _build_out(record: MedicalRecord) -> MedicalRecordOut:
    drug_tests = [
        DrugTestItem(
            id=t.id,
            test_date=str(t.test_date),
            result=t.result,
            notes=t.notes,
        )
        for t in record.drug_tests
    ]
    medication_logs = [
        MedicationLogItem(
            id=m.id,
            treatment_type=m.treatment_type,
            medication_name=m.medication_name,
            dosage=m.dosage,
            frequency=m.frequency,
            prescribed_by=m.prescribed_by,
            start_date=str(m.start_date) if m.start_date else None,
            end_date=str(m.end_date) if m.end_date else None,
            notes=m.notes,
        )
        for m in record.medication_logs
    ]
    return MedicalRecordOut(
        id=record.id,
        admission_id=record.admission_id,
        social_security_validated=record.social_security_validated or False,
        iafa_icd_notes=(record.iafa_icd_data or {}).get("notes"),
        completion_status=record.completion_status or "pending",
        drug_tests=drug_tests,
        medication_logs=medication_logs,
    )


@router.get("/{admission_id}/medical", response_model=MedicalRecordOut)
def get_medical(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = db.query(MedicalRecord).filter(MedicalRecord.admission_id == admission_id).first()
    if not record:
        return MedicalRecordOut(admission_id=admission_id)
    return _build_out(record)


@router.put("/{admission_id}/medical", response_model=MedicalRecordOut)
def upsert_medical(
    admission_id: int,
    data: MedicalRecordUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(MedicalRecord).filter(MedicalRecord.admission_id == admission_id).first()
    )
    iafa_icd_data = {"notes": data.iafa_icd_notes} if data.iafa_icd_notes else None

    if record:
        record.social_security_validated = data.social_security_validated
        record.iafa_icd_data = iafa_icd_data
        record.completion_status = data.completion_status
    else:
        record = MedicalRecord(
            admission_id=admission_id,
            social_security_validated=data.social_security_validated,
            iafa_icd_data=iafa_icd_data,
            completion_status=data.completion_status,
        )
        db.add(record)
        db.flush()

    db.query(DrugTest).filter(DrugTest.medical_record_id == record.id).delete()
    for t in data.drug_tests:
        if not t.test_date:
            continue
        db.add(
            DrugTest(
                medical_record_id=record.id,
                test_date=date.fromisoformat(t.test_date),
                result=t.result,
                notes=t.notes,
            )
        )

    db.query(MedicationLog).filter(MedicationLog.medical_record_id == record.id).delete()
    for m in data.medication_logs:
        if not m.medication_name.strip():
            continue
        db.add(
            MedicationLog(
                medical_record_id=record.id,
                treatment_type=m.treatment_type,
                medication_name=m.medication_name,
                dosage=m.dosage,
                frequency=m.frequency,
                prescribed_by=m.prescribed_by,
                start_date=date.fromisoformat(m.start_date) if m.start_date else None,
                end_date=date.fromisoformat(m.end_date) if m.end_date else None,
                notes=m.notes,
            )
        )

    db.commit()
    db.refresh(record)
    return _build_out(record)
