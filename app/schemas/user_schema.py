from pydantic import BaseModel, Field
from datetime import datetime


class UserBaseSchema(BaseModel):
    username: str = Field(..., max_length=32)
    is_active: bool


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=6, max_length=72)


class UserUpdateSchema(UserBaseSchema):
    password: str | None = None  # Optional for updates


class UserReadSchema(UserBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    username: str
    password: str
