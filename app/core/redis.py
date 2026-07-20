import redis.asyncio as redis
from app.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis():
    """Dependency injection for Redis."""
    return redis_client


async def close_redis():
    """Close Redis connection."""
    await redis_client.close()
