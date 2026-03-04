from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    name: str
    email: str | None = None
    role: str
    hourly_rate: float
    skills_json: dict | None = None
    certifications_json: dict | None = None
    hire_date: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class EmployeeCreate(BaseModel):
    user_id: int | None = None
    name: str
    email: str | None = None
    role: str
    hourly_rate: float = 0
    skills_json: dict | None = None
    certifications_json: dict | None = None
    hire_date: date | None = None


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    week_start: date
    status: str
    total_hours: float
    total_cost: float
    auto_generated: bool
    approved_by: int | None = None
    created_at: datetime
    updated_at: datetime


class ScheduleCreate(BaseModel):
    week_start: date


class ShiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    schedule_id: int
    employee_id: int
    date: date
    start_time: time
    end_time: time
    role: str
    station: str | None = None
    actual_clock_in: datetime | None = None
    actual_clock_out: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ShiftCreate(BaseModel):
    schedule_id: int
    employee_id: int
    date: date
    start_time: time
    end_time: time
    role: str
    station: str | None = None


class ApplicantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None = None
    position: str
    resume_url: str | None = None
    ai_match_score: float | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ApplicantCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    position: str
    resume_url: str | None = None


class TrainingModuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: str
    duration_min: int
    content_url: str | None = None
    required_for_roles: dict | None = None
    created_at: datetime
    updated_at: datetime


class TrainingProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    module_id: int
    status: str
    score: float | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
