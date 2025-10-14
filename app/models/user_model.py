from app.db.base import Base
from pydantic import Field
from sqlalchemy import Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from passlib.context import CryptContext
from typing import cast, List
from datetime import datetime
from app.models.task_model import TaskModel

# Initialize a password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), server_onupdate=func.now())

    # Relationship to tasks
    tasks: Mapped[List["TaskModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # --- Password methods ---
    def set_password(self, password: str):
        """Hashes and stores the password."""
        # bcrypt max length = 72 bytes
        password = password[:72]
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verifies a password against the stored hash."""
        return pwd_context.verify(password, self.password)
