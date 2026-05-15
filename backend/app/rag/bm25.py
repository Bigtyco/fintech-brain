from rank_bm25 import BM25Okapi
import jieba
from app.core.logging import logger


class BM25Index:
    def __init__(self):
        self._documents: list[dict] = []
        self._bm25: BM25Okapi | None = None

    def build_index(self, documents: list[dict]):
        self._documents = documents
        corpus = [self._tokenize(doc["content"]) for doc in documents]
        self._bm25 = BM25Okapi(corpus)
        logger.info(f"BM25 index built with {len(documents)} documents")

    def add_documents(self, documents: list[dict]):
        self._documents.extend(documents)
        corpus = [self._tokenize(doc["content"]) for doc in self._documents]
        self._bm25 = BM25Okapi(corpus)
        logger.info(f"BM25 index updated: {len(self._documents)} total documents")

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        if not self._bm25 or not self._documents:
            return []

        tokenized_query = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)

        scored_docs = list(zip(range(len(scores)), scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scored_docs[:top_k]:
            doc = self._documents[idx].copy()
            doc["bm25_score"] = float(score)
            results.append(doc)
        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return list(jieba.cut(text))


bm25_index = BM25Index()
