# Gestronomy — AI-Powered Restaurant Management System
# Complete Implementation Plan

---

## 1. TECH STACK

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend API** | Python 3.12 + FastAPI | Async-native, OpenAPI auto-docs, best AI/ML ecosystem |
| **Frontend** | Next.js 15 (App Router) + TypeScript | SSR, real-time, excellent DX |
| **Database** | PostgreSQL 16 + SQLAlchemy 2.0 | JSONB for flexible data, robust, production-proven |
| **Migrations** | Alembic | SQLAlchemy native, reliable schema versioning |
| **Cache / Pub-Sub** | Redis 7 | Real-time agent events, caching, session store |
| **Task Queue** | Celery + Redis broker | Background AI jobs, scheduled tasks, agent execution |
| **Real-Time** | WebSockets (FastAPI) + Socket.io (Next.js) | Live dashboard updates, agent activity feed |
| **AI/LLM** | Anthropic Claude API / OpenAI API | Natural language queries, agent reasoning, content generation |
| **ML/Forecasting** | scikit-learn, Prophet, statsmodels | Time-series forecasting, anomaly detection, classification |
| **Computer Vision** | OpenCV + ultralytics (YOLOv8) | Portion detection, PPE compliance, waste classification |
| **OCR** | Tesseract + pytesseract | Invoice/receipt processing |
| **Auth** | JWT (python-jose) + bcrypt | Stateless auth, secure password hashing |
| **Validation** | Pydantic v2 | Request/response validation, settings management |
| **Testing** | pytest + httpx (backend), Jest + Playwright (frontend) | Full coverage strategy |
| **Containerization** | Docker + Docker Compose | Reproducible dev/prod environments |
| **CSS** | Tailwind CSS 4 + shadcn/ui | Rapid UI development, consistent design system |
| **State Management** | Zustand + TanStack Query | Lightweight global state + server state caching |
| **Charts** | Recharts | Dashboard visualizations |

---

## 2. MONOREPO STRUCTURE

