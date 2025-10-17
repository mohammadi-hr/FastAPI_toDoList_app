from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError, ExpiredSignatureError
from app.models.user_model import UserModel
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.services.user_service import get_user_by_id
from app.core.jwt_security import create_access_token
from datetime import timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_DAYS = 7


def get_user_by_authorization_header(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                             algorithms=['HS256'])
        user_id = str(payload.get("user_is"))
        if not user_id:
            raise HTTPException(status_code=401, detail="توکن نامعتبر می باشد")
    except ExpiredSignatureError:
        # ExpiredSignatureError is raised automatically when the exp claim is expired
        raise HTTPException(status_code=401, detail="توکن منقضی شده است")
    except JWTError:
        raise HTTPException(status_code=401, detail="توکن نامعتبر می باشد")

    user = get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="کاربر یافت نشد")
    return user


bearer_scheme = HTTPBearer()


def get_user_by_token_in_cookie(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):

    # access_token = request.cookies.get("access_token")
    access_token = credentials.credentials
    if not access_token:
        raise HTTPException(status_code=401, detail="توکن access یافت نشد")

    try:

        payload = jwt.decode(
            access_token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="توکن نامعتبر")
    except JWTError:
        raise HTTPException(status_code=401, detail="توکن منقضی یا نامعتبر")

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=401, detail="کاربر یافت نشد")

    return user


def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401, detail="Invalid scope for token")

        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token")

    # Create new short-lived access token
    new_access_token = create_access_token(
        data={"user_id": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": new_access_token, "token_type": "bearer"}
