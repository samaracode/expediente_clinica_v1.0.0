import sqlalchemy as sa

from app.db.base_class import Base


class AssistantUsage(Base):
    """Acumulador de gasto del asistente "Ask AI" por mes calendario.

    Una fila por período `YYYY-MM`. Tras cada interacción con el modelo se
    suma el costo real (derivado de `usage` de la API) a la fila del mes en
    curso. El tope mensual (ASSISTANT_MONTHLY_BUDGET_USD) se evalúa leyendo
    `total_cost_usd` del mes actual; al cambiar de mes el gasto vuelve a cero
    solo (no existe fila para el mes nuevo hasta la primera pregunta).
    """

    __tablename__ = "assistant_usage"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    # Período en formato YYYY-MM (p.ej. "2026-07"). Único por mes.
    period = sa.Column(sa.String(7), nullable=False, unique=True, index=True)
    total_cost_usd = sa.Column(sa.Numeric(12, 6), nullable=False, default=0)
    # Contador informativo de preguntas del mes (útil para métricas).
    request_count = sa.Column(sa.Integer, nullable=False, default=0)
    updated_at = sa.Column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )
