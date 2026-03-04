from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Voucher(Base):
    __tablename__ = "vouchers"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    voucher_type: Mapped[str] = mapped_column(String(50), nullable=False)  # percentage_off, fixed_amount, free_item, bogo
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    min_order_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    max_discount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    applicable_items_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"item_ids": [...]} or null for all
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uses_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class VoucherRedemption(Base):
    __tablename__ = "voucher_redemptions"

    voucher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("table_orders.id", ondelete="SET NULL"), nullable=True
    )
    guest_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("guest_profiles.id", ondelete="SET NULL"), nullable=True
    )
    discount_applied: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class GiftCard(Base):
    __tablename__ = "gift_cards"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    initial_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    current_balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    purchaser_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchaser_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CustomerCard(Base):
    __tablename__ = "customer_cards"

    guest_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("guest_profiles.id", ondelete="SET NULL"), nullable=True
    )
    card_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    card_type: Mapped[str] = mapped_column(String(50), nullable=False)  # points, stamps, tier
    points_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tier: Mapped[str | None] = mapped_column(String(50), nullable=True)  # bronze, silver, gold, platinum
    stamps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stamps_target: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    total_spent: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    holder_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
