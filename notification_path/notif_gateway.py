from fastapi import APIRouter, Depends, HTTPException, status, Query
from notification_path.payload_validator import NotificationRequest
from notification_path.notif_use_cases import (
    get_notifier_use_cases,
    Notificator_UseCases,
    ResourceNotFoundError,
    InvalidPayloadError,
)
from typing import Optional

notif_router = APIRouter()


@notif_router.post("/notificate", tags=["Enviar notificação"])
async def notificate(
    nickname: str = Query(..., description="User nickname"),
    body: Optional[NotificationRequest] = None,
    usecases: Notificator_UseCases = Depends(get_notifier_use_cases),
):
    raw_payload = body.payload if body is not None else None
    try:
        usecases.notificate(nickname=nickname, payload=raw_payload)
        return "Notification sent successfully"
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Non-existent nickname or mailbox",
        )
    except InvalidPayloadError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
