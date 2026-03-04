from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.menu_designer.models import MenuTemplate, MenuDesign


# ── Templates ──

async def get_templates(db: AsyncSession) -> list[MenuTemplate]:
    result = await db.execute(select(MenuTemplate).order_by(MenuTemplate.created_at.desc()))
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: int) -> MenuTemplate | None:
    result = await db.execute(select(MenuTemplate).where(MenuTemplate.id == template_id))
    return result.scalar_one_or_none()


async def create_template(db: AsyncSession, data: dict) -> MenuTemplate:
    t = MenuTemplate(**data)
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


async def delete_template(db: AsyncSession, template_id: int) -> bool:
    t = await get_template(db, template_id)
    if not t or t.is_system:
        return False
    await db.delete(t)
    await db.commit()
    return True


# ── Designs ──

async def get_designs(db: AsyncSession) -> list[MenuDesign]:
    result = await db.execute(select(MenuDesign).order_by(MenuDesign.updated_at.desc()))
    return list(result.scalars().all())


async def get_design(db: AsyncSession, design_id: int) -> MenuDesign | None:
    result = await db.execute(select(MenuDesign).where(MenuDesign.id == design_id))
    return result.scalar_one_or_none()


async def create_design(db: AsyncSession, data: dict) -> MenuDesign:
    d = MenuDesign(**data)
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return d


async def update_design(db: AsyncSession, design_id: int, data: dict) -> MenuDesign | None:
    d = await get_design(db, design_id)
    if not d:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(d, k, v)
    await db.commit()
    await db.refresh(d)
    return d


async def publish_design(db: AsyncSession, design_id: int):
    d = await get_design(db, design_id)
    if not d:
        return None
    # Unpublish all others
    all_designs = await get_designs(db)
    for od in all_designs:
        if od.id != design_id and od.status == "published":
            od.status = "draft"
    d.status = "published"
    await db.commit()
    await db.refresh(d)
    return d


async def delete_design(db: AsyncSession, design_id: int) -> bool:
    d = await get_design(db, design_id)
    if not d:
        return False
    await db.delete(d)
    await db.commit()
    return True


async def get_design_preview(db: AsyncSession, design_id: int):
    """Get design data merged with menu items for preview."""
    from app.menu.models import MenuCategory, MenuItem
    d = await get_design(db, design_id)
    if not d:
        return None

    # Fetch menu data
    cats_result = await db.execute(
        select(MenuCategory).where(MenuCategory.is_active == True).order_by(MenuCategory.sort_order)
    )
    categories = list(cats_result.scalars().all())

    items_result = await db.execute(
        select(MenuItem).where(MenuItem.is_available == True).order_by(MenuItem.sort_order)
    )
    items = list(items_result.scalars().all())

    return {
        "design": {
            "id": d.id,
            "name": d.name,
            "template_id": d.template_id,
            "design_data": d.design_data_json,
            "translations": d.translations_json,
            "language": d.language,
            "status": d.status,
        },
        "categories": [{"id": c.id, "name": c.name} for c in categories],
        "items": [
            {
                "id": it.id,
                "name": it.name,
                "description": it.description,
                "price": float(it.price),
                "category_id": it.category_id,
                "allergens": it.allergens_json.get("tags", []) if it.allergens_json else [],
                "dietary_tags": it.dietary_tags_json.get("tags", []) if it.dietary_tags_json else [],
            }
            for it in items
        ],
    }
