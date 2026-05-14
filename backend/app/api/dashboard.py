from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["风控看板"])


@router.get("/overview")
async def get_overview(current_user: User = Depends(get_current_user)):
    return {
        "risk_alerts": 12,
        "pending_reviews": 5,
        "documents_indexed": 128,
        "knowledge_entities": 3456,
    }


@router.get("/risk-trends")
async def get_risk_trends(current_user: User = Depends(get_current_user)):
    return {
        "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "credit_risk": [30, 25, 35, 40, 28, 22],
        "market_risk": [45, 50, 42, 38, 55, 48],
        "operational_risk": [15, 18, 12, 20, 16, 14],
    }


@router.get("/risk-distribution")
async def get_risk_distribution(current_user: User = Depends(get_current_user)):
    return {
        "categories": ["信用风险", "市场风险", "操作风险", "流动性风险", "合规风险"],
        "values": [35, 28, 15, 12, 10],
    }
