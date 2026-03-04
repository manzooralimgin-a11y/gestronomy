# Rollback Runbook (Agents + Tenant/Observability Phases)

## Scope
This runbook covers rollback for:
- Tenant hardening migrations (Phase 4/5)
- AG-01 Service Autopilot
- AG-02 Revenue Control Tower
- UX-03 Exception workflow fields
- Observability additions (SLO endpoint and alerts config)

## Preconditions
- Capture current revision: `backend/.venv/bin/alembic current`
- Capture target head: `backend/.venv/bin/alembic heads`
- Snapshot database before downgrade.

## Application-Level Safety Switches (No DB Rollback)
Use these first if incident is functional and not schema-corrupt:
1. Disable Revenue Control autonomous impact:
   - `PUT /api/agents/revenue-control-tower/policy` with `{ "kill_switch": true }`
2. Keep Service Autopilot non-autonomous:
   - Policy already enforces no execute without approval (`allow_autonomous_execute=false` by default).
3. Restrict access temporarily:
   - Remove agent UI links/feature flags at frontend deploy if required.

## DB Migration Rollback
Rollback one revision:
- `backend/.venv/bin/alembic downgrade -1`

Rollback to a specific safe revision:
- `backend/.venv/bin/alembic downgrade <revision_id>`

Relevant revisions with downgrade support:
- `620206e756c2` (AG-01)
- `9d372db4a5f1` (AG-02)
- `f38a933ea2e0` (UX-03 audit timeline)
- `3649d637c9a4` (UX-03 exception workflow fields)
- `9b4c1d2e7f10` (Phase 4 tenant columns)
- `ab57cd3db3df` (Phase 5 tenant not-null/enforcement)

## Post-Rollback Validation
1. Health: `GET /api/health` returns 200.
2. Auth and tenant checks:
   - Run `backend/tests/test_tenant_isolation_api.py`.
3. Agent safety checks:
   - Run `backend/tests/test_core/test_service_autopilot_api.py`.
   - Run `backend/tests/test_core/test_revenue_control_tower_api.py`.
4. Observability:
   - Run `backend/tests/test_dashboard/test_slo_dashboard_api.py`.
   - Ensure Prometheus rules load from `infrastructure/monitoring/prometheus-alerts.yml`.

## Decision Tree
1. Incident is business-logic only:
   - Apply kill switch/policy limits first.
2. Incident is schema/data compatibility:
   - Downgrade one migration step and redeploy matching app commit.
3. Incident crosses tenant boundaries:
   - Immediately disable affected endpoints at ingress and run tenant isolation suite.
