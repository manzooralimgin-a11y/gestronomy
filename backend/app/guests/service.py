from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.guests.models import GuestProfile, LoyaltyAccount, Order, Promotion
from app.guests.schemas import GuestCreate, OrderCreate, PromotionCreate


async def get_guests(db: AsyncSession, restaurant_id: int, limit: int = 100) -> list[GuestProfile]:
    result = await db.execute(
        select(GuestProfile)
        .where(GuestProfile.restaurant_id == restaurant_id)
        .order_by(GuestProfile.last_visit.desc().nullslast())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_guest_by_id(db: AsyncSession, restaurant_id: int, guest_id: int) -> GuestProfile:
    result = await db.execute(
        select(GuestProfile).where(
            GuestProfile.id == guest_id,
            GuestProfile.restaurant_id == restaurant_id,
        )
    )
    guest = result.scalar_one_or_none()
    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found"
        )
    return guest


async def create_guest(db: AsyncSession, restaurant_id: int, payload: GuestCreate) -> GuestProfile:
    guest = GuestProfile(**payload.model_dump(), restaurant_id=restaurant_id)
    db.add(guest)
    await db.flush()
    await db.refresh(guest)
    return guest


async def get_orders(
    db: AsyncSession, restaurant_id: int, guest_id: int | None = None, limit: int = 100
) -> list[Order]:
    query = (
        select(Order)
        .where(Order.restaurant_id == restaurant_id)
        .order_by(Order.order_date.desc())
        .limit(limit)
    )
    if guest_id:
        await get_guest_by_id(db, restaurant_id, guest_id)
        query = query.where(Order.guest_id == guest_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_order(db: AsyncSession, restaurant_id: int, payload: OrderCreate) -> Order:
    if payload.guest_id is not None:
        await get_guest_by_id(db, restaurant_id, payload.guest_id)
    order = Order(**payload.model_dump(), restaurant_id=restaurant_id)
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order


async def get_churn_risk_guests(
    db: AsyncSession, restaurant_id: int, threshold: float = 0.5
) -> list[GuestProfile]:
    result = await db.execute(
        select(GuestProfile)
        .where(
            GuestProfile.restaurant_id == restaurant_id,
            GuestProfile.churn_risk_score >= threshold,
        )
        .order_by(GuestProfile.churn_risk_score.desc())
    )
    return list(result.scalars().all())


async def get_loyalty_overview(db: AsyncSession, restaurant_id: int) -> dict:
    total = await db.execute(
        select(func.count(LoyaltyAccount.id)).where(LoyaltyAccount.restaurant_id == restaurant_id)
    )
    tier_counts = await db.execute(
        select(LoyaltyAccount.tier, func.count(LoyaltyAccount.id))
        .where(LoyaltyAccount.restaurant_id == restaurant_id)
        .group_by(LoyaltyAccount.tier)
    )
    total_points = await db.execute(
        select(func.sum(LoyaltyAccount.points)).where(
            LoyaltyAccount.restaurant_id == restaurant_id
        )
    )

    tiers = {row[0]: row[1] for row in tier_counts.all()}

    return {
        "total_members": total.scalar() or 0,
        "total_points": total_points.scalar() or 0,
        "tiers": tiers,
    }


async def send_promotion(db: AsyncSession, restaurant_id: int, payload: PromotionCreate) -> Promotion:
    if payload.guest_id is not None:
        await get_guest_by_id(db, restaurant_id, payload.guest_id)
    promotion = Promotion(
        **payload.model_dump(),
        restaurant_id=restaurant_id,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(promotion)
    await db.flush()
    await db.refresh(promotion)
    return promotion
