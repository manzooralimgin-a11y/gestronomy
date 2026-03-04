from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ── QR Table Code ──
class QRTableCodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    table_id: int
    code: str
    is_active: bool
    scan_count: int
    last_scanned_at: datetime | None
    created_at: datetime


class QRTableCodeCreate(BaseModel):
    table_id: int


# ── Public Table Info ──
class TableInfo(BaseModel):
    table_number: str
    section_name: str
    capacity: int


# ── Public Menu (simplified) ──
class PublicMenuItem(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    category_id: int
    category_name: str
    image_url: str | None
    is_available: bool
    prep_time_min: int
    allergens: list[str]
    dietary_tags: list[str]


class PublicMenuCategory(BaseModel):
    id: int
    name: str
    items: list[PublicMenuItem]


# ── Order Submission ──
class QROrderItem(BaseModel):
    menu_item_id: int
    quantity: int = 1
    notes: str | None = None


class QROrderSubmit(BaseModel):
    table_code: str
    guest_name: str = "QR Guest"
    items: list[QROrderItem]
    notes: str | None = None


class QROrderResponse(BaseModel):
    order_id: int
    table_number: str
    status: str
    items_count: int
    total: float
    message: str


class QROrderStatus(BaseModel):
    order_id: int
    status: str
    items: list[dict]
