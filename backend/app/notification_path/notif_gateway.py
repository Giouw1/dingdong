from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from pydantic import BaseModel
from app.notification_path.notif_use_cases import (
    get_notifier_use_cases,
    Notificator_UseCases,
    ResourceNotFoundError,
    InvalidPayloadError,
)
from typing import Optional


"""What is expected to come from network to build a payload"""
class NotificationRequest(BaseModel):
    payload: Optional[str] = None

notif_router = APIRouter()


@notif_router.post("/notificate", status_code=status.HTTP_204_NO_CONTENT, tags=["Enviar notificação"])
async def notificate(
    nickname: str = Query(..., description="User nickname"),
    body: Optional[NotificationRequest] = None,
    usecases: Notificator_UseCases = Depends(get_notifier_use_cases),
):
    raw_payload = body.payload if body is not None else None
    try:
        usecases.notificate(nickname=nickname, payload=raw_payload)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
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
    