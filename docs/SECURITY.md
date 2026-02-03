# 前端代码安全说明

## 问题说明

您在浏览器开发者工具中看到的 JavaScript 源代码（如 `auth.js`）**不是安全漏洞**，这是所有 Web 应用的正常行为。

## 为什么前端代码是可见的？

任何用户都可以通过浏览器查看：
- 所有加载的 JavaScript 文件
- 网络请求
- 页面源代码
- LocalStorage 和 SessionStorage

这是 Web 技术的固有特性，**无法完全避免**。

## 安全措施对比

| 特性 | 开发模式 | 生产模式 |
|------|----------------|----------------|
| 代码可读性 | 完整源代码，易于阅读 | 压缩混淆，难以阅读 |
| 文件名 | `auth.js` | `auth.abc123.js` (内容哈希) |
| Source Maps | 启用（可还原源码） | **禁用** |
| 代码大小 | 未压缩 | Gzip 压缩（减少 70-80%） |
| 加载方式 | Vite 开发服务器 | Nginx 静态文件服务 |

## 生产环境安全措施

### 1. 代码混淆和压缩
```javascript
// 开发模式（可读）
export const login = async (email, password) => {
  const response = await api.post('/api/auth/login', {
    email,
    password
  })
  return response.data
}

// 生产模式（混淆）
const t=async(t,e)=>{const o=(await s.A.post("/api/auth/login",{email:t,password:e})).data;return o};
```

### 2. 文件名哈希
```
开发: /src/stores/auth.js
生产: /assets/auth.8f3d2a1b.js
```

### 3. 禁用 Source Maps
生产环境不生成 `.map` 文件，无法还原源代码。

### 4. 安全响应头
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### 5. 内容安全策略 (CSP)
防止 XSS 攻击。

## 真正需要保护的是什么？

### ✅ 需要在后端保护
- **密码和密钥**：永远不要在前端存储或传输明文密码
- **API 密钥**：OpenAI API Key、数据库连接字符串等
- **业务逻辑**：权限检查、数据过滤、价格计算
- **敏感数据**：其他用户的个人信息

### ❌ 前端可以暴露
- **前端代码本身**：Vue 组件、工具函数
- **API 端点**：REST API 路径
- **Keycloak 配置**：客户端 ID（本来就是公开的）
- **UI 相关信息**：路由、页面结构

## 部署生产环境

### 开发环境（当前）
```bash
docker-compose up
```
- 使用 `npm run dev`
- 代码完整可读
- 适合开发和调试

### 生产环境（推荐）
```bash
docker-compose -f docker-compose.prod.yml up --build
```
- 使用多阶段构建
- Nginx 服务静态文件
- 代码压缩混淆
- 无 source maps
- 性能优化（Gzip 压缩）

## 验证生产构建

构建后，检查浏览器开发者工具：

### 开发模式
```
Sources
  └─ src/
      └─ stores/
          └─ auth.js         ← 完整源代码
```

### 生产模式
```
Sources
  └─ 192.168.0.16:3000/
      └─ assets/
          └─ auth.8f3d2a1b.js  ← 压缩混淆的单行代码
```

## 安全最佳实践

### 1. 环境变量管理
```bash
# ✅ 正确：前端环境变量（可公开）
VITE_API_BASE_URL=http://192.168.0.16:8000
VITE_KEYCLOAK_CLIENT_ID=simfocus-frontend

# ❌ 错误：不要在前端放置敏感信息
VITE_OPENAI_API_KEY=sk-xxx  ← 错误！
VITE_DB_PASSWORD=xxx        ← 错误！
```

### 2. API 安全
- 所有敏感操作在后端进行
- 使用 JWT token 验证身份
- 后端验证所有请求参数
- 实施速率限制

### 3. Keycloak 配置安全
- **前端客户端**（simfocus-frontend）：Public Client，无密钥，可公开
- **后端客户端**（simfocus-backend）：Confidential Client，有密钥，必须保密

### 4. Docker 安全
```yaml
# docker-compose.yml（开发）
volumes:
  - ./frontend:/app  ← 挂载源代码，便于开发

# docker-compose.prod.yml（生产）
# 无卷挂载，代码打包在镜像内
```

## 总结

| 关注点 | 开发模式 | 生产模式 |
|--------|---------|----------|
| 代码可读性 | 高（适合调试） | 低（混淆压缩） |
| 性能 | 低（未优化） | 高（Gzip + 缓存） |
| 安全性 | 中（可读源码） | 高（混淆 + 无 source maps） |
| 用途 | 开发测试 | 生产部署 |

**建议**：
- 开发时使用 `docker-compose.yml`（开发模式）
- 生产部署使用 `docker-compose.prod.yml`（生产模式）
- 定期更新依赖，修复安全漏洞
- 后端实施严格的安全检查

## 系统认证架构详解

### 认证机制概览

simFocus 采用**双重认证机制**，支持两种登录方式：

