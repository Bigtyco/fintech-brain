import json
from langchain_openai import ChatOpenAI
from app.config import get_settings

settings = get_settings()

EXTRACT_PROMPT = """从以下金融文本中抽取实体和关系。

要求：
1. 实体类型：Company(公司), Person(人物), Industry(行业), RiskEvent(风险事件), FinancialIndicator(财务指标), Policy(政策法规)
2. 关系类型：BELONGS_TO(属于), HAS_INDICATOR(拥有指标), CAUSES(导致), TRIGGERS(触发), INVESTS_IN(投资), COMPETES_WITH(竞争), REGULATED_BY(受监管)

输出JSON格式：
{
  "entities": [{"name": "...", "type": "...", "properties": {}}],
  "relations": [{"source": "...", "target": "...", "type": "...", "properties": {}}]
}

文本：
{text}
"""


async def extract_entities(text: str) -> dict:
    llm = ChatOpenAI(
        model=settings.judge_model_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=0,
    )
    response = await llm.ainvoke(EXTRACT_PROMPT.format(text=text))
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"entities": [], "relations": []}
