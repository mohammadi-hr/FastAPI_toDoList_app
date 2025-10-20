from fastapi import FastAPI
from app.api.routes import tasks_route
from app.api.routes import users_route
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.core.redis import get_redis
from contextlib import asynccontextmanager
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection manually
    redis = await get_redis()
    # Initialize FastAPI Cache system
    FastAPICache.init(RedisBackend(redis), prefix=settings.PROJECT_NAME)
    print("✅ Redis Distributed Cache initialized")
    yield
    await redis.close()
    print("Redis Cache connection closed")

app = FastAPI(lifespan=lifespan, title="FastAPI Base To_Do_List Project",
              version="1.0.0", summary="A Simple Task Management Application")


app.include_router(tasks_route.router, prefix="/tasks", tags=["Tasks"])
app.include_router(users_route.router, prefix="/users", tags=["Users"])


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI base To_Do_List project!"}
