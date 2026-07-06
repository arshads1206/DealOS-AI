.PHONY: help dev down build test lint migrate seed clean logs

# ===========================
# DealOS AI — Developer Commands
# ===========================

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===========================
# Development
# ===========================

dev: ## Start full development stack (hot reload)
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

down: ## Stop all containers
	docker compose down

build: ## Build all containers
	docker compose build

restart: ## Restart backend container
	docker compose restart backend

logs: ## Tail logs for all services
	docker compose logs -f

logs-backend: ## Tail backend logs only
	docker compose logs -f backend

# ===========================
# Database
# ===========================

migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Rollback last migration
	docker compose exec backend alembic downgrade -1

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U dealos -d dealos

# ===========================
# Testing
# ===========================

test: ## Run all backend tests
	docker compose exec backend pytest -v --tb=short

test-unit: ## Run unit tests only
	docker compose exec backend pytest tests/unit -v --tb=short

test-integration: ## Run integration tests only
	docker compose exec backend pytest tests/integration -v --tb=short

test-api: ## Run API tests only
	docker compose exec backend pytest tests/api -v --tb=short

test-cov: ## Run tests with coverage report
	docker compose exec backend pytest --cov=app --cov-report=html --cov-report=term-missing

# ===========================
# Linting & Formatting
# ===========================

lint: ## Run all linters
	docker compose exec backend ruff check app/
	docker compose exec backend ruff format --check app/
	docker compose exec backend mypy app/

format: ## Auto-format code
	docker compose exec backend ruff format app/
	docker compose exec backend ruff check --fix app/

# ===========================
# Utilities
# ===========================

shell: ## Open Python shell in backend container
	docker compose exec backend python -c "import IPython; IPython.start_ipython()" 2>/dev/null || \
		docker compose exec backend python

clean: ## Remove containers, volumes, and build artifacts
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
