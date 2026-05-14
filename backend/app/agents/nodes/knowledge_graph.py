from app.agents.state import AgentState
from app.knowledge_graph.neo4j_client import neo4j_client
from app.core.logging import logger


async def knowledge_graph_node(state: AgentState) -> dict:
    messages = state["messages"]
    last = messages[-1] if messages else ""
    query = last["content"] if isinstance(last, dict) else last.content

    if not query:
        return {"kg_results": []}

    try:
        # 从查询中提取关键实体进行搜索
        entities = await neo4j_client.search_entities(query[:20], limit=5)
        all_relations = []
        for entity in entities:
            relations = await neo4j_client.get_entity_relations(entity["name"])
            all_relations.extend(relations)
        return {"kg_results": all_relations}
    except Exception as e:
        logger.warning(f"KG query failed: {e}")
        return {"kg_results": []}
