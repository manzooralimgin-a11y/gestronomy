from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.vouchers import service, schemas

router = APIRouter()


# ────────────────────── VOUCHERS ──────────────────────

@router.get("", response_model=list[schemas.VoucherRead])
async def list_vouchers(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_vouchers(db, active_only)


@router.post("", response_model=schemas.VoucherRead)
async def create_voucher(
    data: schemas.VoucherCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_voucher(db, data.model_dump(), background_tasks)


@router.put("/{voucher_id}", response_model=schemas.VoucherRead)
async def update_voucher(
    voucher_id: int,
    data: schemas.VoucherUpdate,
    db: AsyncSession = Depends(get_db),
):
    v = await service.update_voucher(db, voucher_id, data.model_dump(exclude_unset=True))
    if not v:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return v


@router.delete("/{voucher_id}")
async def delete_voucher(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
):
    ok = await service.delete_voucher(db, voucher_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return {"ok": True}


@router.post("/validate", response_model=schemas.VoucherValidateResponse)
async def validate_voucher(
    data: schemas.VoucherValidate,
    db: AsyncSession = Depends(get_db),
):
    return await service.validate_voucher(db, data.code)


@router.post("/redeem", response_model=schemas.VoucherRedemptionRead)
async def redeem_voucher(
    data: schemas.VoucherRedeem,
    db: AsyncSession = Depends(get_db),
):
    redemption = await service.redeem_voucher(db, data.code, data.order_id, data.deduction_amount)
    if not redemption:
        raise HTTPException(status_code=400, detail="Voucher is invalid or deduction exceeds balance")
    return redemption


@router.get("/{voucher_id}/redemptions", response_model=list[schemas.VoucherRedemptionRead])
async def list_redemptions(
    voucher_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_redemptions(db, voucher_id)


# ────────────────────── CUSTOMER CARDS ──────────────────────

@router.get("/customer-cards", response_model=list[schemas.CustomerCardRead])
async def list_customer_cards(
    db: AsyncSession = Depends(get_db),
):
    return await service.get_customer_cards(db)


@router.post("/customer-cards", response_model=schemas.CustomerCardRead)
async def create_customer_card(
    data: schemas.CustomerCardCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_customer_card(db, data.model_dump())


@router.post("/customer-cards/{card_number}/add-points", response_model=schemas.CustomerCardRead)
async def add_points_to_card(
    card_number: str,
    data: schemas.AddPoints,
    db: AsyncSession = Depends(get_db),
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
):
    cc = await service.redeem_points(db, card_number, data.points)
    if not cc:
        raise HTTPException(status_code=400, detail="Insufficient points or card inactive")
    return cc


@router.post("/customer-cards/{card_number}/stamp", response_model=schemas.CustomerCardRead)
async def add_stamp_to_card(
    card_number: str,
    db: AsyncSession = Depends(get_db),
):
    cc = await service.add_stamp(db, card_number)
    if not cc:
        raise HTTPException(status_code=400, detail="Card not found or inactive")
    return cc
