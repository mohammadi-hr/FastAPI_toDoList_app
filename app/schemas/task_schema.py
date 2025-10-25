from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.task_model import TaskPriority


class TaskBaseSchema(BaseModel):
    title: str = Field(
        ..., max_length=64, min_length=8, description="title of the task"
    )
    description: Optional[str] = Field(max_length=512)
    due_date: Optional[datetime] = Field(description="when the task must be done")
    user_id: int
    priority: TaskPriority = TaskPriority.NORMAL


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskUpdateSchema(TaskBaseSchema):

    is_completed: Optional[bool] = Field(description="to do | doing | done")


class TaskResponseSchema(TaskBaseSchema):
    id: int = Field(..., description="id of the task")
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class TaskFilterParams(BaseModel):
    offset: Optional[int] = Field(default=0, ge=0, description="tasks list pagination")
    limit: int = Field(default=10, le=50, description="number of tasks in each query")
    is_completed: Optional[bool] = None
    search: Optional[str]


class TaskOutFilteration(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_completed: bool

    # class Config:
    #     orm_mode = True
