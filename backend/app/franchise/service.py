from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.franchise.models import Benchmark, Location, LocationMetric
from app.franchise.schemas import LocationCreate


async def get_locations(
    db: AsyncSession, restaurant_id: int, active_only: bool = True, limit: int = 100
) -> list[Location]:
    query = (
        select(Location)
        .where(Location.restaurant_id == restaurant_id)
        .order_by(Location.name)
        .limit(limit)
    )
    if active_only:
        query = query.where(Location.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_location_detail(db: AsyncSession, restaurant_id: int, location_id: int) -> Location:
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.restaurant_id == restaurant_id,
        )
    )
    location = result.scalar_one_or_none()
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return location


async def create_location(db: AsyncSession, restaurant_id: int, payload: LocationCreate) -> Location:
    payload_data = payload.model_dump()
    payload_data["restaurant_id"] = restaurant_id
    location = Location(**payload_data)
    db.add(location)
    await db.flush()
    await db.refresh(location)
    return location


async def get_benchmarks(
    db: AsyncSession, metric_name: str | None = None, limit: int = 100
) -> list[Benchmark]:
    query = select(Benchmark).order_by(Benchmark.date.desc()).limit(limit)
    if metric_name:
        query = query.where(Benchmark.metric_name == metric_name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_rankings(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(LocationMetric).order_by(LocationMetric.date.desc()).limit(200)
    )
    metrics = result.scalars().all()
    rankings: dict[int, dict] = {}
    for m in metrics:
        if m.location_id not in rankings:
            rankings[m.location_id] = {
                "location_id": m.location_id,
                "revenue": float(m.revenue) if m.revenue else 0,
                "net_margin": m.net_margin or 0,
                "guest_score": m.guest_score or 0,
            }
    return sorted(rankings.values(), key=lambda x: x["revenue"], reverse=True)


async def detect_anomalies(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(LocationMetric).order_by(LocationMetric.date.desc()).limit(500)
    )
    metrics = result.scalars().all()
    anomalies: list[dict] = []
    for m in metrics:
        if m.food_cost_pct and m.food_cost_pct > 40:
            anomalies.append({
                "location_id": m.location_id,
                "date": str(m.date),
                "metric": "food_cost_pct",
                "value": m.food_cost_pct,
                "message": "Food cost percentage exceeds 40%",
            })
        if m.labor_cost_pct and m.labor_cost_pct > 35:
            anomalies.append({
                "location_id": m.location_id,
                "date": str(m.date),
                "metric": "labor_cost_pct",
                "value": m.labor_cost_pct,
                "message": "Labor cost percentage exceeds 35%",
            })
    return anomalies
