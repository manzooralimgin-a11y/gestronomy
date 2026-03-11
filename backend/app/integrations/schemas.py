from datetime import datetime
from typing import Any
from pydantic import BaseModel

class VoiceBookerEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    payload: dict[str, Any]

class WebhookResponse(BaseModel):
    status: str
    event_id: str
