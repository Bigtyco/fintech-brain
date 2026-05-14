from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.agents.graph import build_graph


async def get_or_create_conversation(db: AsyncSession, user_id: int, conversation_id: int | None) -> Conversation:
    if conversation_id:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    conv = Conversation(user_id=user_id)
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


async def save_message(db: AsyncSession, conversation_id: int, role: str, content: str, intent: str | None = None) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content, intent=intent)
    db.add(msg)
    await db.flush()
    return msg


async def get_conversation_history(db: AsyncSession, conversation_id: int) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in messages]


async def process_chat(db: AsyncSession, user_id: int, conversation_id: int | None, user_message: str) -> tuple[Conversation, str, str]:
    conv = await get_or_create_conversation(db, user_id, conversation_id)
    await save_message(db, conv.id, "user", user_message)

    history = await get_conversation_history(db, conv.id)
    graph = build_graph()

    result = await graph.ainvoke({
        "messages": history,
        "intent": "",
        "retrieved_docs": [],
        "kg_results": [],
        "context": "",
        "response": "",
    })

    response_text = result.get("response", "抱歉，暂时无法处理您的请求。")
    intent = result.get("intent", "chat")

    await save_message(db, conv.id, "assistant", response_text, intent)

    if conv.title == "新对话":
        conv.title = user_message[:50]

    return conv, response_text, intent


async def list_conversations(db: AsyncSession, user_id: int) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation_detail(db: AsyncSession, conversation_id: int, user_id: int) -> Conversation | None:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
    )
    return result.scalar_one_or_none()
