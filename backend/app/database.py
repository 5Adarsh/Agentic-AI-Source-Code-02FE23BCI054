"""
SQLAlchemy engine, session factory, and declarative Base.
Includes pgvector extension registration and multi-dialect compatibility.
"""
from typing import Generator
import os

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from pgvector.sqlalchemy import Vector

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Register SQLite type compiler mappings so models with JSONB/UUID/Vector work seamlessly
def visit_JSONB(self, type_, **kw):
    return "JSON"

def visit_pg_uuid(self, type_, **kw):
    return "TEXT"

def visit_vector(self, type_, **kw):
    return "BLOB"

SQLiteTypeCompiler.visit_JSONB = visit_JSONB
SQLiteTypeCompiler.visit_UUID = visit_pg_uuid
SQLiteTypeCompiler.visit_VECTOR = visit_vector
SQLiteTypeCompiler.visit_vector = visit_vector


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )

    @event.listens_for(engine, "connect")
    def _enable_pgvector(dbapi_conn, _conn_record):
        """Ensure the pgvector extension is loaded on each new connection in PostgreSQL."""
        try:
            with dbapi_conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                dbapi_conn.commit()
        except Exception as exc:
            logger.warning("Could not enable pgvector extension: %s", exc)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a SQLAlchemy session.
    Automatically closes the session on exit.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_all_tables() -> None:
    """Create all tables (used in tests / initial setup)."""
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """Drop all tables (used in tests only)."""
    Base.metadata.drop_all(bind=engine)
