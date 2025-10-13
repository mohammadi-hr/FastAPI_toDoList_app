from fastapi import APIRouter
from app.schemas.task_schema import TaskResponseSchema

router = APIRouter()


@router.get("/", response_model=list[TaskResponseSchema])
def get_tasks():
    return [{"id": 1, "username": "admin"}]
