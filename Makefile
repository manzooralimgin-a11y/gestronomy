.PHONY: dev dev-backend dev-frontend install install-backend install-frontend db-migrate db-upgrade db-seed test test-backend test-frontend lint clean

# ===== DEVELOPMENT =====
dev:
	@echo "Starting all services..."
	docker compose up -d db redis
	@sleep 2
	$(MAKE) dev-backend & $(MAKE) dev-frontend & wait

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# ===== INSTALL =====
install: install-backend install-frontend

install-backend:
	cd backend && uv sync

install-frontend:
	cd frontend && npm install

# ===== DATABASE =====
db-migrate:
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	cd backend && alembic upgrade head

db-seed:
	cd backend && python -m app.shared.seed

# ===== TESTING =====
test: test-backend test-frontend

test-backend:
	cd backend && UV_CACHE_DIR=.uv-cache uv run --extra dev pytest -v

test-frontend:
	cd frontend && npm test

# ===== LINT =====
lint:
	cd backend && UV_CACHE_DIR=.uv-cache uv run --extra dev ruff check . && UV_CACHE_DIR=.uv-cache uv run --extra dev ruff format --check .
	cd frontend && npm run lint

# ===== CLEAN =====
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules backend/.venv
