import hashlib
import inspect
import json
from functools import wraps
from typing import Any, Callable

from fastapi.concurrency import run_in_threadpool

from app.core import redis_client


def cache_response(expire: int = 86400 * 90):
    """
    A decorator to cache FastAPI endpoint responses in Redis.
    Requires a 'cache' dependency injected into the route.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            redis_client = kwargs.get("cache")

            if not redis_client:
                print("⚠️ No Redis client found in route dependencies. Skipping cache.")

                async def safe_execute():
                    if inspect.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return await run_in_threadpool(func, *args, **kwargs)

            key_data = {
                k: v for k, v in kwargs.items() if k not in ["cache", "request"]
            }

            key_string = (
                f"{func.__name__}_{json.dumps(key_data, sort_keys=True, default=str)}"
            )
            key_hash = hashlib.md5(key_string.encode("utf-8")).hexdigest()
            cache_key = f"fastapi_cache:{func.__name__}:{key_hash}"

            cached_result = await redis_client.get(cache_key)
            if cached_result:
                print(f"⚡ Cache Hit for {cache_key}")
                return json.loads(cached_result)

            print(f"🐢 Cache Miss. Executing {func.__name__}...")
            if inspect.iscoroutinefunction(func):
                # If you wrote: async def get_dashboard(...)
                result = await func(*args, **kwargs)
            else:
                # If you wrote: def get_dashboard(...)
                # We safely offload it to a threadpool so it doesn't block FastAPI!
                result = await run_in_threadpool(func, *args, **kwargs)

            if result is not None:
                await redis_client.setex(
                    name=cache_key, time=expire, value=json.dumps(result)
                )

            return result

        return wrapper

    return decorator


async def flush_fastapi_cache():
    client = redis_client

    pattern = "fastapi_cache:*"
    deleted_count = 0

    print(f"🔍 Searching for cache keys matching: '{pattern}'...")

    async for key in client.scan_iter(match=pattern):
        await client.delete(key)
        deleted_count += 1
        print(f"🗑️ Deleted: {key}")

    print(f"\n✅ Success! Cleared {deleted_count} cached endpoint responses.")

    await client.aclose()
