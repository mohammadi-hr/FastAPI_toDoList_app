from app.models.user_model import UserModel
from datetime import UTC, datetime
from app.scripts.dummy_user_generator import DummyUserGenerator
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


@pytest.fixture(scope='package', autouse=True)
def gen_dummy_users():
    dummy_user_generator = DummyUserGenerator(
        20, datetime(2022, 10, 14, 15, 10, 45))

    test_db = TestingSessionLocal()

    # use a static usrname and password to be testable in pytest
    dummy_user_1 = dummy_user_generator.gen_fake_user(
        'hr.mohammadi', '12345678')
    dummy_user_2 = dummy_user_generator.gen_fake_user('f.akbari', '12345678')
    test_db.add(dummy_user_1)
    test_db.add(dummy_user_2)
    test_db.commit()

    dummy_users = dummy_user_generator.gen_all_users(
        dummy_user_generator.total_users - 2)

    try:
        for user in dummy_users:
            test_db.add(user)
        test_db.commit()

        # test if data seeds correctly into the memory
        users_in_db = test_db.query(UserModel).all()
        print(f"{len(users_in_db)} users added to the test db")
        assert len(users_in_db) == dummy_user_generator.total_users

        yield users_in_db

    except Exception as e:
        test_db.rollback()
        print(f"Feeding dummy users failed ! Error : {e}")
