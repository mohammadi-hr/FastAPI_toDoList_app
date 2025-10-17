from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import UserCreateSchema, UserReadSchema, UserUpdateSchema, UserLoginSchema
from app.services import user_service
from app.core.api_key_security import get_api_key
from app.models.user_model import UserModel
from app.services import tocken_service
from app.models.token_model import TockenModel
from fastapi.security import OAuth2PasswordBearer
from app.schemas.token_schema import TokenBaseSchema
from app.core.jwt_security import create_access_token
from app.services.jwt_service import refresh_token
from datetime import timedelta
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserReadSchema)
def register_user(user_in: UserCreateSchema, db: Session = Depends(get_db)):
    return user_service.create_user(user_in, db)


@router.post("/login", response_model=UserReadSchema)
def login_user(user_login: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(
        username=user_login.username).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="کابر مورد نظر یاقت نشد")
    if not tocken_service.verify_password(user_login.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="نام کاربری یا رمز عبور اشتباه است")

    access_tocken = tocken_service.create_access_token()
    expire_at = tocken_service.token_expiration()

    token_entry = TockenModel(
        user_id=user.id, tocken=access_tocken, expires_at=expire_at)
    db.add(token_entry)
    db.commit()
    db.refresh(token_entry)

    return JSONResponse({"access_token": token_entry.tocken, "token_type": "bearer"})


oauth2_scheme = OAuth2PasswordBearer("/logout")


@router.post("/logout")
def logout_user(token_in: TokenBaseSchema, db: Session = Depends(get_db)):  # Depends(oauth2_scheme)
    token_entry = db.query(TockenModel).filter_by(
        tocken=token_in.token).first()
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="کابر مورد نظر یاقت نشد")
    if token_entry:
        db.delete(token_entry)
        db.commit()
        return JSONResponse({"پیام": "خروج با موفقیت انجام شد"})


# ------------ JWT Authentication -------------

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_DAYS = 7


@router.post("/auth/login")
def jwt_user_login(login_in: UserLoginSchema, response: Response, db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(login_in.username, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="کاربر یافت نشد")
    if not tocken_service.verify_password(login_in.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="رمز عبور نامعتبر می باشد")

    access_payload = {
        "user_id": str(user.id),
        "username": user.username,
        "type": "access"
    }

    # Access token (short life)
    access_token = create_access_token(
        access_payload, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    refresh_payload = {
        "user_id": str(user.id),
        "username": user.username,
        "type": "refresh",
    }

    # Refresh token (long life)
    refresh_token = create_access_token(
        refresh_payload, timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))

    response.set_cookie(key="access_token", value=access_token,
                        httponly=True,
                        secure=True,
                        samesite="strict"
                        )

    response.set_cookie(key="refresh_token", value=refresh_token,
                        httponly=True,
                        secure=True,
                        samesite="strict"
                        )

    return JSONResponse({"پیام": "ورود با موفقیت انجام شد",
                         "access_token": access_token,
                         "refresh_token": refresh_token})


@router.post("/auth/refresh")
def refresh_user_token(ref_token: str, db: Session = Depends(get_db)):
    return refresh_token(ref_token, db)


@router.post("/auth/logout")
def logout_by_jwt_cookies(response: Response):

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refrsh_token")

    return {"message": "خروج با موفقیت انجام شد"}

# ------------ END JWT Authentication ---------


# @router.get("/", response_model=list[UserReadSchema])
# def list_users(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
#     return user_service.get_users(db)

@router.get("/", response_model=list[UserReadSchema])
def list_users(db: Session = Depends(get_db)):
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