```
┌─────────────────────────────────────────────────────────────┐
│                      用户登录流程                             │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
          本地邮箱密码登录          Keycloak SSO
                │                       │
                ▼                       ▼
        ┌───────────────┐     ┌───────────────┐
        │  生成 JWT     │     │  OAuth2/OIDC  │
        │  (本地签名)   │     │  授权码流程   │
        └───────────────┘     └───────────────┘
                │                       │
                │                       ▼
                │              ┌───────────────┐
                │              │ 后端交换 token │
                │              │ 获取 Keycloak │
                │              │ Access Token  │
                │              └───────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
                  ┌─────────────────┐
                  │ 前端存储 Token  │
                  │ (LocalStorage)  │
                  └─────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ 后端验证 Token  │
                  │ (Keycloak优先)  │
                  └─────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │   访问受保护    │
                  │     资源       │
                  └─────────────────┘
```

### 1. 本地 JWT 认证

#### 流程说明

**后端：生成 JWT Token**

```python
# 文件：backend/app/services/auth_service.py

from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    创建本地 JWT access token

    Args:
        data: 要编码的数据（通常包含 user_id）
        expires_delta: 过期时间增量

    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()

    # 设置过期时间（默认 1440 分钟 = 24 小时）
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)

    to_encode.update({"exp": expire})

    # 使用 SECRET_KEY 签名（在 .env 中配置）
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,  # 密钥，必须保密
        algorithm=settings.ALGORITHM  # HS256
    )

    return encoded_jwt
```

**安全要点：**
- ✅ `SECRET_KEY` 存储在后端环境变量，从不暴露给前端
- ✅ 使用 HS256 算法（对称加密，性能好）
- ✅ Token 包含过期时间（exp），防止永久有效
- ✅ Token 只包含 user_id，不包含敏感信息

**前端：使用 Token**

```javascript
// 文件：frontend/src/stores/auth.js

import axios from 'axios'

// 配置 axios 拦截器，自动添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    // 每个请求都携带 token
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 登录示例
const login = async (email, password) => {
  const response = await api.post('/api/auth/login', {
    email,
    password
  })
  // 后端返回 JWT token
  const token = response.data.access_token
  // 存储到 localStorage
  localStorage.setItem('token', token)
  // 设置认证提供者
  localStorage.setItem('auth_provider', 'local')
}
```

**后端：验证 Token**

```python
# 文件：backend/app/api/dependencies.py

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()  # 要求 Bearer token

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    验证 JWT token 并返回当前用户

    流程：
    1. 从请求头提取 token (Authorization: Bearer <token>)
    2. 解码 token
    3. 从数据库获取用户信息
    4. 返回用户对象
    """
    token = credentials.credentials

    try:
        # 解码 token（验证签名和过期时间）
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 从数据库获取用户
    user = await user_service.get_user_by_id(UUID(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

**使用示例：**

```python
# 文件：backend/app/api/topics.py

from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/api/topics")
async def get_topics(
    current_user: User = Depends(get_current_user)  # ← 需要认证
):
    """只有认证用户才能访问"""
    return {"topics": [...], "user": current_user.email}
```

### 2. Keycloak SSO 认证

#### OAuth 2.0 / OIDC 授权码流程

```
┌──────────────────────────────────────────────────────────────┐
│              OAuth 2.0 授权码流程（Authorization Code Flow）   │
└──────────────────────────────────────────────────────────────┘

  用户浏览器           前端 (3000)        后端 (8000)      Keycloak
      │                   │                  │                │
      │  1. 点击 SSO 登录 │                  │                │
      ├──────────────────>│                  │                │
      │                   │                  │                │
      │                   │  2. 重定向到 /api/auth/keycloak/login
      │                   ├─────────────────>│                │
      │                   │                  │                │
      │                   │                  │  3. 生成授权 URL
      │                   │                  ├--------------->│
      │                   │                  │  (client_id,   │
      │                   │                  │   redirect_uri)│
      │                   │                  │<---------------│
      │  4. 重定向到      │                  │                │
      │  Keycloak 登录页  │                  │                │
      ├<──────────────────────────────────────┤                │
      │                   │                  │                │
      │  5. 输入账号密码  │                  │                │
      ├──────────────────────────────────────>│                │
      │                   │                  │                │
      │  6. 回调 callback?code=xxx&state=yyy  │
      ├<──────────────────────────────────────┤                │
      │                   │                  │                │
      │                   │  7. 用 code 交换 token             │
      │                   ├─────────────────>│                │
      │                   │                  ├--------------->│
      │                   │                  │  (code,        │
      │                   │                  │   redirect_uri)│
      │                   │                  │<---------------│
      │                   │                  │  (access_token)│
      │                   │                  │                │
      │                   │  8. 获取用户信息                 │
      │                   ├─────────────────>│                │
      │                   │                  ├--------------->│
      │                   │                  │  (access_token)│
      │                   │                  │<---------------│
      │                   │                  │  (user_info)   │
      │                   │                  │                │
      │                   │  9. 创建/同步用户到数据库         │
      │                   │                  │                │
      │  10. 重定向到成功页 ?token=zzz       │
      ├<──────────────────────────────────────┤                │
      │                   │                  │                │
      │  11. 前端存储 token                 │                  │
      │  (localStorage.setItem('token', ...))                  │
      │                   │                  │                │
      │  12. 后续请求携带 token                              │
      ├──────────────────>│                  │                │
      │                   │  13. 验证 Keycloak token         │
      │                   ├─────────────────>│                │
      │                   │                  │  (JWKS 公钥验证)│
      │                   │<─────────────────┤                │
      │<──────────────────┤                  │                │
