from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_name: str
    action_type: str
    description: str
    input_data: dict | None = None
    output_data: dict | None = None
    status: str
    confidence: float | None = None
    requires_approval: bool
    approved_by: int | None = None
    executed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AgentLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_name: str
    level: str
    message: str
    context_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class AgentConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_name: str
    autonomy_level: str
    thresholds_json: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AgentConfigUpdate(BaseModel):
    autonomy_level: str | None = None
    thresholds_json: dict | None = None
    is_active: bool | None = None


class TableDelayPrediction(BaseModel):
    table_id: int
    table_number: str | None = None
    predicted_wait_min: float
    horizon_minutes: int
    confidence: float
    staffing_pressure_score: float
    target_time: datetime


class PredictorAccuracy(BaseModel):
    sample_size: int
    mae_minutes: float | None = None
    within_10_min_pct: float | None = None
    last_updated_at: datetime | None = None


class ServiceAutopilotPredictionResponse(BaseModel):
    generated_at: datetime
    horizon_minutes: int
    staffing_pressure_score: float
    predictions: list[TableDelayPrediction]
    accuracy: PredictorAccuracy


class ServiceAutopilotSuggestionRead(BaseModel):
    action_id: int
    action_type: str
    title: str
    rationale: str
    projected_wait_delta_min: float
    confidence: float
    requires_approval: bool
    status: str
    payload: dict


class ServiceAutopilotSuggestResponse(BaseModel):
    generated_at: datetime
    staffing_pressure_score: float
    suggestions: list[ServiceAutopilotSuggestionRead]


class ServiceAutopilotActionExecuteResponse(BaseModel):
    action_id: int
    status: str
    executed: bool
    message: str


class RevenueUpsellCandidate(BaseModel):
    menu_item_id: int
    item_name: str
    base_price: float
    demand_score: float
    inventory_risk_score: float
    guest_affinity_score: float
    expected_uplift: float
    rationale: list[str]


class RevenueUpsellOptimizerResponse(BaseModel):
    generated_at: datetime
    guest_id: int | None = None
    candidates: list[RevenueUpsellCandidate]


class RevenueControlPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int | None = None
    kill_switch: bool
    daily_budget_cap: float
    experiment_budget_cap: float
    max_discount_pct: float
    max_price_change_pct: float
    min_margin_pct: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RevenueControlPolicyUpdate(BaseModel):
    kill_switch: bool | None = None
    daily_budget_cap: float | None = None
    experiment_budget_cap: float | None = None
    max_discount_pct: float | None = None
    max_price_change_pct: float | None = None
    min_margin_pct: float | None = None
    is_active: bool | None = None


class RevenueExperimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int | None = None
    name: str
    experiment_type: str
    status: str
    config_json: dict | None = None
    budget_cap: float | None = None
    exposures: int
    conversions: int
    revenue_amount: float
    spent_amount: float
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RevenueExperimentCreate(BaseModel):
    name: str
    experiment_type: str
    config_json: dict | None = None
    budget_cap: float | None = None


class RevenueExperimentEventCreate(BaseModel):
    variant_key: str
    exposures: int = 0
    conversions: int = 0
    revenue_amount: float = 0.0
    spend_amount: float = 0.0


class RevenueExperimentStopResponse(BaseModel):
    experiment_id: int
    status: str
    stopped_at: datetime | None = None


class RevenueExperimentDashboardResponse(BaseModel):
    experiment: RevenueExperimentRead
    control_variant: str
    variants: list[dict]
    total_revenue: float
    total_spend: float
    net_uplift: float
