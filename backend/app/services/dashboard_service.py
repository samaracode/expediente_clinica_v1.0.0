from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session, joinedload

from app.models.admission import Admission, AdmissionStatus
from app.models.finance import Charge, Payment
from app.models.occupancy import ClinicSetting, WaitlistEntry, WaitlistStatus
from app.schemas.dashboard import DashboardSummaryOut, MonthlyFlowItem, StatusCountItem


ACTIVE_STATUSES = {
    AdmissionStatus.consents_pending,
    AdmissionStatus.assessment_in_progress,
    AdmissionStatus.treatment_active,
}

# Roles autorizados a ver morosidad (coherente con lib/access.ts)
FINANCE_ROLES = {"admin", "receptionist"}


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Ocupación
    # ------------------------------------------------------------------

    def _get_capacity(self) -> int:
        row = self.db.query(ClinicSetting).filter(ClinicSetting.key == "capacity").first()
        return int(row.value) if row else 24

    def _active_count(self) -> int:
        return (
            self.db.query(sa.func.count(Admission.id))
            .filter(
                Admission.status == AdmissionStatus.treatment_active,
                Admission.is_deleted == False,  # noqa: E712
            )
            .scalar()
            or 0
        )

    def _waitlist_count(self) -> int:
        return (
            self.db.query(sa.func.count(WaitlistEntry.id))
            .filter(WaitlistEntry.status == WaitlistStatus.waiting)
            .scalar()
            or 0
        )

    # ------------------------------------------------------------------
    # KPIs del mes
    # ------------------------------------------------------------------

    def _admissions_this_month(self) -> int:
        today = date.today()
        start = date(today.year, today.month, 1)
        return (
            self.db.query(sa.func.count(Admission.id))
            .filter(
                Admission.admission_date >= start,
                Admission.admission_date <= today,
                Admission.is_deleted == False,  # noqa: E712
            )
            .scalar()
            or 0
        )

    def _discharges_this_month(self) -> int:
        today = date.today()
        start = date(today.year, today.month, 1)
        return (
            self.db.query(sa.func.count(Admission.id))
            .filter(
                Admission.status.in_([AdmissionStatus.discharged, AdmissionStatus.abandoned]),
                Admission.discharge_date >= start,
                Admission.discharge_date <= today,
                Admission.is_deleted == False,  # noqa: E712
            )
            .scalar()
            or 0
        )

    # ------------------------------------------------------------------
    # Morosidad (solo para roles autorizados)
    # ------------------------------------------------------------------

    def _outstanding_balance(self) -> Decimal:
        admissions = (
            self.db.query(Admission)
            .options(joinedload(Admission.charges), joinedload(Admission.payments))
            .filter(
                Admission.status.in_(ACTIVE_STATUSES),
                Admission.is_deleted == False,  # noqa: E712
            )
            .all()
        )
        total = Decimal(0)
        for adm in admissions:
            charges = sum((c.amount for c in adm.charges), Decimal(0))
            payments = sum((p.amount for p in adm.payments), Decimal(0))
            balance = charges - payments
            if balance > 0:
                total += balance
        return total

    # ------------------------------------------------------------------
    # Gráfico: flujo mensual (últimos 6 meses)
    # ------------------------------------------------------------------

    def _monthly_flow(self) -> list[MonthlyFlowItem]:
        today = date.today()
        result: list[MonthlyFlowItem] = []

        for delta in range(5, -1, -1):
            # calcular mes objetivo
            year = today.year
            month = today.month - delta
            while month <= 0:
                month += 12
                year -= 1

            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            label = f"{year}-{month:02d}"

            admissions_count = (
                self.db.query(sa.func.count(Admission.id))
                .filter(
                    Admission.admission_date >= start,
                    Admission.admission_date <= end,
                    Admission.is_deleted == False,  # noqa: E712
                )
                .scalar()
                or 0
            )
            discharges_count = (
                self.db.query(sa.func.count(Admission.id))
                .filter(
                    Admission.status.in_([AdmissionStatus.discharged, AdmissionStatus.abandoned]),
                    Admission.discharge_date >= start,
                    Admission.discharge_date <= end,
                    Admission.is_deleted == False,  # noqa: E712
                )
                .scalar()
                or 0
            )
            result.append(MonthlyFlowItem(month=label, admissions=admissions_count, discharges=discharges_count))

        return result

    # ------------------------------------------------------------------
    # Gráfico: residentes por estado de admisión
    # ------------------------------------------------------------------

    def _admissions_by_status(self) -> list[StatusCountItem]:
        rows = (
            self.db.query(Admission.status, sa.func.count(Admission.id))
            .filter(Admission.is_deleted == False)  # noqa: E712
            .group_by(Admission.status)
            .all()
        )
        return [StatusCountItem(status=status.value, count=count) for status, count in rows]

    # ------------------------------------------------------------------
    # Método principal
    # ------------------------------------------------------------------

    def get_summary(self, user_role: str) -> DashboardSummaryOut:
        capacity = self._get_capacity()
        active = self._active_count()
        waitlist = self._waitlist_count()
        occupancy_pct = round(active / capacity * 100) if capacity > 0 else 0

        outstanding: Optional[Decimal] = None
        if user_role in FINANCE_ROLES:
            outstanding = self._outstanding_balance()

        return DashboardSummaryOut(
            # ocupación
            active_residents=active,
            capacity=capacity,
            occupancy_pct=occupancy_pct,
            waitlist_count=waitlist,
            # KPIs del mes
            admissions_this_month=self._admissions_this_month(),
            discharges_this_month=self._discharges_this_month(),
            # morosidad (solo roles autorizados)
            outstanding_balance=outstanding,
            # gráficos
            monthly_flow=self._monthly_flow(),
            admissions_by_status=self._admissions_by_status(),
        )
