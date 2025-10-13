from fastapi import APIRouter, Depends, status
from app.schemas.task_schema import TaskResponseSchema, TaskCreateSchema, TaskUpdateSchema, TaskFilterParams, TaskOutFilteration
from app.services import task_service
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=list[TaskResponseSchema])
def get_tasks(db: Session = Depends(get_db)):
    return task_service.get_tasks(db)


@router.get("/{taskid}", response_model=TaskResponseSchema)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task(task_id, db)


@router.post("/", response_model=TaskResponseSchema)
def create_task(task_add: TaskCreateSchema, db: Session = Depends(get_db)):
    return task_service.create_task(task_add, db)


@router.put("/{taskid}", response_model=TaskResponseSchema)
def update_task(task_id: int, task_add: TaskUpdateSchema, db: Session = Depends(get_db)):
    return task_service.update_task(task_id, task_add, db)


@router.delete("/{taskid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id, db: Session = Depends(get_db)):
    task_service.delete_task(task_id, db)


@router.post("/filter", response_model=dict)
def task_filteration(filter: TaskFilterParams, db: Session = Depends(get_db)):
    return task_service.tasks_filteraion(filter, db)
