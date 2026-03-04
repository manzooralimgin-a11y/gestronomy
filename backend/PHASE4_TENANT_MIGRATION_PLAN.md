# Phase 4 Tenant Isolation Migration Plan

## Goal
Add `restaurant_id` to high-impact operational tables (menu, guests, reservations, billing, inventory), backfill deterministic values where possible, and prepare for strict `NOT NULL` enforcement in a later cutover.

## Scope Added In Patch
- Menu: `menu_categories`, `menu_items`, `menu_modifiers`, `menu_combos`, `upsell_rules`
- Guests: `guest_profiles`, `orders`, `loyalty_accounts`, `promotions`
- Reservations: `floor_sections`, `tables`, `reservations`, `waitlist`, `qr_table_codes`, `table_sessions`
- Billing: `table_orders`, `order_items`, `bills`, `payments`, `cash_shifts`, `kds_station_configs`
- Inventory: `vendors`, `inventory_items`, `purchase_orders`, `inventory_movements`, `tva_reports`, `supplier_catalog_items`, `auto_purchase_rules`

## Migration File
- Alembic revision: `9b4c1d2e7f10`
- File: `backend/alembic/versions/9b4c1d2e7f10_phase4_add_restaurant_id_to_core_tables.py`

## What The Migration Does
1. Adds nullable `restaurant_id` column to each scoped table.
2. Adds `ix_<table>_restaurant_id` index on each table.
3. Adds FK to `restaurants(id)` with `ON DELETE SET NULL`.
4. Backfills in two passes:
   - Single-restaurant fallback: if there is exactly one restaurant row, fill straightforward top-level tables.
   - Relationship propagation: derive tenant from parent rows (e.g., `order_items -> table_orders`, `payments -> bills`, `tables -> floor_sections`, etc.).

## Rollout Steps
1. Deploy app version with this migration and model updates.
2. Run `alembic upgrade head`.
3. Validate backfill quality:
   - Check remaining nulls per table.
   - Check cross-table tenant consistency on key joins.
4. Patch service-layer queries/creates to always filter/set `restaurant_id`.
5. Once nulls are zero and service writes are tenant-safe:
   - Add `NOT NULL` constraints in a follow-up migration.
   - Add composite uniqueness where needed (for example, replace global unique email with tenant-scoped uniqueness if product rules require it).

## Validation Queries
Use these after migration:

```sql
-- Null coverage check
SELECT 'menu_items' AS table_name, COUNT(*) AS null_rows FROM menu_items WHERE restaurant_id IS NULL
UNION ALL
SELECT 'orders', COUNT(*) FROM orders WHERE restaurant_id IS NULL
UNION ALL
SELECT 'reservations', COUNT(*) FROM reservations WHERE restaurant_id IS NULL
UNION ALL
SELECT 'table_orders', COUNT(*) FROM table_orders WHERE restaurant_id IS NULL
UNION ALL
SELECT 'payments', COUNT(*) FROM payments WHERE restaurant_id IS NULL
UNION ALL
SELECT 'inventory_items', COUNT(*) FROM inventory_items WHERE restaurant_id IS NULL;
```

```sql
-- Join consistency check example
SELECT COUNT(*) AS mismatches
FROM order_items oi
JOIN table_orders o ON oi.order_id = o.id
WHERE oi.restaurant_id IS DISTINCT FROM o.restaurant_id;
```

## Risk Notes
- In true multi-tenant legacy data with weak foreign links, some rows may remain `NULL` and require manual remediation.
- This phase intentionally keeps columns nullable to avoid unsafe lock-step failures during first deployment.

