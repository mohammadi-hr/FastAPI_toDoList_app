import pathlib
from dotenv import load_dotenv
from app.core.config import settings
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
engine = create_engine(
    settings.SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    test_db = TestingSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close()


# Apply dependency override
@pytest.fixture(scope='module', autouse=True)
def override_session():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

# Create all tables before running tests


@pytest.fixture(scope='session', autouse=True)
def setup_and_teardown_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def client():
    with TestClient(app) as c:
        yield c
