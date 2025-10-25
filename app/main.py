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

import pika
from fastapi.responses import PlainTextResponse
import logging

rabbitMQ_connection = None
rabbitMQ_channel = None

@asynccontextmanager
async def lifespan(app: FastAPI):


    # Initialize Redis connection manually
    redis = await get_redis()
    # Initialize FastAPI Cache system
    FastAPICache.init(RedisBackend(redis), prefix=settings.PROJECT_NAME)
    print("Redis Distributed Cache initialized")

    credentials = pika.PlainCredentials(
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )
    rabbitMQ_connection= pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST,
                                                                           port=settings.RABBITMQ_PORT,
                                                                           credentials=credentials))
    rabbitMQ_channel = rabbitMQ_connection.channel()

    # Store inside FastAPI state (not as globals)
    app.state.rabbitMQ_connection = rabbitMQ_connection
    app.state.rabbitMQ_channel = rabbitMQ_channel

    print("✅ RabbitMQ Connection Initialized")

    yield
    await redis.aclose()
    print("Redis Cache connection closed")

    # --- SHUTDOWN ---
    print("Shutting down... closing RabbitMQ connection")
    rabbitMQ_channel.close()
    rabbitMQ_connection.close()


app = FastAPI(
    lifespan=lifespan,
    title="FastAPI Base To_Do_List Project",
    version="1.0.0",
    summary="A Simple Task Management Application",
    debug=True,
)


app.include_router(tasks_route.router, prefix="/tasks", tags=["Tasks"])
app.include_router(users_route.router, prefix="/users", tags=["Users"])


@app.middleware("http")
async def add_rabbitmq_to_request(request: Request, call_next):
    request.state.rabbitMQ_channel = request.app.state.rabbitMQ_channel
    response = await call_next(request)
    return response

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):

    # Log the full exception
    logger.exception("Exception occurred while handling request")


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

# @app.exception_handler(Exception)
# def internal_exception_handler(request: Request, exc: Exception):
#     print(exc)
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": True,
#             "message" : "Unexpected Server Error",
#             "status_code": 500,
#             "error_code": "InternalServerError",
#             "path": str(request.url),
#         }
#     )


@app.exception_handler(Exception)
async def fallback_exception_handler(request: Request, exc: Exception):
    import traceback
    print("🚨 Original Exception:")
    traceback.print_exc()  # prints full traceback
    return PlainTextResponse(str(exc), status_code=500)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI base To_Do_List project!"}
