from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ── Vouchers ──
class VoucherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    voucher_type: str
    value: float
    min_order_value: float | None
    max_discount: float | None
    applicable_items_json: dict | None
    max_uses: int | None
    uses_count: int
    valid_from: datetime | None
    valid_until: datetime | None
    is_active: bool
    description: str | None
    created_at: datetime


class VoucherCreate(BaseModel):
    code: str
    voucher_type: str
    value: float
    min_order_value: float | None = None
    max_discount: float | None = None
    applicable_items_json: dict | None = None
    max_uses: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool = True
    description: str | None = None


class VoucherUpdate(BaseModel):
    voucher_type: str | None = None
    value: float | None = None
    min_order_value: float | None = None
    max_discount: float | None = None
    max_uses: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    is_active: bool | None = None
    description: str | None = None


class VoucherValidate(BaseModel):
    code: str
    order_total: float | None = None


class VoucherValidateResponse(BaseModel):
    valid: bool
    message: str
    voucher: VoucherRead | None = None
    discount: float = 0


class VoucherRedeem(BaseModel):
    code: str
    order_id: int | None = None
    guest_id: int | None = None
    order_total: float = 0


class VoucherRedemptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    voucher_id: int
    order_id: int | None
    guest_id: int | None
    discount_applied: float
    redeemed_at: datetime


# ── Gift Cards ──
class GiftCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    initial_balance: float
    current_balance: float
    purchaser_name: str | None
    purchaser_email: str | None
    recipient_name: str | None
    recipient_email: str | None
    message: str | None
    is_active: bool
    expires_at: datetime | None
    created_at: datetime


class GiftCardCreate(BaseModel):
    initial_balance: float
    purchaser_name: str | None = None
    purchaser_email: str | None = None
    recipient_name: str | None = None
    recipient_email: str | None = None
    message: str | None = None
    expires_at: datetime | None = None


class GiftCardCharge(BaseModel):
    amount: float
    order_id: int | None = None


class GiftCardReload(BaseModel):
    amount: float


# ── Customer Cards ──
class CustomerCardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    guest_id: int | None
    card_number: str
    card_type: str
    points_balance: int
    tier: str | None
    stamps_count: int
    stamps_target: int
    total_spent: float
    holder_name: str | None
    is_active: bool
    created_at: datetime


class CustomerCardCreate(BaseModel):
    guest_id: int | None = None
    card_type: str = "points"
    stamps_target: int = 10
    holder_name: str | None = None


class AddPoints(BaseModel):
    points: int
    reason: str | None = None


class RedeemPoints(BaseModel):
    points: int
