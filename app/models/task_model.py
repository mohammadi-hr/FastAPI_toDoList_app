from app.db.base import Base
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    func,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship


class TaskPriority(str, Enum):
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("UserModel", back_populates="tasks", uselist=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)

    priority = Column(
        SQLEnum(TaskPriority, name="priority_enum"),
        nullable=False,
        default=TaskPriority.NORMAL,
    )

    due_date = Column(DateTime, default=None)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())
