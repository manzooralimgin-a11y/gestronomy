from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class VendorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    reliability_score: float
    avg_delivery_days: float
    pricing_json: dict | None = None
    is_active: bool
    delivery_days_json: dict | None = None
    minimum_order_value: float = 0
    catalog_url: str | None = None
    payment_terms: str | None = None
    lead_time_days: int = 1
    created_at: datetime
    updated_at: datetime


class VendorCreate(BaseModel):
    name: str
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    delivery_days_json: dict | None = None
    minimum_order_value: float = 0
    catalog_url: str | None = None
    payment_terms: str | None = None
    lead_time_days: int = 1


class VendorUpdate(BaseModel):
    name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    delivery_days_json: dict | None = None
    minimum_order_value: float | None = None
    catalog_url: str | None = None
    payment_terms: str | None = None
    lead_time_days: int | None = None
    is_active: bool | None = None


class InventoryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    unit: str
    current_stock: float
    par_level: float
    cost_per_unit: float
    vendor_id: int | None = None
    location: str | None = None
    last_counted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class InventoryItemCreate(BaseModel):
    name: str
    category: str
    unit: str
    current_stock: float = 0
    par_level: float = 0
    cost_per_unit: float = 0
    vendor_id: int | None = None
    location: str | None = None


class InventoryItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    current_stock: float | None = None
    par_level: float | None = None
    cost_per_unit: float | None = None
    vendor_id: int | None = None
    location: str | None = None


class PurchaseOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int | None = None
    status: str
    total: float
    order_date: date
    delivery_date: date | None = None
    auto_generated: bool
    line_items_json: dict | None = None
    expected_delivery_date: date | None = None
    actual_delivery_date: date | None = None
    delivery_status: str = "pending"
    received_items_json: dict | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class PurchaseOrderCreate(BaseModel):
    vendor_id: int | None = None
    order_date: date
    delivery_date: date | None = None
    total: float = 0
    line_items_json: dict | None = None
    expected_delivery_date: date | None = None
    notes: str | None = None


class PurchaseOrderUpdate(BaseModel):
    status: str | None = None
    delivery_date: date | None = None
    expected_delivery_date: date | None = None
    notes: str | None = None


class GoodsReceiptCreate(BaseModel):
    received_items_json: dict
    actual_delivery_date: date | None = None
    notes: str | None = None


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    quantity: float
    movement_type: str
    reason: str | None = None
    created_at: datetime
    updated_at: datetime


class TVAReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    period: str
    theoretical_usage: float
    actual_usage: float
    variance: float
    variance_cost: float
    created_at: datetime
    updated_at: datetime


# ── Supplier Catalog (F7) ──

class SupplierCatalogItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    inventory_item_id: int | None = None
    supplier_sku: str | None = None
    supplier_name: str
    unit_price: float
    unit: str
    min_order_qty: float
    is_available: bool
    created_at: datetime
    updated_at: datetime


class SupplierCatalogItemCreate(BaseModel):
    inventory_item_id: int | None = None
    supplier_sku: str | None = None
    supplier_name: str
    unit_price: float
    unit: str
    min_order_qty: float = 1
    is_available: bool = True


class AutoPurchaseRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_item_id: int
    vendor_id: int
    trigger_type: str
    reorder_point: float
    reorder_quantity: float
    is_active: bool
    last_triggered_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AutoPurchaseRuleCreate(BaseModel):
    inventory_item_id: int
    vendor_id: int
    trigger_type: str = "below_par"
    reorder_point: float
    reorder_quantity: float
    is_active: bool = True


class AutoPurchaseRuleUpdate(BaseModel):
    trigger_type: str | None = None
    reorder_point: float | None = None
    reorder_quantity: float | None = None
    is_active: bool | None = None


class PriceComparison(BaseModel):
    inventory_item_id: int
    item_name: str
    vendors: list[dict]
