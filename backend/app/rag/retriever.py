from app.rag.milvus_client import search_vectors
from app.rag.embeddings import get_embedding
from app.rag.bm25 import bm25_index
from app.rag.reranker import rerank
from app.core.logging import logger


def rrf_fusion(vector_results: list[dict], bm25_results: list[dict], k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for rank, doc in enumerate(vector_results):
        key = f"{doc['doc_id']}_{doc.get('chunk_index', 0)}"
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
        doc_map[key] = doc

    for rank, doc in enumerate(bm25_results):
        key = f"{doc.get('doc_id', 0)}_{doc.get('chunk_index', 0)}"
        scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
        if key not in doc_map:
            doc_map[key] = doc

    sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    results = []
    for key in sorted_keys:
        doc = doc_map[key].copy()
        doc["rrf_score"] = scores[key]
        results.append(doc)

    return results


async def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = await get_embedding(query)

    vector_results = search_vectors(query_embedding, top_k=20)

    bm25_results = bm25_index.search(query, top_k=20)

    fused = rrf_fusion(vector_results, bm25_results)

    reranked = await rerank(query, fused, top_k=top_k)

    logger.info(f"Hybrid search: query='{query}', vector={len(vector_results)}, bm25={len(bm25_results)}, final={len(reranked)}")
    return reranked
