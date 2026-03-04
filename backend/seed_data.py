"""Seed the database with sample restaurant data for the dashboard."""

import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone
import random

# Ensure app is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.database import async_session

# Import ALL models so SQLAlchemy can resolve foreign keys
from app.auth.models import User, Restaurant  # noqa: F401
from app.dashboard.models import KPISnapshot, Alert, DashboardQuery  # noqa: F401
from app.core.models import AgentAction, AgentLog, AgentConfig  # noqa: F401
from app.inventory.models import InventoryItem, Vendor, PurchaseOrder, InventoryMovement, TVAReport  # noqa: F401
from app.guests.models import GuestProfile, Order, LoyaltyAccount, Promotion  # noqa: F401
from app.workforce.models import Employee, Schedule, Shift, Applicant, TrainingModule, TrainingProgress  # noqa: F401
from app.accounting.models import ChartOfAccount, GLEntry, Invoice, Budget, Reconciliation  # noqa: F401
from app.vision.models import VisionAlert, WasteLog, ComplianceEvent  # noqa: F401
from app.forecasting.models import Forecast, ForecastInput  # noqa: F401
from app.maintenance.models import Equipment, IoTReading, MaintenanceTicket, EnergyReading  # noqa: F401
from app.digital_twin.models import Scenario, SimulationRun  # noqa: F401
from app.food_safety.models import HACCPLog, TemperatureReading, AllergenAlert, ComplianceScore  # noqa: F401
from app.franchise.models import Location, LocationMetric, Benchmark  # noqa: F401
from app.marketing.models import Review, Campaign, SocialPost  # noqa: F401


