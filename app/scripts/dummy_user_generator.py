from datetime import datetime, timezone
from passlib.context import CryptContext
from app.models.user_model import UserModel
from faker import Faker
import random
from typing import Optional


class DummyUserGenerator:

    def __init__(self, total_users: int, created_from: datetime):
        self.total_users = total_users
        self.created_from = created_from
        self.faker = Faker()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.utc = timezone.utc

    def gen_fake_username(self,  username: Optional[str] = None) -> str:
        if username:
            self.username = username
            return username
        return self.faker.user_name()

    def gen_fake_password(self, password: Optional[str] = None) -> str:
        pwd_to_hash = password if password else self.faker.password()
        return self.pwd_context.hash(pwd_to_hash)

    def gen_fake_datetime(self):
        return self.faker.date_time_between(
            start_date=self.created_from,
            end_date=datetime.now(tz=self.utc),
            tzinfo=self.utc,
        )

    def gen_fake_user(self,  username: Optional[str] = None, password: Optional[str] = None) -> UserModel:

        # if default username or password not set use faker to make them
        user_name = username if username else self.gen_fake_username(username)
        pass_word = self.gen_fake_password(
            password) if password else self.pwd_context.hash(self.gen_fake_password(password))

        user = UserModel(
            username=user_name,
            password=pass_word,
            user_type=random.choice(["ADMIN", "USER"]),
            created_at=self.gen_fake_datetime(),
            is_active=random.choice([True, False]),
        )

        return user

    def gen_all_users(self, total: Optional[int] | None):
        if total:
            return [self.gen_fake_user(username=None, password=None) for _ in range(total)]
        return [self.gen_fake_user(username=None, password=None) for _ in range(self.total_users)]
