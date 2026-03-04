from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EquipmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    location: str | None = None
    model_name: str | None = None
    serial_number: str | None = None
    install_date: date | None = None
    last_service: date | None = None
    health_score: float
    status: str
    created_at: datetime
    updated_at: datetime


class EquipmentCreate(BaseModel):
    name: str
    type: str
    location: str | None = None
    model_name: str | None = None
    serial_number: str | None = None
    install_date: date | None = None
    last_service: date | None = None
    health_score: float = 100
    status: str = "operational"


class IoTReadingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class IoTReadingCreate(BaseModel):
    equipment_id: int
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime


class MaintenanceTicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipment_id: int
    issue: str
    priority: str
    status: str
    auto_generated: bool
    technician: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class MaintenanceTicketCreate(BaseModel):
    equipment_id: int
    issue: str
    priority: str = "medium"
    status: str = "open"
    auto_generated: bool = False
    technician: str | None = None


class EnergyReadingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone: str
    reading_kwh: float
    cost: float | None = None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class EnergyReadingCreate(BaseModel):
    zone: str
    reading_kwh: float
    cost: float | None = None
    timestamp: datetime
