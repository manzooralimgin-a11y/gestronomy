# Rollback Documentation

This document describes the procedures for rolling back changes across the three primary tiers of the application stack: Database, Backend, and Frontend.

## 1. Database Rollback
If a database schema change needs to be reverted, we use Alembic to step back the migrations.

- **Command**: `cd backend && uv run alembic downgrade -1`
- **Verification**: Check constraints and tables for accuracy before proceeding. Ensure `plan.md` reflects schema state if manual alterations occur.
- **Data Protection**: Take a snapshot of the PostgreSQL database before executing a downgrade to prevent accidental data loss in production.

## 2. Backend Rollback
If a backend deployment introduces critical system failures, revert the container image or code deployment.

- **Docker/Container (Production)**: Update `docker-compose.prod.yml` to reference the previous stable tag and run `docker compose -f docker-compose.prod.yml up -d backend`.
- **Render/Platform**: Trigger a redeploy of the previous successful build via the hosting platform's dashboard.
- **Verification**: Monitor `GET /api/metrics` to ensure the error rate drops back below the 5% threshold. Check `GET /api/health` to confirm the service is healthy.

## 3. Frontend Rollback
Since the frontend is built on Next.js, rollbacks are mostly handled at the edge/hosting layer.

- **Vercel/Hosting**: Click "Promote to Production" on the last stable preview deployment.
- **Verification**: Open a fresh browser window and verify that caching isn't retaining the broken state. Check console for JS errors.