```
gestronomy/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── README.md
├── Makefile                        # Common commands (make dev, make test, etc.)
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml              # Python dependencies (Poetry/uv)
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/              # Migration files
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entry, middleware, CORS
│   │   ├── config.py              # Settings via Pydantic BaseSettings
│   │   ├── database.py            # SQLAlchemy engine, session factory
│   │   ├── dependencies.py        # Shared FastAPI dependencies
│   │   │
│   │   ├── auth/
│   │   │   ├── router.py          # /auth/login, /auth/register, /auth/me
│   │   │   ├── service.py         # Auth business logic
│   │   │   ├── models.py          # User, Role SQLAlchemy models
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   └── utils.py           # JWT encode/decode, password hashing
│   │   │
│   │   ├── core/                  # MODULE A — Agentic AI Core
│   │   │   ├── router.py          # /agents/status, /agents/actions, /agents/logs
│   │   │   ├── meta_agent.py      # MetaAgent orchestrator
│   │   │   ├── base_agent.py      # Abstract base class for all agents
│   │   │   ├── agent_registry.py  # Agent discovery and lifecycle
│   │   │   ├── agents/
│   │   │   │   ├── finance_agent.py
│   │   │   │   ├── inventory_agent.py
│   │   │   │   ├── labor_agent.py
│   │   │   │   ├── quality_agent.py
│   │   │   │   ├── guest_agent.py
│   │   │   │   ├── supply_agent.py
│   │   │   │   ├── energy_agent.py
│   │   │   │   └── marketing_agent.py
│   │   │   ├── schemas.py
│   │   │   └── models.py         # AgentAction, AgentLog DB models
│   │   │
│   │   ├── accounting/            # MODULE B — Zero-Touch Accounting
│   │   │   ├── router.py         # /accounting/invoices, /gl, /reports, /tax
│   │   │   ├── service.py
│   │   │   ├── models.py         # Invoice, GLEntry, Account, Budget, TaxFiling
│   │   │   ├── schemas.py
│   │   │   ├── ocr_processor.py  # Invoice OCR pipeline
│   │   │   └── reconciliation.py # Auto-reconciliation engine
│   │   │
│   │   ├── vision/               # MODULE C — Computer Vision Kitchen
│   │   │   ├── router.py         # /vision/alerts, /vision/waste, /vision/compliance
│   │   │   ├── service.py
│   │   │   ├── models.py         # VisionAlert, WasteLog, ComplianceEvent
│   │   │   ├── schemas.py
│   │   │   ├── pipeline.py       # CV processing pipeline (YOLO + custom models)
│   │   │   ├── portion_analyzer.py
│   │   │   ├── safety_monitor.py
│   │   │   └── waste_classifier.py
│   │   │
│   │   ├── forecasting/          # MODULE D — Demand Forecasting
│   │   │   ├── router.py         # /forecast/sales, /forecast/items, /forecast/labor
│   │   │   ├── service.py
│   │   │   ├── models.py         # Forecast, ForecastInput, ForecastAccuracy
│   │   │   ├── schemas.py
│   │   │   ├── engine.py         # Forecasting model orchestration
│   │   │   ├── features.py       # Feature engineering (40+ variables)
│   │   │   └── trainers/
│   │   │       ├── prophet_trainer.py
│   │   │       └── lstm_trainer.py
│   │   │
│   │   ├── inventory/            # MODULE E — Inventory & Supply Chain
│   │   │   ├── router.py         # /inventory/items, /orders, /vendors, /tva
│   │   │   ├── service.py
│   │   │   ├── models.py         # InventoryItem, PurchaseOrder, Vendor, Receipt
│   │   │   ├── schemas.py
│   │   │   ├── auto_ordering.py  # Autonomous procurement logic
│   │   │   └── vendor_intelligence.py
│   │   │
│   │   ├── workforce/            # MODULE F — Workforce Management
│   │   │   ├── router.py         # /workforce/schedule, /employees, /hiring, /training
│   │   │   ├── service.py
│   │   │   ├── models.py         # Employee, Schedule, Shift, Applicant, Training
│   │   │   ├── schemas.py
│   │   │   ├── scheduler.py      # AI scheduling engine
│   │   │   ├── hiring_pipeline.py
│   │   │   └── lms.py           # Learning management system
│   │   │
│   │   ├── guests/               # MODULE G — Guest Intelligence
│   │   │   ├── router.py         # /guests/profiles, /loyalty, /churn, /pricing
│   │   │   ├── service.py
│   │   │   ├── models.py         # GuestProfile, LoyaltyAccount, Order, ChurnScore
│   │   │   ├── schemas.py
│   │   │   ├── personalization.py
│   │   │   ├── churn_predictor.py
│   │   │   └── dynamic_pricing.py
│   │   │
│   │   ├── dashboard/            # MODULE H — Financial Dashboard
│   │   │   ├── router.py         # /dashboard/live, /dashboard/query, /dashboard/alerts
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   ├── nl_query.py       # Natural language query engine (LLM-powered)
│   │   │   └── websocket.py      # WebSocket handlers for real-time data
│   │   │
│   │   ├── maintenance/          # MODULE I — Predictive Maintenance & Energy
│   │   │   ├── router.py         # /maintenance/equipment, /energy, /alerts
│   │   │   ├── service.py
│   │   │   ├── models.py         # Equipment, MaintenanceTicket, EnergyReading, IoTSensor
│   │   │   ├── schemas.py
│   │   │   ├── failure_predictor.py
│   │   │   └── energy_optimizer.py
│   │   │
│   │   ├── digital_twin/         # MODULE J — Digital Twin Simulation
│   │   │   ├── router.py         # /simulation/scenarios, /simulation/run, /results
│   │   │   ├── service.py
│   │   │   ├── models.py         # Scenario, SimulationRun, SimulationResult
│   │   │   ├── schemas.py
│   │   │   ├── simulator.py      # Core simulation engine
│   │   │   └── scenario_builder.py
│   │   │
│   │   ├── food_safety/          # MODULE K — Food Safety & Compliance
│   │   │   ├── router.py         # /safety/haccp, /safety/temperature, /safety/allergens
│   │   │   ├── service.py
│   │   │   ├── models.py         # HACCPLog, TempReading, AllergenAlert, ComplianceScore
│   │   │   ├── schemas.py
│   │   │   ├── haccp_engine.py
│   │   │   └── compliance_assistant.py  # LLM-powered food safety Q&A
│   │   │
│   │   ├── franchise/            # MODULE L — Multi-Location Intelligence
│   │   │   ├── router.py         # /franchise/locations, /benchmarks, /compliance
│   │   │   ├── service.py
│   │   │   ├── models.py         # Location, LocationMetric, Benchmark
│   │   │   ├── schemas.py
│   │   │   └── benchmarking.py
│   │   │
│   │   ├── marketing/            # MODULE M — Marketing & Reputation
│   │   │   ├── router.py         # /marketing/reviews, /campaigns, /social, /seo
│   │   │   ├── service.py
│   │   │   ├── models.py         # Review, Campaign, SocialPost, SEOMetric
│   │   │   ├── schemas.py
│   │   │   ├── review_monitor.py
│   │   │   ├── content_generator.py  # AI content generation
│   │   │   └── reputation_engine.py
│   │   │
│   │   ├── shared/               # Shared utilities
│   │   │   ├── events.py         # Redis pub/sub event bus
│   │   │   ├── llm.py            # LLM client wrapper (Claude/OpenAI)
│   │   │   ├── notifications.py  # Push/email/SMS notification service
│   │   │   ├── pagination.py     # Pagination helpers
│   │   │   ├── exceptions.py     # Custom exception classes
│   │   │   └── constants.py      # Shared enums and constants
│   │   │
│   │   └── websockets/           # WebSocket hub
│   │       ├── manager.py        # Connection manager
│   │       └── handlers.py       # Event handlers for real-time updates
│   │
│   └── tests/
│       ├── conftest.py           # Fixtures, test DB setup
│       ├── test_auth/
│       ├── test_core/
│       ├── test_accounting/
│       ├── test_vision/
│       ├── test_forecasting/
│       ├── test_inventory/
│       ├── test_workforce/
│       ├── test_guests/
│       ├── test_dashboard/
│       ├── test_maintenance/
│       ├── test_digital_twin/
│       ├── test_food_safety/
│       ├── test_franchise/
│       └── test_marketing/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── components.json          # shadcn/ui config
│   │
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── layout.tsx       # Root layout (sidebar, providers)
│   │   │   ├── page.tsx         # Landing / redirect to dashboard
│   │   │   ├── globals.css
│   │   │   │
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   │
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx           # Dashboard layout (sidebar + header)
│   │   │   │   ├── page.tsx             # MODULE H — Live Command Center
│   │   │   │   │
│   │   │   │   ├── agents/              # MODULE A
│   │   │   │   │   ├── page.tsx         # Agent fleet overview
│   │   │   │   │   └── [id]/page.tsx    # Individual agent detail
│   │   │   │   │
│   │   │   │   ├── accounting/          # MODULE B
│   │   │   │   │   ├── page.tsx         # P&L, GL overview
│   │   │   │   │   ├── invoices/page.tsx
│   │   │   │   │   ├── reports/page.tsx
│   │   │   │   │   └── tax/page.tsx
│   │   │   │   │
│   │   │   │   ├── kitchen/             # MODULE C
│   │   │   │   │   ├── page.tsx         # Vision dashboard
│   │   │   │   │   ├── alerts/page.tsx
│   │   │   │   │   └── waste/page.tsx
│   │   │   │   │
│   │   │   │   ├── forecasting/         # MODULE D
│   │   │   │   │   └── page.tsx         # Forecast charts + accuracy
│   │   │   │   │
│   │   │   │   ├── inventory/           # MODULE E
│   │   │   │   │   ├── page.tsx         # Stock levels
│   │   │   │   │   ├── orders/page.tsx  # Purchase orders
│   │   │   │   │   └── vendors/page.tsx
│   │   │   │   │
│   │   │   │   ├── workforce/           # MODULE F
│   │   │   │   │   ├── page.tsx         # Schedule view
│   │   │   │   │   ├── employees/page.tsx
│   │   │   │   │   ├── hiring/page.tsx
│   │   │   │   │   └── training/page.tsx
│   │   │   │   │
│   │   │   │   ├── guests/              # MODULE G
│   │   │   │   │   ├── page.tsx         # Guest profiles
│   │   │   │   │   ├── loyalty/page.tsx
│   │   │   │   │   └── pricing/page.tsx
│   │   │   │   │
│   │   │   │   ├── maintenance/         # MODULE I
│   │   │   │   │   ├── page.tsx         # Equipment dashboard
│   │   │   │   │   └── energy/page.tsx
│   │   │   │   │
│   │   │   │   ├── simulation/          # MODULE J
│   │   │   │   │   ├── page.tsx         # Scenario builder
│   │   │   │   │   └── results/page.tsx
│   │   │   │   │
│   │   │   │   ├── safety/              # MODULE K
│   │   │   │   │   ├── page.tsx         # Compliance dashboard
│   │   │   │   │   └── haccp/page.tsx
│   │   │   │   │
│   │   │   │   ├── franchise/           # MODULE L
│   │   │   │   │   ├── page.tsx         # Multi-location overview
│   │   │   │   │   └── [locationId]/page.tsx
│   │   │   │   │
│   │   │   │   ├── marketing/           # MODULE M
│   │   │   │   │   ├── page.tsx         # Reputation dashboard
│   │   │   │   │   ├── reviews/page.tsx
│   │   │   │   │   └── campaigns/page.tsx
│   │   │   │   │
│   │   │   │   └── settings/
│   │   │   │       └── page.tsx         # System settings
│   │   │   │
│   │   │   └── api/                     # Next.js API routes (proxy/BFF)
│   │   │       └── [...proxy]/route.ts  # Proxy to FastAPI backend
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                      # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── chart.tsx
│   │   │   │   └── ...                  # All shadcn components
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── sidebar.tsx          # Main navigation sidebar
│   │   │   │   ├── header.tsx           # Top bar with search + notifications
│   │   │   │   ├── mobile-nav.tsx
│   │   │   │   └── breadcrumbs.tsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── live-metrics.tsx     # Real-time KPI cards
│   │   │   │   ├── agent-activity.tsx   # Agent action log feed
│   │   │   │   ├── ai-chat.tsx          # Natural language query panel
│   │   │   │   └── alerts-panel.tsx     # Active alerts
│   │   │   │
│   │   │   └── shared/
│   │   │       ├── data-table.tsx       # Reusable data table
│   │   │       ├── stat-card.tsx        # KPI stat card
│   │   │       ├── loading.tsx
│   │   │       └── error-boundary.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                   # API client (axios/fetch wrapper)
│   │   │   ├── auth.ts                  # Auth helpers, token management
│   │   │   ├── websocket.ts             # WebSocket client
│   │   │   └── utils.ts                 # Formatters, helpers
│   │   │
│   │   ├── stores/
│   │   │   ├── auth-store.ts            # Zustand auth state
│   │   │   ├── dashboard-store.ts       # Live dashboard state
│   │   │   └── notification-store.ts    # Notification state
│   │   │
│   │   └── types/
│   │       ├── api.ts                   # API response types
│   │       ├── models.ts               # Shared model types
│   │       └── agents.ts               # Agent-related types
│   │
│   └── tests/
│       ├── e2e/                         # Playwright E2E tests
│       └── unit/                        # Jest unit tests
│
└── infrastructure/
    ├── nginx/
    │   └── nginx.conf                   # Reverse proxy config
    └── scripts/
        ├── seed.py                      # Database seeding script
        └── generate_mock_data.py        # Generate realistic test data
```

