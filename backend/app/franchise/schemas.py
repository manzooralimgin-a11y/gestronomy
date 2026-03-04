from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int | None = None
    name: str
    address: str | None = None
    city: str | None = None
    region: str | None = None
    manager_id: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LocationCreate(BaseModel):
    restaurant_id: int | None = None
    name: str
    address: str | None = None
    city: str | None = None
    region: str | None = None
    manager_id: int | None = None
    is_active: bool = True


class LocationMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_id: int
    date: date
    food_cost_pct: float | None = None
    labor_cost_pct: float | None = None
    net_margin: float | None = None
    guest_score: float | None = None
    compliance_score: float | None = None
    revenue: float | None = None
    created_at: datetime
    updated_at: datetime


class LocationMetricCreate(BaseModel):
    location_id: int
    date: date
    food_cost_pct: float | None = None
    labor_cost_pct: float | None = None
    net_margin: float | None = None
    guest_score: float | None = None
    compliance_score: float | None = None
    revenue: float | None = None


class BenchmarkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    metric_name: str
    group_avg: float
    top_performer_id: int | None = None
    bottom_performer_id: int | None = None
    date: date
    created_at: datetime
    updated_at: datetime
