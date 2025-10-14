from app.db.base import Base
from pydantic import Field
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship


class TaskModel(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(32))
    description = Column(String(512), nullable=True)
    due_date = Column(DateTime, default=None)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        server_onupdate=func.now())

    user = relationship("User", back_populates="tasks", uselist=False)
