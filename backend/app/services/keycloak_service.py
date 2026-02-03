"""
Keycloak OIDC 服务（生产级）

功能特性：
1. 异步 HTTP 客户端（连接池、HTTP/2 支持）
2. JWKS 公钥缓存（减少 Keycloak 请求）
3. 智能重试机制（指数退避）
4. 完善的错误处理和日志
5. Token 验证和刷新
6. 用户信息同步
"""

import logging
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
from jose import jwt, jwk
from jose.exceptions import JWTError
from cachetools import TTLCache
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.core.keycloak_config import keycloak_config

logger = logging.getLogger(__name__)


class KeycloakConnectionError(Exception):
    """Keycloak 连接错误"""
    pass


class KeycloakTokenError(Exception):
    """Token 错误"""
    pass


class KeycloakService:
    """
    Keycloak OIDC 服务（生产级）

    特性：
    - 异步 HTTP 客户端（连接池）
    - JWKS 公钥缓存（TTL 1小时）
    - 智能重试（指数退避）
    - 健康检查
    """

    def __init__(self):
        self.config = keycloak_config
        self._jwks_cache: TTLCache = TTLCache(
            maxsize=10,
            ttl=self.config.jwks_cache_ttl
        )
        self._client: Optional[httpx.AsyncClient] = None
        self._last_health_check: Optional[datetime] = None
        # 存储 kid -> key 的映射
        self._jwks_keys_map: Dict[str, Any] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        """
        获取 HTTP 客户端（懒加载）

        Returns:
            配置好的异步 HTTP 客户端
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.server_url,
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                ),
                http2=True,  # 启用 HTTP/2
            )
        return self._client

    async def close(self):
        """关闭 HTTP 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # ========================================
    # 健康检查
    # ========================================

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            Keycloak 是否可用
        """
        try:
            client = await self._get_client()

            # 检查 Realm 是否可访问
            response = await client.get(
                f"realms/{self.config.realm}/.well-known/openid-configuration",
                timeout=5.0
            )
            response.raise_for_status()

            self._last_health_check = datetime.now()
            logger.info("Keycloak health check passed")
            return True

        except Exception as e:
            logger.error(f"Keycloak health check failed: {e}")
            return False

    # ========================================
    # Token 操作
    # ========================================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        交换授权码获取 token

        Args:
            code: 授权码
            redirect_uri: 回调 URL（必须与授权请求中的完全一致）

        Returns:
            Token 响应，包含 access_token, refresh_token, expires_in 等

        Raises:
            KeycloakTokenError: Token 交换失败

        注意：
            授权码是通过 frontend_client_id 获取的，所以也必须用 frontend_client_id 来交换
            frontend_client 是 public client，不需要 client_secret
        """
        try:
            client = await self._get_client()

            # 使用 frontend_client_id 交换 token（与授权请求保持一致）
            response = await client.post(
                f"realms/{self.config.realm}/protocol/openid-connect/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.config.frontend_client_id,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()

            tokens = response.json()

            logger.info(
                f"Token exchanged successfully, "
                f"expires_in: {tokens.get('expires_in')}s"
            )

            return tokens

        except httpx.HTTPStatusError as e:
            logger.error(f"Token exchange failed: {e.response.status_code} - {e.response.text}")
            raise KeycloakTokenError(f"Failed to exchange code: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            raise KeycloakTokenError(f"Unexpected error: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新 access token

        Args:
            refresh_token: 刷新 token

        Returns:
            新的 token 响应

        Raises:
            KeycloakTokenError: Token 刷新失败
        """
        try:
            client = await self._get_client()

            response = await client.post(
                f"realms/{self.config.realm}/protocol/openid-connect/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.config.backend_client_id,
                    "client_secret": self.config.backend_client_secret,
                    "refresh_token": refresh_token,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()

            tokens = response.json()

            logger.info("Token refreshed successfully")

            return tokens

        except httpx.HTTPStatusError as e:
            logger.error(f"Token refresh failed: {e.response.status_code}")
            raise KeycloakTokenError(f"Failed to refresh token: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {e}")
            raise KeycloakTokenError(f"Unexpected error: {str(e)}")

    # ========================================
    # Token 验证
    # ========================================

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证 Keycloak JWT token

        Args:
            token: JWT access token

        Returns:
            Token payload（解码后的内容），验证失败返回 None
        """
        try:
            # 解码 token 的 header 获取 kid
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')

            # 获取 JWKS 公钥映射（kid -> key）
            keys_map = await self._get_jwks_keys()

            # 从映射中获取对应的 key
            key = keys_map.get(kid)
            if not key:
                logger.error(f"No key found for kid: {kid}")
                return None

            # 解码并验证 token（不验证 audience，接受 Keycloak 的任何 audience）
            # options={'verify_aud': False} 禁用 audience 验证
            payload = jwt.decode(
                token,
                key=key.to_dict(),  # 转换为字典格式
                algorithms=["RS256"],
                issuer=self.config.issuer,
                options={'verify_aud': False}  # 不验证 audience
            )

            logger.debug(f"Token verified for user: {payload.get('sub')}")

            return payload

        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return None

    async def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Token 内省（向 Keycloak 验证 token）

        Args:
            token: 要验证的 token

        Returns:
            内省结果，包含 active 状态等信息
        """
        try:
            client = await self._get_client()

            response = await client.post(
                f"realms/{self.config.realm}/protocol/openid-connect/token/introspect",
                data={
                    "client_id": self.config.backend_client_id,
                    "client_secret": self.config.backend_client_secret,
                    "token": token,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Token introspection failed: {e}")
            return {"active": False}

    # ========================================
    # 用户信息
    # ========================================

    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息

        Args:
            access_token: 有效的 access token

        Returns:
            用户信息字典
        """
        try:
            client = await self._get_client()

            response = await client.get(
                f"realms/{self.config.realm}/protocol/openid-connect/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )
            response.raise_for_status()

            user_info = response.json()

            logger.debug(f"User info retrieved: {user_info.get('email')}")

            return user_info

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user info: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user info: {e}")
            return None

    # ========================================
    # 登出
    # ========================================

    async def logout(self, refresh_token: str) -> bool:
        """
        登出用户

        Args:
            refresh_token: 刷新 token

        Returns:
            是否成功登出
        """
        try:
            client = await self._get_client()

            response = await client.post(
                f"realms/{self.config.realm}/protocol/openid-connect/logout",
                data={
                    "client_id": self.config.backend_client_id,
                    "client_secret": self.config.backend_client_secret,
                    "refresh_token": refresh_token,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()

            logger.info("User logged out successfully")

            return True

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False

    # ========================================
    # 辅助方法
    # ========================================

    async def _get_jwks_keys(self) -> Dict[str, Any]:
        """
        获取 JWKS 公钥（带缓存）

        Returns:
            kid -> key 的映射字典

        Raises:
            KeycloakConnectionError: 无法获取公钥
        """
        # 检查缓存
        cache_key = f"{self.config.server_url}_{self.config.realm}"
        if cache_key in self._jwks_cache:
            logger.debug("Using cached JWKS keys")
            return self._jwks_cache[cache_key]

        try:
            client = await self._get_client()

            response = await client.get(
                f"realms/{self.config.realm}/protocol/openid-connect/certs"
            )
            response.raise_for_status()

            jwks_data = response.json()

            # 构建 kid -> key 的映射
            keys_map = {}
            for key_data in jwks_data.get('keys', []):
                try:
                    kid = key_data.get('kid')
                    if kid:
                        key = jwk.construct(key_data)
                        keys_map[kid] = key
                except Exception as e:
                    logger.warning(f"Failed to construct key {key_data.get('kid')}: {e}")

            if not keys_map:
                raise KeycloakConnectionError("No valid keys found in JWKS")

            # 缓存公钥映射
            self._jwks_cache[cache_key] = keys_map

            logger.info(f"JWKS keys loaded and cached ({len(keys_map)} keys)")

            return keys_map

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch JWKS: {e.response.status_code}")
            raise KeycloakConnectionError(f"Cannot fetch JWKS: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error fetching JWKS: {e}")
            raise KeycloakConnectionError(f"Cannot fetch JWKS: {str(e)}")

    def get_auth_url(
        self,
        redirect_uri: str,
        state: Optional[str] = None,
        scope: str = "openid profile email"
    ) -> str:
        """
        生成 Keycloak 授权 URL

        Args:
            redirect_uri: 回调 URL
            state: 状态参数（防 CSRF）
            scope: OAuth scope

        Returns:
            授权 URL
        """
        from urllib.parse import urlencode

        params = {
            "client_id": self.config.frontend_client_id,
            "response_type": "code",
            "scope": scope,
            "redirect_uri": redirect_uri,
        }

        if state:
            params["state"] = state

        return f"{self.config.authorization_endpoint}?{urlencode(params)}"


# ========================================
# 全局服务实例
# ========================================

_keycloak_service: Optional[KeycloakService] = None


async def get_keycloak_service() -> KeycloakService:
    """
    获取 Keycloak 服务单例

    Returns:
        KeycloakService 实例
    """
    global _keycloak_service

    if _keycloak_service is None:
        if not keycloak_config.enabled:
            logger.warning("Keycloak is disabled in configuration")
            return None

        _keycloak_service = KeycloakService()

        # 启动时进行健康检查
        await _keycloak_service.health_check()

    return _keycloak_service


async def close_keycloak_service():
    """关闭 Keycloak 服务"""
    global _keycloak_service

    if _keycloak_service:
        await _keycloak_service.close()
        _keycloak_service = None
