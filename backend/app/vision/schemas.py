from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisionAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_type: str
    severity: str
    description: str
    image_url: str | None = None
    confidence: float | None = None
    station: str | None = None
    resolved: bool
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class VisionAlertCreate(BaseModel):
    alert_type: str
    severity: str = "warning"
    description: str
    image_url: str | None = None
    confidence: float | None = None
    station: str | None = None


class WasteLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_name: str
    category: str
    weight_g: float
    cost: float
    reason: str | None = None
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime


class WasteLogCreate(BaseModel):
    item_name: str
    category: str
    weight_g: float
    cost: float
    reason: str | None = None
    image_url: str | None = None


class ComplianceEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    employee_id: int | None = None
    station: str | None = None
    details: str | None = None
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime
