"""Seed menu items, floor sections, tables, and sample reservations.

DEPRECATED: Use migrate_master.py instead — it handles multi-tenant seeding
and auto-creates default restaurant + admin user.
"""

import asyncio
from datetime import date, time, datetime, timezone, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Import ALL models to resolve FK references
from app.database import Base
from app.auth.models import User, Restaurant
from app.core.models import AgentAction, AgentLog, AgentConfig
from app.accounting.models import ChartOfAccount, GLEntry, Invoice, Budget, Reconciliation
from app.vision.models import VisionAlert, WasteLog, ComplianceEvent
from app.forecasting.models import Forecast, ForecastInput
from app.inventory.models import InventoryItem, PurchaseOrder, Vendor, InventoryMovement, TVAReport
from app.workforce.models import Employee, Schedule, Shift, Applicant, TrainingModule, TrainingProgress
from app.guests.models import GuestProfile, Order, LoyaltyAccount, Promotion
from app.dashboard.models import DashboardQuery, Alert, KPISnapshot
from app.maintenance.models import Equipment, IoTReading, MaintenanceTicket, EnergyReading
from app.digital_twin.models import Scenario, SimulationRun
from app.food_safety.models import HACCPLog, TemperatureReading, AllergenAlert, ComplianceScore
from app.franchise.models import Location, LocationMetric, Benchmark
from app.marketing.models import Review, Campaign, SocialPost
from app.menu.models import MenuCategory, MenuItem, MenuModifier, MenuItemModifier, MenuCombo
from app.reservations.models import FloorSection, Table, Reservation, WaitlistEntry, TableSession
from app.billing.models import TableOrder, OrderItem, Bill, Payment


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(text("SELECT COUNT(*) FROM menu_categories"))
        count = result.scalar()
        if count and count > 0:
            print(f"Menu already seeded ({count} categories). Skipping.")
            await engine.dispose()
            return

        print("🍽️  Seeding menu categories...")
        categories = [
            MenuCategory(name="Appetizers", description="Start your meal right", icon="🥗", color="#f59e0b", sort_order=1),
            MenuCategory(name="Soups", description="Warm & comforting", icon="🍜", color="#06b6d4", sort_order=2),
            MenuCategory(name="Salads", description="Fresh and healthy", icon="🥗", color="#22c55e", sort_order=3),
            MenuCategory(name="Main Course", description="Chef's finest selections", icon="🍽️", color="#e94560", sort_order=4),
            MenuCategory(name="Pasta", description="Italian classics", icon="🍝", color="#f97316", sort_order=5),
            MenuCategory(name="Seafood", description="Ocean to table", icon="🦐", color="#3b82f6", sort_order=6),
            MenuCategory(name="Desserts", description="Sweet endings", icon="🍰", color="#ec4899", sort_order=7),
            MenuCategory(name="Beverages", description="Drinks & cocktails", icon="🥤", color="#8b5cf6", sort_order=8),
        ]
        db.add_all(categories)
        await db.flush()
        cat_map = {c.name: c.id for c in categories}

        print("🍕 Seeding menu items (30+)...")
        items = [
            # Appetizers
            MenuItem(category_id=cat_map["Appetizers"], name="Bruschetta al Pomodoro", description="Toasted ciabatta with fresh tomatoes, basil, and garlic", price=9.50, cost=2.80, prep_time_min=8, is_featured=True, dietary_tags_json={"tags": ["Vegetarian"]}, allergens_json={"tags": ["Gluten"]}),
            MenuItem(category_id=cat_map["Appetizers"], name="Carpaccio di Manzo", description="Thinly sliced beef with arugula, parmesan, and truffle oil", price=14.00, cost=5.50, prep_time_min=10, allergens_json={"tags": ["Dairy"]}),
            MenuItem(category_id=cat_map["Appetizers"], name="Calamari Fritti", description="Crispy fried squid with lemon aioli", price=12.00, cost=4.00, prep_time_min=10),
            MenuItem(category_id=cat_map["Appetizers"], name="Burrata e Prosciutto", description="Creamy burrata with prosciutto di parma and figs", price=16.00, cost=7.00, prep_time_min=5, is_featured=True, allergens_json={"tags": ["Dairy"]}),
            # Soups
            MenuItem(category_id=cat_map["Soups"], name="French Onion Soup", description="Classic onion soup with gruyère crouton", price=10.00, cost=2.50, prep_time_min=12, allergens_json={"tags": ["Gluten", "Dairy"]}),
            MenuItem(category_id=cat_map["Soups"], name="Lobster Bisque", description="Rich & creamy lobster soup with cognac", price=14.00, cost=5.00, prep_time_min=10, is_featured=True, allergens_json={"tags": ["Shellfish", "Dairy"]}),
            # Salads
            MenuItem(category_id=cat_map["Salads"], name="Caesar Salad", description="Romaine, parmesan, croutons, classic dressing", price=11.00, cost=3.00, prep_time_min=7, dietary_tags_json={"tags": ["Gluten-Free Option"]}),
            MenuItem(category_id=cat_map["Salads"], name="Niçoise Salad", description="Tuna, olives, egg, green beans, potatoes", price=15.00, cost=5.00, prep_time_min=10),
            MenuItem(category_id=cat_map["Salads"], name="Quinoa & Avocado Bowl", description="Quinoa, avocado, cherry tomatoes, lime dressing", price=13.00, cost=4.00, prep_time_min=8, dietary_tags_json={"tags": ["Vegan", "Gluten-Free"]}),
            # Main Course
            MenuItem(category_id=cat_map["Main Course"], name="Beef Tenderloin", description="8oz tenderloin, red wine jus, roasted vegetables", price=34.00, cost=14.00, prep_time_min=25, is_featured=True, allergens_json={"tags": ["Dairy"]}),
            MenuItem(category_id=cat_map["Main Course"], name="Duck Confit", description="Slow-cooked duck leg, lentils, orange glaze", price=28.00, cost=10.00, prep_time_min=20),
            MenuItem(category_id=cat_map["Main Course"], name="Lamb Rack", description="Herb-crusted rack of lamb with mint pesto", price=36.00, cost=15.00, prep_time_min=25, is_featured=True),
            MenuItem(category_id=cat_map["Main Course"], name="Pan-Seared Chicken", description="Free-range chicken, mushroom risotto, truffle jus", price=24.00, cost=8.00, prep_time_min=20),
            MenuItem(category_id=cat_map["Main Course"], name="Vegetable Wellington", description="Seasonal vegetables in puff pastry, mushroom duxelles", price=22.00, cost=7.00, prep_time_min=20, dietary_tags_json={"tags": ["Vegetarian"]}),
            # Pasta
            MenuItem(category_id=cat_map["Pasta"], name="Truffle Tagliatelle", description="Fresh pasta, black truffle, parmesan cream", price=24.00, cost=8.00, prep_time_min=15, is_featured=True, allergens_json={"tags": ["Gluten", "Dairy"]}),
            MenuItem(category_id=cat_map["Pasta"], name="Spaghetti Carbonara", description="Guanciale, pecorino, egg yolk, black pepper", price=18.00, cost=5.00, prep_time_min=12, allergens_json={"tags": ["Gluten", "Dairy", "Eggs"]}),
            MenuItem(category_id=cat_map["Pasta"], name="Penne Arrabbiata", description="Spicy tomato sauce, garlic, chili flakes", price=16.00, cost=3.50, prep_time_min=12, dietary_tags_json={"tags": ["Vegan"]}, allergens_json={"tags": ["Gluten"]}),
            MenuItem(category_id=cat_map["Pasta"], name="Lobster Linguine", description="Half lobster, cherry tomatoes, white wine sauce", price=32.00, cost=14.00, prep_time_min=18, allergens_json={"tags": ["Shellfish", "Gluten"]}),
            # Seafood
            MenuItem(category_id=cat_map["Seafood"], name="Grilled Sea Bass", description="Whole sea bass, lemon butter, capers", price=30.00, cost=12.00, prep_time_min=20, is_featured=True),
            MenuItem(category_id=cat_map["Seafood"], name="Salmon Fillet", description="Atlantic salmon, dill cream, roasted asparagus", price=26.00, cost=9.00, prep_time_min=18, dietary_tags_json={"tags": ["Gluten-Free"]}),
            MenuItem(category_id=cat_map["Seafood"], name="Seafood Platter", description="Oysters, prawns, crab, lobster tail", price=55.00, cost=25.00, prep_time_min=15, allergens_json={"tags": ["Shellfish"]}),
            # Desserts
            MenuItem(category_id=cat_map["Desserts"], name="Tiramisu", description="Classic Italian mascarpone & espresso dessert", price=10.00, cost=3.00, prep_time_min=5, allergens_json={"tags": ["Dairy", "Eggs", "Gluten"]}),
            MenuItem(category_id=cat_map["Desserts"], name="Crème Brûlée", description="Tahitian vanilla bean, caramelized sugar", price=11.00, cost=2.50, prep_time_min=5, is_featured=True, allergens_json={"tags": ["Dairy", "Eggs"]}),
            MenuItem(category_id=cat_map["Desserts"], name="Chocolate Fondant", description="Warm chocolate lava cake, vanilla ice cream", price=12.00, cost=3.50, prep_time_min=12, allergens_json={"tags": ["Dairy", "Eggs", "Gluten"]}),
            MenuItem(category_id=cat_map["Desserts"], name="Lemon Tart", description="Tangy lemon curd, meringue, berry coulis", price=10.00, cost=2.50, prep_time_min=5, dietary_tags_json={"tags": ["Vegetarian"]}),
            MenuItem(category_id=cat_map["Desserts"], name="Sorbet Selection", description="Three scoops: mango, raspberry, passion fruit", price=8.00, cost=2.00, prep_time_min=3, dietary_tags_json={"tags": ["Vegan", "Gluten-Free"]}),
            # Beverages
            MenuItem(category_id=cat_map["Beverages"], name="Espresso", description="Double shot Italian espresso", price=3.50, cost=0.50, prep_time_min=2),
            MenuItem(category_id=cat_map["Beverages"], name="Fresh Orange Juice", description="Freshly squeezed daily", price=5.00, cost=1.50, prep_time_min=3, dietary_tags_json={"tags": ["Vegan", "Gluten-Free"]}),
            MenuItem(category_id=cat_map["Beverages"], name="Sparkling Water", description="San Pellegrino 750ml", price=4.50, cost=1.00, prep_time_min=1),
            MenuItem(category_id=cat_map["Beverages"], name="House Red Wine", description="Glass of Côtes du Rhône", price=8.00, cost=2.50, prep_time_min=1),
            MenuItem(category_id=cat_map["Beverages"], name="Cocktail – Negroni", description="Gin, Campari, sweet vermouth", price=12.00, cost=3.00, prep_time_min=5),
        ]
        db.add_all(items)
        await db.flush()

        print("🏗️  Seeding floor sections...")
        sections = [
            FloorSection(name="Main Dining", description="Main indoor dining area", sort_order=1),
            FloorSection(name="Terrace", description="Outdoor seating area", sort_order=2),
            FloorSection(name="Private Room", description="Private dining for groups", sort_order=3),
            FloorSection(name="Bar Area", description="Bar counter & high tables", sort_order=4),
        ]
        db.add_all(sections)
        await db.flush()
        sec_map = {s.name: s.id for s in sections}

        print("🪑 Seeding tables (15)...")
        tables_data = [
            # Main Dining
            Table(section_id=sec_map["Main Dining"], table_number="M1", capacity=2, min_capacity=1, shape="square", position_x=1, position_y=1),
            Table(section_id=sec_map["Main Dining"], table_number="M2", capacity=2, min_capacity=1, shape="square", position_x=2, position_y=1),
            Table(section_id=sec_map["Main Dining"], table_number="M3", capacity=4, min_capacity=2, shape="square", position_x=3, position_y=1),
            Table(section_id=sec_map["Main Dining"], table_number="M4", capacity=4, min_capacity=2, shape="round", position_x=1, position_y=2),
            Table(section_id=sec_map["Main Dining"], table_number="M5", capacity=6, min_capacity=3, shape="rectangle", position_x=2, position_y=2),
            Table(section_id=sec_map["Main Dining"], table_number="M6", capacity=6, min_capacity=3, shape="rectangle", position_x=3, position_y=2),
            # Terrace
            Table(section_id=sec_map["Terrace"], table_number="T1", capacity=2, min_capacity=1, shape="round", position_x=1, position_y=1),
            Table(section_id=sec_map["Terrace"], table_number="T2", capacity=2, min_capacity=1, shape="round", position_x=2, position_y=1),
            Table(section_id=sec_map["Terrace"], table_number="T3", capacity=4, min_capacity=2, shape="square", position_x=3, position_y=1),
            Table(section_id=sec_map["Terrace"], table_number="T4", capacity=4, min_capacity=2, shape="square", position_x=1, position_y=2),
            # Private Room
            Table(section_id=sec_map["Private Room"], table_number="P1", capacity=8, min_capacity=4, shape="rectangle", position_x=1, position_y=1),
            Table(section_id=sec_map["Private Room"], table_number="P2", capacity=12, min_capacity=6, shape="rectangle", position_x=2, position_y=1),
            # Bar Area
            Table(section_id=sec_map["Bar Area"], table_number="B1", capacity=2, min_capacity=1, shape="round", position_x=1, position_y=1, status="occupied"),
            Table(section_id=sec_map["Bar Area"], table_number="B2", capacity=2, min_capacity=1, shape="round", position_x=2, position_y=1),
            Table(section_id=sec_map["Bar Area"], table_number="B3", capacity=4, min_capacity=2, shape="square", position_x=3, position_y=1),
        ]
        db.add_all(tables_data)
        await db.flush()

        print("📅 Seeding reservations...")
        today = date.today()
        tomorrow = today + timedelta(days=1)

        reservations_data = [
            Reservation(
                guest_name="Sophie Martin", guest_phone="+33612345678", guest_email="sophie@email.com",
                table_id=tables_data[2].id, party_size=3, reservation_date=today,
                start_time=time(12, 0), duration_min=90, status="completed", source="online",
            ),
            Reservation(
                guest_name="Pierre Dupont", guest_phone="+33698765432",
                table_id=tables_data[4].id, party_size=5, reservation_date=today,
                start_time=time(19, 0), duration_min=120, status="confirmed", source="phone",
                special_requests="Anniversary dinner — please prepare a cake",
            ),
            Reservation(
                guest_name="Jean-Luc Bernard", guest_phone="+33611223344",
                table_id=tables_data[3].id, party_size=4, reservation_date=today,
                start_time=time(19, 30), duration_min=90, status="confirmed", source="phone",
            ),
            Reservation(
                guest_name="Marie Leclerc", guest_email="marie.l@email.com",
                table_id=tables_data[0].id, party_size=2, reservation_date=today,
                start_time=time(20, 0), duration_min=90, status="confirmed", source="online",
                special_requests="Window seat preferred",
            ),
            Reservation(
                guest_name="Carlos Rodriguez", guest_phone="+33699887766",
                table_id=tables_data[10].id, party_size=8, reservation_date=today,
                start_time=time(20, 30), duration_min=150, status="confirmed", source="phone",
                special_requests="Business dinner — need projector",
            ),
            Reservation(
                guest_name="Anna Schmidt", guest_phone="+33644556677",
                table_id=tables_data[5].id, party_size=6, reservation_date=tomorrow,
                start_time=time(19, 0), duration_min=120, status="confirmed", source="online",
            ),
            Reservation(
                guest_name="Yuki Tanaka", guest_email="yuki@email.com",
                table_id=tables_data[1].id, party_size=2, reservation_date=tomorrow,
                start_time=time(12, 30), duration_min=90, status="confirmed", source="online",
                special_requests="Vegetarian menu only",
            ),
        ]
        db.add_all(reservations_data)
        await db.flush()

        print("⏳ Seeding waitlist...")
        waitlist_data = [
            WaitlistEntry(
                guest_name="Thomas Moreau", guest_phone="+33677889900",
                party_size=3, estimated_wait_min=20,
                check_in_time=datetime.now(timezone.utc) - timedelta(minutes=10),
            ),
            WaitlistEntry(
                guest_name="Elena Rossi", guest_phone="+33655443322",
                party_size=2, estimated_wait_min=10,
                check_in_time=datetime.now(timezone.utc) - timedelta(minutes=5),
            ),
        ]
        db.add_all(waitlist_data)

        print("🍽️  Seeding menu combos...")
        combos = [
            MenuCombo(
                name="Lunch Special", description="Appetizer + Main + Dessert",
                combo_price=29.90,
                items_json={"appetizer": "Any appetizer", "main": "Any main course", "dessert": "Any dessert"},
                savings_amount=8.00,
            ),
            MenuCombo(
                name="Seafood Feast", description="Seafood platter + Sea bass + Wine",
                combo_price=79.90,
                items_json={"starter": "Seafood Platter", "main": "Grilled Sea Bass", "wine": "Bottle of white wine"},
                savings_amount=15.00,
            ),
        ]
        db.add_all(combos)

        print("📝 Seeding modifiers...")
        modifiers = [
            MenuModifier(name="Extra Cheese", group_name="Additions", price_adjustment=2.00),
            MenuModifier(name="Truffle Oil", group_name="Additions", price_adjustment=4.00),
            MenuModifier(name="Side Salad", group_name="Sides", price_adjustment=3.50),
            MenuModifier(name="Fries", group_name="Sides", price_adjustment=3.00),
            MenuModifier(name="Gluten-Free Bread", group_name="Dietary", price_adjustment=1.50),
            MenuModifier(name="Extra Spicy", group_name="Cooking", price_adjustment=0),
            MenuModifier(name="Well Done", group_name="Cooking", price_adjustment=0),
            MenuModifier(name="Medium Rare", group_name="Cooking", price_adjustment=0, is_default=True),
        ]
        db.add_all(modifiers)

        await db.commit()
        print("✅ Seeding complete!")
        print(f"   → {len(categories)} categories")
        print(f"   → {len(items)} menu items")
        print(f"   → {len(sections)} floor sections")
        print(f"   → {len(tables_data)} tables")
        print(f"   → {len(reservations_data)} reservations")
        print(f"   → {len(waitlist_data)} waitlist entries")
        print(f"   → {len(combos)} combos")
        print(f"   → {len(modifiers)} modifiers")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