---

## 3. DATABASE SCHEMA (Key Tables by Module)

### Shared / Auth
- **users** (id, email, password_hash, full_name, role, is_active, created_at)
- **restaurant** (id, name, address, timezone, currency, settings_json, created_at)

### Module A — Agentic Core
- **agent_actions** (id, agent_name, action_type, description, input_data, output_data, status, confidence, requires_approval, approved_by, created_at)
- **agent_logs** (id, agent_name, level, message, context_json, created_at)
- **agent_configs** (id, agent_name, autonomy_level, thresholds_json, is_active)

### Module B — Accounting
- **chart_of_accounts** (id, code, name, type, parent_id, is_active)
- **gl_entries** (id, account_id, date, debit, credit, description, source_type, source_id, created_by)
- **invoices** (id, vendor_id, invoice_number, date, due_date, total, status, ocr_confidence, raw_image_url, line_items_json)
- **budgets** (id, account_id, period, amount, actual_amount)
- **reconciliations** (id, bank_transaction_id, gl_entry_id, status, matched_at)

### Module C — Computer Vision
- **vision_alerts** (id, alert_type, severity, description, image_url, confidence, station, resolved, created_at)
- **waste_logs** (id, item_id, category, weight_g, cost, reason, image_url, created_at)
- **compliance_events** (id, event_type, employee_id, station, details, image_url, created_at)

