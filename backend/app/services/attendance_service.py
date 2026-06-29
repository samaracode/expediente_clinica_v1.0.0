"""
Capa de lógica de negocio para el módulo de Asistencia.

Criterio de expected_status (documentado):
- Se considera "residente activo" toda admisión con status en
  {consents_pending, assessment_in_progress, treatment_active}.
- Para cada admisión activa, en la fecha dada:
  1. Si tiene un ExitPass con status=approved cuya departure_date <= fecha
     Y que aún no haya retornado (return_date_actual IS NULL)
     Y cuya return_date_expected >= fecha (o return_date_expected IS NULL):
       → expected_status = on_pass
     (No hay PassType que mapee a external_appointment en el modelo actual;
      si se agrega en el futuro, mapear PassType.special → external_appointment.)
  2. En cualquier otro caso → expected_status = present.
"""

from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.admission import Admission, AdmissionStatus
from app.models.attendance import (
    AttendanceEntry,
    AttendanceRollCall,
    PresenceStatus,
    Shift,
)
from app.models.follow_up import ExitPass, PassStatus
from app.models.resident import Resident
from app.schemas.attendance import (
    AttendanceSummaryOut,
    EntryIn,
    EntryOut,
    RollCallCreate,
    RollCallOut,
    RosterEntryOut,
    RosterOut,
)

# Statuses que cuentan como "residente activo"
ACTIVE_STATUSES = {
    AdmissionStatus.consents_pending,
    AdmissionStatus.assessment_in_progress,
    AdmissionStatus.treatment_active,
}


def _compute_expected_status(admission: Admission, target_date: date, db: Session) -> PresenceStatus:
    """
    Calcula el estado esperado de una admisión activa para una fecha dada.

    Regla:
    - Si tiene ExitPass aprobado vigente para esa fecha → on_pass.
    - En caso contrario → present.

    Un ExitPass cuenta como "vigente" si:
      status == approved
      AND departure_date (como date) <= target_date
      AND return_date_actual IS NULL
      AND (return_date_expected IS NULL OR return_date_expected (como date) >= target_date)
    """
    passes = (
        db.query(ExitPass)
        .filter(
            ExitPass.admission_id == admission.id,
            ExitPass.status == PassStatus.approved,
            ExitPass.departure_date != None,  # noqa: E711
            ExitPass.return_date_actual == None,  # noqa: E711
        )
        .all()
    )

    for ep in passes:
        if ep.departure_date is None:
            continue
        dep_date = ep.departure_date.date() if isinstance(ep.departure_date, datetime) else ep.departure_date
        if dep_date > target_date:
            continue
        if ep.return_date_expected is not None:
            ret_date = (
                ep.return_date_expected.date()
                if isinstance(ep.return_date_expected, datetime)
                else ep.return_date_expected
            )
            if ret_date < target_date:
                continue
        # Pase vigente encontrado
        return PresenceStatus.on_pass

    return PresenceStatus.present


def _get_active_admissions(db: Session) -> List[Admission]:
    return (
        db.query(Admission)
        .options(joinedload(Admission.resident))
        .filter(Admission.status.in_(list(ACTIVE_STATUSES)))
        .all()
    )


