from app.agents.state import AgentState
from app.rag.retriever import hybrid_search
from app.core.logging import logger


async def retrieval_node(state: AgentState) -> dict:
    messages = state["messages"]
    last = messages[-1] if messages else ""
    query = last["content"] if isinstance(last, dict) else last.content

    if not query:
        return {"retrieved_docs": [], "context": ""}

    try:
        docs = await hybrid_search(query, top_k=5)
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        docs = []

    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[文档{i}] {doc['content']}")
    context = "\n\n".join(context_parts) if context_parts else ""

    return {"retrieved_docs": docs, "context": context}
