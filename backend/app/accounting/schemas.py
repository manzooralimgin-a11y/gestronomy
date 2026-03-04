from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ChartOfAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    type: str
    parent_id: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class GLEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    date: date
    debit: float
    credit: float
    description: str
    source_type: str | None = None
    source_id: int | None = None
    created_at: datetime
    updated_at: datetime


class GLEntryCreate(BaseModel):
    account_id: int
    date: date
    debit: float = 0
    credit: float = 0
    description: str
    source_type: str | None = None
    source_id: int | None = None


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int | None = None
    invoice_number: str
    date: date
    due_date: date | None = None
    total: float
    status: str
    ocr_confidence: float | None = None
    raw_image_url: str | None = None
    line_items_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class InvoiceCreate(BaseModel):
    vendor_id: int | None = None
    invoice_number: str
    date: date
    total: float
    line_items_json: dict | None = None


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    period: str
    amount: float
    actual_amount: float
    created_at: datetime
    updated_at: datetime


class BudgetCreate(BaseModel):
    account_id: int
    period: str
    amount: float


class ReconciliationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bank_transaction_id: str
    gl_entry_id: int | None = None
    status: str
    matched_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
