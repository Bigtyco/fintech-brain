from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import login_rate_limiter
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services.auth_service import register_user, authenticate_user, create_tokens, refresh_access_token
from app.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["认证"])
settings = get_settings()

COOKIE_KWARGS = {
    "httponly": True,
    "secure": False,  # Docker HTTP 环境；生产环境应改 True
    "samesite": "lax",
    "path": "/",
}


def _set_token_cookies(response: Response, tokens: TokenResponse) -> None:
    max_access = settings.jwt_access_token_expire_minutes * 60
    max_refresh = settings.jwt_refresh_token_expire_days * 86400
    response.set_cookie("access_token", tokens.access_token, max_age=max_access, **COOKIE_KWARGS)
    response.set_cookie("refresh_token", tokens.refresh_token, max_age=max_refresh, **COOKIE_KWARGS)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(req: RegisterRequest, _rate: None = Depends(login_rate_limiter), db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, req)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, response: Response, _rate: None = Depends(login_rate_limiter), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    tokens = create_tokens(user)
    _set_token_cookies(response, tokens)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token", "")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="未提供刷新令牌")
    tokens = await refresh_access_token(db, refresh_token)
    if not tokens:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")
    _set_token_cookies(response, tokens)
    return tokens


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"detail": "已登出"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