### Module D — Forecasting
- **forecasts** (id, forecast_type, target_date, item_id, predicted_value, confidence_lower, confidence_upper, actual_value, model_version, created_at)
- **forecast_inputs** (id, forecast_id, variable_name, variable_value)

### Module E — Inventory
- **inventory_items** (id, name, category, unit, current_stock, par_level, cost_per_unit, vendor_id, location, last_counted_at)
- **purchase_orders** (id, vendor_id, status, total, order_date, delivery_date, auto_generated, line_items_json)
- **vendors** (id, name, contact_info, reliability_score, avg_delivery_days, pricing_json, is_active)
- **inventory_movements** (id, item_id, quantity, movement_type, reason, created_at)
- **tva_reports** (id, item_id, period, theoretical_usage, actual_usage, variance, variance_cost)

### Module F — Workforce
- **employees** (id, user_id, name, role, hourly_rate, skills_json, certifications_json, hire_date, status)
- **schedules** (id, week_start, status, total_hours, total_cost, auto_generated, approved_by)
- **shifts** (id, schedule_id, employee_id, date, start_time, end_time, role, station, actual_clock_in, actual_clock_out)
- **applicants** (id, name, email, position, resume_url, ai_match_score, status, created_at)
- **training_modules** (id, title, category, duration_min, content_url, required_for_roles)
- **training_progress** (id, employee_id, module_id, status, score, completed_at)

### Module G — Guests
- **guest_profiles** (id, name, email, phone, dietary_json, flavor_profile_json, clv, churn_risk_score, visit_count, last_visit, created_at)
- **orders** (id, guest_id, order_date, channel, total, items_json, discount, tip)
- **loyalty_accounts** (id, guest_id, tier, points, rewards_json)
- **promotions** (id, guest_id, type, offer, status, sent_at, redeemed_at)

### Module H — Dashboard
- **dashboard_queries** (id, user_id, query_text, ai_response, response_data_json, created_at)
- **alerts** (id, module, severity, title, message, is_read, action_taken, created_at)
- **kpi_snapshots** (id, metric_name, value, previous_value, target_value, timestamp)

### Module I — Maintenance & Energy
- **equipment** (id, name, type, location, model, serial_number, install_date, last_service, health_score, status)
- **iot_readings** (id, equipment_id, sensor_type, value, unit, timestamp)
- **maintenance_tickets** (id, equipment_id, issue, priority, status, auto_generated, technician, resolved_at)
- **energy_readings** (id, zone, reading_kwh, cost, timestamp)

### Module J — Digital Twin
- **scenarios** (id, name, description, scenario_type, parameters_json, created_by, created_at)
- **simulation_runs** (id, scenario_id, status, results_json, started_at, completed_at)

### Module K — Food Safety
- **haccp_logs** (id, check_type, station, value, is_compliant, auto_logged, created_at)
- **temperature_readings** (id, location, sensor_id, temp_f, is_safe, timestamp)
- **allergen_alerts** (id, order_id, allergen, guest_id, severity, action_taken, created_at)
- **compliance_scores** (id, date, score, violations_count, auto_resolved, manual_resolved)

### Module L — Franchise
- **locations** (id, restaurant_id, name, address, region, manager_id, is_active)
- **location_metrics** (id, location_id, date, food_cost_pct, labor_cost_pct, net_margin, guest_score, compliance_score)
- **benchmarks** (id, metric_name, group_avg, top_performer_id, bottom_performer_id, date)

### Module M — Marketing
- **reviews** (id, platform, rating, text, sentiment_score, ai_response, response_status, created_at)
- **campaigns** (id, name, type, target_segment, content, status, sent_count, open_rate, conversion_rate)
- **social_posts** (id, platform, content, media_urls, status, engagement_json, scheduled_at, published_at)

---

## 4. API DESIGN (Key Endpoints)

