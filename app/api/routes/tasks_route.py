from fastapi import APIRouter, Depends, status, Request
from app.schemas.task_schema import TaskResponseSchema, TaskCreateSchema, TaskUpdateSchema, TaskFilterParams, TaskOutFilteration
from app.services import task_service
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.jwt_service import get_user_by_token_in_cookie
from app.models.user_model import UserModel

router = APIRouter()


@router.get("/", response_model=list[TaskResponseSchema])
def get_tasks(user: UserModel = Depends(get_user_by_token_in_cookie), db: Session = Depends(get_db)):
    return task_service.get_tasks(user, db)


@router.get("/{taskid}", response_model=TaskResponseSchema)
def get_task(task_id: int, user: UserModel = Depends(get_user_by_token_in_cookie), db: Session = Depends(get_db)):
    return task_service.get_task(user, task_id, db)


@router.post("/", response_model=TaskResponseSchema)
def create_task(task_add: TaskCreateSchema, user: UserModel = Depends(get_user_by_token_in_cookie), db: Session = Depends(get_db)):
    return task_service.create_task(user, task_add, db)


@router.put("/{taskid}", response_model=TaskResponseSchema)
def update_task(task_add: TaskUpdateSchema, task_id: int, user: UserModel = Depends(get_user_by_token_in_cookie), db: Session = Depends(get_db)):
    return task_service.update_task(user, task_id, task_add, db)


@router.delete("/{taskid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id, user: UserModel = Depends(get_user_by_token_in_cookie), db: Session = Depends(get_db)):
    task_service.delete_task(user, task_id, db)


@router.post("/filter", response_model=dict)
def task_filteration(filter: TaskFilterParams, db: Session = Depends(get_db)):
    return task_service.tasks_filteraion(filter, db)
