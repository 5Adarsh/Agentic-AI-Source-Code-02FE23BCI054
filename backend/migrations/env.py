"""Alembic environment configuration for RIAP.

Supports both online (connected) and offline (SQL script) migration modes.
Uses DATABASE_URL from the environment so the same code works in Docker,
CI and local dev without editing alembic.ini.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Import all models so SQLAlchemy / Alembic can see the metadata.
# Keep this import even if individual symbols are unused — the side-effect
# (registering models with Base.metadata) is the entire point.
# ---------------------------------------------------------------------------
from app.database import Base  # noqa: F401
import app.models  # noqa: F401  — registers all ORM models

# ---------------------------------------------------------------------------
# Alembic Config object (alembic.ini values)
# ---------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url with the DATABASE_URL env var when present.
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # asyncpg driver variant needed for async engine; keep sync URL for offline
    config.set_main_option("sqlalchemy.url", database_url)

# Attach Python logging configured in alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline mode — emit SQL to stdout instead of connecting
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine. Calls to
    context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — connect and run migrations
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
