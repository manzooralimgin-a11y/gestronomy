from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.vision.models import ComplianceEvent, VisionAlert, WasteLog
from app.vision.schemas import VisionAlertCreate, WasteLogCreate


async def get_alerts(
    db: AsyncSession, resolved: bool | None = None, limit: int = 100
) -> list[VisionAlert]:
    query = select(VisionAlert).order_by(VisionAlert.created_at.desc()).limit(limit)
    if resolved is not None:
        query = query.where(VisionAlert.resolved == resolved)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_alert(db: AsyncSession, payload: VisionAlertCreate) -> VisionAlert:
    alert = VisionAlert(**payload.model_dump())
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def get_waste_logs(
    db: AsyncSession, category: str | None = None, limit: int = 100
) -> list[WasteLog]:
    query = select(WasteLog).order_by(WasteLog.created_at.desc()).limit(limit)
    if category:
        query = query.where(WasteLog.category == category)
    result = await db.execute(query)
    return list(result.scalars().all())


async def log_waste(db: AsyncSession, payload: WasteLogCreate) -> WasteLog:
    waste = WasteLog(**payload.model_dump())
    db.add(waste)
    await db.flush()
    await db.refresh(waste)
    return waste


async def get_compliance_events(
    db: AsyncSession, event_type: str | None = None, limit: int = 100
) -> list[ComplianceEvent]:
    query = select(ComplianceEvent).order_by(ComplianceEvent.created_at.desc()).limit(limit)
    if event_type:
        query = query.where(ComplianceEvent.event_type == event_type)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_vision_stats(db: AsyncSession) -> dict:
    alert_count = await db.execute(select(func.count(VisionAlert.id)))
    unresolved_count = await db.execute(
        select(func.count(VisionAlert.id)).where(VisionAlert.resolved == False)
    )
    waste_total = await db.execute(select(func.sum(WasteLog.cost)))
    compliance_count = await db.execute(select(func.count(ComplianceEvent.id)))

    return {
        "total_alerts": alert_count.scalar() or 0,
        "unresolved_alerts": unresolved_count.scalar() or 0,
        "total_waste_cost": float(waste_total.scalar() or 0),
        "total_compliance_events": compliance_count.scalar() or 0,
    }
