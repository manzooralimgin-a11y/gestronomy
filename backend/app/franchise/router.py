from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.database import get_db
from app.dependencies import get_current_tenant_user
from app.franchise.schemas import BenchmarkRead, LocationCreate, LocationRead
from app.franchise.service import (
    create_location,
    detect_anomalies,
    get_benchmarks,
    get_location_detail,
    get_locations,
    get_rankings,
)

router = APIRouter()


@router.get("/locations", response_model=list[LocationRead])
async def list_locations(
    active_only: bool = True,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_locations(db, current_user.restaurant_id, active_only, limit)


@router.get("/locations/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_location_detail(db, current_user.restaurant_id, location_id)


@router.post("/locations", response_model=LocationRead, status_code=201)
async def add_location(
    payload: LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_location(db, current_user.restaurant_id, payload)


@router.get("/benchmarks", response_model=list[BenchmarkRead])
async def list_benchmarks(
    metric_name: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await get_benchmarks(db, metric_name, limit)


@router.get("/rankings", response_model=list[dict[str, Any]])
async def location_rankings(db: AsyncSession = Depends(get_db)):
    return await get_rankings(db)


@router.get("/anomalies", response_model=list[dict[str, Any]])
async def location_anomalies(db: AsyncSession = Depends(get_db)):
    return await detect_anomalies(db)
