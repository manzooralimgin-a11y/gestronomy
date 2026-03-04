from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DashboardQueryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    query_text: str
    ai_response: str | None = None
    response_data_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    module: str
    severity: str
    title: str
    message: str
    is_read: bool
    action_taken: str | None = None
    owner: str | None = None
    status: str
    sla_status: str
    sla_minutes: int | None = None
    due_at: datetime | None = None
    resolved_at: datetime | None = None
    resolved_by: int | None = None
    created_at: datetime
    updated_at: datetime


class KPISnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    metric_name: str
    value: float
    previous_value: float | None = None
    target_value: float | None = None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class NLQueryRequest(BaseModel):
    query: str


class NLQueryResponse(BaseModel):
    query: str
    answer: str
    data: Any | None = None


class AlertUpdate(BaseModel):
    is_read: bool | None = None
    action_taken: str | None = None
    owner: str | None = None
    status: str | None = None
    sla_status: str | None = None
    sla_minutes: int | None = None


class ExceptionInboxItem(BaseModel):
    id: int
    source_type: str
    module: str
    severity: str
    title: str
    message: str
    owner: str
    status: str
    impact_score: int
    sla_minutes: int
    sla_status: str
    due_at: datetime | None = None
    recommended_actions: list[str]
    created_at: datetime


class ExceptionWorkflowUpdate(BaseModel):
    owner: str | None = None
    sla_status: str | None = None
    sla_minutes: int | None = None
    status: str | None = None
    action_taken: str | None = None


class ExplainableRecommendation(BaseModel):
    id: int
    agent_name: str
    title: str
    recommendation: str
    rationale: str
    confidence: float | None = None
    estimated_impact: str | None = None
    requires_approval: bool
    rollback_strategy: str | None = None
    status: str
    created_at: datetime


class AuditTimelineEvent(BaseModel):
    id: str
    event_type: str
    actor_type: str
    actor_name: str
    entity_type: str | None = None
    entity_id: int | None = None
    action: str
    detail: str
    created_at: datetime


class SLOBreach(BaseModel):
    metric: str
    threshold: float
    actual: float
    severity: str
    message: str


class SLODashboardResponse(BaseModel):
    window_minutes: int
    api_p95_latency_ms: float
    api_error_rate_pct: float
    queue_lag: int | None = None
    thresholds: dict
    breaches: list[SLOBreach]
