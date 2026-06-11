from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.notification_service import Notification, NotificationService

router = APIRouter()


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("/notifications", response_model=list[Notification])
def get_notifications(
    service: NotificationService = Depends(get_notification_service),
    _: object = Depends(get_current_user),
):
    return service.get_notifications()
