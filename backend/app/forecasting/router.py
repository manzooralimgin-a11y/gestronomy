from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.forecasting.schemas import ForecastRead
from app.forecasting.service import (
    get_accuracy_metrics,
    get_item_forecast,
    get_labor_forecast,
    get_sales_forecast,
    trigger_retrain,
)

router = APIRouter()


@router.get("/sales", response_model=list[ForecastRead])
async def sales_forecast(limit: int = 30, db: AsyncSession = Depends(get_db)):
    return await get_sales_forecast(db, limit)


@router.get("/items/{item_id}", response_model=list[ForecastRead])
async def item_forecast(item_id: int, limit: int = 30, db: AsyncSession = Depends(get_db)):
    return await get_item_forecast(db, item_id, limit)


@router.get("/labor", response_model=list[ForecastRead])
async def labor_forecast(limit: int = 30, db: AsyncSession = Depends(get_db)):
    return await get_labor_forecast(db, limit)


@router.get("/accuracy")
async def accuracy(db: AsyncSession = Depends(get_db)):
    return await get_accuracy_metrics(db)


@router.post("/retrain")
async def retrain(forecast_type: str = "sales", db: AsyncSession = Depends(get_db)):
    return await trigger_retrain(db, forecast_type)
