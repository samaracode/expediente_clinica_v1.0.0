"""
Capa de lógica de negocio para el módulo de Entrega de turno (Shift Handover).

Ventanas de turno (UTC) para acotar los eventos del auto-resumen:
  morning:   06:00–14:00
  afternoon: 14:00–22:00
  night:     22:00–06:00 (día siguiente)
"""

from datetime import date, datetime, time, timezone, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.admission import Admission, AdmissionStatus
from app.models.attendance import AttendanceRollCall, AttendanceEntry, PresenceStatus, Shift
from app.models.follow_up import ExitPass
from app.models.handover import HandoverStatus, ShiftHandover, ShiftIncident, ShiftTask
from app.models.medication import MedicationAdministration, AdministrationStatus
from app.schemas.handover import (
    ShiftHandoverOut,
    ShiftIncidentCreate,
    ShiftIncidentOut,
    ShiftTaskCreate,
    ShiftTaskOut,
    ShiftTaskPatch,
)


# ---------------------------------------------------------------------------
# Ventanas de turno
# ---------------------------------------------------------------------------

def _shift_window(target_date: date, shift: Shift):
    """Devuelve (start_dt, end_dt) aware-UTC para filtrar eventos del turno."""
    if shift == Shift.morning:
        start = datetime.combine(target_date, time(6, 0), tzinfo=timezone.utc)
        end = datetime.combine(target_date, time(14, 0), tzinfo=timezone.utc)
    elif shift == Shift.afternoon:
        start = datetime.combine(target_date, time(14, 0), tzinfo=timezone.utc)
        end = datetime.combine(target_date, time(22, 0), tzinfo=timezone.utc)
    else:  # night: 22:00 → 06:00 del día siguiente
        start = datetime.combine(target_date, time(22, 0), tzinfo=timezone.utc)
        end = datetime.combine(target_date + timedelta(days=1), time(6, 0), tzinfo=timezone.utc)
    return start, end


