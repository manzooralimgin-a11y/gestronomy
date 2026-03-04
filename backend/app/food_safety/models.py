from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HACCPLog(Base):
    __tablename__ = "haccp_logs"

    check_type: Mapped[str] = mapped_column(String(100), nullable=False)
    station: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    is_compliant: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_logged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class TemperatureReading(Base):
    __tablename__ = "temperature_readings"

    location: Mapped[str] = mapped_column(String(255), nullable=False)
    sensor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    temp_f: Mapped[float] = mapped_column(Float, nullable=False)
    is_safe: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AllergenAlert(Base):
    __tablename__ = "allergen_alerts"

    order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allergen: Mapped[str] = mapped_column(String(100), nullable=False)
    guest_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    action_taken: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ComplianceScore(Base):
    __tablename__ = "compliance_scores"

    date: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    violations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    auto_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    manual_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
