from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HACCPLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    check_type: str
    station: str | None = None
    value: str
    is_compliant: bool
    auto_logged: bool
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class HACCPLogCreate(BaseModel):
    check_type: str
    station: str | None = None
    value: str
    is_compliant: bool = True
    auto_logged: bool = False
    notes: str | None = None


class TemperatureReadingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location: str
    sensor_id: str | None = None
    temp_f: float
    is_safe: bool
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class TemperatureReadingCreate(BaseModel):
    location: str
    sensor_id: str | None = None
    temp_f: float
    is_safe: bool = True
    timestamp: datetime


class AllergenAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int | None = None
    allergen: str
    guest_id: int | None = None
    severity: str
    action_taken: str | None = None
    created_at: datetime
    updated_at: datetime


class ComplianceScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    score: float
    violations_count: int
    auto_resolved: int
    manual_resolved: int
    created_at: datetime
    updated_at: datetime


class ComplianceAskRequest(BaseModel):
    question: str


class ComplianceAskResponse(BaseModel):
    question: str
    answer: str
    references: list[str] | None = None
