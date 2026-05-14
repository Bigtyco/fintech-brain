import json
from typing import Optional
from app.core.redis import redis_client


async def cache_get(key: str) -> Optional[dict]:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_set(key: str, value: dict, expire: int = 3600) -> None:
    await redis_client.set(key, json.dumps(value, ensure_ascii=False), ex=expire)


async def cache_delete(key: str) -> None:
    await redis_client.delete(key)
