from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse, ConversationDetailResponse
from app.services.chat_service import process_chat, list_conversations, get_conversation_detail

router = APIRouter(prefix="/api/chat", tags=["对话"])


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info(f"Chat request from user {current_user.id}: {req.message[:50]}...")
        conv, response_text, intent = await process_chat(
            db, current_user.id, req.conversation_id, req.message
        )
        logger.info(f"Chat response ready: conversation_id={conv.id}, intent={intent}, length={len(response_text)}")
        return ChatResponse(conversation_id=conv.id, message=response_text, intent=intent)
    except Exception as e:
        logger.error(f"Chat API error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_conversations(db, current_user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await get_conversation_detail(db, conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conv
