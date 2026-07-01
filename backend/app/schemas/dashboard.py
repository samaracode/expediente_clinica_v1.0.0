from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class MonthlyFlowItem(BaseModel):
    month: str          # formato "YYYY-MM"
    admissions: int
    discharges: int


class StatusCountItem(BaseModel):
    status: str
    count: int


class DashboardSummaryOut(BaseModel):
    # Ocupación
    active_residents: int
    capacity: int
    occupancy_pct: int
    waitlist_count: int

    # KPIs del mes actual
    admissions_this_month: int
    discharges_this_month: int

    # Morosidad — solo presente para roles admin / receptionist
    outstanding_balance: Optional[Decimal] = None

    # Gráficos
    monthly_flow: list[MonthlyFlowItem]
    admissions_by_status: list[StatusCountItem]
