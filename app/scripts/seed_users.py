
from faker import Faker
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import importlib


fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def import_module_by_name(module_path: str):
    module = importlib.import_module(module_path)
    return module


def import_user_type():
    from app.models.user_model import UserType
    return UserType


user_type = import_user_type()


def create_fake_user(db: Session, username: str, password: str, userType):
    user_module = import_module_by_name("app.models.user_model")
    hashed_password = pwd_context.hash(password)
    user = user_module.UserModel(
        username=username,
        password=hashed_password,
        user_type=userType
    )
    db.add(user)
    return user


def seed_users(n: int = 10):
    user_module = import_module_by_name("app.models.user_model")
    db = SessionLocal()
    try:

        create_fake_user(db, "mohammadi-hr", "12345678",
                         user_module.UserType.ADMIN)

        for _ in range(n):
            username = fake.user_name()
            password = fake.password(length=10)
            create_fake_user(db, username, password, user_module.UserType.USER)
        db.commit()
        print(f"Seeded {n + 1} users successfully.")

    except Exception as e:
        db.rollback()
        print(f"seeding users error ... {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
