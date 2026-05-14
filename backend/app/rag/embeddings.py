import httpx
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


async def get_embedding(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.siliconflow_base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.siliconflow_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.embedding_model,
                "input": text,
                "encoding_format": "float",
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.siliconflow_base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.siliconflow_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.embedding_model,
                "input": texts,
                "encoding_format": "float",
            },
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]