async def seed():
    async with async_session() as session:
        now = datetime.now(timezone.utc)

        # ── KPI Snapshots (6 core metrics) ──
        kpi_data = [
            {"metric_name": "total_sales", "value": 12847.50, "previous_value": 11920.00, "target_value": 13000.00},
            {"metric_name": "labor_pct", "value": 28.5, "previous_value": 30.2, "target_value": 27.0},
            {"metric_name": "food_cost_pct", "value": 31.2, "previous_value": 32.8, "target_value": 30.0},
            {"metric_name": "net_margin", "value": 18.3, "previous_value": 16.1, "target_value": 20.0},
            {"metric_name": "covers", "value": 247, "previous_value": 231, "target_value": 260},
            {"metric_name": "avg_ticket", "value": 52.00, "previous_value": 51.60, "target_value": 55.00},
        ]

        for kpi in kpi_data:
            session.add(KPISnapshot(**kpi, timestamp=now))

        # Add historical KPI data (last 7 days)
        for days_ago in range(1, 8):
            ts = now - timedelta(days=days_ago)
            for kpi in kpi_data:
                jitter = random.uniform(0.9, 1.1)
                session.add(KPISnapshot(
                    metric_name=kpi["metric_name"],
                    value=round(kpi["value"] * jitter, 2),
                    previous_value=round(kpi["previous_value"] * jitter, 2) if kpi["previous_value"] else None,
                    target_value=kpi["target_value"],
                    timestamp=ts,
                ))

        # ── Alerts ──
        alerts = [
            {"module": "Inventory", "severity": "critical", "title": "Low Stock: Salmon Fillet", "message": "Salmon fillet below PAR level (2.5 kg remaining, PAR: 8 kg). Auto-order triggered."},
            {"module": "Food Safety", "severity": "critical", "title": "Walk-in Cooler Temp Alert", "message": "Walk-in cooler #2 temp reached 6.2C, exceeding 4C threshold. Maintenance notified."},
            {"module": "Workforce", "severity": "warning", "title": "Understaffed: Friday Dinner", "message": "Friday dinner has 3 servers but forecast needs 5. AI recommends calling 2 more."},
            {"module": "Accounting", "severity": "warning", "title": "Invoice Overdue: FreshFarms", "message": "Invoice #INV-2847 from FreshFarms ($3,240) is 15 days overdue."},
            {"module": "Guests", "severity": "warning", "title": "VIP Guest Arriving", "message": "VIP Sarah Chen (Platinum) has reservation at 7:30 PM. Table #12, gluten-free."},
            {"module": "Marketing", "severity": "info", "title": "Review Response Needed", "message": "3 new Google reviews (avg 4.2 stars). AI-drafted responses ready for approval."},
            {"module": "Maintenance", "severity": "info", "title": "Dishwasher Maintenance Due", "message": "Commercial dishwasher HB-400 due for maintenance in 3 days."},
            {"module": "Forecasting", "severity": "info", "title": "Weekend Forecast Updated", "message": "Saturday covers estimated at 285 (+12% vs last week). Weather clear."},
        ]

        for alert in alerts:
            session.add(Alert(**alert, is_read=False))

        # ── Agent Actions (activity feed) ──
        agent_actions = [
            {"agent_name": "InventoryAgent", "action_type": "auto_order", "description": "Auto-ordered 10kg Salmon Fillet from OceanFresh Suppliers", "status": "completed"},
            {"agent_name": "FinanceAgent", "action_type": "analysis", "description": "Daily P&L report generated — net margin 18.3%", "status": "completed"},
            {"agent_name": "WorkforceAgent", "action_type": "scheduling", "description": "Optimized Saturday schedule — saved 12 labor hours", "status": "completed"},
            {"agent_name": "QualityAgent", "action_type": "monitoring", "description": "Food safety compliance score: 96.4%", "status": "completed"},
            {"agent_name": "GuestAgent", "action_type": "prediction", "description": "Churn risk detected for 3 guests — offers queued", "status": "completed"},
            {"agent_name": "MarketingAgent", "action_type": "content", "description": "Generated social post for weekend special — pending approval", "status": "pending"},
            {"agent_name": "SupplyAgent", "action_type": "vendor_analysis", "description": "Vendor price comparison — potential 8% savings on produce", "status": "completed"},
            {"agent_name": "EnergyAgent", "action_type": "optimization", "description": "HVAC adjusted — projected 15% energy savings today", "status": "completed"},
            {"agent_name": "InventoryAgent", "action_type": "waste_tracking", "description": "Waste report: 2.1% food waste rate (target <3%)", "status": "completed"},
            {"agent_name": "FinanceAgent", "action_type": "alert", "description": "Flagged unusual $890 refund on POS terminal #3", "status": "review"},
            {"agent_name": "WorkforceAgent", "action_type": "alert", "description": "Maria called in sick — replacement Alex confirmed", "status": "completed"},
            {"agent_name": "GuestAgent", "action_type": "loyalty", "description": "Upgraded 5 guests to Gold tier based on visits", "status": "completed"},
        ]

        for action in agent_actions:
            session.add(AgentAction(
                agent_name=action["agent_name"],
                action_type=action["action_type"],
                description=action["description"],
                status=action["status"],
                input_data={},
                output_data={"result": "success"},
                confidence=round(random.uniform(0.85, 0.99), 2),
            ))

        # ── Sample Inventory Items (uses current_stock, not quantity) ──
        inventory_items = [
            {"name": "Salmon Fillet", "category": "Seafood", "unit": "kg", "current_stock": 2.5, "par_level": 8.0, "cost_per_unit": 24.50},
            {"name": "Wagyu Ribeye", "category": "Meat", "unit": "kg", "current_stock": 12.0, "par_level": 10.0, "cost_per_unit": 89.00},
            {"name": "Organic Mixed Greens", "category": "Produce", "unit": "kg", "current_stock": 5.2, "par_level": 8.0, "cost_per_unit": 6.80},
            {"name": "Truffle Oil", "category": "Specialty", "unit": "bottles", "current_stock": 6, "par_level": 4.0, "cost_per_unit": 32.00},
            {"name": "Prosecco DOC", "category": "Beverages", "unit": "bottles", "current_stock": 24, "par_level": 18.0, "cost_per_unit": 12.50},
            {"name": "Arborio Rice", "category": "Dry Goods", "unit": "kg", "current_stock": 15.0, "par_level": 10.0, "cost_per_unit": 4.20},
            {"name": "Heavy Cream", "category": "Dairy", "unit": "liters", "current_stock": 8.0, "par_level": 12.0, "cost_per_unit": 3.80},
            {"name": "Sourdough Bread", "category": "Bakery", "unit": "loaves", "current_stock": 18, "par_level": 20.0, "cost_per_unit": 5.50},
        ]

        for item in inventory_items:
            session.add(InventoryItem(**item))

        # ── Sample Guest Profiles (model uses: name, email, phone, visit_count, clv, churn_risk_score) ──
        guests = [
            {"name": "Sarah Chen", "email": "sarah.chen@email.com", "phone": "+1-555-0101", "visit_count": 47, "clv": 6840.00, "churn_risk_score": 0.05},
            {"name": "Michael Rodriguez", "email": "m.rodriguez@email.com", "phone": "+1-555-0102", "visit_count": 28, "clv": 3920.00, "churn_risk_score": 0.12},
            {"name": "Emma Thompson", "email": "emma.t@email.com", "phone": "+1-555-0103", "visit_count": 22, "clv": 2860.00, "churn_risk_score": 0.08},
            {"name": "James Park", "email": "james.park@email.com", "phone": "+1-555-0104", "visit_count": 15, "clv": 1950.00, "churn_risk_score": 0.25},
            {"name": "Olivia Martinez", "email": "olivia.m@email.com", "phone": "+1-555-0105", "visit_count": 12, "clv": 1440.00, "churn_risk_score": 0.35},
        ]

        for guest in guests:
            session.add(GuestProfile(**guest))

        # ── Sample Employees (model uses: name, email, role, hourly_rate, status) ──
        employees = [
            {"name": "Alex Johnson", "email": "alex.j@gestronomy.com", "role": "Head Chef", "hourly_rate": 35.00, "status": "active"},
            {"name": "Maria Santos", "email": "maria.s@gestronomy.com", "role": "Server", "hourly_rate": 18.00, "status": "active"},
            {"name": "David Kim", "email": "david.k@gestronomy.com", "role": "Sous Chef", "hourly_rate": 28.00, "status": "active"},
            {"name": "Lisa Brown", "email": "lisa.b@gestronomy.com", "role": "Bar Manager", "hourly_rate": 25.00, "status": "active"},
            {"name": "Ryan O'Brien", "email": "ryan.o@gestronomy.com", "role": "Server", "hourly_rate": 17.00, "status": "active"},
            {"name": "Sophie Laurent", "email": "sophie.l@gestronomy.com", "role": "Pastry Chef", "hourly_rate": 26.00, "status": "active"},
        ]

        for emp in employees:
            session.add(Employee(**emp))

        # ── Agent Configs (8 specialized agents) ──
        agent_configs = [
            {"agent_name": "FinanceAgent", "autonomy_level": "supervised", "is_active": True,
             "thresholds_json": {"description": "Monitors P&L, cash flow, invoices, and flags anomalies", "display_name": "Finance Agent"}},
            {"agent_name": "InventoryAgent", "autonomy_level": "full", "is_active": True,
             "thresholds_json": {"description": "Tracks stock levels, triggers auto-orders, manages PAR levels", "display_name": "Inventory Agent"}},
            {"agent_name": "WorkforceAgent", "autonomy_level": "supervised", "is_active": True,
             "thresholds_json": {"description": "Optimizes schedules, manages shifts, handles staffing gaps", "display_name": "Workforce Agent"}},
            {"agent_name": "QualityAgent", "autonomy_level": "full", "is_active": True,
             "thresholds_json": {"description": "Monitors food safety compliance, HACCP logs, temperature alerts", "display_name": "Quality Agent"}},
            {"agent_name": "GuestAgent", "autonomy_level": "supervised", "is_active": True,
             "thresholds_json": {"description": "Predicts churn risk, manages loyalty tiers, personalizes offers", "display_name": "Guest Agent"}},
            {"agent_name": "SupplyAgent", "autonomy_level": "full", "is_active": True,
             "thresholds_json": {"description": "Compares vendor pricing, optimizes procurement, tracks deliveries", "display_name": "Supply Agent"}},
            {"agent_name": "EnergyAgent", "autonomy_level": "full", "is_active": True,
             "thresholds_json": {"description": "Optimizes HVAC and equipment schedules to reduce energy costs", "display_name": "Energy Agent"}},
            {"agent_name": "MarketingAgent", "autonomy_level": "supervised", "is_active": False,
             "thresholds_json": {"description": "Generates social content, drafts review responses, manages campaigns", "display_name": "Marketing Agent"}},
        ]

        for config in agent_configs:
            session.add(AgentConfig(**config))

        await session.commit()
        print("Database seeded successfully!")
        print(f"   - {len(kpi_data)} current KPIs + {len(kpi_data) * 7} historical")
        print(f"   - {len(alerts)} alerts")
        print(f"   - {len(agent_actions)} agent actions")
        print(f"   - {len(inventory_items)} inventory items")
        print(f"   - {len(guests)} guest profiles")
        print(f"   - {len(employees)} employees")


if __name__ == "__main__":
    asyncio.run(seed())
