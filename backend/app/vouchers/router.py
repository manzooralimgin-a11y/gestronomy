from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.vouchers import service, schemas

router = APIRouter()


# ────────────────────── VOUCHERS ──────────────────────

@router.get("", response_model=list[schemas.VoucherRead])
async def list_vouchers(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.get_vouchers(db, active_only)


@router.post("", response_model=schemas.VoucherRead)
async def create_voucher(
    data: schemas.VoucherCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.create_voucher(db, data.model_dump())


@router.put("/{voucher_id}", response_model=schemas.VoucherRead)
async def update_voucher(
    voucher_id: int,
    data: schemas.VoucherUpdate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    v = await service.update_voucher(db, voucher_id, data.model_dump(exclude_unset=True))
    if not v:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return v


@router.delete("/{voucher_id}")
async def delete_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    ok = await service.delete_voucher(db, voucher_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return {"ok": True}


@router.post("/validate", response_model=schemas.VoucherValidateResponse)
async def validate_voucher(
    data: schemas.VoucherValidate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.validate_voucher(db, data.code, data.order_total)


@router.post("/redeem", response_model=schemas.VoucherRedemptionRead)
async def redeem_voucher(
    data: schemas.VoucherRedeem,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    redemption = await service.redeem_voucher(db, data.code, data.order_id, data.guest_id, data.order_total)
    if not redemption:
        raise HTTPException(status_code=400, detail="Voucher is invalid or cannot be redeemed")
    return redemption


@router.get("/{voucher_id}/redemptions", response_model=list[schemas.VoucherRedemptionRead])
async def list_redemptions(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.get_redemptions(db, voucher_id)


# ────────────────────── GIFT CARDS ──────────────────────

@router.get("/gift-cards", response_model=list[schemas.GiftCardRead])
async def list_gift_cards(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.get_gift_cards(db)


@router.post("/gift-cards", response_model=schemas.GiftCardRead)
async def create_gift_card(
    data: schemas.GiftCardCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.create_gift_card(db, data.model_dump())


@router.get("/gift-cards/{code}/balance")
async def get_gift_card_balance(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — check gift card balance."""
    gc = await service.get_gift_card_by_code(db, code)
    if not gc:
        raise HTTPException(status_code=404, detail="Gift card not found")
    return {"code": gc.code, "current_balance": float(gc.current_balance), "is_active": gc.is_active}


@router.post("/gift-cards/{code}/charge", response_model=schemas.GiftCardRead)
async def charge_gift_card(
    code: str,
    data: schemas.GiftCardCharge,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    gc = await service.charge_gift_card(db, code, data.amount)
    if not gc:
        raise HTTPException(status_code=400, detail="Cannot charge: insufficient balance or card inactive")
    return gc


@router.post("/gift-cards/{code}/reload", response_model=schemas.GiftCardRead)
async def reload_gift_card(
    code: str,
    data: schemas.GiftCardReload,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    gc = await service.reload_gift_card(db, code, data.amount)
    if not gc:
        raise HTTPException(status_code=404, detail="Gift card not found")
    return gc


# ────────────────────── CUSTOMER CARDS ──────────────────────

@router.get("/customer-cards", response_model=list[schemas.CustomerCardRead])
async def list_customer_cards(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.get_customer_cards(db)


@router.post("/customer-cards", response_model=schemas.CustomerCardRead)
async def create_customer_card(
    data: schemas.CustomerCardCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await service.create_customer_card(db, data.model_dump())


@router.post("/customer-cards/{card_number}/add-points", response_model=schemas.CustomerCardRead)
async def add_points_to_card(
    card_number: str,
    data: schemas.AddPoints,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cc = await service.add_points(db, card_number, data.points)
    if not cc:
        raise HTTPException(status_code=400, detail="Card not found or inactive")
    return cc


@router.post("/customer-cards/{card_number}/redeem-points", response_model=schemas.CustomerCardRead)
async def redeem_points_from_card(
    card_number: str,
    data: schemas.RedeemPoints,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cc = await service.redeem_points(db, card_number, data.points)
    if not cc:
        raise HTTPException(status_code=400, detail="Insufficient points or card inactive")
    return cc


@router.post("/customer-cards/{card_number}/stamp", response_model=schemas.CustomerCardRead)
async def add_stamp_to_card(
    card_number: str,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    cc = await service.add_stamp(db, card_number)
    if not cc:
        raise HTTPException(status_code=400, detail="Card not found or inactive")
    return cc