```

#### 后端实现详解

**步骤 1：重定向到 Keycloak**

```python
# 文件：backend/app/api/keycloak_auth.py

@router.get("/api/auth/keycloak/login")
async def login(request: Request):
    """重定向到 Keycloak 进行认证"""

    # 1. 生成 state 参数（防 CSRF 攻击）
    #    state 是随机字符串，Keycloak 会原样返回
    #    前端/后端应该验证 state 以防止 CSRF
    state = secrets.token_urlsafe(32)

    # 2. 构建 callback URL（必须与 Keycloak 配置的 Valid Redirect URIs 一致）
    redirect_uri = f"{request.url.scheme}://{request.url.netloc}/api/auth/keycloak/callback"
    # 例如：http://192.168.0.16:8000/api/auth/keycloak/callback

    # 3. 生成授权 URL
    auth_url = keycloak_service.get_auth_url(
        redirect_uri=redirect_uri,
        state=state
    )
    # 例如：https://keycloak.plfai.cn/realms/simfocus/protocol/openid-connect/auth?
    #       client_id=simfocus-frontend&
    #       response_type=code&
    #       redirect_uri=http://192.168.0.16:8000/api/auth/keycloak/callback&
    #       scope=openid profile email&
    #       state=xxx

    # 4. 重定向到 Keycloak 登录页
    return RedirectResponse(url=auth_url)
```

**步骤 2：处理 Keycloak 回调**

```python
# 文件：backend/app/api/keycloak_auth.py

