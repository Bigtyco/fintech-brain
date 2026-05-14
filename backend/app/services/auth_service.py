from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


async def register_user(db: AsyncSession, req: RegisterRequest) -> User:
    existing = await db.execute(
        select(User).where((User.username == req.username) | (User.email == req.email))
    )
    if existing.scalar_one_or_none():
        raise ValueError("用户名或邮箱已存在")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=get_password_hash(req.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_tokens(user: User) -> TokenResponse:
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse | None:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None
    return create_tokens(user)
