from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ── Menu Category ──

class MenuCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MenuCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int = 0
    is_active: bool = True


class MenuCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


# ── Menu Item ──

class MenuItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    description: str | None = None
    price: float
    cost: float
    image_url: str | None = None
    is_available: bool
    is_featured: bool
    prep_time_min: int
    allergens_json: dict | None = None
    dietary_tags_json: dict | None = None
    nutrition_json: dict | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime


class MenuItemCreate(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    price: float
    cost: float = 0
    image_url: str | None = None
    is_available: bool = True
    is_featured: bool = False
    prep_time_min: int = 15
    allergens_json: dict | None = None
    dietary_tags_json: dict | None = None
    nutrition_json: dict | None = None
    sort_order: int = 0


class MenuItemUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = None
    cost: float | None = None
    image_url: str | None = None
    is_available: bool | None = None
    is_featured: bool | None = None
    prep_time_min: int | None = None
    allergens_json: dict | None = None
    dietary_tags_json: dict | None = None
    nutrition_json: dict | None = None
    sort_order: int | None = None


# ── Menu Modifier ──

class MenuModifierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    group_name: str
    price_adjustment: float
    is_default: bool
    created_at: datetime
    updated_at: datetime


class MenuModifierCreate(BaseModel):
    name: str
    group_name: str
    price_adjustment: float = 0
    is_default: bool = False


class MenuModifierUpdate(BaseModel):
    name: str | None = None
    group_name: str | None = None
    price_adjustment: float | None = None
    is_default: bool | None = None


# ── Menu Item Modifier (link) ──

class MenuItemModifierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    modifier_id: int
    created_at: datetime
    updated_at: datetime


class MenuItemModifierCreate(BaseModel):
    item_id: int
    modifier_id: int


# ── Menu Combo ──

class MenuComboRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    combo_price: float
    items_json: dict
    savings_amount: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MenuComboCreate(BaseModel):
    name: str
    description: str | None = None
    combo_price: float
    items_json: dict
    savings_amount: float = 0
    is_active: bool = True


class MenuComboUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    combo_price: float | None = None
    items_json: dict | None = None
    savings_amount: float | None = None
    is_active: bool | None = None


# ── Upsell Rule (F9) ──

class UpsellRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trigger_item_id: int
    suggested_item_id: int
    rule_type: str
    message: str | None = None
    priority: int
    is_active: bool
    times_shown: int
    times_accepted: int
    created_at: datetime
    updated_at: datetime


class UpsellRuleCreate(BaseModel):
    trigger_item_id: int
    suggested_item_id: int
    rule_type: str = "frequently_bought_together"
    message: str | None = None
    priority: int = 0
    is_active: bool = True


class UpsellRuleUpdate(BaseModel):
    rule_type: str | None = None
    message: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class UpsellSuggestion(BaseModel):
    rule_id: int
    suggested_item: MenuItemRead
    rule_type: str
    message: str | None = None


# ── Analytics ──

class MenuAnalytics(BaseModel):
    total_items: int
    active_items: int
    categories_count: int
    avg_food_cost_pct: float
    featured_count: int
    combos_count: int