### Auth
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
POST   /api/auth/refresh
```

### Module A — Agents
```
GET    /api/agents                    # List all agents + status
GET    /api/agents/{name}             # Agent detail
GET    /api/agents/{name}/actions     # Agent action history
POST   /api/agents/{name}/approve     # Approve pending action
POST   /api/agents/{name}/config      # Update agent configuration
GET    /api/agents/activity-feed      # WebSocket: live agent activity
```

### Module B — Accounting
```
GET    /api/accounting/gl             # General ledger entries
GET    /api/accounting/pl             # P&L report
GET    /api/accounting/invoices       # List invoices
POST   /api/accounting/invoices       # Upload/create invoice
POST   /api/accounting/invoices/ocr   # OCR process invoice image
GET    /api/accounting/cash-flow      # Cash flow forecast
GET    /api/accounting/budgets        # Budget vs actual
GET    /api/accounting/reports/{type} # Generate specific report
```

### Module C — Vision
```
GET    /api/vision/alerts             # Active vision alerts
GET    /api/vision/waste              # Waste tracking log
GET    /api/vision/compliance         # Compliance events
POST   /api/vision/analyze            # Submit image for analysis
GET    /api/vision/stats              # Vision system stats
```

### Module D — Forecasting
```
GET    /api/forecast/sales            # Sales forecast
GET    /api/forecast/items/{id}       # Per-item forecast
GET    /api/forecast/labor            # Labor demand forecast
GET    /api/forecast/accuracy         # Model accuracy metrics
POST   /api/forecast/retrain          # Trigger model retrain
```

### Module E — Inventory
```
GET    /api/inventory/items           # All inventory items
PUT    /api/inventory/items/{id}      # Update item (count, par)
GET    /api/inventory/orders          # Purchase orders
POST   /api/inventory/orders          # Create PO (manual)
GET    /api/inventory/vendors         # Vendor list
GET    /api/inventory/tva             # TVA report
GET    /api/inventory/low-stock       # Items below PAR
```

### Module F — Workforce
```
GET    /api/workforce/schedule        # Current schedule
POST   /api/workforce/schedule/generate  # AI generate schedule
PUT    /api/workforce/schedule/{id}/approve
GET    /api/workforce/employees       # Employee list
POST   /api/workforce/employees       # Add employee
GET    /api/workforce/labor-tracker   # Live labor % vs sales
GET    /api/workforce/hiring          # Applicant pipeline
GET    /api/workforce/training        # Training modules + progress
```

### Module G — Guests
```
GET    /api/guests                    # Guest profiles
GET    /api/guests/{id}               # Guest detail (360° view)
GET    /api/guests/churn-risk         # At-risk guests
GET    /api/guests/loyalty            # Loyalty program overview
POST   /api/guests/promotions         # Send targeted promotion
GET    /api/guests/pricing            # Dynamic pricing status
```

### Module H — Dashboard
```
GET    /api/dashboard/live            # WebSocket: live KPIs
GET    /api/dashboard/alerts          # Active alerts
POST   /api/dashboard/query           # Natural language query
GET    /api/dashboard/kpis            # KPI summary
GET    /api/dashboard/snapshot        # Point-in-time snapshot
```

### Module I — Maintenance
```
GET    /api/maintenance/equipment     # Equipment list
GET    /api/maintenance/equipment/{id} # Equipment detail + health
GET    /api/maintenance/tickets       # Maintenance tickets
GET    /api/maintenance/predictions   # Failure predictions
GET    /api/energy/usage              # Energy consumption
GET    /api/energy/savings            # Optimization recommendations
```

### Module J — Digital Twin
```
GET    /api/simulation/scenarios      # Saved scenarios
POST   /api/simulation/scenarios      # Create scenario
POST   /api/simulation/run            # Run simulation
GET    /api/simulation/results/{id}   # Simulation results
```

### Module K — Food Safety
```
GET    /api/safety/haccp              # HACCP log
GET    /api/safety/temperatures       # Temperature readings
GET    /api/safety/allergens          # Allergen alerts
GET    /api/safety/compliance-score   # Daily compliance score
POST   /api/safety/ask                # AI compliance assistant
```

### Module L — Franchise
```
GET    /api/franchise/locations        # All locations
GET    /api/franchise/locations/{id}   # Location detail
GET    /api/franchise/benchmarks       # Cross-location benchmarks
GET    /api/franchise/rankings         # Location rankings
GET    /api/franchise/anomalies        # Detected anomalies
```

### Module M — Marketing
```
GET    /api/marketing/reviews          # Reviews across platforms
POST   /api/marketing/reviews/{id}/respond # AI respond to review
GET    /api/marketing/campaigns        # Campaign list
POST   /api/marketing/campaigns        # Create campaign
GET    /api/marketing/social           # Social posts
POST   /api/marketing/social/generate  # AI generate content
GET    /api/marketing/reputation       # Reputation score + trends
```

---

## 5. AGENT SYSTEM ARCHITECTURE

### Communication Pattern: Event-Driven via Redis Pub/Sub

```
┌─────────────────────────────────────────────┐
│              MetaAgent (Orchestrator)         │
│  - Subscribes to ALL agent channels          │
│  - Resolves cross-agent conflicts            │
│  - Manages priority queue                    │
│  - Escalates to human when confidence < threshold │
│  - Generates daily summary reports           │
└─────────────────┬───────────────────────────┘
                  │ Redis Pub/Sub
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Finance │ │Inventory│ │ Labor   │  ... (8 agents)
│ Agent   │ │ Agent   │ │ Agent   │
└─────────┘ └─────────┘ └─────────┘

Each agent follows the loop:
  PERCEIVE → REASON → PLAN → ACT → VERIFY → LEARN → REPORT
```

### Base Agent Interface:
```python
class BaseAgent(ABC):
    name: str
    autonomy_level: str  # "full", "semi", "human_required"
    confidence_threshold: float  # Below this → escalate to human

    async def perceive(self) -> dict        # Read live data
    async def reason(self, data) -> dict    # Analyze with AI
    async def plan(self, analysis) -> list  # Generate action options
    async def act(self, action) -> dict     # Execute approved action
    async def verify(self, result) -> bool  # Confirm success
    async def learn(self, outcome) -> None  # Update internal model
    async def report(self, log) -> None     # Log to audit trail
