import io
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import (
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
    UserLoginSchema,
)
from app.services import user_service
from app.models.user_model import UserModel
from app.services import tocken_service
from app.models.token_model import TockenModel
from fastapi.security import OAuth2PasswordBearer
from app.schemas.token_schema import TokenBaseSchema
from app.core.jwt_security import create_access_token
from app.services.jwt_service import refresh_token
from datetime import timedelta, datetime
import os
import csv
import json
from app.scripts.dummy_user_generator import DummyUserGenerator
from typing import List


router = APIRouter()


@router.post("/register", response_model=UserReadSchema)
def register_user(user_in: UserCreateSchema, db: Session = Depends(get_db)):
    user = user_service.create_user(user_in, db)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"details": "ثبت نام با موفقیت انجام شد"})


@router.post("/login", response_model=UserReadSchema)
def login_user(user_login: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(
        username=user_login.username).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="کابر مورد نظر یاقت نشد"
        )
    if not tocken_service.verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است",
        )

    access_tocken = tocken_service.create_access_token()
    expire_at = tocken_service.token_expiration()

    token_entry = TockenModel(
        user_id=user.id, tocken=access_tocken, expires_at=expire_at
    )
    db.add(token_entry)
    db.commit()
    db.refresh(token_entry)

    return JSONResponse({"access_token": token_entry.tocken, "token_type": "bearer"})


oauth2_scheme = OAuth2PasswordBearer("/logout")


@router.post("/logout")
def logout_user(
    token_in: TokenBaseSchema, db: Session = Depends(get_db)
):  # Depends(oauth2_scheme)
    token_entry = db.query(TockenModel).filter_by(
        tocken=token_in.token).first()
    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="کابر مورد نظر یاقت نشد"
        )
    if token_entry:
        db.delete(token_entry)
        db.commit()
        return JSONResponse({"پیام": "خروج با موفقیت انجام شد"})


# ------------ JWT Authentication -------------


ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_DAYS = 7


@router.post("/auth/login")
def jwt_user_login(
    login_in: UserLoginSchema, response: Response, db: Session = Depends(get_db)
):
    user = user_service.get_user_by_username(login_in.username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="کاربر یافت نشد"
        )
    if not tocken_service.verify_password(login_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="رمز عبور نامعتبر می باشد"
        )

    access_payload = {
        "user_id": str(user.id),
        "username": user.username,
        "type": "access",
    }

    # Access token (short life)
    access_token = create_access_token(
        access_payload, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_payload = {
        "user_id": str(user.id),
        "username": user.username,
        "type": "refresh",
    }

    # Refresh token (long life)
    refresh_token = create_access_token(
        refresh_payload, timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    # write tokens as a json data to the file
    os.makedirs("static", exist_ok=True)
    with open("static/jwt_token.txt", "a") as token_writer:

        token_data_string = {
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        json.dump(token_data_string, token_writer, indent=2)

        # token_writer.write(
        #     f"user_id: {user.id}\naccess_token: {access_token}\nrefresh_token: {refresh_token}\n")
        # print(f"size of the token file is: {write_token.tell()}")

    return JSONResponse(
        {
            "پیام": "ورود با موفقیت انجام شد",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


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


# --------- Users to csv file ---------


@router.post("/export")
def export_users_csv(db: Session = Depends(get_db)):
    users = user_service.get_users(db)
    users_data = [
        {k: v for k, v in user.__dict__.items() if k != "_sa_instance_state"}
        for user in users
    ]

    with io.StringIO() as in_memory_text_stream:
        writer = csv.DictWriter(
            in_memory_text_stream,
            fieldnames=[
                "username",
                "password",
                "user_type",
                "tasks",
                "is_active",
                "id",
                "created_at",
                "updated_at",
            ],
        )
        writer.writeheader()
        writer.writerows(users_data)

        csv_data = in_memory_text_stream.getvalue()

        csv_filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        os.makedirs("log/exports", exist_ok=True)
        file_path = os.path.join("log/exports", csv_filename)

        # save csv file on the server
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "username",
                    "password",
                    "user_type",
                    "tasks",
                    "is_active",
                    "id",
                    "created_at",
                    "updated_at",
                ],
                quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC,
            )
            writer.writeheader()
            writer.writerows(users_data)

        # Download csv file
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={csv_filename}"},
        )


# ---------------- feed users table ----------------


@router.post("/gen", response_model=List[UserReadSchema])
def feed_users_table(users: int, created_from: datetime, db: Session = Depends(get_db)):
    dummy_users = DummyUserGenerator(users, created_from)
    dummy_users_list = dummy_users.gen_all_users(dummy_users.total_users)
    try:
        # db.bulk_save_objects(dummy_users_list)

        for dm in dummy_users_list:
            db.add(dm)
        db.commit()  # ✅ now IDs are assigned

        for dm in dummy_users_list:
            db.refresh(dm)

    except Exception as e:
        db.rollback()
        print(f"Feeding users table failed ! Error : {e}")

    return dummy_users_list
