from langchain_core.tools import tool
from app.rag.retriever import hybrid_search


@tool
async def search_financial_docs(query: str) -> str:
    """搜索金融文档库，获取相关文档片段。用于回答需要参考内部文档的问题。"""
    results = await hybrid_search(query, top_k=3)
    if not results:
        return "未找到相关文档。"
    return "\n\n".join([f"[文档{i+1}] {r['content']}" for i, r in enumerate(results)])
