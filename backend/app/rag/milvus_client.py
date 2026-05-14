from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

COLLECTION_NAME = "finance_documents"
VECTOR_DIM = 1024  # BGE-large 维度


def connect_milvus():
    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=settings.milvus_port,
    )
    logger.info(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")


def ensure_collection() -> Collection:
    if utility.has_collection(COLLECTION_NAME):
        return Collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="doc_id", dtype=DataType.INT64),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192),
        FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=4096),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM),
    ]
    schema = CollectionSchema(fields, description="金融文档向量库")
    collection = Collection(COLLECTION_NAME, schema)

    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024},
    }
    collection.create_index("embedding", index_params)
    logger.info(f"Created Milvus collection: {COLLECTION_NAME}")
    return collection


def get_collection() -> Collection:
    connect_milvus()
    return ensure_collection()


def insert_vectors(doc_id: int, chunks: list[dict], embeddings: list[list[float]]):
    collection = get_collection()
    data = [
        [doc_id] * len(chunks),
        list(range(len(chunks))),
        [c["content"] for c in chunks],
        [str(c.get("metadata", {})) for c in chunks],
        embeddings,
    ]
    result = collection.insert(data)
    collection.flush()
    return result


def search_vectors(query_embedding: list[float], top_k: int = 20) -> list[dict]:
    collection = get_collection()
    collection.load()
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"nprobe": 16}},
        limit=top_k,
        output_fields=["doc_id", "chunk_index", "content", "metadata"],
    )
    hits = []
    for hit in results[0]:
        hits.append({
            "id": hit.id,
            "score": hit.score,
            "content": hit.entity.get("content"),
            "doc_id": hit.entity.get("doc_id"),
            "chunk_index": hit.entity.get("chunk_index"),
            "metadata": hit.entity.get("metadata"),
        })
    return hits
