from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from app.models.task_model import TaskModel
from app.schemas.task_schema import (
    TaskResponseSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskFilterParams,
)
from app.services import task_service
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.jwt_service import get_user_by_token_in_cookie
from app.models.user_model import UserModel
from urllib.request import urlopen
import json
from app.scripts.dummy_task_generator import DummyTaskGenerator
from app.core.redis import get_redis

router = APIRouter()


@router.get("/", response_model=list[TaskResponseSchema])
async def get_tasks(
    user: UserModel = Depends(get_user_by_token_in_cookie),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):

    cache_key = "tasks:all"
    cached = await redis.get(cache_key)

    if cached:
        print(" Redis Cache Hit !")
        return json.loads(cached)
    print(" Redis Cache Miss !")
    tasks = task_service.get_tasks(user, db)
    tasks_data = [
        {
            "id": t.id,
            "user_id": t.user_id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "created_at": getattr(t.created_at, "isoformat", lambda: None)(),
            "updated_at": getattr(t.updated_at, "isoformat", lambda: None)(),
            "due_date": getattr(t.due_date, "isoformat", lambda: None)(),
            "is_completed": t.is_completed,
        }
        for t in tasks
    ]

    await redis.set(cache_key, json.dumps(tasks_data), ex=120)

    return tasks_data


@router.get("/{taskid}", response_model=TaskResponseSchema)
def get_task(
    task_id: int,
    user: UserModel = Depends(get_user_by_token_in_cookie),
    db: Session = Depends(get_db),
):
    return task_service.get_task(user, task_id, db)


@router.post("/", response_model=TaskResponseSchema)
async def create_task(
    task_add: TaskCreateSchema,
    user: UserModel = Depends(get_user_by_token_in_cookie),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):

    task = task_service.create_task(user, task_add, db)

    await redis.delete("tasks:all")

    return task


@router.put("/{taskid}", response_model=TaskResponseSchema)
async def update_task(
    task_add: TaskUpdateSchema,
    task_id: int,
    user: UserModel = Depends(get_user_by_token_in_cookie),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    return task_service.update_task(user, task_id, task_add, db)


@router.delete("/{taskid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id,
    user: UserModel = Depends(get_user_by_token_in_cookie),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    task_service.delete_task(user, task_id, db)


@router.post("/filter", response_model=dict)
def task_filteration(filter: TaskFilterParams, db: Session = Depends(get_db)):
    return task_service.tasks_filteraion(filter, db)


# ---------- read tasks as json from api ---------------


@router.post("/api_call", description="read tasks from webservice and return json")
def read_tasks_from_api(url: str = Query(..., description="URL of the API")):
    with urlopen(url) as api_call:
        json_tasks_as_binary = api_call.read().decode("utf-8")  # convert binary to str
        json_tasks = json.loads(json_tasks_as_binary)

        return json.dumps(json_tasks, indent=2)


@router.post("/gen")
def seed_tasks_table(
    tasks: int,
    users: int,
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db),
):
    dummy_tasks_gen = DummyTaskGenerator(tasks, users, start, end)
    tasks_list = dummy_tasks_gen.generate_all_tasks()
    try:
        for t in tasks_list:
            task = TaskModel(
                user_id=t["user_id"],
                title=t["title"],
                description=t["description"],
                priority=t["priority"],
                is_completed=t["is_completed"],
                created_at=t["created_at"],
                due_date=t["due_date"],
            )
            db.add(task)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Seeding tasks table failed ! Error: {e}")

    return tasks_list
