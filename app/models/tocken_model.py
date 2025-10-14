
from app.db.base import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.user_model import UserModel


class TockenModel(Base):

    __tablename__ = "tockens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tocken = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime, default=datetime.now(),
                        onupdate=datetime.now())

    user = relationship("UserModel", back_populates="token", uselist=False)