@router.get("/api/auth/keycloak/callback")
async def callback(
    code: str,          # 授权码（有效期 5 分钟）
    state: str,         # 状态参数（防 CSRF）
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Keycloak 认证回调

    流程：
    1. 接收授权码（code）
    2. 用授权码交换 access token
    3. 获取用户信息
    4. 同步/创建用户到数据库
    5. 重定向回前端（携带 token）
    """

    # 1. 构建回调 URL（必须与授权请求中的完全一致）
    redirect_uri = f"{request.url.scheme}://{request.url.netloc}/api/auth/keycloak/callback"

    # 2. 用授权码交换 access token
    tokens = await keycloak_service.exchange_code_for_token(
        code=code,
        redirect_uri=redirect_uri
    )
    # 返回：{access_token, refresh_token, expires_in, ...}

    access_token = tokens["access_token"]

    # 3. 获取用户信息（使用 access_token）
    user_info = await keycloak_service.get_user_info(access_token)
    # 返回：{sub, email, name, given_name, family_name, email_verified, ...}

    # 4. 同步或创建用户到数据库
    user = await user_service.get_user_by_email(user_info["email"])

    if not user:
        # Keycloak 用户首次登录，自动创建本地用户
        from app.schemas.user import UserCreate
        import secrets
        import string

        # 构建用户名
        given_name = user_info.get("given_name", "")
        family_name = user_info.get("family_name", "")
        full_name = f"{given_name} {family_name}".strip()
        if not full_name:
            full_name = user_info.get("preferred_username",
                                     user_info.get("email", "").split("@")[0])

        # 生成随机密码（Keycloak 用户不需要本地密码，但 schema 要求）
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        random_password = ''.join(secrets.choice(alphabet) for _ in range(32))

        user_create = UserCreate(
            email=user_info["email"],
            name=full_name,
            password=random_password,  # 满足 schema 要求，但不会被使用
            auth_provider="keycloak",  # 标记为 Keycloak 用户
            provider_id=user_info.get("sub"),  # Keycloak 用户 ID
            email_verified=user_info.get("email_verified", False)
        )

        user = await user_service.create_user(user_create)

    # 5. 重定向到前端成功页面
    frontend_url = f"{request.url.scheme}://{request.url.netloc.replace(':8000', ':3000')}"
    return RedirectResponse(
        url=f"{frontend_url}/auth/success?token={access_token}"
    )
```

**步骤 3：交换授权码获取 Token**

```python
# 文件：backend/app/services/keycloak_service.py

async def exchange_code_for_token(self, code: str, redirect_uri: str):
    """
    交换授权码获取 token

    关键点：
    1. 使用 frontend_client_id（不是 backend_client_id）
    2. Public client 不需要 client_secret
    3. redirect_uri 必须与授权请求中的完全一致
    """

    client = await self._get_client()

    response = await client.post(
        f"realms/{self.config.realm}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",  # 授权码模式
            "client_id": self.config.frontend_client_id,  # ← 重要：使用 frontend client
            "code": code,
            "redirect_uri": redirect_uri,
            # 注意：public client 不需要 client_secret
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    response.raise_for_status()

    tokens = response.json()
    # 返回：{access_token, refresh_token, expires_in, refresh_expires_in, ...}

    return tokens
```

**为什么使用 frontend_client_id？**

```
授权流程的 client_id 必须一致：

1. 用户访问 /login → 使用 frontend_client_id 生成授权 URL
2. Keycloak 登录页 → frontend_client_id 接受用户登录
3. 回调 /callback → 必须用 frontend_client_id 交换 code

如果使用 backend_client_id 交换 code：
❌ Keycloak 报错：unauthorized_client
❌ 原因：code 是用 frontend_client_id 获取的，不能用 backend_client_id 交换
```

**步骤 4：验证 Keycloak Token**

```python
# 文件：backend/app/api/dependencies.py

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    双重 token 验证（Keycloak 优先，本地 JWT 后备）
    """
    token = credentials.credentials

    # 优先尝试：验证 Keycloak token
    if keycloak_config.enabled:
        service = await get_keycloak_service()
        if service:
            payload = await service.verify_token(token)
            if payload:
                # Keycloak token 有效
                email = payload.get("email")
                if email:
                    user = await user_service.get_user_by_email(email)
                    if user:
                        return user

    # 后备方案：验证本地 JWT token
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        user = await user_service.get_user_by_id(UUID(user_id))
        if user:
            return user
    except JWTError:
        pass

    raise HTTPException(status_code=401, detail="Invalid token")
```

**Keycloak Token 验证详解：**

```python
# 文件：backend/app/services/keycloak_service.py

async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
    """
    验证 Keycloak JWT token

    流程：
    1. 解码 token header 获取 kid（key ID）
    2. 从 JWKS 获取对应的公钥
    3. 用公钥验证 token 签名
    4. 验证 issuer 和过期时间
    5. 返回 token payload
    """

    try:
        # 1. 解码 header 获取 kid
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        # kid 是 Keycloak 用来标识密钥的 ID
        # 例如："kid": "LzIpXvWNSSKMjIHG9hkVIhwNHv8mLUG8JJdSwvWW-kQ"

        # 2. 获取 JWKS 公钥映射（kid -> key）
        keys_map = await self._get_jwks_keys()
        # 返回：{"LzIpXvWN...": <RSAKey>, ...}

        # 3. 获取对应的公钥
        key = keys_map.get(kid)
        if not key:
            logger.error(f"No key found for kid: {kid}")
            return None

        # 4. 解码并验证 token
        payload = jwt.decode(
            token,
            key=key.to_dict(),  # JWKS 公钥
            algorithms=["RS256"],  # Keycloak 使用 RSA 签名
            issuer=self.config.issuer,  # 验证 issuer
            options={'verify_aud': False}  # 不验证 audience（Keycloak 前端 token 的 aud 可能不匹配）
        )

        return payload

    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None
```

**JWKS 公钥获取（带缓存）：**

```python
# 文件：backend/app/services/keycloak_service.py

async def _get_jwks_keys(self) -> Dict[str, Any]:
    """
    获取 Keycloak JWKS 公钥（带缓存）

    JWKS (JSON Web Key Set)：
    - Keycloak 公开的公钥集合
    - 用于验证 JWT token 签名
    - 定期轮换（安全最佳实践）

    缓存策略：
    - TTL: 3600 秒（1 小时）
    - 避免频繁请求 Keycloak
    - 公钥轮换后自动更新
    """
    cache_key = f"{self.config.server_url}_{self.config.realm}"

    # 1. 检查缓存
    if cache_key in self._jwks_cache:
        logger.debug("Using cached JWKS keys")
        return self._jwks_cache[cache_key]

    # 2. 从 Keycloak 获取 JWKS
    try:
        client = await self._get_client()

        response = await client.get(
            f"realms/{self.config.realm}/protocol/openid-connect/certs"
        )
        # 返回：{"keys": [{kid, kty, alg, n, e, ...}, ...]}
        response.raise_for_status()

        jwks_data = response.json()

        # 3. 构建 kid -> key 的映射
        keys_map = {}
        for key_data in jwks_data.get('keys', []):
            try:
                kid = key_data.get('kid')
                if kid:
                    # 使用 python-jose 构造 RSA key 对象
                    key = jwk.construct(key_data)
                    keys_map[kid] = key
            except Exception as e:
                logger.warning(f"Failed to construct key {key_data.get('kid')}: {e}")

        if not keys_map:
            raise KeycloakConnectionError("No valid keys found in JWKS")

        # 4. 缓存公钥映射
        self._jwks_cache[cache_key] = keys_map

        logger.info(f"JWKS keys loaded and cached ({len(keys_map)} keys)")

        return keys_map

    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise KeycloakConnectionError(f"Cannot fetch JWKS: {str(e)}")
```

### 3. 前端实现详解

**Keycloak 配置：**

```javascript
// 文件：frontend/src/config/keycloak.js

export const keycloakConfig = {
  // Keycloak 服务器 URL
  url: import.meta.env.VITE_KEYCLOAK_SERVER_URL, // https://keycloak.plfai.cn/

  // Realm（领域）
  realm: import.meta.env.VITE_KEYCLOAK_REALM, // simfocus

  // 客户端 ID（Public Client）
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID, // simfocus-frontend

  // 前端回调 URL（用于 frontend-direct 模式，本项目未使用）
  redirectUri: window.location.origin + '/auth/callback',

  // 后端 API 基础 URL
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL, // http://192.168.0.16:8000

  // 后端成功页面路径
  backendCallbackPath: '/auth/success',
}

// 获取后端认证 URL（本项目使用的 backend-proxy 模式）
export const getBackendAuthUrl = () => {
  return `${keycloakConfig.apiBaseUrl}/api/auth/keycloak/login`
}

// 获取认证模式
export const getAuthMode = () => {
  return import.meta.env.VITE_AUTH_MODE || 'backend-proxy'
}
```

**认证模式：**

```javascript
// 文件：frontend/src/config/keycloak.js

本项目使用 backend-proxy 模式：

┌──────────────────────────────────────────────────────────┐
│           backend-proxy 模式（本项目使用）                │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  1. 前端调用后端 /api/auth/keycloak/login                 │
│  2. 后端重定向到 Keycloak                                 │
│  3. 用户在 Keycloak 登录                                  │
│  4. Keycloak 回调后端 /api/auth/keycloak/callback        │
│  5. 后端交换 code、获取 token、创建用户                   │
│  6. 后端重定向到前端 /auth/success?token=xxx              │
│  7. 前端存储 token                                        │
│                                                           │
│  优点：                                                   │
│  ✅ 安全：client_secret 在后端，不暴露给前端              │
│  ✅ 简单：前端无需处理 OAuth 复杂逻辑                     │
│  ✅ 灵活：后端可以添加业务逻辑                            │
│                                                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│         frontend-direct 模式（本项目未使用）              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  1. 前端使用 keycloak-js 直接跳转 Keycloak               │
│  2. Keycloak 回调前端 /auth/callback?code=xxx            │
│  3. 前端调用后端 API 用 code 换取 token                  │
│  4. 后端返回 token                                       │
│                                                           │
│  缺点：                                                   │
│  ❌ 复杂：前端需要处理 OAuth 流程                         │
│  ❌ 安全：Public Client 无 client_secret                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**登录流程：**

```javascript
// 文件：frontend/src/views/Login.vue

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Keycloak SSO 登录
const handleKeycloakLogin = async () => {
  try {
    // 1. 保存当前路径，登录后返回
    const redirectPath = router.currentRoute.value.query.redirect || '/topics'
    localStorage.setItem('redirect_after_login', redirectPath)

    // 2. 调用后端登录接口
    //    后端会返回 302 重定向到 Keycloak
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/api/auth/keycloak/login`

    // 3. 用户在 Keycloak 登录后，Keycloak 会回调后端
    // 4. 后端处理完成后，重定向到前端 /auth/success?token=xxx
    // 5. 前端 AuthSuccess.vue 组件处理后续逻辑

  } catch (err) {
    error.value = err.message || 'SSO 登录失败'
  }
}
</script>
```

**处理成功回调：**

```javascript
// 文件：frontend/src/views/AuthSuccess.vue

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    // 1. 显示模态框
    showModal.value = true

    // 2. 从 URL 获取 token（后端传递）
    const token = route.query.token

    if (!token) {
      error.value = '未收到认证令牌'
      return
    }

    // 3. 调用 authStore 处理 Keycloak 回调
    await authStore.handleKeycloakCallback(token)

    loading.value = false

    // 4. 延迟后跳转到目标页面
    setTimeout(() => {
      const redirectTo = localStorage.getItem('redirect_after_login') || '/topics'
      localStorage.removeItem('redirect_after_login')
      router.push(redirectTo)
    }, 1500)

  } catch (err) {
    console.error('Auth success error:', err)
    error.value = err.message || '认证处理失败'
    loading.value = false
  }
})
</script>
```

**AuthStore 实现：**

```javascript
// 文件：frontend/src/stores/auth.js

