from passlib.context import CryptContext
from secrets import token_urlsafe
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.db.session import get_db
from fastapi.security import OAuth2PasswordBearer
from app.models.token_model import TockenModel
from app.models.user_model import UserModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token():
    return token_urlsafe(32)


def token_expiration(minutes=30):
    return datetime.now() + timedelta(minutes=minutes)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    token_entry = db.query(TockenModel).filter_by(tocken=token).first()
    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=" توکن نامعتبراست"
        )
    if datetime.fromtimestamp(token_entry.expires_at) < datetime.now():  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=" توکن منقضی شده است"
        )

    user = db.query(UserModel).filter_by(user_id=token_entry.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_UNAUTHORIZED, detail="کابر یافت نشد"
        )

    return user
