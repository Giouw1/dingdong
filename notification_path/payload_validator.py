from pydantic import BaseModel
from typing import Optional


class NotificationRequest(BaseModel):
    payload: Optional[str] = None