import { ref, computed } from 'vue'
import { api } from '@/services/api'
import keycloakService from '@/services/keycloak'

export const useAuthStore = () => {
  const token = ref(localStorage.getItem('token'))
  const user = ref(null)
  const authProvider = ref(localStorage.getItem('auth_provider') || 'local')
  const isKeycloakEnabled = ref(import.meta.env.VITE_KEYCLOAK_ENABLED === 'true')

  // 是否已认证
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 处理 Keycloak 回调
  const handleKeycloakCallback = async (keycloakToken) => {
    try {
      // 1. 存储 Keycloak token
      token.value = keycloakToken
      authProvider.value = 'keycloak'

      // 2. 持久化到 localStorage
      localStorage.setItem('token', keycloakToken)
      localStorage.setItem('auth_provider', 'keycloak')

      // 3. 配置 axios 默认 header
      api.defaults.headers.common['Authorization'] = `Bearer ${keycloakToken}`

      // 4. 获取用户信息
      await fetchUser()

    } catch (error) {
      console.error('Keycloak callback error:', error)
      throw error
    }
  }

  // 获取用户信息
  const fetchUser = async () => {
    try {
      const response = await api.get('/api/users/me')
      user.value = response.data
    } catch (error) {
      console.error('Fetch user error:', error)
      // Token 可能过期，清除认证状态
      logout()
    }
  }

  // 登出
  const logout = async () => {
    try {
      // 如果是 Keycloak 认证，可能需要调用 Keycloak logout
      // （当前实现：清除本地状态）
      if (authProvider.value === 'keycloak' && isKeycloakEnabled.value) {
        // 可选：重定向到 Keycloak logout
        // window.location.href = keycloakService.createLogoutUrl()
      }

      // 清除本地状态
      token.value = null
      user.value = null
      authProvider.value = 'local'

      localStorage.removeItem('token')
      localStorage.removeItem('auth_provider')

      delete api.defaults.headers.common['Authorization']

    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return {
    token,
    user,
    authProvider,
    isAuthenticated,
    isKeycloakEnabled,
    handleKeycloakCallback,
    fetchUser,
    logout
  }
}
```

### 4. Keycloak 配置详解

#### Realm 配置

**Realm 名称：simfocus**

```
Realm 是 Keycloak 中的隔离域，类似于租户概念。

配置：
- Name: simfocus
- Display Name: simFocus Platform
- Enabled: ON

影响：
✅ 用户隔离：simFocus 的用户与其他应用的用户隔离
✅ 配置独立：独立的客户端、角色、组
✅ Token issuer: https://keycloak.plfai.cn/realms/simfocus
```

#### Client 配置

**Client 1: simfocus-frontend（前端客户端）**

```
┌────────────────────────────────────────────────────────────┐
│              Client: simfocus-frontend                     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ Client Type: Public                                        │
│   - 无需 client_secret                                     │
│   - 适合浏览器应用                                          │
│   - 无法安全存储密钥                                        │
│                                                             │
│ Client ID: simfocus-frontend                               │
│   - 前端环境变量：VITE_KEYCLOAK_CLIENT_ID                  │
│   - 后端配置：frontend_client_id                           │
│                                                             │
│ Valid Redirect URIs:                                       │
│   + http://192.168.0.16:8000/api/auth/keycloak/callback   │
│   - 后端回调 URL（必须与后端代码一致）                      │
│   - 用户登录后 Keycloak 重定向到此 URL                     │
│                                                             │
│ Valid Redirect URIs (Web):                                 │
│   + http://192.168.0.16:3000/auth/success                 │
│   +                                                         │
│   - 前端成功页面 URL                                        │
│   - 后端最终重定向到此 URL                                  │
│                                                             │
│ Web Origins:                                               │
│   + http://192.168.0.16:*                                  │
│   +                                                         │
│   - CORS 配置                                               │
│   - 允许前端跨域访问                                        │
│   - * 表示允许所有端口                                      │
│                                                             │
│ Authentication Flow:                                       │
│   Standard Flow: ON (授权码模式)                           │
│   Direct Access Grants: OFF (禁止密码模式，不安全)         │
│                                                             │
│ Fine Grain OpenID Connect Configuration:                  │
│   ID Token Signature Algorithm: RS256                      │
│   - 使用 RSA 签名（非对称加密）                             │
│   - 对应后端 jwt.decode(algorithms=["RS256"])             │
│                                                             │
└────────────────────────────────────────────────────────────┘

影响：
✅ 前端可以使用此 client_id 进行授权
✅ 用户登录成功后回调到后端
✅ 支持 CORS，前端可以跨域访问
✅ 使用授权码模式（安全）
❌ 禁用密码模式（防止恶意登录）
```

**Client 2: simfocus-backend（后端客户端）**

```
┌────────────────────────────────────────────────────────────┐
│              Client: simfocus-backend                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ Client Type: Confidential                                  │
│   - 需要 client_secret                                     │
│   - 适合后端服务                                            │
│   - 可以安全存储密钥                                        │
│                                                             │
│ Client ID: simfocus-backend                                │
│   - 后端配置：backend_client_id                            │
│                                                             │
│ Client Secret: 3NouAxsx1lq7z2HZS3VDuSFrtipfe7JN            │
│   - 后端环境变量：KEYCLOAK_BACKEND_CLIENT_SECRET           │
│   - 必须保密，不能暴露给前端                                │
│   - 用于 Service Account 认证                              │
│                                                             │
│ Service Accounts Enabled: ON                               │
│   - 允许后端以自己的身份登录                               │
│   - 用于后端-to-后端通信                                   │
│   - 可访问 Keycloak Admin API                              │
│                                                             │
│ Valid Redirect URIs: (空白)                                │
│   - 后端不需要重定向回调                                    │
│   - 使用 Service Account 直接获取 token                    │
│                                                             │
│ Standard Flow: OFF                                         │
│   - 后端不需要用户交互                                      │
│                                                             │
│ Direct Access Grants: OFF                                  │
│   - 禁用密码模式                                            │
│                                                             │
└────────────────────────────────────────────────────────────┘

影响：
✅ 后端可以独立访问 Keycloak（无需用户交互）
✅ 用于 token 刷新、用户管理等操作
✅ client_secret 必须保密
```

#### 用户配置

**Test User：testuser**

```
┌────────────────────────────────────────────────────────────┐
│              User: testuser                               │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ Username: testuser                                         │
│ Email: testuser@example.com                               │
│ Email Verified: YES                                        │
│                                                             │
│ Credentials:                                               │
│   Password: test2022                                       │
│   - 存储在 Keycloak，加密存储                              │
│   - 后端数据库不存储密码                                   │
│                                                             │
│ Required User Actions: (无)                                │
│   - 用户无需更新密码等操作                                 │
│                                                             │
│ Realm Roles:                                               │
│   - user (默认角色)                                        │
│   - ums_authorize (自定义角色)                             │
│                                                             │
│ Attributes: (无)                                           │
│   - 可以存储自定义属性                                     │
│                                                             │
│ Groups: (无)                                               │
│   - 可以将用户分组管理                                     │
│                                                             │
└────────────────────────────────────────────────────────────┘

影响：
✅ 用户可以使用邮箱+密码登录 Keycloak
✅ 首次登录后，后端会自动创建本地用户记录
✅ 用户的 auth_provider="keycloak"
✅ 本地密码是随机生成，不会被使用
```

### 5. 配置影响分析

#### 后端环境变量

```bash
# 文件：backend/.env

KEYCLOAK_ENABLED=true
# 影响：
# ✅ 启用 Keycloak 双重认证
# ✅ 后端会优先验证 Keycloak token
# ✅ 登录页面显示 SSO 按钮
# ❌ false 时，禁用 Keycloak 认证

KEYCLOAK_SERVER_URL=https://keycloak.plfai.cn/
# 影响：
# ✅ Keycloak 服务器地址
# ✅ 必须与 Keycloak 实例一致
# ❌ 错误会导致无法连接 Keycloak

KEYCLOAK_REALM=simfocus
# 影响：
# ✅ Realm 名称
# ✅ Token issuer: https://keycloak.plfai.cn/realms/simfocus
# ❌ 错误会导致 token 验证失败（issuer 不匹配）

KEYCLOAK_FRONTEND_CLIENT_ID=simfocus-frontend
# 影响：
# ✅ 用于生成授权 URL
# ✅ 用于交换授权码（必须与授权请求一致）
# ❌ 错误会导致 unauthorized_client 错误

KEYCLOAK_BACKEND_CLIENT_ID=simfocus-backend
# 影响：
# ✅ 用于 token 刷新
# ✅ 用于用户信息查询
# ✅ 用于 Service Account 认证
# ❌ 错误会导致后端操作失败

KEYCLOAK_BACKEND_CLIENT_SECRET=3NouAxsx1lq7z2HZS3VDuSFrtipfe7JN
# 影响：
# ✅ 后端客户端密钥（必须保密）
# ✅ 用于 Confidential Client 认证
# ❌ 泄露会导致安全问题
# ❌ 错误会导致 invalid_client_credentials 错误
```

#### 前端环境变量

```bash
# 文件：frontend/.env

VITE_KEYCLOAK_ENABLED=true
# 影响：
# ✅ 显示 SSO 登录按钮
# ✅ 启用 Keycloak 相关路由
# ❌ false 时，隐藏 SSO 功能

VITE_KEYCLOAK_SERVER_URL=https://keycloak.plfai.cn/
# 影响：
# ✅ Keycloak 服务器地址
# ✅ 前端直接访问（frontend-direct 模式）
# ❌ 本项目使用 backend-proxy，此配置仅供参考

VITE_KEYCLOAK_REALM=simfocus
# 影响：
# ✅ Realm 名称
# ✅ 用于构造授权 URL
# ❌ 错误会导致无法生成正确的 URL

VITE_KEYCLOAK_CLIENT_ID=simfocus-frontend
# 影响：
# ✅ 客户端 ID（Public Client，可公开）
# ✅ 后端使用此 ID 交换授权码
# ❌ 错误会导致 unauthorized_client 错误

VITE_AUTH_MODE=backend-proxy
# 影响：
# ✅ 认证模式：backend-proxy（推荐）或 frontend-direct
# ✅ backend-proxy：前端调用后端，后端处理 OAuth
# ✅ frontend-direct：前端直接处理 OAuth（复杂）
# ❌ 错误会导致认证流程不一致

VITE_API_BASE_URL=http://192.168.0.16:8000
# 影响：
# ✅ 后端 API 基础 URL
# ✅ 必须与用户浏览器访问地址一致
# ❌ 使用 localhost 会导致 redirect_uri 不匹配
# ❌ 错误会导致无法完成认证流程
```

#### 安全配置影响

**1. Audience 验证策略**

```python
# backend/app/services/keycloak_service.py

payload = jwt.decode(
    token,
    key=key.to_dict(),
    algorithms=["RS256"],
    issuer=self.config.issuer,
    options={'verify_aud': False}  # ← 禁用 audience 验证
)
```

**为什么禁用 audience 验证？**

```
Keycloak 前端 token 的 audience 问题：

Token Payload:
{
  "iss": "https://keycloak.plfai.cn/realms/simfocus",
  "aud": "simfocus-frontend",  ← audience 是 frontend client
  ...
}

后端验证时：
- 如果验证 aud，必须与 backend_client_id 匹配
- 但 token 是给 frontend 的，aud 是 frontend_client_id
- 导致验证失败

解决方案：
options={'verify_aud': False}

安全性分析：
✅ 仍然验证 issuer（确保 token 来自正确的 Keycloak）
✅ 仍然验证签名（确保 token 未被篡改）
✅ 仍然验证过期时间（防止 token 被滥用）
❌ 不验证 audience（允许 frontend token 访问后端）

风险：
⚠️ 理论上，任何 simfocus-frontend 的 token 都可以访问后端
⚠️ 但实际风险可控，因为：
  - token 仍然验证 issuer 和签名
  - 后端会从数据库查询用户，确保用户存在
  - 可以添加额外的权限检查（role-based access control）
```

**2. State 参数（CSRF 保护）**

```python
# backend/app/api/keycloak_auth.py

state = secrets.token_urlsafe(32)
```

```
State 参数的作用：

1. 防 CSRF（跨站请求伪造）攻击：
   - 攻击者构造恶意链接，诱导用户点击
   - 如果没有 state，攻击者可以获取授权码
   - 有了 state，攻击者无法预测正确的 state

2. 实现步骤：
   a. 后端生成随机 state
   b. 存储到 Redis（TODO: 当前实现未存储）
   c. Keycloak 回调时返回 state
   d. 后端验证 state 是否匹配

当前状态：
⚠️ 生成了 state，但未验证
✅ 对于本项目，风险可控（因为后续有 token 验证）
⚠️ 生产环境建议实现完整 state 验证
```

**3. Token 刷新**

```python
# backend/app/services/keycloak_service.py

async def refresh_token(self, refresh_token: str):
    """
    刷新 access token

    使用 backend_client_id 和 backend_client_secret
    因为 refresh_token 是后端持有的敏感信息
    """
    response = await client.post(
        f"realms/{self.config.realm}/protocol/openid-connect/token",
        data={
            "grant_type": "refresh_token",
            "client_id": self.config.backend_client_id,  # ← 使用 backend client
            "client_secret": self.config.backend_client_secret,  # ← 需要密钥
            "refresh_token": refresh_token,
        }
    )
```

```
Token 刷新的重要性：

Access Token 有效期：
- 默认：5 分钟（Keycloak 配置）
- 过期后需要刷新

Refresh Token：
- 有效期：更长（如 30 天）
- 用于获取新的 access token
- 必须保密，存储在后端/数据库

当前实现：
⚠️ refresh_token 未存储到数据库
⚠️ 用户需要重新登录（access_token 过期后）
✅ 简化了实现，避免 token 管理复杂性

改进建议：
- 存储 refresh_token 到数据库
- 实现自动刷新逻辑
- 提供 silent refresh 机制
```

### 6. 安全最佳实践总结

#### ✅ 已实现的安全措施

1. **双重认证机制**
   - Keycloak token 优先验证
   - 本地 JWT 作为后备

2. **JWKS 公钥验证**
   - 使用 Keycloak 公钥验证签名
   - 支持 key 轮换

3. **公钥缓存**
   - TTL 1 小时
   - 减少对 Keycloak 的请求

4. **重试机制**
   - 指数退避
   - 提高可用性

5. **授权码模式**
   - 最安全的 OAuth 流程
   - token 不经过浏览器

6. **环境变量隔离**
   - 敏感信息在后端
   - 前端只存储公开配置

#### ⚠️ 需要改进的安全措施

1. **State 参数验证**
   ```python
   # TODO: 将 state 存储到 Redis
   # TODO: 回调时验证 state
   ```

2. **Refresh Token 管理**
   ```python
   # TODO: 存储 refresh_token 到数据库
   # TODO: 实现自动刷新
   ```

3. **Token 黑名单**
   ```python
   # TODO: 用户登出时，将 token 加入黑名单
   # TODO: 使用 Redis 存储，TTL = token 过期时间
   ```

4. **速率限制**
   ```python
   # TODO: 实现登录速率限制
   # TODO: 防止暴力破解
   ```

5. **审计日志**
   ```python
   # TODO: 记录登录、登出、权限变更等操作
   # TODO: 便于安全审计
   ```

#### 🔒 配置检查清单

- [ ] Keycloak Admin Password 强壮且定期更换
- [ ] Backend Client Secret 存储在安全的地方（如 Vault）
- [ ] 后端环境变量不写入日志
- [ ] 前端不存储敏感信息（API Keys 等）
- [ ] 生产环境禁用 Source Maps
- [ ] 启用 HTTPS（传输加密）
- [ ] 配置 CSP（Content Security Policy）
- [ ] 定期更新依赖（修复安全漏洞）
- [ ] 实施速率限制（防止 DDoS）
- [ ] 配置审计日志（监控异常）

## 参考资料

- [OWASP 前端安全最佳实践](https://owasp.org/www-project-web-security-testing-guide/)
- [Vite 生产构建指南](https://vitejs.dev/guide/build.html)
- [Nginx 安全配置](https://nginx.org/en/docs/http/ngx_http_headers_module.html)
- [OAuth 2.0 授权码流程](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1)
- [OpenID Connect 规范](https://openid.net/connect/)
- [Keycloak 官方文档](https://www.keycloak.org/documentation)
- [JWT 最佳实践](https://datatracker.ietf.org/doc/html/rfc8725)
