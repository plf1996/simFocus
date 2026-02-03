"""
Keycloak OIDC 配置（生产级）

功能特性：
1. 环境变量自动加载
2. 配置验证
3. 支持开关切换
4. 敏感信息保护
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import os


class KeycloakConfig(BaseModel):
    """Keycloak 配置模型"""

    # 基础配置
    enabled: bool = Field(
        default=False,
        description="是否启用 Keycloak 认证"
    )

    # 服务器配置（从 .env 读取）
    server_url: str = Field(
        default="https://keycloak.plfai.cn/",
        description="Keycloak 服务器 URL"
    )

    realm: str = Field(
        default="simfocus",
        description="Realm 名称"
    )

    # 客户端配置
    frontend_client_id: str = Field(
        default="simfocus-frontend",
        description="前端客户端 ID"
    )

    backend_client_id: str = Field(
        default="simfocus-backend",
        description="后端客户端 ID"
    )

    backend_client_secret: str = Field(
        default="",
        description="后端客户端密钥"
    )

    # 连接配置
    timeout: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="HTTP 请求超时时间（秒）"
    )

    max_connections: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="最大连接池大小"
    )

    max_keepalive_connections: int = Field(
        default=20,
        ge=5,
        le=100,
        description="最大保持连接数"
    )

    # 缓存配置
    jwks_cache_ttl: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="JWKS 公钥缓存时间（秒）"
    )

    # 重试配置
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="最大重试次数"
    )

    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="重试延迟（秒）"
    )

    @field_validator('server_url')
    @classmethod
    def normalize_server_url(cls, v: str) -> str:
        """标准化服务器 URL"""
        if not v.endswith('/'):
            v += '/'
        return v

    @property
    def issuer(self) -> str:
        """获取 issuer"""
        return f"{self.server_url}realms/{self.realm}"

    @property
    def authorization_endpoint(self) -> str:
        """授权端点"""
        return f"{self.issuer}/protocol/openid-connect/auth"

    @property
    def token_endpoint(self) -> str:
        """Token 端点"""
        return f"{self.issuer}/protocol/openid-connect/token"

    @property
    def userinfo_endpoint(self) -> str:
        """用户信息端点"""
        return f"{self.issuer}/protocol/openid-connect/userinfo"

    @property
    def jwks_uri(self) -> str:
        """JWKS 公钥端点"""
        return f"{self.issuer}/protocol/openid-connect/certs"

    @property
    def logout_endpoint(self) -> str:
        """登出端点"""
        return f"{self.issuer}/protocol/openid-connect/logout"

    @property
    def introspection_endpoint(self) -> str:
        """Token 内省端点"""
        return f"{self.issuer}/protocol/openid-connect/token/introspect"


def load_keycloak_config() -> KeycloakConfig:
    """
    从环境变量加载 Keycloak 配置

    环境变量映射（.env 文件）：
    - Keycloak_Base_URL -> server_url
    - Realm_Name -> realm
    - Frontend_Client_ID -> frontend_client_id
    - Backend_Client_ID -> backend_client_id
    - Backend_Client_Secret -> backend_client_secret
    """
    # 从环境变量读取（支持你的 .env 格式）
    config = KeycloakConfig(
        enabled=os.getenv("KEYCLOAK_ENABLED", "true").lower() == "true",
        server_url=os.getenv("Keycloak_Base_URL", "https://keycloak.plfai.cn/"),
        realm=os.getenv("Realm_Name", "simfocus"),
        frontend_client_id=os.getenv("Frontend_Client_ID", "simfocus-frontend"),
        backend_client_id=os.getenv("Backend_Client_ID", "simfocus-backend"),
        backend_client_secret=os.getenv("Backend_Client_Secret", ""),
    )

    return config


# 全局配置实例
keycloak_config = load_keycloak_config()
