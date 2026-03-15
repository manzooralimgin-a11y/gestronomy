from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reliability_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    avg_delivery_days: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    pricing_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Supplier interface fields (F7)
    delivery_days_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    minimum_order_value: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    catalog_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    current_stock: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    par_level: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    cost_per_unit: Mapped[float] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    vendor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_counted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    vendor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    auto_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    line_items_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Supplier interface fields (F7)
    expected_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    received_items_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)


class TVAReport(Base):
    __tablename__ = "tva_reports"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id"), nullable=False
    )
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    theoretical_usage: Mapped[float] = mapped_column(Float, nullable=False)
    actual_usage: Mapped[float] = mapped_column(Float, nullable=False)
    variance: Mapped[float] = mapped_column(Float, nullable=False)
    variance_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)


class SupplierCatalogItem(Base):
    __tablename__ = "supplier_catalog_items"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    inventory_item_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True
    )
    supplier_sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    min_order_qty: Mapped[float] = mapped_column(Float, default=1, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AutoPurchaseRule(Base):
    __tablename__ = "auto_purchase_rules"

    restaurant_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("restaurants.id", ondelete="SET NULL"), nullable=True
    )
    inventory_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False
    )
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    trigger_type: Mapped[str] = mapped_column(String(30), default="below_par", nullable=False)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
