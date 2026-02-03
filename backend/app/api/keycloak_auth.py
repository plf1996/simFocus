"""
Keycloak OIDC 认证路由

实现 OAuth2/OIDC 授权码流程：
1. 前端重定向到 Keycloak 登录
2. 用户登录后回调，携带授权码
3. 后端用授权码交换 token
4. 后端同步/创建用户到数据库
5. 重定向回前端，携带 token
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.keycloak_config import keycloak_config
from app.services.keycloak_service import get_keycloak_service
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/keycloak", tags=["Keycloak Auth"])


# ========================================
# 认证流程
# ========================================

@router.get("/login")
async def login(request: Request):
    """
    重定向到 Keycloak 进行认证

    前端应该直接访问此端点，让用户在 Keycloak 登录页面登录
    """
    if not keycloak_config.enabled:
        raise HTTPException(
            status_code=503,
            detail="Keycloak authentication is not enabled"
        )

    service = await get_keycloak_service()
    if not service:
        raise HTTPException(
            status_code=503,
            detail="Keycloak service is not available"
        )

    # 生成 state 参数（CSRF 保护）
    state = secrets.token_urlsafe(32)

    # TODO: 在生产环境中，应该将 state 存储在 Redis 中
    # 并设置过期时间（如 5 分钟）

    # 构建回调 URL - 注意这里的路径要匹配前端配置
    redirect_uri = f"{request.url.scheme}://{request.url.netloc}/api/auth/keycloak/callback"

    # 生成授权 URL
    auth_url = service.get_auth_url(
        redirect_uri=redirect_uri,
        state=state
    )

    logger.info(f"Redirecting to Keycloak for authentication, state={state[:8]}...")

    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Keycloak 认证回调

    处理流程：
    1. 接收授权码
    2. 用授权码交换 access token
    3. 获取用户信息
    4. 同步/创建用户到数据库
    5. 重定向回前端
    """
    if not keycloak_config.enabled:
        raise HTTPException(
            status_code=503,
            detail="Keycloak authentication is not enabled"
        )

    try:
        service = await get_keycloak_service()

        # TODO: 验证 state 参数（从 Redis 中获取并比对）

        # 构建回调 URL（必须与授权请求中的完全一致）
        redirect_uri = f"{request.url.scheme}://{request.url.netloc}/api/auth/keycloak/callback"

        # 用授权码交换 token
        logger.info("Exchanging authorization code for token")
        tokens = await service.exchange_code_for_token(
            code=code,
            redirect_uri=redirect_uri
        )

        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token", "")

        # 获取用户信息
        user_info = await service.get_user_info(access_token)
        if not user_info:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve user information"
            )

        logger.info(f"User authenticated: {user_info.get('email')}")

        # 同步或创建用户到数据库
        from app.services.user_service import UserService

        user_service = UserService(db)
        user = await user_service.get_user_by_email(user_info["email"])

        if not user:
            # 创建新用户
            from app.schemas.user import UserCreate
            from uuid import uuid4
            import secrets
            import string

            # 构建用户名
            given_name = user_info.get("given_name", "")
            family_name = user_info.get("family_name", "")
            full_name = f"{given_name} {family_name}".strip()
            if not full_name:
                full_name = user_info.get("preferred_username", user_info.get("email", "").split("@")[0])

            # 为 Keycloak 用户生成随机密码（不会被使用，但满足 schema 要求）
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            random_password = ''.join(secrets.choice(alphabet) for _ in range(32))

            user_create = UserCreate(
                email=user_info["email"],
                name=full_name,
                password=random_password,  # Keycloak 用户不需要本地密码，生成随机密码满足 schema
                auth_provider="keycloak",
                provider_id=user_info.get("sub", str(uuid4())),
                email_verified=user_info.get("email_verified", False)
            )

            user = await user_service.create_user(user_create)
            logger.info(f"Created new user: {user.email}")

        # TODO: 将 refresh_token 存储到数据库或 Redis
        # await user_service.update_keycloak_tokens(user.id, refresh_token)

        # 重定向到前端成功页面
        # 注意：这里的 URL 需要与前端的 URL 一致
        frontend_url = f"{request.url.scheme}://{request.url.netloc.replace(':8000', ':3000')}"
        return RedirectResponse(
            url=f"{frontend_url}/auth/success?token={access_token}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication callback error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )


# ========================================
# Token 管理
# ========================================

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    刷新 access token

    Args:
        refresh_token: 刷新 token

    Returns:
        新的 token 信息
    """
    if not keycloak_config.enabled:
        raise HTTPException(
            status_code=503,
            detail="Keycloak authentication is not enabled"
        )

    service = await get_keycloak_service()

    try:
        tokens = await service.refresh_token(refresh_token)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token", refresh_token),
            "expires_in": tokens.get("expires_in", 300),
            "token_type": tokens.get("token_type", "Bearer")
        }

    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout(refresh_token: str):
    """
    从 Keycloak 登出

    Args:
        refresh_token: 刷新 token

    Returns:
        登出结果
    """
    if not keycloak_config.enabled:
        raise HTTPException(
            status_code=503,
            detail="Keycloak authentication is not enabled"
        )

    service = await get_keycloak_service()

    success = await service.logout(refresh_token)

    if success:
        return {"message": "Logged out successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to logout from Keycloak"
        )


# ========================================
# 健康检查
# ========================================

@router.get("/health")
async def health_check():
    """
    Keycloak 服务健康检查

    Returns:
        健康状态
    """
    service = await get_keycloak_service()

    if not service:
        return {
            "status": "disabled",
            "message": "Keycloak authentication is not enabled"
        }

    is_healthy = await service.health_check()

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "config": {
            "server_url": keycloak_config.server_url,
            "realm": keycloak_config.realm,
            "frontend_client_id": keycloak_config.frontend_client_id,
            "backend_client_id": keycloak_config.backend_client_id,
        }
    }
