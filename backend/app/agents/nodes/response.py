from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings

settings = get_settings()

RESPONSE_PROMPT = """你是智能金融投研与风控助手。请根据以下信息，综合生成回复。

上下文信息：
{context}

知识图谱信息：
{kg_info}

要求：
1. 回复专业、准确、有条理
2. 适当引用数据来源
3. 如果信息不足，坦诚告知
4. 使用 Markdown 格式化回复"""


async def response_node(state: AgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.judge_model_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=0.5,
    )

    context = state.get("context", "暂无相关文档信息")
    kg_results = state.get("kg_results", [])
    kg_info = "\n".join([str(r) for r in kg_results]) if kg_results else "暂无知识图谱信息"

    messages = state["messages"]
    last = messages[-1] if messages else ""
    user_msg = last["content"] if isinstance(last, dict) else last.content

    response = await llm.ainvoke([
        SystemMessage(content=RESPONSE_PROMPT.format(context=context, kg_info=kg_info)),
        HumanMessage(content=user_msg),
    ])

    return {"response": response.content}