```

### Event Flow Example:
1. IoT sensor → publishes `sensor.temperature.alert` to Redis
2. QualityAgent subscribes, picks it up
3. QualityAgent reasons: "Walk-in cooler at 48°F, threshold 40°F"
4. QualityAgent plans: [dispatch maintenance ticket, alert manager]
5. QualityAgent acts: creates MaintenanceTicket, publishes `agent.action.quality`
6. MetaAgent logs the action, notifies frontend via WebSocket
7. EnergyAgent also reacts: adjusts HVAC to compensate

---

## 6. IMPLEMENTATION PHASES

### PHASE 1 — Foundation (Week 1-2)
**Goal: Project scaffolding, auth, database, and basic infrastructure**

- [ ] Initialize monorepo structure (backend + frontend)
- [ ] Set up Docker Compose (PostgreSQL, Redis, backend, frontend)
- [ ] Configure FastAPI app with CORS, middleware, error handling
- [ ] Set up SQLAlchemy + Alembic with base models
- [ ] Implement auth system (register, login, JWT, middleware)
- [ ] Set up Next.js with Tailwind + shadcn/ui
- [ ] Build dashboard layout (sidebar, header, routing)
- [ ] Create API client + auth flow in frontend
- [ ] Set up Redis connection + event bus foundation
- [ ] Set up Celery for background tasks
- [ ] Create database seed script with realistic demo data

### PHASE 2 — Dashboard & Real-Time Core (Week 3-4)
**Goal: MODULE H (Dashboard) + MODULE A (Agent Core) — the system's nerve center**

- [ ] Build KPI snapshot API + live data WebSocket
- [ ] Create live command center dashboard (real-time metrics)
- [ ] Implement agent base class + MetaAgent orchestrator
- [ ] Build agent action logging + activity feed API
- [ ] Create alerts system (create, read, resolve)
- [ ] Build NL query engine with LLM integration (Claude API)
- [ ] Frontend: live metrics cards, agent activity feed, AI chat panel
- [ ] Frontend: alerts panel with severity and actions

### PHASE 3 — Financial Engine (Week 5-6)
**Goal: MODULE B (Accounting) + MODULE H enhancements**

- [ ] Chart of accounts CRUD + GL entry system
- [ ] P&L report generation (automated)
- [ ] Invoice processing pipeline (upload → OCR → classify → approve)
- [ ] Budget system (create, track, auto-adjust)
- [ ] Cash flow forecasting (90-day rolling)
- [ ] FinanceAgent: anomaly detection, auto-GL coding
- [ ] Frontend: accounting pages (GL, invoices, P&L, budgets)
- [ ] Frontend: financial reports with export

### PHASE 4 — Forecasting & Inventory (Week 7-9)
**Goal: MODULE D (Forecasting) + MODULE E (Inventory) — operational backbone**

- [ ] Feature engineering pipeline (40+ variables)
- [ ] Time-series forecasting engine (Prophet + custom)
- [ ] Per-item, per-hour sales forecast API
- [ ] Forecast accuracy tracking + self-correction
- [ ] Inventory item management + stock tracking
- [ ] PAR level engine (AI-calculated minimums)
- [ ] Auto-ordering system (forecast → PO generation)
- [ ] Vendor management + intelligence (scoring, price watching)
- [ ] TVA (Theoretical vs Actual) analysis engine
- [ ] InventoryAgent + SupplyAgent implementation
- [ ] Frontend: forecast dashboard, inventory management, vendor pages

### PHASE 5 — Workforce Management (Week 10-11)
**Goal: MODULE F (Workforce) — AI scheduling + HR**

- [ ] Employee management (CRUD, skills matrix, certifications)
- [ ] AI scheduling engine (40+ variable optimization)
- [ ] Shift management (create, swap, approve)
- [ ] Labor vs. sales real-time tracker
- [ ] Hiring pipeline (applicant tracking, AI screening)
- [ ] Training LMS (modules, progress, certification tracking)
- [ ] LaborAgent implementation
- [ ] Frontend: schedule view, employee management, hiring, training

### PHASE 6 — Guest Intelligence & Marketing (Week 12-13)
**Goal: MODULE G (Guests) + MODULE M (Marketing)**

- [ ] 360° guest profile system
- [ ] Order history tracking + behavioral analysis
- [ ] Churn prediction model
- [ ] Loyalty program engine (tiers, points, rewards)
- [ ] Dynamic pricing engine
- [ ] GuestAgent implementation
- [ ] Review monitoring + sentiment analysis
- [ ] AI review response generation
- [ ] Campaign management (create, target, send)
- [ ] Social content AI generation
- [ ] MarketingAgent implementation
- [ ] Frontend: guest profiles, loyalty, reviews, campaigns

### PHASE 7 — Kitchen Intelligence & Safety (Week 14-15)
**Goal: MODULE C (Computer Vision) + MODULE K (Food Safety)**

- [ ] Computer vision pipeline (image upload → multi-model analysis)
- [ ] Portion control analysis
- [ ] Waste classification + tracking
- [ ] Hygiene/PPE compliance detection
- [ ] HACCP digital log system (auto + manual entries)
- [ ] Continuous temperature monitoring system
- [ ] Allergen management + real-time alerts
- [ ] AI compliance assistant (LLM-powered Q&A)
- [ ] Compliance scoring engine
- [ ] QualityAgent implementation
- [ ] Frontend: kitchen dashboard, waste tracking, HACCP logs, compliance

### PHASE 8 — Maintenance, Energy & Digital Twin (Week 16-17)
**Goal: MODULE I (Maintenance) + MODULE J (Digital Twin)**

- [ ] Equipment registry + health scoring
- [ ] IoT reading ingestion pipeline
- [ ] Predictive failure model (anomaly detection)
- [ ] Maintenance ticket automation
- [ ] Energy consumption tracking
- [ ] Energy optimization recommendations
- [ ] EnergyAgent implementation
- [ ] Digital Twin simulation engine
- [ ] Scenario builder (pricing, menu, hours, staffing)
- [ ] What-if analysis with financial projections
- [ ] Frontend: equipment dashboard, energy, simulation builder

### PHASE 9 — Multi-Location & Integration (Week 18-19)
**Goal: MODULE L (Franchise) + system-wide polish**

- [ ] Multi-location data model extensions
- [ ] Cross-location benchmarking engine
- [ ] Location ranking system (hourly updates)
- [ ] Anomaly detection across portfolio
- [ ] Best-practice identification + sharing
- [ ] Franchise compliance scoring
- [ ] Frontend: multi-location overview, rankings, benchmarks

### PHASE 10 — Integration, Testing & Production Readiness (Week 20-22)
**Goal: System-wide integration, E2E testing, deployment**

- [ ] Full agent integration testing (all 8 agents + MetaAgent)
- [ ] Cross-module event flow testing
- [ ] Performance optimization (DB queries, caching, pagination)
- [ ] Security audit (auth, input validation, SQL injection)
- [ ] API documentation finalization (OpenAPI)
- [ ] E2E test suite (Playwright) for critical flows
- [ ] Load testing for WebSocket connections
- [ ] Production Docker configuration
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring + logging setup
- [ ] Production deployment guide

---

## 7. KEY ARCHITECTURAL DECISIONS

1. **Monorepo** — Backend + frontend in one repo for easier development and deployment coordination
2. **Event-driven agents** — Redis pub/sub for agent communication (lightweight, fast, scales well)
3. **Celery for heavy AI tasks** — Forecasting, CV processing, report generation run as async tasks
4. **WebSocket for real-time** — Dashboard and agent activity feed use WebSocket for sub-second updates
5. **LLM abstraction layer** — `shared/llm.py` wraps Claude/OpenAI so we can switch providers easily
6. **Database-first design** — All state in PostgreSQL, Redis only for cache/pub-sub/sessions
7. **API-first** — Full OpenAPI documentation, frontend uses typed API client
8. **Modular architecture** — Each module is a self-contained FastAPI router package with its own models, schemas, services
9. **Single restaurant first** — No multi-tenant complexity; `restaurant` table exists for future expansion
10. **Seed data** — Realistic demo data generator for development and demos

---

## 8. DOCKER COMPOSE (Development)

```yaml
services:
  db:         PostgreSQL 16 on port 5432
  redis:      Redis 7 on port 6379
  backend:    FastAPI on port 8000 (hot reload)
  celery:     Celery worker
  celery-beat: Celery periodic task scheduler
  frontend:   Next.js on port 3000 (hot reload)
