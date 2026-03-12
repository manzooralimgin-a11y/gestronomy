import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import BackgroundTasks
from app.vouchers.models import Voucher, VoucherRedemption, CustomerCard
from app.vouchers.qr_service import generate_qr_base64
from app.vouchers import email_service

# ────────────────────── VOUCHERS ──────────────────────

async def get_vouchers(db: AsyncSession, active_only: bool = False) -> list[Voucher]:
    q = select(Voucher).order_by(Voucher.created_at.desc())
    if active_only:
        q = q.where(Voucher.status == "active")
    result = await db.execute(q)
    vouchers = list(result.scalars().all())
    for v in vouchers:
        v.qr_code_base64 = generate_qr_base64(v.code)
    return vouchers


async def get_voucher(db: AsyncSession, voucher_id: int) -> Voucher | None:
    result = await db.execute(select(Voucher).where(Voucher.id == voucher_id))
    return result.scalar_one_or_none()


async def create_voucher(db: AsyncSession, data: dict, background_tasks: BackgroundTasks) -> Voucher:
    code = f"GV-{secrets.token_hex(4).upper()}"
    data["amount_remaining"] = data["amount_total"]
    
    v = Voucher(code=code, **data)
    db.add(v)
    await db.commit()
    await db.refresh(v)
    v.qr_code_base64 = generate_qr_base64(v.code)
    
    if v.customer_email:
        background_tasks.add_task(
            email_service.send_voucher_email,
            voucher_id=v.id,
            code=v.code,
            amount=v.amount_total,
            email=v.customer_email,
            name=v.customer_name
        )
        
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


async def validate_voucher(db: AsyncSession, code: str):
    """Validate a voucher code against POS system rules."""
    result = await db.execute(select(Voucher).where(Voucher.code == code))
    v = result.scalar_one_or_none()

    if not v:
        return {"valid": False, "message": "Voucher not found", "voucher": None}
    
    if v.status != "active":
        return {"valid": False, "message": f"Voucher is marked as {v.status}", "voucher": v}
        
    if v.amount_remaining <= 0:
        return {"valid": False, "message": "Voucher balance is completely depleted", "voucher": v}

    if v.expiry_date:
        now = datetime.now(timezone.utc)
        if now > v.expiry_date:
            return {"valid": False, "message": "Voucher has expired", "voucher": v}

    v.qr_code_base64 = generate_qr_base64(v.code)
    return {"valid": True, "message": "Voucher is valid", "voucher": v}


async def redeem_voucher(db: AsyncSession, code: str, order_id: int | None, deduction_amount: float):
    """Redeem a voucher securely. Deducts the amount and updates status if emptied."""
    validation = await validate_voucher(db, code)
    if not validation["valid"]:
        return None

    v = validation["voucher"]
    
    if float(v.amount_remaining) < deduction_amount:
        return None
        
    v.amount_remaining = float(v.amount_remaining) - deduction_amount
    
    if float(v.amount_remaining) <= 0:
        v.status = "used"

    redemption = VoucherRedemption(
        voucher_id=v.id,
        order_id=order_id,
        discount_applied=deduction_amount,
        redeemed_at=datetime.now(timezone.utc),
    )
    db.add(redemption)

    await db.commit()
    await db.refresh(redemption)
    return redemption


async def get_redemptions(db: AsyncSession, voucher_id: int) -> list[VoucherRedemption]:
    result = await db.execute(
        select(VoucherRedemption).where(VoucherRedemption.voucher_id == voucher_id).order_by(VoucherRedemption.redeemed_at.desc())
    )
    return list(result.scalars().all())


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
