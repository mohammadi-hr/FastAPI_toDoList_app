from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.task_model import TaskModel
from app.schemas.task_schema import TaskCreateSchema, TaskUpdateSchema, TaskFilterParams
from fastapi.responses import JSONResponse
from app.models.user_model import UserModel


def get_tasks(user: UserModel, db: Session = Depends(get_db)):
    return db.query(TaskModel).filter_by(user_id=user.id).all()


def create_task(user: UserModel, user_add: TaskCreateSchema, db: Session = Depends(get_db)):
    task = TaskModel(**user_add.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(user: UserModel, task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter_by(
        id=task_id, user_id=user.id).one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    return task


def update_task(user: UserModel, task_id: int, task_update: TaskUpdateSchema, db: Session = Depends(get_db)):
    task = get_task(user, task_id, db)
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(user: UserModel, task_id: int, db: Session = Depends(get_db)):
    task = get_task(user, task_id, db)
    if task:
        db.delete(task)
        db.commit()
    return JSONResponse({"response": f"task {task_id} deleted"})


def tasks_filteraion(filter: TaskFilterParams, db: Session = Depends(get_db)):

    query = db.query(TaskModel)

    if filter.is_completed is not None:
        query = query.filter(TaskModel.is_completed == filter.is_completed)

    if filter.search:
        query = query.filter(or_(TaskModel.title.ilike(
            f"%{filter.search}%")), TaskModel.description.ilike(f"%{filter.search}%"))

    # pagination
    total = query.count()
    result = query.offset(filter.offset).limit(filter.limit).all

    return {
        "total": total,
        "skip": filter.offset,
        "limit": filter.limit,
        "results": result
    }