```

**Single command to start:** `make dev` → `docker compose up`

---

## 9. ADVANCED FEATURES (Beyond the Vision Document)

These are cutting-edge features that go beyond the original 13-module vision, positioning Gestronomy as a next-generation platform.

### 🧠 A1. Autonomous Agent-to-Agent Negotiation
Agents don't just report to MetaAgent — they negotiate with each other. Example: InventoryAgent wants to order expensive wagyu, but FinanceAgent flags cash flow is tight. They autonomously reach a compromise (order half now, half next week) without human intervention. Uses a **multi-agent debate protocol** where agents present arguments and MetaAgent arbitrates.

### 🗣️ A2. Voice-First Command Interface (Whisper + TTS)
Full voice interface using OpenAI Whisper (speech-to-text) + ElevenLabs/OpenAI TTS. Managers walk through the kitchen and say: "Hey Gestronomy, how are we doing tonight?" — and get a spoken real-time summary. Implemented as a WebSocket audio stream with server-side Whisper processing.

```
Microphone → WebSocket → Whisper STT → NL Query Engine → LLM → TTS → Speaker
```

### 📱 A3. Progressive Web App (PWA) + Push Notifications
The Next.js frontend ships as a PWA with:
- Offline mode (cached dashboards, last-known KPIs)
- Push notifications for critical agent alerts (cooler temp, labor overage)
- Install-to-homescreen for mobile-first managers
- Background sync for pending approvals

### 🔮 A4. Predictive Menu Engineering AI
Goes beyond the Digital Twin. Uses guest order data + ingredient costs + prep time + margin analysis to:
- Auto-rank every menu item by profitability × popularity (Stars/Plowhorses/Puzzles/Dogs matrix)
- Suggest new menu items based on trending flavor profiles in your market
- Auto-generate seasonal menu recommendations with projected financial impact
- A/B test menu layouts in the app and measure conversion

### 🌐 A5. Real-Time Supplier Marketplace
Instead of fixed vendor relationships, build a **live bidding system** where:
- The system broadcasts purchase needs to qualified suppliers
- Suppliers can bid in real-time (price, delivery time, quality guarantee)
- AI auto-selects the best bid based on weighted scoring (price, reliability, freshness)
- Creates a competitive market that drives costs down automatically

### 📊 A6. AI-Powered "Why" Engine (Causal Analysis)
Not just "what happened" but "why it happened." Uses causal inference models to:
- "Why did revenue drop 12% Tuesday?" → "Rain (-8%) + competitor promo nearby (-4%)"
- "Why is Location #47 underperforming?" → "New manager (inexperienced scheduling) + HVAC issues (guest complaints about temperature)"
- Automatically attributes root causes with confidence scores and suggests corrective actions

### 🎮 A7. Gamification & Staff Engagement Engine
Turn restaurant operations into an engaging experience:
- **Leaderboards**: Kitchen speed, food waste reduction, guest satisfaction scores per employee
- **Achievements**: "Zero waste day", "Perfect compliance week", "5-star review streak"
- **Challenges**: Team-based competitions (e.g., "Which shift can hit the lowest food cost %?")
- **Rewards integration**: Earn points → redeem for extra PTO, shift preferences, bonuses
- Real-time scoreboard displayed on kitchen displays

### 🛡️ A8. AI Fraud Detection & Loss Prevention
Advanced anomaly detection specifically for restaurant fraud:
- **Void/comp abuse detection**: AI flags employees with statistically unusual void/discount patterns
- **Cash handling anomalies**: Expected cash vs actual drawer count, trend analysis
- **Inventory shrinkage**: Computer vision at delivery + prep tracks every item — AI detects unexplained losses
- **Time theft detection**: Correlates clock-in location (geofence) + POS activity patterns
- **Supplier kickback detection**: Flags when a manager consistently selects higher-priced vendors

### 🧪 A9. A/B Testing Platform (Built-In Experimentation)
Run controlled experiments on anything:
- **Price testing**: Different prices for same item at different times/channels
- **Menu layout testing**: Different menu orderings in the app for different guest segments
- **Promotion testing**: Test offer types (% off vs $ off vs free item) with statistical significance
- **Scheduling experiments**: Test different staffing levels and measure impact on guest satisfaction + speed
- Full statistical significance calculator with auto-stop when confidence threshold reached

### 🤖 A10. Robotic Kitchen Integration API
Future-proof API layer for robotic kitchen equipment:
- Standard interface for automated cooking equipment (fryers, grills, drink stations)
- Robot task queue: Agent system can dispatch cooking tasks to robotic equipment
- Integration with Miso Robotics (Flippy), Picnic (pizza assembly), etc.
- Status monitoring dashboard for all robotic equipment
- Human-robot collaboration workflows (robot preps, human finishes)

### 📡 A11. Real-Time Geospatial Intelligence
Location-aware intelligence layer:
- **Heat maps**: Customer density around the restaurant (anonymized mobile data)
- **Competitor radar**: Track nearby restaurant openings, closings, pricing changes, reviews
- **Event proximity alerts**: Concert/sports event 3 blocks away → auto-adjust forecast + staffing
- **Delivery zone optimization**: AI-optimized delivery boundaries based on order density + driver efficiency
- **New location scouting**: Score potential new locations by foot traffic, demographics, competition

### 🔗 A12. Blockchain Supply Chain Transparency
For restaurants marketing "farm-to-table" or "organic":
- Immutable supply chain tracking from farm → distributor → restaurant → plate
- QR code on menu items: guests scan to see origin, certifications, journey
- Automated sustainability scoring per menu item
- Regulatory compliance proof (organic, non-GMO, allergen-free) with blockchain verification

### 💬 A13. Multi-Channel Guest Communication Hub
Unified inbox for all guest communications:
- WhatsApp, SMS, email, in-app messaging, social media DMs — all in one place
- AI auto-categorizes: complaint, reservation, question, praise
- AI suggests responses (manager approves in one click)
- Sentiment tracking across all channels per guest
- Automated reservation confirmations, wait-time notifications, order updates

### 📈 A14. Investor / Owner Portal
Separate read-only portal for restaurant investors/owners:
- High-level financial dashboards (revenue, EBITDA, cash flow, ROI)
- Comparison to industry benchmarks
- AI-generated monthly narrative reports ("Here's how your restaurant performed...")
- Cap table and distribution management
- Automated investor update emails (monthly, AI-written)

### ⚡ A15. Edge AI Computing (On-Premise Intelligence)
For latency-critical decisions that can't wait for cloud:
- Deploy lightweight ML models on edge devices (Nvidia Jetson, Raspberry Pi)
- Computer vision runs locally (sub-50ms response for portion/safety alerts)
- Temperature monitoring and alerts even if internet goes down
- Local cache syncs to cloud when connection restores
- Reduces cloud compute costs for high-frequency operations

---

## 10. ADVANCED DATABASE ADDITIONS

### For Advanced Features
```
-- A6: Causal Analysis
causal_analyses (id, trigger_metric, cause_json, confidence, period, created_at)

