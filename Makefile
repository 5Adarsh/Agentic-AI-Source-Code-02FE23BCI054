# =============================================================================
# RIAP — Makefile
# Developer convenience wrappers around docker compose commands.
# Usage: make <target>  (e.g. make up, make migrate MSG="add users table")
# =============================================================================

DC = docker compose

.PHONY: help up down build logs restart \
        migrate makemigrations \
        shell-db shell-backend \
        test lint clean \
        tools-up tools-down

# Default target — print help
help:
	@echo ""
	@echo "RIAP — Research Intelligence & Publication Analytics Portal"
	@echo "============================================================"
	@echo ""
	@echo "Service management:"
	@echo "  make up              Start all services in detached mode"
	@echo "  make down            Stop and remove containers"
	@echo "  make build           Rebuild all Docker images"
	@echo "  make logs            Follow logs from all services"
	@echo "  make restart         down + up"
	@echo ""
	@echo "Database / migrations:"
	@echo "  make migrate         Apply all pending Alembic migrations"
	@echo "  make makemigrations  Auto-generate a migration (MSG=<description>)"
	@echo "  make shell-db        Open psql inside the db container"
	@echo ""
	@echo "Development:"
	@echo "  make shell-backend   Bash shell inside the backend container"
	@echo "  make test            Run pytest inside the backend container"
	@echo "  make lint            Run ruff + mypy inside the backend container"
	@echo ""
	@echo "Extras:"
	@echo "  make tools-up        Start optional tools profile (pgAdmin)"
	@echo "  make tools-down      Stop the tools profile"
	@echo "  make clean           Remove containers, volumes and orphans"
	@echo ""

# ---------------------------------------------------------------------------
# Service management
# ---------------------------------------------------------------------------

up:
	$(DC) up -d

down:
	$(DC) down

build:
	$(DC) build

logs:
	$(DC) logs -f

restart: down up

# ---------------------------------------------------------------------------
# Database / Alembic migrations
# ---------------------------------------------------------------------------

migrate:
	$(DC) exec backend alembic upgrade head

# Usage: make makemigrations MSG="describe what changed"
makemigrations:
	$(DC) exec backend alembic revision --autogenerate -m "$(MSG)"

shell-db:
	$(DC) exec db psql -U riap_user riap_db

# ---------------------------------------------------------------------------
# Development shells & testing
# ---------------------------------------------------------------------------

shell-backend:
	$(DC) exec backend bash

test:
	$(DC) exec backend pytest tests/ -v --tb=short

lint:
	$(DC) exec backend sh -c "ruff check . && mypy app/"

# ---------------------------------------------------------------------------
# Optional tools profile (pgAdmin on :5050)
# ---------------------------------------------------------------------------

tools-up:
	$(DC) --profile tools up -d pgadmin

tools-down:
	$(DC) --profile tools down pgadmin

# ---------------------------------------------------------------------------
# Clean — destructive!
# ---------------------------------------------------------------------------

clean:
	$(DC) down -v --remove-orphans
