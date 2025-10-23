from app.models.user_model import UserModel
from datetime import datetime
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
from app.core.jwt_security import create_access_token
from app.services.tocken_service import get_password_hash
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


# def override_get_redis():
#     import fakeredis
#     yield fakeredis.FakeRedis()
#
#
# # Apply dependency override
# @pytest.fixture(scope='module', autouse=True)
# def override_redis_session():
#     app.dependency_overrides[get_redis] = override_get_redis
#     yield
#     app.dependency_overrides.pop(get_redis, None)


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


@pytest.fixture(scope='function')
def authorized_client():

    with TestClient(app) as c:
        db_gen = override_get_db()
        db = next(db_gen)
    user = db.query(UserModel).filter_by(username='hr.mohammadi').first()
    if not user:
        user = UserModel(
            username='hr.mohammadi',
            is_active=True,
            password=get_password_hash('12345678'),
            user_type='admin',
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    payload = {
        "user_id": str(user.id),
        "username": user.username,
        "type": "access",
    }

    access_token = create_access_token(payload)
    # async with AsyncClient(app=app, base_url="http://test") as client:
    #     client.headers.update({"Authorization": f"Bearer {access_token}"})
    #     try:
    #         yield client
    #     finally:
    #         try:
    #             next(db_gen)
    #         except StopIteration:
    #             pass

    c.headers.update({"Authorization": f"Bearer {access_token}"})
    yield c


@pytest.fixture(scope='package', autouse=True)
def gen_dummy_users():
    dummy_user_generator = DummyUserGenerator(
        20, datetime(2022, 10, 14, 15, 10, 45))

    db_gen = override_get_db()
    test_db = next(db_gen)

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
