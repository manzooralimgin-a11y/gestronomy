from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_lower: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_upper: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)


class ForecastInput(Base):
    __tablename__ = "forecast_inputs"

    forecast_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("forecasts.id"), nullable=False
    )
    variable_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variable_value: Mapped[str] = mapped_column(String(500), nullable=False)
