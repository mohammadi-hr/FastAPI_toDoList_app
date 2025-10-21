
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import (
    create_engine,
    StaticPool)
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Create a new engine for the in-memory SQLite database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# Create all tables before running tests
Base.metadata.create_all(bind=engine)


def override_get_db():
    test_db = TestingSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close()


# Apply dependency override
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
