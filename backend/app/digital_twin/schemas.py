from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ScenarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    scenario_type: str
    parameters_json: dict | None = None
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime


class ScenarioCreate(BaseModel):
    name: str
    description: str | None = None
    scenario_type: str
    parameters_json: dict | None = None


class SimulationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    status: str
    results_json: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SimulationRunCreate(BaseModel):
    scenario_id: int
