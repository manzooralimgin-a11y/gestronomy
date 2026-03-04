from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.forecasting.models import Forecast


async def get_sales_forecast(db: AsyncSession, limit: int = 30) -> list[Forecast]:
    result = await db.execute(
        select(Forecast)
        .where(Forecast.forecast_type == "sales")
        .order_by(Forecast.target_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_item_forecast(
    db: AsyncSession, item_id: int, limit: int = 30
) -> list[Forecast]:
    result = await db.execute(
        select(Forecast)
        .where(Forecast.forecast_type == "items", Forecast.item_id == item_id)
        .order_by(Forecast.target_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_labor_forecast(db: AsyncSession, limit: int = 30) -> list[Forecast]:
    result = await db.execute(
        select(Forecast)
        .where(Forecast.forecast_type == "labor")
        .order_by(Forecast.target_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_accuracy_metrics(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Forecast).where(
            Forecast.actual_value.is_not(None),
            Forecast.predicted_value.is_not(None),
        )
    )
    forecasts = result.scalars().all()

    if not forecasts:
        return {"total_evaluated": 0, "mae": None, "mape": None}

    errors = [abs(f.actual_value - f.predicted_value) for f in forecasts]
    pct_errors = [
        abs(f.actual_value - f.predicted_value) / f.actual_value
        for f in forecasts
        if f.actual_value != 0
    ]

    mae = sum(errors) / len(errors)
    mape = (sum(pct_errors) / len(pct_errors) * 100) if pct_errors else None

    return {
        "total_evaluated": len(forecasts),
        "mae": round(mae, 2),
        "mape": round(mape, 2) if mape is not None else None,
    }


async def trigger_retrain(db: AsyncSession, forecast_type: str) -> dict:
    return {
        "status": "queued",
        "forecast_type": forecast_type,
        "message": f"Retrain job for {forecast_type} has been queued",
    }
