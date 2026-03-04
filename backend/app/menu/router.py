from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.database import get_db
from app.dependencies import get_current_tenant_user
from app.menu.schemas import (
    MenuAnalytics,
    MenuCategoryCreate,
    MenuCategoryRead,
    MenuCategoryUpdate,
    MenuComboCreate,
    MenuComboRead,
    MenuComboUpdate,
    MenuItemCreate,
    MenuItemModifierCreate,
    MenuItemModifierRead,
    MenuItemRead,
    MenuItemUpdate,
    MenuModifierCreate,
    MenuModifierRead,
    MenuModifierUpdate,
    UpsellRuleCreate,
    UpsellRuleRead,
    UpsellRuleUpdate,
)
from app.menu.service import (
    create_category,
    create_combo,
    create_item,
    create_modifier,
    create_upsell_rule,
    delete_category,
    delete_combo,
    delete_item,
    delete_modifier,
    delete_upsell_rule,
    get_categories,
    get_combos,
    get_item_by_id,
    get_item_modifiers,
    get_item_suggestions,
    get_items,
    get_menu_analytics,
    get_modifiers,
    get_upsell_rules,
    link_item_modifier,
    record_upsell_accepted,
    unlink_item_modifier,
    update_category,
    update_combo,
    update_item,
    update_modifier,
    update_upsell_rule,
)

router = APIRouter()


@router.get("/categories", response_model=list[MenuCategoryRead])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_categories(db, current_user.restaurant_id)


@router.post("/categories", response_model=MenuCategoryRead, status_code=201)
async def add_category(
    payload: MenuCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_category(db, current_user.restaurant_id, payload)


@router.put("/categories/{category_id}", response_model=MenuCategoryRead)
async def edit_category(
    category_id: int,
    payload: MenuCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_category(db, current_user.restaurant_id, category_id, payload)


@router.delete("/categories/{category_id}", status_code=204)
async def remove_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_category(db, current_user.restaurant_id, category_id)


@router.get("/items", response_model=list[MenuItemRead])
async def list_items(
    category_id: int | None = None,
    dietary: str | None = None,
    search: str | None = None,
    available: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_items(
        db,
        current_user.restaurant_id,
        category_id,
        dietary,
        search,
        available,
    )


@router.post("/items", response_model=MenuItemRead, status_code=201)
async def add_item(
    payload: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_item(db, current_user.restaurant_id, payload)


@router.get("/items/{item_id}", response_model=MenuItemRead)
async def item_detail(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_item_by_id(db, current_user.restaurant_id, item_id)


@router.put("/items/{item_id}", response_model=MenuItemRead)
async def edit_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_item(db, current_user.restaurant_id, item_id, payload)


@router.delete("/items/{item_id}", status_code=204)
async def remove_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_item(db, current_user.restaurant_id, item_id)


@router.get("/items/{item_id}/suggestions")
async def item_suggestions(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_item_suggestions(db, current_user.restaurant_id, item_id)


@router.get("/items/{item_id}/modifiers", response_model=list[MenuModifierRead])
async def list_item_modifiers(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_item_modifiers(db, current_user.restaurant_id, item_id)


@router.post("/items/{item_id}/modifiers", response_model=MenuItemModifierRead, status_code=201)
async def add_item_modifier(
    item_id: int,
    payload: MenuItemModifierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    payload.item_id = item_id
    return await link_item_modifier(db, current_user.restaurant_id, payload)


@router.delete("/item-modifiers/{link_id}", status_code=204)
async def remove_item_modifier(
    link_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await unlink_item_modifier(db, current_user.restaurant_id, link_id)


@router.get("/modifiers", response_model=list[MenuModifierRead])
async def list_modifiers(
    group_name: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_modifiers(db, current_user.restaurant_id, group_name)


@router.post("/modifiers", response_model=MenuModifierRead, status_code=201)
async def add_modifier(
    payload: MenuModifierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_modifier(db, current_user.restaurant_id, payload)


@router.put("/modifiers/{modifier_id}", response_model=MenuModifierRead)
async def edit_modifier(
    modifier_id: int,
    payload: MenuModifierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_modifier(db, current_user.restaurant_id, modifier_id, payload)


@router.delete("/modifiers/{modifier_id}", status_code=204)
async def remove_modifier(
    modifier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_modifier(db, current_user.restaurant_id, modifier_id)


@router.get("/combos", response_model=list[MenuComboRead])
async def list_combos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_combos(db, current_user.restaurant_id)


@router.post("/combos", response_model=MenuComboRead, status_code=201)
async def add_combo(
    payload: MenuComboCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_combo(db, current_user.restaurant_id, payload)


@router.put("/combos/{combo_id}", response_model=MenuComboRead)
async def edit_combo(
    combo_id: int,
    payload: MenuComboUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_combo(db, current_user.restaurant_id, combo_id, payload)


@router.delete("/combos/{combo_id}", status_code=204)
async def remove_combo(
    combo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_combo(db, current_user.restaurant_id, combo_id)


@router.get("/upsell-rules", response_model=list[UpsellRuleRead])
async def list_upsell_rules(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_upsell_rules(db, current_user.restaurant_id, active_only)


@router.post("/upsell-rules", response_model=UpsellRuleRead, status_code=201)
async def add_upsell_rule(
    payload: UpsellRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await create_upsell_rule(db, current_user.restaurant_id, payload)


@router.put("/upsell-rules/{rule_id}", response_model=UpsellRuleRead)
async def edit_upsell_rule(
    rule_id: int,
    payload: UpsellRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await update_upsell_rule(db, current_user.restaurant_id, rule_id, payload)


@router.delete("/upsell-rules/{rule_id}", status_code=204)
async def remove_upsell_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    await delete_upsell_rule(db, current_user.restaurant_id, rule_id)


@router.post("/upsell-rules/{rule_id}/accepted", response_model=UpsellRuleRead)
async def upsell_accepted(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await record_upsell_accepted(db, current_user.restaurant_id, rule_id)


@router.get("/analytics", response_model=MenuAnalytics)
async def menu_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_tenant_user),
):
    return await get_menu_analytics(db, current_user.restaurant_id)
