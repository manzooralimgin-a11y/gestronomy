from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manager_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LocationMetric(Base):
    __tablename__ = "location_metrics"

    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    food_cost_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    labor_cost_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_margin: Mapped[float | None] = mapped_column(Float, nullable=True)
    guest_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    compliance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    revenue: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)


class Benchmark(Base):
    __tablename__ = "benchmarks"

    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    group_avg: Mapped[float] = mapped_column(Float, nullable=False)
    top_performer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bottom_performer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
