from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation, Message

router = APIRouter(prefix="/api/dashboard", tags=["风控看板"])


@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    conv_count = (await db.execute(select(func.count(Conversation.id)))).scalar() or 0
    msg_count = (await db.execute(
        select(func.count(Message.id)).where(Message.role == "assistant")
    )).scalar() or 0
    risk_count = (await db.execute(
        select(func.count(Message.id)).where(Message.intent == "risk")
    )).scalar() or 0

    return {
        "documents_indexed": doc_count,
        "conversations": conv_count,
        "ai_responses": msg_count,
        "risk_queries": risk_count,
    }


@router.get("/risk-trends")
async def get_risk_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    labels = []
    risk_counts = []
    research_counts = []

    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = (now - timedelta(days=30 * (i - 1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = now

        labels.append(f"{month_start.month}月")

        risk_n = (await db.execute(
            select(func.count(Message.id)).where(
                Message.intent == "risk",
                Message.created_at >= month_start,
                Message.created_at < month_end,
            )
        )).scalar() or 0
        research_n = (await db.execute(
            select(func.count(Message.id)).where(
                Message.intent == "research",
                Message.created_at >= month_start,
                Message.created_at < month_end,
            )
        )).scalar() or 0

        risk_counts.append(risk_n)
        research_counts.append(research_n)

    return {
        "labels": labels,
        "risk_queries": risk_counts,
        "research_queries": research_counts,
    }


@router.get("/risk-distribution")
async def get_risk_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    intent_counts = (await db.execute(
        select(Message.intent, func.count(Message.id))
        .where(Message.intent.isnot(None))
        .group_by(Message.intent)
    )).all()

    intent_labels = {"research": "投研分析", "risk": "风险评估", "chat": "通用对话"}
    categories = []
    values = []
    for intent, count in intent_counts:
        categories.append(intent_labels.get(intent, intent))
        values.append(count)

    if not categories:
        categories = ["暂无数据"]
        values = [0]

    return {"categories": categories, "values": values}
