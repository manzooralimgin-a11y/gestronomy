from datetime import date, time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.reservations.models import Reservation
from app.websockets.connection_manager import manager
from app.qr_ordering import service as qr_service, schemas as qr_schemas

router = APIRouter()

class RestaurantReservationCreate(BaseModel):
    restaurant_id: int
    guest_name: str
    guest_email: EmailStr
    guest_phone: str
    party_size: int
    reservation_date: date
    start_time: str # HH:MM
    special_requests: Optional[str] = None

@router.post("/reserve")
async def create_restaurant_reservation(
    res: RestaurantReservationCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        h, m = map(int, res.start_time.split(":"))
        start_time_obj = time(h, m)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

    new_res = Reservation(
        restaurant_id=res.restaurant_id,
        guest_name=res.guest_name,
        guest_email=res.guest_email,
        guest_phone=res.guest_phone,
        party_size=res.party_size,
        reservation_date=res.reservation_date,
        start_time=start_time_obj,
        special_requests=res.special_requests,
        status="confirmed",
        source="online",
    )

    db.add(new_res)
    await db.commit()
    await db.refresh(new_res)

    # Broadcast to Management Dashboard via WebSockets
    await manager.broadcast(
        {
            "type": "NEW_RESERVATION",
            "reservation_id": new_res.id,
            "guest_name": new_res.guest_name,
            "party_size": new_res.party_size,
            "reservation_date": str(new_res.reservation_date),
            "start_time": str(new_res.start_time)
        },
        restaurant_id=new_res.restaurant_id
    )

    return {
        "id": new_res.id,
        "status": new_res.status,
        "guest_name": new_res.guest_name
    }


# ── Public aliases for menu / table / order ──────────────────────────

@router.get("/menu")
async def public_restaurant_menu(db: AsyncSession = Depends(get_db)):
    """Get full restaurant menu (public)."""
    menu = await qr_service.get_public_menu(db)
    return {"categories": menu}


@router.get("/table/{code}")
async def public_table_info(code: str, db: AsyncSession = Depends(get_db)):
    """Get table info by QR code."""
    info = await qr_service.get_table_by_code(db, code)
    if not info:
        raise HTTPException(status_code=404, detail="Invalid or expired QR code")
    return info


@router.post("/order", response_model=qr_schemas.QROrderResponse)
async def public_submit_order(
    data: qr_schemas.QROrderSubmit, db: AsyncSession = Depends(get_db)
):
    """Submit an order from the restaurant app."""
    result = await qr_service.submit_qr_order(
        db, data.table_code, data.guest_name,
        [item.model_dump() for item in data.items], data.notes
    )
    if not result:
        raise HTTPException(status_code=400, detail="Invalid QR code or table")
    return result
