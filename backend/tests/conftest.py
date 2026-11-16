"""
Pytest configuration and isolated testing fixtures.
All test data is transient and completely isolated from production database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pgvector.sqlalchemy import Vector

# Teach SQLite how to render PostgreSQL-specific JSONB, UUID, and Vector types for in-memory tests
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

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.utils.auth import hash_password

# Isolated in-memory SQLite database specifically for test runner
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session):
    user = User(
        email="test_admin@university.edu",
        hashed_password=hash_password("SecurePassword123!"),
        full_name="Test Administrator",
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
