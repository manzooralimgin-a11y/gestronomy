from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentAction(Base):
    __tablename__ = "agent_actions"

    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    input_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"

    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    context_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class AgentConfig(Base):
    __tablename__ = "agent_configs"

    agent_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    autonomy_level: Mapped[str] = mapped_column(String(20), default="semi", nullable=False)
    thresholds_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ServiceAutopilotPrediction(Base):
    __tablename__ = "service_autopilot_predictions"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    table_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tables.id", ondelete="SET NULL"), nullable=True
    )
    horizon_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    target_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    predicted_wait_min: Mapped[float] = mapped_column(Float, nullable=False)
    staffing_pressure_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    actual_wait_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_abs_min: Mapped[float | None] = mapped_column(Float, nullable=True)


class RevenueControlPolicy(Base):
    __tablename__ = "revenue_control_policies"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), unique=True, nullable=True
    )
    kill_switch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    daily_budget_cap: Mapped[float] = mapped_column(Numeric(12, 2), default=500, nullable=False)
    experiment_budget_cap: Mapped[float] = mapped_column(Numeric(12, 2), default=200, nullable=False)
    max_discount_pct: Mapped[float] = mapped_column(Float, default=30, nullable=False)
    max_price_change_pct: Mapped[float] = mapped_column(Float, default=25, nullable=False)
    min_margin_pct: Mapped[float] = mapped_column(Float, default=15, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RevenueExperiment(Base):
    __tablename__ = "revenue_experiments"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    experiment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    budget_cap: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    exposures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revenue_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    spent_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RevenueExperimentEvent(Base):
    __tablename__ = "revenue_experiment_events"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    experiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("revenue_experiments.id", ondelete="CASCADE"), nullable=False
    )
    variant_key: Mapped[str] = mapped_column(String(80), nullable=False)
    exposures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revenue_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    spend_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RevenueUpsellRecommendation(Base):
    __tablename__ = "revenue_upsell_recommendations"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    guest_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("guest_profiles.id", ondelete="SET NULL"), nullable=True
    )
    menu_item_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expected_uplift: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    factors_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
