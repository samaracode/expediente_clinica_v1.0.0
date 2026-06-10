from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.treatment import StageName, StageStatus, TreatmentPlan, TreatmentStage
from app.models.user import User
from app.schemas.treatment import (
    TreatmentPlanOut,
    TreatmentPlanUpsert,
    TreatmentStageOut,
)

router = APIRouter()

STAGE_ORDER = {
    StageName.orientation: 1,
    StageName.adaptation: 2,
    StageName.development: 3,
    StageName.consolidation: 4,
    StageName.reintegration: 5,
}

STAGE_DEFAULTS = list(STAGE_ORDER.keys())


def _build_stage_out(stage: TreatmentStage) -> TreatmentStageOut:
    name = stage.stage_name.value if isinstance(stage.stage_name, StageName) else stage.stage_name
    status = stage.status.value if isinstance(stage.status, StageStatus) else stage.status
    return TreatmentStageOut(
        id=stage.id,
        stage_name=name,
        stage_order=stage.stage_order,
        start_date=str(stage.start_date) if stage.start_date else None,
        end_date=str(stage.end_date) if stage.end_date else None,
        progress_notes=stage.progress_notes,
        extension_consent_signed=stage.extension_consent_signed or False,
        advancement_criteria=stage.advancement_criteria,
        status=status,
    )


def _build_plan_out(plan: TreatmentPlan) -> TreatmentPlanOut:
    db_stages = {s.stage_name: s for s in plan.stages}
    stages = []
    for sn in STAGE_DEFAULTS:
        if sn in db_stages:
            stages.append(_build_stage_out(db_stages[sn]))
        else:
            stages.append(TreatmentStageOut(stage_name=sn.value, stage_order=STAGE_ORDER[sn]))
    return TreatmentPlanOut(
        id=plan.id,
        admission_id=plan.admission_id,
        recommendations=plan.recommendations,
        plan_details=plan.plan_details,
        life_project=plan.life_project,
        created_at=str(plan.created_at) if plan.created_at else None,
        updated_at=str(plan.updated_at) if plan.updated_at else None,
        stages=stages,
    )


def _empty_plan_out(admission_id: int) -> TreatmentPlanOut:
    stages = [
        TreatmentStageOut(stage_name=sn.value, stage_order=STAGE_ORDER[sn])
        for sn in STAGE_DEFAULTS
    ]
    return TreatmentPlanOut(admission_id=admission_id, stages=stages)


@router.get("/{admission_id}/treatment-plan", response_model=TreatmentPlanOut)
def get_treatment_plan(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    plan = db.query(TreatmentPlan).filter(TreatmentPlan.admission_id == admission_id).first()
    if not plan:
        return _empty_plan_out(admission_id)
    return _build_plan_out(plan)


@router.put("/{admission_id}/treatment-plan", response_model=TreatmentPlanOut)
def upsert_treatment_plan(
    admission_id: int,
    data: TreatmentPlanUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    plan = db.query(TreatmentPlan).filter(TreatmentPlan.admission_id == admission_id).first()

    if plan:
        plan.recommendations = data.recommendations
        plan.plan_details = data.plan_details
        plan.life_project = data.life_project
    else:
        plan = TreatmentPlan(
            admission_id=admission_id,
            created_by_id=current_user.id,
            recommendations=data.recommendations,
            plan_details=data.plan_details,
            life_project=data.life_project,
        )
        db.add(plan)
        db.flush()

    for stage_data in data.stages:
        try:
            stage_name = StageName(stage_data.stage_name)
        except ValueError:
            continue

        existing = (
            db.query(TreatmentStage)
            .filter(
                TreatmentStage.treatment_plan_id == plan.id,
                TreatmentStage.stage_name == stage_name,
            )
            .first()
        )

        start = date.fromisoformat(stage_data.start_date) if stage_data.start_date else None
        end = date.fromisoformat(stage_data.end_date) if stage_data.end_date else None
        try:
            status = StageStatus(stage_data.status)
        except ValueError:
            status = StageStatus.pending

        if existing:
            existing.start_date = start
            existing.end_date = end
            existing.progress_notes = stage_data.progress_notes
            existing.extension_consent_signed = stage_data.extension_consent_signed
            existing.advancement_criteria = stage_data.advancement_criteria
            existing.status = status
        else:
            db.add(
                TreatmentStage(
                    treatment_plan_id=plan.id,
                    stage_name=stage_name,
                    stage_order=STAGE_ORDER[stage_name],
                    start_date=start,
                    end_date=end,
                    progress_notes=stage_data.progress_notes,
                    extension_consent_signed=stage_data.extension_consent_signed,
                    advancement_criteria=stage_data.advancement_criteria,
                    status=status,
                )
            )

    db.commit()
    db.refresh(plan)
    return _build_plan_out(plan)
