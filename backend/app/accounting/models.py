from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ChartOfAccount(Base):
    __tablename__ = "chart_of_accounts"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class GLEntry(Base):
    __tablename__ = "gl_entries"

    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    debit: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    credit: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"

    vendor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True
    )
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    line_items_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Budget(Base):
    __tablename__ = "budgets"

    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chart_of_accounts.id"), nullable=False
    )
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    actual_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)


class Reconciliation(Base):
    __tablename__ = "reconciliations"

    bank_transaction_id: Mapped[str] = mapped_column(String(255), nullable=False)
    gl_entry_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("gl_entries.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="unmatched", nullable=False)
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
