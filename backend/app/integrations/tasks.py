import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, update
import logging

from app.shared.celery_app import celery
from app.database import async_session
from app.integrations.models import WebhookEvent, WebhookAudit
from app.reservations.models import Reservation

logger = logging.getLogger(__name__)

async def process_voicebooker_event_async(event_id: str):
    async with async_session() as db:
        # 1. Fetch event
        stmt = select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        if not event:
            logger.error(f"Event {event_id} not found")
            return

        if event.processing_status == "processed":
            logger.info(f"Event {event_id} already processed, skipping.")
            return

        payload = event.raw_payload
        # payload_dict here is {"event_id": "...", "event_type": "...", "timestamp": "...", "payload": {...}}
        event_type = payload.get("event_type")
        event_payload = payload.get("payload", {})

        try:
            if event_type == "booking.created":
                dt = datetime.fromisoformat(event_payload.get("datetime", "").replace("Z", "+00:00"))
                customer = event_payload.get("customer", {})
                
                reservation = Reservation(
                    restaurant_id=1,  # Default to 1
                    guest_name=customer.get("name", "Unknown VoiceBooker Guest"),
                    guest_phone=customer.get("phone"),
                    party_size=event_payload.get("party_size", 2),
                    reservation_date=dt.date(),
                    start_time=dt.time(),
                    source="voicebooker",
                    notes=f"VoiceBooker Ref: {event_payload.get('booking_id')} | " + event_payload.get("notes", ""),
                    status="confirmed"
                )
                db.add(reservation)
                await db.flush()
                
                audit = WebhookAudit(
                    event_id=event_id,
                    action="create_reservation",
                    actor="system",
                    message=f"Created reservation {reservation.id} for {reservation.guest_name}"
                )
                db.add(audit)
                
            elif event_type == "booking.cancelled":
                booking_ref = event_payload.get("booking_id")
                if booking_ref:
                    # Cancel any booking containing the ref in notes
                    booking_search = f"%VoiceBooker Ref: {booking_ref}%"
                    stmt = select(Reservation).where(Reservation.notes.like(booking_search))
                    reservations = (await db.execute(stmt)).scalars().all()
                    
                    for r in reservations:
                        r.status = "cancelled"
                        
                    audit = WebhookAudit(
                        event_id=event_id,
                        action="cancel_reservation",
                        actor="system",
                        message=f"Cancelled {len(reservations)} reservation(s) matching ref {booking_ref}"
                    )
                    db.add(audit)
                
            event.processing_status = "processed"
            event.processed_at = datetime.now(timezone.utc)
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error processing webhook {event_id}")
            async with async_session() as error_db:
                await error_db.execute(
                    update(WebhookEvent).where(WebhookEvent.event_id == event_id).values(
                        processing_status="error",
                        error=str(e)
                    )
                )
                await error_db.commit()

@celery.task(name="integrations.process_voicebooker_event")
def process_voicebooker_event(event_id: str):
    """Celery task to process a voicebooker event idempotently."""
    asyncio.run(process_voicebooker_event_async(event_id))