def _get_roll_call(db: Session, target_date: date, shift: Shift) -> Optional[AttendanceRollCall]:
    return (
        db.query(AttendanceRollCall)
        .options(
            joinedload(AttendanceRollCall.entries).joinedload(AttendanceEntry.admission).joinedload(Admission.resident)
        )
        .filter(
            AttendanceRollCall.date == target_date,
            AttendanceRollCall.shift == shift,
        )
        .first()
    )


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # GET /attendance/roll-call  — roster pre-llenado (sin persistir)
    # ------------------------------------------------------------------

    def get_roster(self, target_date: date, shift: Shift) -> RosterOut:
        """
        Si ya existe un pase guardado para (date, shift), lo devuelve.
        Si no, calcula el estado esperado de cada residente activo y devuelve
        el roster sin persistir aún.
        """
        existing = _get_roll_call(self.db, target_date, shift)

        if existing:
            # Devolver lo guardado
            roster_entries: List[RosterEntryOut] = []
            for entry in existing.entries:
                admission = entry.admission
                resident: Resident = admission.resident
                roster_entries.append(
                    RosterEntryOut(
                        admission_id=admission.id,
                        resident_id=resident.id,
                        resident_name=f"{resident.first_name} {resident.last_name}",
                        expected_status=entry.expected_status,
                        actual_status=entry.actual_status,
                        note=entry.note,
                        entry_id=entry.id,
                    )
                )
            return RosterOut(
                date=target_date,
                shift=shift,
                roll_call_id=existing.id,
                conducted_by_user_id=existing.conducted_by_user_id,
                conducted_at=existing.conducted_at,
                notes=existing.notes,
                entries=roster_entries,
            )

        # Calcular estado esperado sin persistir
        active_admissions = _get_active_admissions(self.db)
        roster_entries = []
        for admission in active_admissions:
            resident: Resident = admission.resident
            expected = _compute_expected_status(admission, target_date, self.db)
            roster_entries.append(
                RosterEntryOut(
                    admission_id=admission.id,
                    resident_id=resident.id,
                    resident_name=f"{resident.first_name} {resident.last_name}",
                    expected_status=expected,
                    actual_status=None,
                    note=None,
                    entry_id=None,
                )
            )
        return RosterOut(
            date=target_date,
            shift=shift,
            roll_call_id=None,
            entries=roster_entries,
        )

    # ------------------------------------------------------------------
    # POST /attendance/roll-call  — guardar/confirmar (upsert)
    # ------------------------------------------------------------------

    def confirm_roll_call(
        self,
        data: RollCallCreate,
        current_user_id: Optional[int],
    ) -> RollCallOut:
        """
        Crea o actualiza el AttendanceRollCall para (date, shift).
        Si ya existe, elimina las entries previas y las reemplaza (upsert).
        """
        existing = (
            self.db.query(AttendanceRollCall)
            .filter(
                AttendanceRollCall.date == data.date,
                AttendanceRollCall.shift == data.shift,
            )
            .first()
        )

        if existing:
            # Actualizar metadatos
            existing.conducted_by_user_id = current_user_id
            existing.conducted_at = datetime.now(timezone.utc)
            existing.notes = data.notes
            # Eliminar entries viejas (cascade o manual)
            self.db.query(AttendanceEntry).filter(
                AttendanceEntry.roll_call_id == existing.id
            ).delete(synchronize_session=False)
            roll_call = existing
        else:
            roll_call = AttendanceRollCall(
                date=data.date,
                shift=data.shift,
                conducted_by_user_id=current_user_id,
                conducted_at=datetime.now(timezone.utc),
                notes=data.notes,
            )
            self.db.add(roll_call)
            self.db.flush()

        # Crear las entries nuevas
        new_entries: List[AttendanceEntry] = []
        for entry_in in data.entries:
            new_entries.append(
                AttendanceEntry(
                    roll_call_id=roll_call.id,
                    admission_id=entry_in.admission_id,
                    expected_status=entry_in.expected_status,
                    actual_status=entry_in.actual_status,
                    note=entry_in.note,
                )
            )
        self.db.add_all(new_entries)
        self.db.commit()
        self.db.refresh(roll_call)

        # Recargar con entries
        self.db.refresh(roll_call)
        # Cargar entries explícitamente después del commit
        entries_db = (
            self.db.query(AttendanceEntry)
            .filter(AttendanceEntry.roll_call_id == roll_call.id)
            .all()
        )
        return RollCallOut(
            id=roll_call.id,
            date=roll_call.date,
            shift=roll_call.shift,
            conducted_by_user_id=roll_call.conducted_by_user_id,
            conducted_at=roll_call.conducted_at,
            notes=roll_call.notes,
            entries=[EntryOut.model_validate(e) for e in entries_db],
        )

    # ------------------------------------------------------------------
    # GET /attendance/today  — resumen del día
    # ------------------------------------------------------------------

    def get_today_summary(self, target_date: Optional[date] = None) -> AttendanceSummaryOut:
        """
        Resumen de conteo para una fecha (default: hoy).
        Usa el último roll-call del día si existe; si no, calcula el estado esperado.
        """
        if target_date is None:
            target_date = date.today()

        # Buscar el roll-call más reciente del día (cualquier turno)
        latest_roll_call = (
            self.db.query(AttendanceRollCall)
            .filter(AttendanceRollCall.date == target_date)
            .order_by(AttendanceRollCall.conducted_at.desc())
            .first()
        )

        counts = {
            PresenceStatus.present: 0,
            PresenceStatus.on_pass: 0,
            PresenceStatus.external_appointment: 0,
            PresenceStatus.hospitalized: 0,
            PresenceStatus.absent_without_leave: 0,
            PresenceStatus.discharged: 0,
        }

        if latest_roll_call:
            entries = (
                self.db.query(AttendanceEntry)
                .filter(AttendanceEntry.roll_call_id == latest_roll_call.id)
                .all()
            )
            for e in entries:
                counts[e.actual_status] = counts.get(e.actual_status, 0) + 1
            source = "roll_call"
        else:
            # Calcular desde estado esperado
            active_admissions = _get_active_admissions(self.db)
            for admission in active_admissions:
                expected = _compute_expected_status(admission, target_date, self.db)
                counts[expected] = counts.get(expected, 0) + 1
            source = "expected"

        total = sum(counts.values())
        return AttendanceSummaryOut(
            date=target_date,
            source=source,
            total=total,
            present=counts[PresenceStatus.present],
            on_pass=counts[PresenceStatus.on_pass],
            external_appointment=counts[PresenceStatus.external_appointment],
            hospitalized=counts[PresenceStatus.hospitalized],
            absent_without_leave=counts[PresenceStatus.absent_without_leave],
            discharged=counts[PresenceStatus.discharged],
        )

    # ------------------------------------------------------------------
    # GET /admissions/{admission_id}/attendance  — historial por residente
    # ------------------------------------------------------------------

    def get_admission_history(self, admission_id: int) -> List[EntryOut]:
        """Historial de entries de asistencia para una admisión, más reciente primero."""
        admission = self.db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admisión no encontrada")

        entries = (
            self.db.query(AttendanceEntry)
            .join(AttendanceRollCall, AttendanceEntry.roll_call_id == AttendanceRollCall.id)
            .filter(AttendanceEntry.admission_id == admission_id)
            .order_by(AttendanceRollCall.date.desc(), AttendanceRollCall.conducted_at.desc())
            .all()
        )
        return [EntryOut.model_validate(e) for e in entries]
