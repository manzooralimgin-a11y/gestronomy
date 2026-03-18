"""
Adapter endpoints for the hotel landing page (Next.js static export).

The landing page sends payloads with slightly different field names than the
internal API.  These thin public endpoints accept the landing-page format,
map the fields, persist to DB, and emit real-time events.
"""

from datetime import date, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.reservations.models import Reservation
from app.websockets.connection_manager import manager

router = APIRouter()


# ── Landing: restaurant reservation ────────────────────────────────────
class LandingReservation(BaseModel):
    name: str
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    persons: int
    phone: str = ""
    email: str = ""
    acceptedPolicy: bool = False


@router.post("/reservations/")
async def landing_reservation(payload: LandingReservation, db: AsyncSession = Depends(get_db)):
    """Accept reservation from the landing page and persist."""
    try:
        res_date = date.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
    try:
        h, m = map(int, payload.time.split(":"))
        start_time_obj = time(h, m)
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid time format, expected HH:MM")

    new_res = Reservation(
        restaurant_id=1,
        guest_name=payload.name,
        guest_email=payload.email or None,
        guest_phone=payload.phone or None,
        party_size=payload.persons,
        reservation_date=res_date,
        start_time=start_time_obj,
        special_requests=None,
        status="confirmed",
        source="landing",
    )
    db.add(new_res)
    await db.commit()
    await db.refresh(new_res)

    await manager.broadcast(
        {
            "type": "reservation.created",
            "reservation_id": new_res.id,
            "guest_name": new_res.guest_name,
            "party_size": new_res.party_size,
            "reservation_date": str(new_res.reservation_date),
            "start_time": str(new_res.start_time),
        },
        restaurant_id=1,
    )

    return {"id": new_res.id, "status": "confirmed", "guest_name": new_res.guest_name}


# ── Landing: event bookings ────────────────────────────────────────────
class LandingEventBooking(BaseModel):
    name: str
    email: str
    phone: str = ""
    address: str = ""
    tickets: int = 1
    acceptedPolicy: bool = False
    eventTitle: Optional[str] = None
    eventDate: Optional[str] = None


@router.post("/event-bookings/")
async def landing_event_booking(payload: LandingEventBooking, db: AsyncSession = Depends(get_db)):
    """Accept event-ticket purchase from the landing page.

    Events don't have a dedicated model yet, so we store them as
    reservations with source='event' and the event info in notes.
    """
    today = date.today()

    new_res = Reservation(
        restaurant_id=1,
        guest_name=payload.name,
        guest_email=payload.email or None,
        guest_phone=payload.phone or None,
        party_size=payload.tickets,
        reservation_date=today,
        start_time=time(19, 0),
        special_requests=f"Event: {payload.eventTitle or 'N/A'} | Date: {payload.eventDate or 'N/A'} | Addr: {payload.address}",
        status="confirmed",
        source="event",
    )
    db.add(new_res)
    await db.commit()
    await db.refresh(new_res)

    await manager.broadcast(
        {
            "type": "booking.created",
            "reservation_id": new_res.id,
            "guest_name": new_res.guest_name,
            "tickets": payload.tickets,
            "event": payload.eventTitle,
        },
        restaurant_id=1,
    )

    return {"id": new_res.id, "status": "confirmed", "tickets": payload.tickets}


# ── Landing: tagungen (conference room inquiry) ────────────────────────
class LandingTagung(BaseModel):
    name: str
    email: str
    phone: str = ""
    company: str = ""
    participants: int = 1
    date: str = ""
    message: str = ""
    acceptedPolicy: bool = False


@router.post("/tagungen/")
async def landing_tagung(payload: LandingTagung, db: AsyncSession = Depends(get_db)):
    """Accept conference room inquiry from the landing page."""
    try:
        req_date = date.fromisoformat(payload.date) if payload.date else date.today()
    except ValueError:
        req_date = date.today()

    new_res = Reservation(
        restaurant_id=1,
        guest_name=payload.name,
        guest_email=payload.email or None,
        guest_phone=payload.phone or None,
        party_size=payload.participants,
        reservation_date=req_date,
        start_time=time(9, 0),
        special_requests=f"Tagung | Company: {payload.company} | Message: {payload.message}",
        status="confirmed",
        source="tagung",
    )
    db.add(new_res)
    await db.commit()
    await db.refresh(new_res)

    return {"id": new_res.id, "status": "received", "company": payload.company}
