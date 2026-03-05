import json
import asyncio
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import models
from app.config import settings
from app.auth.models import Restaurant
from app.menu.models import MenuCategory, MenuItem

async def migrate_menu():
    print("🚀 Starting menu migration...")
    
    # Initialize DB engine
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # 1. Get the first restaurant ID
        result = await db.execute(select(Restaurant).limit(1))
        restaurant = result.scalar_one_or_none()
        
        if not restaurant:
            print("❌ No restaurant found in database. Please register/login first.")
            return
        
        restaurant_id = restaurant.id
        print(f"📍 Using Restaurant ID: {restaurant_id} ({restaurant.name})")
        
        # 2. Ensure a default category exists
        result = await db.execute(select(MenuCategory).where(MenuCategory.restaurant_id == restaurant_id, MenuCategory.name == "General"))
        category = result.scalar_one_or_none()
        
        if not category:
            print("📁 Creating 'General' category...")
            category = MenuCategory(
                restaurant_id=restaurant_id,
                name="General",
                description="Imported items",
                icon="🍴",
                color="#6366f1",
                sort_order=0
            )
            db.add(category)
            await db.flush()
        
        category_id = category.id
        
        # 3. Load data from JSON
        json_path = os.path.join(os.path.dirname(__file__), "..", "data", "gastronovi_raw_items.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return
            
        print(f"📦 Loaded {len(raw_items)} items from JSON.")
        
        # 4. Ingest items
        count = 0
        skipped = 0
        for item_data in raw_items:
            name = item_data.get("title")
            price = item_data.get("price", 0.0)
            
            if not name:
                continue
                
            # Check if item exists
            result = await db.execute(select(MenuItem).where(MenuItem.restaurant_id == restaurant_id, MenuItem.name == name))
            existing = result.scalar_one_or_none()
            
            if existing:
                skipped += 1
                continue
                
            # Create new item
            new_item = MenuItem(
                restaurant_id=restaurant_id,
                category_id=category_id,
                name=name,
                description="",
                price=float(price),
                cost=float(price) * 0.3, # Estimating 30% food cost
                prep_time_min=10,
                is_available=True
            )
            db.add(new_item)
            count += 1
            
            if count % 20 == 0:
                print(f"✅ Processed {count} items...")
                
        await db.commit()
        print(f"🎉 Migration complete!")
        print(f"📊 Added: {count} | Skipped: {skipped} | Total: {len(raw_items)}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_menu())
