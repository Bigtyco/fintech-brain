import json
from typing import Optional
from app.core.redis import redis_client
from app.core.logging import logger


async def cache_get(key: str) -> Optional[list | dict]:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_set(key: str, value: list | dict, expire: int = 3600) -> None:
    await redis_client.set(key, json.dumps(value, ensure_ascii=False), ex=expire)


async def cache_delete(key: str) -> None:
    await redis_client.delete(key)


async def cache_delete_by_prefix(prefix: str) -> int:
    """Delete all keys matching prefix. Returns count of deleted keys."""
    deleted = 0
    async for key in redis_client.scan_iter(match=f"{prefix}*"):
        await redis_client.delete(key)
        deleted += 1
    if deleted:
        logger.info(f"Cache invalidated: {deleted} keys with prefix '{prefix}'")
    return deleted
