import httpx
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


async def rerank(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    if not documents:
        return []

    contents = [doc["content"] for doc in documents]

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.siliconflow_base_url}/rerank",
            headers={
                "Authorization": f"Bearer {settings.siliconflow_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.reranker_model,
                "query": query,
                "documents": contents,
                "top_n": top_k,
                "return_documents": False,
            },
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("results", []):
        idx = item["index"]
        doc = documents[idx].copy()
        doc["rerank_score"] = item["relevance_score"]
        results.append(doc)

    return results
