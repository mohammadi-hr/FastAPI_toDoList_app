from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import UserCreateSchema, UserReadSchema, UserUpdateSchema
from app.services import user_service
from app.core.api_key_security import get_api_key

router = APIRouter()


@router.post("/", response_model=UserReadSchema)
def create_user(user_in: UserCreateSchema, db: Session = Depends(get_db)):
    return user_service.create_user(user_in, db)


@router.get("/", response_model=list[UserReadSchema])
def list_users(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return user_service.get_users(db)


@router.get("/{user_id}", response_model=UserReadSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(user_id, db)


@router.put("/{user_id}", response_model=UserReadSchema)
def update_user(user_id: int, user_in: UserUpdateSchema, db: Session = Depends(get_db)):
    return user_service.update_user(user_id, user_in, db)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(user_id, db)
