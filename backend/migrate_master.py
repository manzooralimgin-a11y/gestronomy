import asyncio
import json
import os
import random
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import models
from app.config import settings
from app.database import Base
from app.auth.models import Restaurant, User
from app.menu.models import MenuCategory, MenuItem, MenuModifier, MenuCombo
from app.reservations.models import FloorSection, Table, Reservation, WaitlistEntry
from app.dashboard.models import KPISnapshot, Alert
from app.core.models import AgentAction
from app.inventory.models import InventoryItem
from app.workforce.models import Employee

async def migrate_master():
    print("🚀 Starting Master Data Migration...")
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # 1. Verification of Restaurant Context
        result = await db.execute(select(Restaurant).limit(1))
        restaurant = result.scalar_one_or_none()
        if not restaurant:
            print("❌ No restaurant found. Please register/login in the app first.")
            return
        
        rid = restaurant.id
        print(f"📍 Context: Restaurant ID {rid} ({restaurant.name})")

        # ---------------------------------------------------------
        # 2. SEATING DATA (Floor Sections & Tables)
        # ---------------------------------------------------------
        print("🪑 Migrating Seating Data...")
        sections_data = [
            {"name": "Main Dining", "description": "Main indoor dining area", "sort_order": 1},
            {"name": "Terrace", "description": "Outdoor seating area", "sort_order": 2},
            {"name": "Private Room", "description": "Private dining for groups", "sort_order": 3},
            {"name": "Bar Area", "description": "Bar counter & high tables", "sort_order": 4},
        ]
        
        sec_map = {}
        for s in sections_data:
            res = await db.execute(select(FloorSection).where(FloorSection.restaurant_id == rid, FloorSection.name == s["name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                new_sec = FloorSection(restaurant_id=rid, **s)
                db.add(new_sec)
                await db.flush()
                sec_map[s["name"]] = new_sec.id
                print(f"   + Added section: {s['name']}")
            else:
                sec_map[s["name"]] = existing.id

        tables_data = [
            # Main Dining
            {"section_id": sec_map.get("Main Dining"), "table_number": "M1", "capacity": 2, "min_capacity": 1, "shape": "square", "position_x": 1, "position_y": 1},
            {"section_id": sec_map.get("Main Dining"), "table_number": "M2", "capacity": 2, "min_capacity": 1, "shape": "square", "position_x": 2, "position_y": 1},
            {"section_id": sec_map.get("Main Dining"), "table_number": "M3", "capacity": 4, "min_capacity": 2, "shape": "square", "position_x": 3, "position_y": 1},
            {"section_id": sec_map.get("Main Dining"), "table_number": "M4", "capacity": 4, "min_capacity": 2, "shape": "round", "position_x": 1, "position_y": 2},
            # Terrace
            {"section_id": sec_map.get("Terrace"), "table_number": "T1", "capacity": 2, "min_capacity": 1, "shape": "round", "position_x": 1, "position_y": 1},
        ]
        
        for t in tables_data:
            if not t["section_id"]: continue
            res = await db.execute(select(Table).where(Table.restaurant_id == rid, Table.table_number == t["table_number"]))
            if not res.scalar_one_or_none():
                db.add(Table(restaurant_id=rid, **t))
                print(f"   + Added table: {t['table_number']}")
                
        # ---------------------------------------------------------
        # 3. MENU DATA (Categories & Items)
        # ---------------------------------------------------------
        print("🍽️  Migrating Menu Data...")
        # Add core categories from seed_menu_reservations
        core_cats = ["Appetizers", "Main Course", "Desserts", "Beverages", "General"]
        cat_map = {}
        for cname in core_cats:
            res = await db.execute(select(MenuCategory).where(MenuCategory.restaurant_id == rid, MenuCategory.name == cname))
            existing = res.scalar_one_or_none()
            if not existing:
                new_cat = MenuCategory(restaurant_id=rid, name=cname, icon="🍴", color="#6366f1")
                db.add(new_cat)
                await db.flush()
                cat_map[cname] = new_cat.id
                print(f"   + Added category: {cname}")
            else:
                cat_map[cname] = existing.id

        # Ingest gastronovi_raw_items.json into 'General'
        json_path = os.path.join(os.path.dirname(__file__), "data", "gastronovi_raw_items.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
            
            added_count = 0
            for item in raw_items:
                res = await db.execute(select(MenuItem).where(MenuItem.restaurant_id == rid, MenuItem.name == item["title"]))
                if not res.scalar_one_or_none():
                    db.add(MenuItem(
                        restaurant_id=rid,
                        category_id=cat_map["General"],
                        name=item["title"],
                        price=float(item["price"]),
                        cost=float(item["price"]) * 0.3
                    ))
                    added_count += 1
            print(f"   + Imported {added_count} items from JSON")

        # ---------------------------------------------------------
        # 4. ADVANCED DATA (KPIs, Alerts, Agent Actions)
        # ---------------------------------------------------------
        print("📊 Migrating Advanced Features Data...")
        now = datetime.now(timezone.utc)
        
        # KPIs - limited check: just check if any KPIs today
        res = await db.execute(select(KPISnapshot).limit(1))
        if not res.scalar_one_or_none():
            kpi_data = [
                {"metric_name": "total_sales", "value": 12847.50, "previous_value": 11920.00, "target_value": 13000.00},
                {"metric_name": "labor_pct", "value": 28.5, "previous_value": 30.2, "target_value": 27.0},
            ]
            for k in kpi_data:
                db.add(KPISnapshot(**k, timestamp=now))
            print("   + Seeded Dashboard KPIs")

        # Agent Actions
        res = await db.execute(select(AgentAction).limit(1))
        if not res.scalar_one_or_none():
            actions = [
                {"agent_name": "InventoryAgent", "action_type": "auto_order", "description": "Auto-ordered 10kg Salmon Fillet", "status": "completed"},
                {"agent_name": "FinanceAgent", "action_type": "analysis", "description": "Daily P&L report generated", "status": "completed"},
            ]
            for a in actions:
                db.add(AgentAction(**a, confidence=0.95, input_data={}, output_data={}))
            print("   + Seeded Agent Activity Feed")

        # ---------------------------------------------------------
        # 5. RESERVATIONS & GUESTS
        # ---------------------------------------------------------
        print("📅 Seeding sample reservations...")
        res = await db.execute(select(Reservation).limit(1))
        if not res.scalar_one_or_none():
            # Minimal seed to verify flow
            db.add(Reservation(
                restaurant_id=rid,
                guest_name="Sarah Cloud",
                guest_email="sarah@cloud.com",
                party_size=4,
                reservation_date=date.today(),
                start_time=time(19, 0),
                status="confirmed",
                source="online"
            ))
            print("   + Seeded sample reservation")

        await db.commit()
        print("✅ Master Migration Successful!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_master())
