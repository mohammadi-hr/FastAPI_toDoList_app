from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema
from app.db.session import get_db


def create_user(user_in: UserCreateSchema, db: Session = Depends(get_db)) -> UserModel:
    existing = (
        db.query(UserModel).filter(UserModel.username == user_in.username).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = UserModel(username=user_in.username)
    user.set_password(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(username_in: str, db: Session):
    user = db.query(UserModel).filter(UserModel.username == username_in).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="نام کاربری نامعتبر می باشد"
        )
    return user


def get_users(db: Session = Depends(get_db)) -> list[UserModel]:
    return db.query(UserModel).all()


def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UserModel:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(
    user_id: int, user_in: UserUpdateSchema, db: Session = Depends(get_db)
) -> UserModel:
    user = get_user_by_id(user_id, db)

    user.username = user_in.username
    user.is_active = user_in.is_active
    if user_in.password:
        user.set_password(user_in.password)

    db.commit()
    db.refresh(user)
    return user


def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(user_id, db)
    db.delete(user)
    db.commit()
    return None
