from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ForecastRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    forecast_type: str
    target_date: date
    item_id: int | None = None
    predicted_value: float
    confidence_lower: float | None = None
    confidence_upper: float | None = None
    actual_value: float | None = None
    model_version: str | None = None
    created_at: datetime
    updated_at: datetime


class ForecastInputRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    forecast_id: int
    variable_name: str
    variable_value: str
    created_at: datetime
    updated_at: datetime


class ForecastRequest(BaseModel):
    forecast_type: str
    target_date: date
    item_id: int | None = None
