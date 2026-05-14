from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.router import router_node
from app.agents.nodes.retrieval import retrieval_node
from app.agents.nodes.knowledge_graph import knowledge_graph_node
from app.agents.nodes.research import research_node
from app.agents.nodes.risk_control import risk_control_node
from app.agents.nodes.response import response_node
from app.core.logging import logger


def route_intent(state: AgentState) -> str:
    intent = state.get("intent", "chat")
    logger.info(f"Routing to: {intent}")
    if intent == "research":
        return "research"
    elif intent == "risk":
        return "risk"
    else:
        return "chat"


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("kg_query", knowledge_graph_node)
    workflow.add_node("research", research_node)
    workflow.add_node("risk_control", risk_control_node)
    workflow.add_node("response", response_node)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "research": "retrieval",
            "risk": "retrieval",
            "chat": "response",
        },
    )

    workflow.add_edge("retrieval", "kg_query")
    workflow.add_conditional_edges(
        "kg_query",
        lambda state: state.get("intent", "chat"),
        {
            "research": "research",
            "risk": "risk_control",
        },
    )

    workflow.add_edge("research", END)
    workflow.add_edge("risk_control", END)
    workflow.add_edge("response", END)

    return workflow.compile()
