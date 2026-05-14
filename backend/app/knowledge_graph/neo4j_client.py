from neo4j import AsyncGraphDatabase
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


class Neo4jClient:
    def __init__(self):
        self._driver = None

    async def connect(self):
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")

    async def close(self):
        if self._driver:
            await self._driver.close()

    async def search_entities(self, keyword: str, limit: int = 20) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (n)
                WHERE n.name CONTAINS $keyword
                RETURN n.name AS name, labels(n) AS labels, properties(n) AS props
                LIMIT $limit
                """,
                keyword=keyword,
                limit=limit,
            )
            records = await result.data()
            return records

    async def get_entity_relations(self, entity_name: str) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (a)-[r]->(b)
                WHERE a.name = $name
                RETURN a.name AS source, type(r) AS relation, b.name AS target, properties(r) AS props
                UNION
                MATCH (a)-[r]->(b)
                WHERE b.name = $name
                RETURN a.name AS source, type(r) AS relation, b.name AS target, properties(r) AS props
                """,
                name=entity_name,
            )
            return await result.data()

    async def get_subgraph(self, center: str, depth: int = 2) -> tuple[list, list]:
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH path = (center)-[*1..$depth]-(neighbor)
                WHERE center.name = $center
                WITH nodes(path) AS ns, relationships(path) AS rs
                UNWIND ns AS n
                WITH COLLECT(DISTINCT {id: elementId(n), name: n.name, labels: labels(n)}) AS nodes,
                     rs
                UNWIND rs AS r
                RETURN nodes, COLLECT(DISTINCT {
                    source: elementId(startNode(r)),
                    target: elementId(endNode(r)),
                    type: type(r)
                }) AS edges
                """,
                center=center,
                depth=depth,
            )
            record = await result.single()
            if record:
                return record["nodes"], record["edges"]
            return [], []

    async def add_entity(self, name: str, entity_type: str, properties: dict = None):
        props = properties or {}
        async with self._driver.session() as session:
            await session.run(
                f"""
                MERGE (n:{entity_type} {{name: $name}})
                SET n += $props
                """,
                name=name,
                props=props,
            )

    async def add_relation(self, source: str, target: str, relation: str, properties: dict = None):
        props = properties or {}
        async with self._driver.session() as session:
            await session.run(
                f"""
                MATCH (a {{name: $source}})
                MATCH (b {{name: $target}})
                MERGE (a)-[r:{relation}]->(b)
                SET r += $props
                """,
                source=source,
                target=target,
                props=props,
            )


neo4j_client = Neo4jClient()
