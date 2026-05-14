from fastapi import APIRouter, Depends, Query
from app.deps import get_current_user
from app.models.user import User
from app.knowledge_graph.neo4j_client import neo4j_client

router = APIRouter(prefix="/api/knowledge", tags=["知识图谱"])


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=1, max_length=200),
    current_user: User = Depends(get_current_user),
):
    results = await neo4j_client.search_entities(q)
    return {"query": q, "results": results}


@router.get("/entity/{entity_name}")
async def get_entity_relations(
    entity_name: str,
    current_user: User = Depends(get_current_user),
):
    results = await neo4j_client.get_entity_relations(entity_name)
    return {"entity": entity_name, "relations": results}


@router.get("/graph")
async def get_subgraph(
    center: str = Query(..., min_length=1),
    depth: int = Query(2, ge=1, le=3),
    current_user: User = Depends(get_current_user),
):
    nodes, edges = await neo4j_client.get_subgraph(center, depth)
    return {"center": center, "nodes": nodes, "edges": edges}
