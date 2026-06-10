from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission, EconomicSituation, HouseholdMember
from app.models.user import User
from app.schemas.economic_situation import EconomicSituationOut, EconomicSituationUpsert

router = APIRouter()


def _build_out(situation: EconomicSituation, members: list) -> EconomicSituationOut:
    return EconomicSituationOut(
        id=situation.id,
        admission_id=situation.admission_id,
        has_worked=situation.has_worked,
        current_job=situation.current_job,
        work_phone=situation.work_phone,
        workplace=situation.workplace,
        job_title=situation.job_title,
        tenure_months=situation.tenure_months,
        monthly_income_colones=float(situation.monthly_income_colones) if situation.monthly_income_colones is not None else None,
        house_type=situation.house_type,
        rent_amount=float(situation.rent_amount) if situation.rent_amount is not None else None,
        family_income_notes=(situation.family_income_data or {}).get("notes"),
        financial_assistance_notes=(situation.financial_assistance_data or {}).get("notes"),
        household_members=[m.full_name for m in members],
    )


@router.get("/{admission_id}/economic-situation", response_model=EconomicSituationOut)
def get_economic_situation(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    situation = (
        db.query(EconomicSituation)
        .filter(EconomicSituation.admission_id == admission_id)
        .first()
    )
    members = (
        db.query(HouseholdMember)
        .filter(HouseholdMember.admission_id == admission_id)
        .all()
    )

    if not situation:
        return EconomicSituationOut(
            admission_id=admission_id,
            household_members=[m.full_name for m in members],
        )

    return _build_out(situation, members)


@router.put("/{admission_id}/economic-situation", response_model=EconomicSituationOut)
def upsert_economic_situation(
    admission_id: int,
    data: EconomicSituationUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    situation = (
        db.query(EconomicSituation)
        .filter(EconomicSituation.admission_id == admission_id)
        .first()
    )

    family_income_data = {"notes": data.family_income_notes} if data.family_income_notes else None
    financial_assistance_data = {"notes": data.financial_assistance_notes} if data.financial_assistance_notes else None

    if situation:
        situation.has_worked = data.has_worked
        situation.current_job = data.current_job
        situation.work_phone = data.work_phone
        situation.workplace = data.workplace
        situation.job_title = data.job_title
        situation.tenure_months = data.tenure_months
        situation.monthly_income_colones = data.monthly_income_colones
        situation.house_type = data.house_type
        situation.rent_amount = data.rent_amount
        situation.family_income_data = family_income_data
        situation.financial_assistance_data = financial_assistance_data
    else:
        situation = EconomicSituation(
            admission_id=admission_id,
            has_worked=data.has_worked,
            current_job=data.current_job,
            work_phone=data.work_phone,
            workplace=data.workplace,
            job_title=data.job_title,
            tenure_months=data.tenure_months,
            monthly_income_colones=data.monthly_income_colones,
            house_type=data.house_type,
            rent_amount=data.rent_amount,
            family_income_data=family_income_data,
            financial_assistance_data=financial_assistance_data,
        )
        db.add(situation)

    # Replace household members
    db.query(HouseholdMember).filter(HouseholdMember.admission_id == admission_id).delete()
    for name in data.household_members:
        name = name.strip()
        if name:
            db.add(HouseholdMember(admission_id=admission_id, full_name=name))

    db.commit()
    db.refresh(situation)
    members = (
        db.query(HouseholdMember)
        .filter(HouseholdMember.admission_id == admission_id)
        .all()
    )
    return _build_out(situation, members)
