from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.keycloak_config import keycloak_config
from app.services.keycloak_service import get_keycloak_service
from app.models.user import User
from typing import Annotated, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前认证用户（支持双重验证）

    验证流程：
    1. 优先尝试验证 Keycloak token
    2. 如果 Keycloak 验证失败，回退到本地 JWT
    3. 从数据库加载用户信息
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # 尝试验证 Keycloak token（如果启用）
    if keycloak_config.enabled:
        try:
            service = await get_keycloak_service()
            if service:
                payload = await service.verify_token(token)

                if payload:
                    # Token 来自 Keycloak
                    email = payload.get("email")

                    if email:
                        from app.services.user_service import UserService
                        user_service = UserService(db)
                        user = await user_service.get_user_by_email(email)

                        if user:
                            logger.info(f"User authenticated via Keycloak: {user.email}")
                            return user

        except Exception as e:
            logger.debug(f"Keycloak token verification failed: {e}")
            # 继续尝试本地 JWT

    # 回退到本地 JWT token 验证
    try:
        internal_payload = decode_access_token(token)
        user_id: str = internal_payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # 从数据库查询用户
    from app.services.user_service import UserService
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id=UUID(user_id))

    if user is None:
        raise credentials_exception

    logger.info(f"User authenticated via internal JWT: {user.email}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
