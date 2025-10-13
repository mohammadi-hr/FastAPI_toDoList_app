from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.task_model import TaskModel
from app.schemas.task_schema import TaskCreateSchema, TaskUpdateSchema, TaskResponseSchema
from fastapi.responses import JSONResponse


def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()


def create_task(user_add: TaskCreateSchema, db: Session = Depends(get_db)):
    task = TaskModel(**user_add.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    return task


def update_task(task_id: int, task_update: TaskUpdateSchema, db: Session = Depends(get_db)):
    task = get_task(task_id, db)
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task(task_id, db)
    if task:
        db.delete(task)
        db.commit()
    return JSONResponse({"response": f"task {task_id} deleted"})
