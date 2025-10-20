import os
import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDID_DB = os.getenv("REDIS_DB", 0)

redis_client = None


async def get_redis():

    global redis_client

    if redis_client is None:

        redis_client = await redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDID_DB}",
            encoding="utf-8",
            decode_responses=True,
        )

    return redis_client
