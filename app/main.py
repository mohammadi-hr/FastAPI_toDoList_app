from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.api.routes import tasks_route
from app.api.routes import users_route
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.exceptions import AppException
from app.core.redis import get_redis
from contextlib import asynccontextmanager
from app.core.config import settings

from fastapi.exceptions import RequestValidationError
from app.core.exception_handlers import validation_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection manually
    redis = await get_redis()
    # Initialize FastAPI Cache system
    FastAPICache.init(RedisBackend(redis), prefix=settings.PROJECT_NAME)
    print("✅ Redis Distributed Cache initialized")
    yield
    await redis.aclose()
    print("Redis Cache connection closed")


app = FastAPI(
    lifespan=lifespan,
    title="FastAPI Base To_Do_List Project",
    version="1.0.0",
    summary="A Simple Task Management Application",
)


app.include_router(tasks_route.router, prefix="/tasks", tags=["Tasks"])
app.include_router(users_route.router, prefix="/users", tags=["Users"])

@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
                "error": True,
                "message": exc.message,
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "path": str(request.url),
                }
            )

@app.exception_handler(Exception)
def internal_exception_handler(request: Request, exc: Exception):
    print(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message" : "Unexpected Server Error",
            "status_code": 500,
            "error_code": "InternalServerError",
            "path": str(request.url),
        }
    )

app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI base To_Do_List project!"}
