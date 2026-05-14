COMMON_QUERIES = {
    "company_relations": """
        MATCH (c:Company)-[r]->(target)
        WHERE c.name = $company_name
        RETURN c.name AS company, type(r) AS relation, target.name AS target, labels(target) AS target_labels
    """,
    "risk_chain": """
        MATCH path = (start:RiskEvent)-[:CAUSES|TRIGGERS*1..3]->(end)
        WHERE start.name = $event_name
        RETURN [n IN nodes(path) | n.name] AS chain
    """,
    "industry_peers": """
        MATCH (c:Company)-[:BELONGS_TO]->(industry:Industry)<-[:BELONGS_TO]-(peer:Company)
        WHERE c.name = $company_name AND c <> peer
        RETURN peer.name AS peer, industry.name AS industry
    """,
    "financial_indicators": """
        MATCH (c:Company)-[:HAS_INDICATOR]->(i:FinancialIndicator)
        WHERE c.name = $company_name
        RETURN i.name AS indicator, i.value AS value, i.period AS period
        ORDER BY i.period DESC
        LIMIT 10
    """,
}
