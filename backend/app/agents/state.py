from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    intent: str
    retrieved_docs: list[dict]
    kg_results: list[dict]
    context: str
    response: str
