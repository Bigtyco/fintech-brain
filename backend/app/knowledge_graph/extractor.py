import json
import re
from langchain_openai import ChatOpenAI
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

EXTRACT_PROMPT = """从以下金融文本中抽取实体和关系。

要求：
1. 实体类型：Company(公司), Person(人物), Industry(行业), RiskEvent(风险事件), FinancialIndicator(财务指标), Policy(政策法规)
2. 关系类型：BELONGS_TO(属于), HAS_INDICATOR(拥有指标), CAUSES(导致), TRIGGERS(触发), INVESTS_IN(投资), COMPETES_WITH(竞争), REGULATED_BY(受监管)

只输出纯JSON，不要添加任何其他文字、代码块标记或解释：
{{"entities": [{{"name": "...", "type": "Company", "properties": {{}}}}], "relations": [{{"source": "...", "target": "...", "type": "BELONGS_TO", "properties": {{}}}}]}}

文本：
{text}
"""


def _clean_identifier(value: str) -> str:
    """Strip non-ASCII chars (e.g. Chinese annotations) to produce valid Neo4j identifiers."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "", value)
    return cleaned if cleaned else "Unknown"


def _extract_json_from_text(raw: str) -> dict:
    """Try to extract JSON from LLM response, handling markdown code blocks and extra text."""
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding first { ... } block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"entities": [], "relations": []}


async def extract_entities(text: str) -> dict:
    llm = ChatOpenAI(
        model=settings.judge_model_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=0,
    )
    response = await llm.ainvoke(EXTRACT_PROMPT.format(text=text))
    raw = response.content.strip()
    logger.info(f"KG extraction raw response (first 200 chars): {raw[:200]}")

    result = _extract_json_from_text(raw)

    # Validate and clean structure
    if not isinstance(result.get("entities"), list):
        result["entities"] = []
    if not isinstance(result.get("relations"), list):
        result["relations"] = []

    # Clean entity types and relation types for Neo4j compatibility
    for entity in result["entities"]:
        entity["type"] = _clean_identifier(entity.get("type", "Unknown"))
    for rel in result["relations"]:
        rel["type"] = _clean_identifier(rel.get("type", "RELATED_TO"))

    logger.info(f"KG extraction result: {len(result['entities'])} entities, {len(result['relations'])} relations")
    return result
