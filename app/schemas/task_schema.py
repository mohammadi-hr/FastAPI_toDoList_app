from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBaseSchema(BaseModel):
    title: str = Field(..., max_length=64, min_length=8,
                       description='title of the task')
    description: Optional[str] = Field(max_length=512)


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskUpdateSchema(TaskBaseSchema):
    due_date: Optional[datetime] = Field(
        description='when the task must be done')
    is_completed: Optional[bool] = Field(description='to do | doing | done')


class TaskResponseSchema(TaskBaseSchema):
    id: int = Field(..., description='id of the task')
    created_at: datetime
    updated_at: datetime
