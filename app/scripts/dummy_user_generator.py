
from datetime import datetime, timezone, tzinfo
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user_model import UserModel, UserType
from faker import Faker
import random


class DummyUserGenerator:

    def __init__(self, total_users: int, created_from: datetime):
        self.total_users = total_users
        self.created_from = created_from
        self.faker = Faker()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.utc = timezone.utc

    def gen_fake_username(self):
        return self.faker.user_name()

    def gen_fake_password(self):
        return self.pwd_context.hash(self.faker.password())

    def gen_fake_datetime(self):
        return self.faker.date_time_between(start_date=self.created_from, end_date=datetime.now(tz=self.utc), tzinfo=self.utc)

    def gen_fake_user(self):

        user = UserModel(
            username=self.gen_fake_username(),
            password=self.gen_fake_password(),
            user_type=random.choice(["ADMIN", "USER"]),
            created_at=self.gen_fake_datetime(),
            is_active=random.choice([True, False])
        )

        return user

    def gen_all_users(self):
        return [self.gen_fake_user() for _ in range(self.total_users)]
