import os

import redis.asyncio as redis

# Initialize the client here
# (It will connect lazily when first used, or you can manage it in main.py's lifespan)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def get_redis():
    """FastAPI Dependency for Redis"""
    return redis_client
