import json
from langchain_core.tools import tool
from app.knowledge_graph.neo4j_client import neo4j_client


@tool
async def query_knowledge_graph(entity_name: str) -> str:
    """查询知识图谱中实体的关系信息。用于获取公司关系、行业关联、风险传导链等。"""
    relations = await neo4j_client.get_entity_relations(entity_name)
    if not relations:
        return f"未找到与'{entity_name}'相关的知识图谱信息。"
    return json.dumps(relations, ensure_ascii=False, indent=2)
