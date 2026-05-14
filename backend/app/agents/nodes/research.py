from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()

RESEARCH_PROMPT = """你是一位资深金融投研分析师。基于以下上下文信息，为用户提供专业的投资研究分析。

要求：
1. 分析要有理有据，引用具体数据
2. 给出明确的观点和建议
3. 提示潜在风险
4. 使用专业但易懂的语言

上下文信息：
{context}

知识图谱信息：
{kg_info}"""


async def research_node(state: AgentState) -> dict:
    try:
        llm = ChatOpenAI(
            model=settings.judge_model_name,
            api_key=settings.api_key,
            base_url=settings.base_url,
            temperature=0.3,
            timeout=120,
        )

        context = state.get("context", "")
        kg_results = state.get("kg_results", [])
        kg_info = "\n".join([str(r) for r in kg_results]) if kg_results else "暂无知识图谱信息"

        messages = state["messages"]
        last = messages[-1] if messages else ""
        user_msg = last["content"] if isinstance(last, dict) else last.content

        logger.info(f"Calling LLM for research: model={settings.judge_model_name}, base_url={settings.base_url}")
        response = await llm.ainvoke([
            SystemMessage(content=RESEARCH_PROMPT.format(context=context, kg_info=kg_info)),
            HumanMessage(content=user_msg),
        ])
        logger.info(f"LLM response received, length={len(response.content)}")

        return {"response": response.content}
    except Exception as e:
        logger.error(f"Research node error: {type(e).__name__}: {e}")
        return {"response": f"抱歉，分析过程中出现错误：{str(e)}"}