class HandoverService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # compute_auto_summary
    # ------------------------------------------------------------------

    def compute_auto_summary(self, target_date: date, shift: Shift) -> Dict[str, Any]:
        """
        Calcula el resumen automático del turno con:
        - medications: tomas omitidas/rechazadas en la ventana
        - attendance: ausencias AWOL y discrepancias del roll-call
        - exit_passes: permisos con departure_date o return_date_actual en la ventana
        - admissions: ingresos del día (admission_date == target_date)
        - note sobre egresos (sin timestamp confiable)
        """
        start_dt, end_dt = _shift_window(target_date, shift)

        # --- medications: omitted / refused en la ventana ---
        med_admins = (
            self.db.query(MedicationAdministration)
            .filter(
                MedicationAdministration.status.in_([
                    AdministrationStatus.omitted,
                    AdministrationStatus.refused,
                ]),
                MedicationAdministration.scheduled_at >= start_dt,
                MedicationAdministration.scheduled_at < end_dt,
            )
            .all()
        )
        medications_summary = [
            {
                "administration_id": ma.id,
                "order_id": ma.order_id,
                "admission_id": ma.admission_id,
                "status": ma.status.value,
                "scheduled_at": ma.scheduled_at.isoformat() if ma.scheduled_at else None,
                "reason": ma.reason,
            }
            for ma in med_admins
        ]

        # --- attendance: AWOL y discrepancias del roll-call (date, shift) ---
        roll_call = (
            self.db.query(AttendanceRollCall)
            .filter(
                AttendanceRollCall.date == target_date,
                AttendanceRollCall.shift == shift,
            )
            .first()
        )
        attendance_summary = []
        if roll_call:
            entries = (
                self.db.query(AttendanceEntry)
                .filter(AttendanceEntry.roll_call_id == roll_call.id)
                .all()
            )
            for entry in entries:
                if (
                    entry.actual_status == PresenceStatus.absent_without_leave
                    or entry.expected_status != entry.actual_status
                ):
                    attendance_summary.append({
                        "entry_id": entry.id,
                        "admission_id": entry.admission_id,
                        "expected_status": entry.expected_status.value,
                        "actual_status": entry.actual_status.value,
                        "note": entry.note,
                    })

        # --- exit_passes: departure o retorno en el día ---
        passes = (
            self.db.query(ExitPass)
            .filter(ExitPass.departure_date.isnot(None))
            .all()
        )
        exit_passes_summary = []
        for ep in passes:
            in_window = False
            reason_keys = []

            if ep.departure_date is not None:
                dep_date = ep.departure_date.date() if isinstance(ep.departure_date, datetime) else ep.departure_date
                if dep_date == target_date:
                    in_window = True
                    reason_keys.append("departure")

            if ep.return_date_actual is not None:
                ret_date = ep.return_date_actual.date() if isinstance(ep.return_date_actual, datetime) else ep.return_date_actual
                if ret_date == target_date:
                    in_window = True
                    reason_keys.append("return")

            if in_window:
                exit_passes_summary.append({
                    "exit_pass_id": ep.id,
                    "admission_id": ep.admission_id,
                    "status": ep.status.value,
                    "departure_date": ep.departure_date.isoformat() if ep.departure_date else None,
                    "return_date_actual": ep.return_date_actual.isoformat() if ep.return_date_actual else None,
                    "events": reason_keys,
                })

        # --- admissions: ingresos del día ---
        new_admissions = (
            self.db.query(Admission)
            .filter(Admission.admission_date == target_date)
            .all()
        )
        admissions_summary = [
            {
                "admission_id": a.id,
                "resident_id": a.resident_id,
                "admission_number": a.admission_number,
                "status": a.status.value,
            }
            for a in new_admissions
        ]

        return {
            "medications": medications_summary,
            "attendance": attendance_summary,
            "exit_passes": exit_passes_summary,
            "admissions": admissions_summary,
            "note": "egresos omitidos: sin timestamp confiable",
        }

    # ------------------------------------------------------------------
    # Handover: get_or_create, close, receive
    # ------------------------------------------------------------------

    def _get_or_create(self, target_date: date, shift: Shift) -> ShiftHandover:
        existing = (
            self.db.query(ShiftHandover)
            .filter(ShiftHandover.date == target_date, ShiftHandover.shift == shift)
            .first()
        )
        if existing:
            return existing
        handover = ShiftHandover(date=target_date, shift=shift, status=HandoverStatus.open)
        self.db.add(handover)
        self.db.commit()
        self.db.refresh(handover)
        return handover

    def get_handover_by_id(self, handover_id: int) -> ShiftHandover:
        handover = self.db.query(ShiftHandover).filter(ShiftHandover.id == handover_id).first()
        if not handover:
            raise HTTPException(status_code=404, detail="Entrega de turno no encontrada")
        return handover

    def get_handover(self, target_date: date, shift: Shift) -> ShiftHandoverOut:
        handover = self._get_or_create(target_date, shift)
        out = ShiftHandoverOut.model_validate(handover)
        # Abierto → resumen en vivo (sin persistir); cerrado → snapshot congelado.
        if handover.status == HandoverStatus.open:
            out.auto_summary = self.compute_auto_summary(target_date, shift)
        return out

    def get_auto_summary(self, handover_id: int) -> Dict[str, Any]:
        handover = self.get_handover_by_id(handover_id)
        return self.compute_auto_summary(handover.date, handover.shift)

    def close(self, handover_id: int, current_user_id: Optional[int], notes: Optional[str]) -> ShiftHandoverOut:
        handover = self.get_handover_by_id(handover_id)
        if handover.status == HandoverStatus.closed:
            raise HTTPException(status_code=400, detail="La entrega ya está cerrada")
        if handover.status == HandoverStatus.received:
            raise HTTPException(status_code=400, detail="La entrega ya fue recibida")
        handover.auto_summary = self.compute_auto_summary(handover.date, handover.shift)
        if notes is not None:
            handover.notes = notes
        handover.closed_by_user_id = current_user_id
        handover.closed_at = datetime.now(timezone.utc)
        handover.status = HandoverStatus.closed
        self.db.commit()
        self.db.refresh(handover)
        return ShiftHandoverOut.model_validate(handover)

    def receive(self, handover_id: int, current_user_id: Optional[int]) -> ShiftHandoverOut:
        handover = self.get_handover_by_id(handover_id)
        if handover.status != HandoverStatus.closed:
            raise HTTPException(
                status_code=400,
                detail="La entrega debe estar cerrada antes de poder ser recibida",
            )
        handover.received_by_user_id = current_user_id
        handover.received_at = datetime.now(timezone.utc)
        handover.status = HandoverStatus.received
        self.db.commit()
        self.db.refresh(handover)
        return ShiftHandoverOut.model_validate(handover)

    # ------------------------------------------------------------------
    # Incidentes
    # ------------------------------------------------------------------

    def list_incidents(self, handover_id: int) -> List[ShiftIncidentOut]:
        self.get_handover_by_id(handover_id)
        incidents = (
            self.db.query(ShiftIncident)
            .filter(ShiftIncident.handover_id == handover_id)
            .order_by(ShiftIncident.created_at.asc())
            .all()
        )
        return [ShiftIncidentOut.model_validate(i) for i in incidents]

    def create_incident(
        self, handover_id: int, data: ShiftIncidentCreate, current_user_id: Optional[int]
    ) -> ShiftIncidentOut:
        self.get_handover_by_id(handover_id)
        incident = ShiftIncident(
            handover_id=handover_id,
            admission_id=data.admission_id,
            type=data.type,
            severity=data.severity,
            description=data.description,
            action_taken=data.action_taken,
            reported_by_user_id=data.reported_by_user_id or current_user_id,
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return ShiftIncidentOut.model_validate(incident)

    # ------------------------------------------------------------------
    # Tareas / pendientes
    # ------------------------------------------------------------------

    def list_tasks(self, handover_id: int) -> List[ShiftTaskOut]:
        self.get_handover_by_id(handover_id)
        tasks = (
            self.db.query(ShiftTask)
            .filter(ShiftTask.handover_id == handover_id)
            .order_by(ShiftTask.created_at.asc())
            .all()
        )
        return [ShiftTaskOut.model_validate(t) for t in tasks]

    def create_task(
        self, handover_id: int, data: ShiftTaskCreate, current_user_id: Optional[int]
    ) -> ShiftTaskOut:
        self.get_handover_by_id(handover_id)
        task = ShiftTask(
            handover_id=handover_id,
            related_admission_id=data.related_admission_id,
            description=data.description,
            due_at=data.due_at,
            is_done=False,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return ShiftTaskOut.model_validate(task)

    def patch_task(
        self, task_id: int, data: ShiftTaskPatch, current_user_id: Optional[int]
    ) -> ShiftTaskOut:
        task = self.db.query(ShiftTask).filter(ShiftTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Tarea no encontrada")
        if data.description is not None:
            task.description = data.description
        if data.due_at is not None:
            task.due_at = data.due_at
        if data.is_done is not None:
            task.is_done = data.is_done
            if data.is_done:
                task.done_by_user_id = data.done_by_user_id or current_user_id
            else:
                task.done_by_user_id = None
        elif data.done_by_user_id is not None:
            task.done_by_user_id = data.done_by_user_id
        self.db.commit()
        self.db.refresh(task)
        return ShiftTaskOut.model_validate(task)
