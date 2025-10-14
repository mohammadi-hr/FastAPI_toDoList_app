from app.db.base import Base
from pydantic import Field
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

# Initialize a password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32))
    passwoed = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())

    tasks = relationship("TaskModel", back_populates="user")

    # --- Password methods ---
    def set_password(self, password: str):
        """Hashes and stores the password."""
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verifies a password against the stored hash."""
        return pwd_context.verify(password, self.password)
