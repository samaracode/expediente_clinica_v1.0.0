from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit import AuditLog, OperationType


class AuditService:
    """Registra acciones sensibles (contraseñas, roles, permisos, activación de
    usuarios). No hay visor en v1: se consulta por BD si hace falta."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        user_id: Optional[int],
        operation_type: str,
        table_affected: str,
        record_id: Optional[int] = None,
    ) -> None:
        entry = AuditLog(
            user_id=user_id,
            operation_type=OperationType(operation_type),
            table_affected=table_affected,
            record_id=record_id,
        )
        self.db.add(entry)
        self.db.commit()
