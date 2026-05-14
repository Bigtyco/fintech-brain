from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings

settings = get_settings()

RISK_PROMPT = """你是一位专业的金融风控专家。基于以下上下文信息，为用户提供风险评估与控制建议。

要求：
1. 识别主要风险类型（信用风险、市场风险、操作风险、流动性风险等）
2. 评估风险等级（高/中/低）
3. 给出具体的风险控制建议
4. 引用相关法规或合规要求

上下文信息：
{context}

知识图谱信息：
{kg_info}"""


async def risk_control_node(state: AgentState) -> dict:
    llm = ChatOpenAI(
        model=settings.judge_model_name,
        api_key=settings.api_key,
        base_url=settings.base_url,
        temperature=0.2,
    )

    context = state.get("context", "")
    kg_results = state.get("kg_results", [])
    kg_info = "\n".join([str(r) for r in kg_results]) if kg_results else "暂无知识图谱信息"

    messages = state["messages"]
    last = messages[-1] if messages else ""
    user_msg = last["content"] if isinstance(last, dict) else last.content

    response = await llm.ainvoke([
        SystemMessage(content=RISK_PROMPT.format(context=context, kg_info=kg_info)),
        HumanMessage(content=user_msg),
    ])

    return {"response": response.content}
