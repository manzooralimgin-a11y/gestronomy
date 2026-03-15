from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.dependencies import get_current_tenant_user
from app.hms.models import HotelProperty, Room, HotelReservation
from typing import Any

router = APIRouter()

@router.get("/overview")
async def get_hms_overview(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_tenant_user)
):
    # For now, return a default property or fallback
    query = select(HotelProperty).limit(1)
    result = await db.execute(query)
    property = result.scalar_one_or_none()

    if not property:
        # Fallback data if no property exists yet
        return {
            "hotel_name": "DAS Elb Magdeburg",
            "city": "Magdeburg",
            "total_rooms": 30,
            "occupied": 18,
            "available": 10,
            "cleaning": 2
        }

    # Count rooms by status
    status_counts = await db.execute(
        select(Room.status, func.count(Room.id))
        .where(Room.property_id == property.id)
        .group_by(Room.status)
    )
    counts = {s: c for s, c in status_counts.all()}

    return {
        "hotel_name": property.name,
        "city": property.city,
        "total_rooms": await db.scalar(select(func.count(Room.id)).where(Room.property_id == property.id)),
        "occupied": counts.get("occupied", 0),
        "available": counts.get("available", 0),
        "cleaning": counts.get("cleaning", 0)
    }

@router.get("/rooms")
async def get_hms_rooms(
    db: AsyncSession = Depends(get_db),
    user: Any = Depends(get_current_tenant_user)
):
    query = select(Room).limit(50)
    result = await db.execute(query)
    rooms = result.scalars().all()
    return {"items": rooms}