-- A7: Gamification
achievements (id, name, description, criteria_json, icon, points)
employee_achievements (id, employee_id, achievement_id, earned_at)
leaderboards (id, category, period, rankings_json, generated_at)

-- A8: Fraud Detection
fraud_alerts (id, alert_type, employee_id, severity, evidence_json, status, created_at)
loss_prevention_reports (id, period, shrinkage_amount, anomalies_json)

-- A9: Experimentation
experiments (id, name, hypothesis, type, variants_json, status, start_date, end_date)
experiment_results (id, experiment_id, variant, metric, value, sample_size, p_value)

-- A14: Investor Portal
investors (id, name, email, ownership_pct, joined_at)
investor_reports (id, period, content_html, metrics_json, sent_at)
```

---

## 11. IMPLEMENTATION PHASES (Extended with Advanced Features)

### PHASE 11 — Advanced AI Features (Week 23-25)
- [ ] Causal "Why" Engine (A6)
- [ ] Agent-to-Agent Negotiation protocol (A1)
- [ ] A/B Testing platform (A9)
- [ ] Fraud Detection & Loss Prevention (A8)
- [ ] Predictive Menu Engineering (A4)

### PHASE 12 — Advanced Interfaces & Engagement (Week 26-28)
- [ ] Voice Interface with Whisper + TTS (A2)
- [ ] PWA + Push Notifications (A3)
- [ ] Gamification Engine (A7)
- [ ] Multi-Channel Communication Hub (A13)
- [ ] Investor/Owner Portal (A14)

### PHASE 13 — Future-Proofing (Week 29-31)
- [ ] Edge AI Computing setup (A15)
- [ ] Geospatial Intelligence (A11)
- [ ] Supplier Marketplace (A5)
- [ ] Robotic Kitchen Integration API (A10)
- [ ] Blockchain Supply Chain (A12)

---

## SUMMARY

| Dimension | Decision |
|-----------|----------|
| Architecture | Modular monorepo, event-driven, API-first |
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 + Celery |
| Frontend | Next.js 15 + TypeScript + Tailwind + shadcn/ui |
| Database | PostgreSQL 16 + Redis 7 |
| AI/ML | Claude API + scikit-learn + Prophet + YOLOv8 + Whisper |
| Real-time | WebSocket (FastAPI ↔ Next.js) + Edge AI |
| Auth | JWT + bcrypt |
| Infrastructure | Docker Compose (dev), CI/CD ready, Edge nodes |
| Core Timeline | 10 phases over ~22 weeks (13 core modules) |
| Advanced Timeline | +3 phases over ~9 weeks (15 advanced features) |
| Total Features | 13 core modules (A→M) + 15 advanced features (A1→A15) = **28 feature areas** |
| Total Timeline | ~31 weeks for full system with advanced features |
