import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.vouchers.models import Voucher, VoucherRedemption, GiftCard, CustomerCard


# ────────────────────── VOUCHERS ──────────────────────

async def get_vouchers(db: AsyncSession, active_only: bool = False) -> list[Voucher]:
    q = select(Voucher).order_by(Voucher.created_at.desc())
    if active_only:
        q = q.where(Voucher.is_active == True)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_voucher(db: AsyncSession, voucher_id: int) -> Voucher | None:
    result = await db.execute(select(Voucher).where(Voucher.id == voucher_id))
    return result.scalar_one_or_none()


async def create_voucher(db: AsyncSession, data: dict) -> Voucher:
    v = Voucher(**data)
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


async def update_voucher(db: AsyncSession, voucher_id: int, data: dict) -> Voucher | None:
    v = await get_voucher(db, voucher_id)
    if not v:
        return None
    for k, val in data.items():
        if val is not None:
            setattr(v, k, val)
    await db.commit()
    await db.refresh(v)
    return v


async def delete_voucher(db: AsyncSession, voucher_id: int) -> bool:
    v = await get_voucher(db, voucher_id)
    if not v:
        return False
    await db.delete(v)
    await db.commit()
    return True


async def validate_voucher(db: AsyncSession, code: str, order_total: float | None = None):
    """Validate a voucher code and return discount info."""
    result = await db.execute(select(Voucher).where(Voucher.code == code))
    v = result.scalar_one_or_none()

    if not v:
        return {"valid": False, "message": "Voucher not found", "voucher": None, "discount": 0}
    if not v.is_active:
        return {"valid": False, "message": "Voucher is inactive", "voucher": v, "discount": 0}
    if v.max_uses and v.uses_count >= v.max_uses:
        return {"valid": False, "message": "Voucher has been fully redeemed", "voucher": v, "discount": 0}

    now = datetime.now(timezone.utc)
    if v.valid_from and now < v.valid_from:
        return {"valid": False, "message": "Voucher is not yet active", "voucher": v, "discount": 0}
    if v.valid_until and now > v.valid_until:
        return {"valid": False, "message": "Voucher has expired", "voucher": v, "discount": 0}

    if v.min_order_value and order_total and order_total < float(v.min_order_value):
        return {"valid": False, "message": f"Minimum order value is €{v.min_order_value}", "voucher": v, "discount": 0}

    # Calculate discount
    discount = 0.0
    if order_total:
        if v.voucher_type == "percentage_off":
            discount = order_total * (float(v.value) / 100)
        elif v.voucher_type == "fixed_amount":
            discount = float(v.value)
        elif v.voucher_type == "free_item":
            discount = float(v.value)
        elif v.voucher_type == "bogo":
            discount = order_total * 0.5  # simplified: 50% off

        if v.max_discount:
            discount = min(discount, float(v.max_discount))

    return {"valid": True, "message": "Voucher is valid", "voucher": v, "discount": round(discount, 2)}


async def redeem_voucher(db: AsyncSession, code: str, order_id: int | None, guest_id: int | None, order_total: float):
    """Redeem a voucher — creates redemption record and increments uses."""
    validation = await validate_voucher(db, code, order_total)
    if not validation["valid"]:
        return None

    v = validation["voucher"]
    discount = validation["discount"]

    redemption = VoucherRedemption(
        voucher_id=v.id,
        order_id=order_id,
        guest_id=guest_id,
        discount_applied=discount,
        redeemed_at=datetime.now(timezone.utc),
    )
    db.add(redemption)

    v.uses_count += 1
    await db.commit()
    await db.refresh(redemption)
    return redemption


async def get_redemptions(db: AsyncSession, voucher_id: int) -> list[VoucherRedemption]:
    result = await db.execute(
        select(VoucherRedemption).where(VoucherRedemption.voucher_id == voucher_id).order_by(VoucherRedemption.redeemed_at.desc())
    )
    return list(result.scalars().all())


# ────────────────────── GIFT CARDS ──────────────────────

async def get_gift_cards(db: AsyncSession) -> list[GiftCard]:
    result = await db.execute(select(GiftCard).order_by(GiftCard.created_at.desc()))
    return list(result.scalars().all())


async def create_gift_card(db: AsyncSession, data: dict) -> GiftCard:
    code = f"GC-{secrets.token_hex(6).upper()}"
    gc = GiftCard(code=code, current_balance=data["initial_balance"], **data)
    db.add(gc)
    await db.commit()
    await db.refresh(gc)
    return gc


async def get_gift_card_by_code(db: AsyncSession, code: str) -> GiftCard | None:
    result = await db.execute(select(GiftCard).where(GiftCard.code == code))
    return result.scalar_one_or_none()


async def charge_gift_card(db: AsyncSession, code: str, amount: float) -> GiftCard | None:
    """Charge (deduct) from a gift card."""
    gc = await get_gift_card_by_code(db, code)
    if not gc or not gc.is_active:
        return None
    if gc.expires_at and datetime.now(timezone.utc) > gc.expires_at:
        return None
    if float(gc.current_balance) < amount:
        return None

    gc.current_balance = float(gc.current_balance) - amount
    await db.commit()
    await db.refresh(gc)
    return gc


async def reload_gift_card(db: AsyncSession, code: str, amount: float) -> GiftCard | None:
    """Add balance to a gift card."""
    gc = await get_gift_card_by_code(db, code)
    if not gc:
        return None
    gc.current_balance = float(gc.current_balance) + amount
    gc.is_active = True
    await db.commit()
    await db.refresh(gc)
    return gc


# ────────────────────── CUSTOMER CARDS ──────────────────────

async def get_customer_cards(db: AsyncSession) -> list[CustomerCard]:
    result = await db.execute(select(CustomerCard).order_by(CustomerCard.created_at.desc()))
    return list(result.scalars().all())


async def create_customer_card(db: AsyncSession, data: dict) -> CustomerCard:
    card_number = f"CC-{secrets.token_hex(6).upper()}"
    cc = CustomerCard(card_number=card_number, **data)
    db.add(cc)
    await db.commit()
    await db.refresh(cc)
    return cc


async def get_card_by_number(db: AsyncSession, card_number: str) -> CustomerCard | None:
    result = await db.execute(select(CustomerCard).where(CustomerCard.card_number == card_number))
    return result.scalar_one_or_none()


async def add_points(db: AsyncSession, card_number: str, points: int) -> CustomerCard | None:
    cc = await get_card_by_number(db, card_number)
    if not cc or not cc.is_active:
        return None
    cc.points_balance += points
    # Auto-tier upgrade
    if cc.card_type == "points":
        if cc.points_balance >= 5000:
            cc.tier = "platinum"
        elif cc.points_balance >= 2000:
            cc.tier = "gold"
        elif cc.points_balance >= 500:
            cc.tier = "silver"
        else:
            cc.tier = "bronze"
    await db.commit()
    await db.refresh(cc)
    return cc


async def redeem_points(db: AsyncSession, card_number: str, points: int) -> CustomerCard | None:
    cc = await get_card_by_number(db, card_number)
    if not cc or not cc.is_active:
        return None
    if cc.points_balance < points:
        return None
    cc.points_balance -= points
    await db.commit()
    await db.refresh(cc)
    return cc


async def add_stamp(db: AsyncSession, card_number: str) -> CustomerCard | None:
    cc = await get_card_by_number(db, card_number)
    if not cc or not cc.is_active:
        return None
    cc.stamps_count += 1
    if cc.stamps_count >= cc.stamps_target:
        cc.stamps_count = 0  # Reset after completing card
    await db.commit()
    await db.refresh(cc)
    return cc
