#!/usr/bin/env python3
"""
Update Gestronomy tables to match exact gastronovi (Das Elb Restaurant) table plan.
Run: PYTHONPATH=/Users/ali/Desktop/gestronomy/backend python scripts/update_tables.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from app.database import async_session
from app.reservations.models import FloorSection, Table

# ══════════════════════════════════════════════════════════════
# Exact table layout from gastronovi front office (Das Elb Restaurant)
# Extracted 2026-03-03 from office.gastronovi.com
# 3 sections, 109 tables, 409 total seats
# ══════════════════════════════════════════════════════════════

SECTIONS = [
    {"name": "Restaurant", "description": "Main dining area — 175 seats", "sort_order": 1},
    {"name": "Terrasse", "description": "Outdoor terrace — 174 seats", "sort_order": 2},
    {"name": "Tagung (Main area)", "description": "Conference / meeting area — 60 seats", "sort_order": 3},
]

# Restaurant — 52 tables, 175 seats
RESTAURANT_TABLES = [
    # Bar stools / single seats (5 × 1 seat = 5)
    ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1),
    # 2-seat tables (13 × 2 = 26)
    ("11", 2), ("12", 2), ("13", 2), ("14", 2), ("15", 2), ("16", 2),
    ("21/1", 2), ("22/1", 2), ("23/1", 2), ("24/1", 2),
    ("31/1", 2), ("33/1", 2), ("22/2", 2),
    # Window (Fenster) tables
    ("21 Fenster", 5), ("22 Fenster", 7), ("23 Fenster", 8),
    ("24 Fenster", 4), ("25 Fenster", 4),
    # 4-seat tables (31 × 4 = 124)
    ("10", 4), ("31", 4), ("32", 4), ("33", 4), ("34", 4), ("35", 4),
    ("36", 4), ("37", 4), ("38", 4), ("39", 4),
    ("16/1", 4), ("25/1", 4), ("32/1", 4),
    ("33/2", 4), ("34/2", 4), ("35/2", 4), ("36/2", 4),
    ("21/2", 4), ("22/3", 4), ("23/3", 4), ("24/3", 4),
    ("1/1", 4), ("2/1", 4), ("3/1", 4), ("4/1", 4), ("5/1", 4),
    ("21/3", 4), ("21/4", 4), ("22/4", 4),
]

# Terrasse — 41 tables, 174 seats
TERRASSE_TABLES = [
    # 2-seat tables (7 × 2 = 14)
    ("46", 2), ("60", 2), ("64", 2), ("66/1", 2), ("67/1", 2), ("72", 2), ("73", 2),
    # 3-seat tables (3 × 3 = 9)
    ("63", 3), ("71", 3), ("74", 3),
    # 4-seat tables (21 × 4 = 84)
    ("42", 4), ("44", 4), ("45", 4), ("49", 4),
    ("51/1", 4), ("52", 4), ("53", 4), ("54", 4), ("55", 4), ("56", 4),
    ("57", 4), ("58", 4), ("75", 4), ("76", 4),
    ("80", 4), ("81", 4), ("82", 4), ("83", 4),
    ("Lounge 1", 4), ("Lounge 2", 4), ("Lounge 3", 4),
    # 5-seat tables (1 × 5 = 5)
    ("47", 5),
    # 6-seat tables (5 × 6 = 30)
    ("40", 6), ("43", 6), ("51", 6), ("68", 6), ("70", 6),
    # 8-seat tables (4 × 8 = 32)
    ("41", 8), ("61", 8), ("62", 8), ("Lounge", 8),
]

# Tagung (Main area) — 16 tables, 60 seats
TAGUNG_TABLES = [
    ("100", 4), ("101", 4), ("102", 4), ("103", 4), ("104", 4),
    ("105", 4), ("106", 4), ("107", 4), ("108", 4), ("109", 4),
    ("110", 4), ("111", 4), ("112", 4), ("113", 4), ("114", 4),
    ("1000 Tagung", 0),
]


async def main():
    print("=" * 60)
    print("  Gastronovi Table Plan → Gestronomy")
    print("=" * 60)

    async with async_session() as db:
        # ── 1. Clear existing tables, sections, and dependent data ──
        print("\n[1/3] Clearing existing table data...")
        # Clear FK references first
        await db.execute(text("UPDATE reservations SET table_id = NULL"))
        await db.execute(text("DELETE FROM table_sessions"))
        await db.execute(text("DELETE FROM qr_table_codes"))
        await db.execute(text("DELETE FROM tables"))
        await db.execute(text("DELETE FROM floor_sections"))
        await db.commit()
        print("  ✓ Cleared all tables, sections, and references")

        # ── 2. Create sections ──
        print("\n[2/3] Creating floor sections...")
        section_map = {}
        for s_data in SECTIONS:
            section = FloorSection(**s_data)
            db.add(section)
            await db.flush()
            section_map[s_data["name"]] = section.id
            print(f"  ✓ {s_data['name']} (id={section.id})")
        await db.commit()

        # ── 3. Create tables ──
        print("\n[3/3] Creating tables...")
        table_data = [
            ("Restaurant", RESTAURANT_TABLES),
            ("Terrasse", TERRASSE_TABLES),
            ("Tagung (Main area)", TAGUNG_TABLES),
        ]

        total = 0
        total_seats = 0
        for section_name, tables in table_data:
            section_id = section_map[section_name]
            for table_number, capacity in tables:
                # Determine shape based on capacity
                if capacity <= 1:
                    shape = "circle"
                elif capacity <= 4:
                    shape = "square"
                elif capacity <= 6:
                    shape = "rectangle"
                else:
                    shape = "rectangle"

                t = Table(
                    section_id=section_id,
                    table_number=str(table_number),
                    capacity=capacity,
                    min_capacity=1 if capacity > 0 else 0,
                    shape=shape,
                    status="available",
                    is_active=True,
                )
                db.add(t)
                total += 1
                total_seats += capacity

            await db.flush()
            print(f"  ✓ {section_name}: {len(tables)} tables")

        await db.commit()

        # ── Summary ──
        section_count = (await db.execute(text("SELECT COUNT(*) FROM floor_sections"))).scalar()
        table_count = (await db.execute(text("SELECT COUNT(*) FROM tables"))).scalar()

        print("\n" + "=" * 60)
        print("  Table Plan Update Complete!")
        print(f"  Sections:     {section_count}")
        print(f"  Tables:       {table_count}")
        print(f"  Total Seats:  {total_seats}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
