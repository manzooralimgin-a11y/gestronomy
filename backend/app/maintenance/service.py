from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.models import EnergyReading, Equipment, IoTReading, MaintenanceTicket
from app.maintenance.schemas import (
    EnergyReadingCreate,
    EquipmentCreate,
    IoTReadingCreate,
    MaintenanceTicketCreate,
)


async def get_equipment_list(
    db: AsyncSession, status_filter: str | None = None, limit: int = 100
) -> list[Equipment]:
    query = select(Equipment).order_by(Equipment.name).limit(limit)
    if status_filter:
        query = query.where(Equipment.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_equipment_by_id(db: AsyncSession, equipment_id: int) -> Equipment:
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    equipment = result.scalar_one_or_none()
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found"
        )
    return equipment


async def create_equipment(db: AsyncSession, payload: EquipmentCreate) -> Equipment:
    equipment = Equipment(**payload.model_dump())
    db.add(equipment)
    await db.flush()
    await db.refresh(equipment)
    return equipment


async def get_tickets(
    db: AsyncSession, status_filter: str | None = None, limit: int = 100
) -> list[MaintenanceTicket]:
    query = select(MaintenanceTicket).order_by(MaintenanceTicket.created_at.desc()).limit(limit)
    if status_filter:
        query = query.where(MaintenanceTicket.status == status_filter)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_ticket(
    db: AsyncSession, payload: MaintenanceTicketCreate
) -> MaintenanceTicket:
    ticket = MaintenanceTicket(**payload.model_dump())
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def get_failure_predictions(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Equipment).where(Equipment.health_score < 50).order_by(Equipment.health_score)
    )
    equipment_list = result.scalars().all()
    return [
        {
            "equipment_id": eq.id,
            "name": eq.name,
            "health_score": eq.health_score,
            "predicted_failure": "Stub: ML prediction pending",
        }
        for eq in equipment_list
    ]


async def get_energy_usage(
    db: AsyncSession, zone: str | None = None, limit: int = 100
) -> list[EnergyReading]:
    query = select(EnergyReading).order_by(EnergyReading.timestamp.desc()).limit(limit)
    if zone:
        query = query.where(EnergyReading.zone == zone)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_energy_savings(db: AsyncSession) -> dict:
    return {
        "message": "Stub: Energy savings analysis pending",
        "estimated_savings_kwh": 0,
        "estimated_savings_cost": 0,
    }
