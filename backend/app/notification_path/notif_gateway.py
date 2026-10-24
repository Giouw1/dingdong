from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from app.notification_path.notif_use_cases import (
    get_notifier_use_cases,
    Notificator_UseCases,
    ResourceNotFoundError,
    InvalidPayloadError,
)
from configs.config import get_frontend_settings, FrontendSettings
from typing import Optional
from datetime import datetime
import time

#AI Implemented, a server-cache that puts a timer into every nickname notificated.
class RingDebouncer:
    """
    Prevents duplicate ring notifications from rapid camera pre-fetches or multiple quick scans.
    Tracks timestamps per nickname with a cooldown window.
    """
    def __init__(self, cooldown_seconds: float = 3.0):
        self.cooldown_seconds = cooldown_seconds
        self._last_rings: dict[str, float] = {}

    def should_ring(self, nickname: str) -> bool:
        now = time.time()
        last_time = self._last_rings.get(nickname, 0.0)
        if now - last_time < self.cooldown_seconds:
            return False
        self._last_rings[nickname] = now
        if len(self._last_rings) > 1000:
            self._cleanup(now)
        return True

    def record_failure(self, nickname: str) -> None:
        """Removes the nickname from the debounce tracker if the operation failed (e.g. 404)."""
        self._last_rings.pop(nickname, None)

    def _cleanup(self, now: float) -> None:
        self._last_rings = {
            k: v for k, v in self._last_rings.items()
            if now - v < self.cooldown_seconds * 2
        }


_ring_debouncer = RingDebouncer(cooldown_seconds=3.0)


def get_ring_debouncer() -> RingDebouncer:
    return _ring_debouncer


"""What is expected to come from network to build a payload"""
class NotificationRequest(BaseModel):
    payload: Optional[str] = None


notif_router = APIRouter()


@notif_router.post("/notificate", status_code=status.HTTP_204_NO_CONTENT, tags=["Enviar notificação"])
def notificate(
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


@notif_router.get("/ring", response_class=FileResponse, tags=["Enviar notificação"], summary="Tocar campainha instantaneamente via QR Code (GET)",)
def ring(
    nickname: str = Query(..., description="User nickname to notify"),
    usecases: Notificator_UseCases = Depends(get_notifier_use_cases),
    debouncer: RingDebouncer = Depends(get_ring_debouncer),
    frontend_settings: FrontendSettings = Depends(get_frontend_settings),
):
    """
    Direct scan-to-ring endpoint for physical QR codes.
    Doesn't "work" with the 
        """
    headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    is_new_ring = debouncer.should_ring(nickname)
    if is_new_ring:
        try:
            usecases.notificate(
                nickname=nickname,
                payload=f"Campainha tocada via QR Code",
            )
        except ResourceNotFoundError:
            debouncer.record_failure(nickname)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Non-existent nickname or mailbox",
            )
        except InvalidPayloadError:
            debouncer.record_failure(nickname)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload",
            )
    else:
        headers["X-Ring-Debounced"] = "true"

    notified_file = frontend_settings.FRONTEND_PATH / "notified.html"
    if not notified_file.exists():
        return HTMLResponse(
            content=f"<html><body><h1>Campainha tocada para @{nickname}!</h1></body></html>",
            status_code=status.HTTP_200_OK,
            headers=headers,
        )

    return FileResponse(
        path=notified_file,
        status_code=status.HTTP_200_OK,
        media_type="text/html",
        headers=headers,
    )
