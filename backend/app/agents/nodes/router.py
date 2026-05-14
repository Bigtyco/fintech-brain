from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

ROUTER_PROMPT = """你是一个金融投研与风控系统的意图路由器。根据用户的最新消息，判断其意图类别。

意图类别：
- research: 投研分析相关（股票分析、行业研究、公司调研、投资建议、财务分析等）
- risk: 风控相关（风险评估、合规审查、风险预警、信用分析等）
- chat: 普通闲聊或通用问题

只回复类别名称，不要其他内容。"""


async def router_node(state: AgentState) -> dict:
    try:
        llm = ChatOpenAI(
            model=settings.judge_model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
            temperature=0,
            timeout=60,
        )

        messages = state["messages"]
        last = messages[-1] if messages else ""
        user_msg = last["content"] if isinstance(last, dict) else last.content

        logger.info(f"Calling LLM for routing: model={settings.judge_model_name}")
        response = await llm.ainvoke([
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=user_msg),
        ])

        intent = response.content.strip().lower()
        if intent not in ("research", "risk", "chat"):
            intent = "chat"

        logger.info(f"Router intent: {intent}")
        return {"intent": intent}
    except Exception as e:
        logger.error(f"Router node error: {type(e).__name__}: {e}")
        return {"intent": "chat"}
