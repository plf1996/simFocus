# simFocus 后端 API 接口文档

**版本**: v1.0
**Base URL**: `http://localhost:8000`
**API 前缀**: `/api`
**文档日期**: 2026-02-03

---

## 目录

1. [概述](#1-概述)
2. [认证机制](#2-认证机制)
3. [通用响应格式](#3-通用响应格式)
4. [错误码说明](#4-错误码说明)
5. [API 接口详情](#5-api-接口详情)
   - [5.1 认证接口](#51-认证接口)
   - [5.2 用户接口](#52-用户接口)
   - [5.3 API 密钥接口](#53-api-密钥接口)
   - [5.4 议题接口](#54-议题接口)
   - [5.5 角色接口](#55-角色接口)
   - [5.6 讨论接口](#56-讨论接口)
   - [5.7 消息接口](#57-消息接口)
   - [5.8 报告接口](#58-报告接口)
6. [数据模型](#6-数据模型)

---

## 1. 概述

### 1.1 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15 (asyncpg)
- **缓存**: Redis 7
- **认证**: JWT + Keycloak SSO
- **文档**: 自动生成 Swagger/OpenAPI

### 1.2 通用说明

- 所有接口默认返回 JSON 格式
- 时间戳使用 ISO 8601 格式（UTC 时区）
- UUID 使用标准 RFC 4122 格式
- 所有需要认证的接口都需要在 Header 中携带 JWT Token

### 1.3 访问 API 文档

启动服务后，访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 2. 认证机制

### 2.1 双重认证支持

simFocus 支持两种认证方式：

1. **Keycloak SSO**（优先）
   - 企业单点登录
   - 由 Keycloak 服务器签发 JWT

2. **本地 JWT 认证**
   - 邮箱 + 密码登录
   - 由后端签发 JWT

### 2.2 认证流程

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  客户端   │────────▶│ Keycloak │────────▶│  后端API  │
└──────────┘         └──────────┘         └──────────┘
     │                   │
     │                   │ (失败)
     │                   ▼
     │            ┌──────────┐
     └───────────▶│ 本地JWT   │
                  │  认证    │
                  └──────────┘
```

### 2.3 请求头格式

```
Authorization: Bearer <access_token>
```

### 2.4 Token 有效期

- **Access Token**: 24 小时（1440 分钟）
- **Refresh Token**: 未实现（计划中）

---

## 3. 通用响应格式

### 3.1 成功响应

```json
{
  "data": { ... },
  "message": "Success",
  "timestamp": "2026-02-03T10:30:00Z"
}
```

### 3.2 错误响应

```json
{
  "detail": "错误描述信息",
  "status_code": 400,
  "timestamp": "2026-02-03T10:30:00Z"
}
```

### 3.3 分页响应

```json
{
  "items": [ ... ],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

---

## 4. 错误码说明

| HTTP 状态码 | 说明 | 示例 |
|------------|------|------|
| 200 | 请求成功 | GET /api/auth/me |
| 201 | 创建成功 | POST /api/auth/register |
| 204 | 删除成功（无内容） | DELETE /api/users/me |
| 400 | 请求参数错误 | 密码格式不正确 |
| 401 | 未认证 | Token 无效或过期 |
| 403 | 无权限 | 访问他人资源 |
| 404 | 资源不存在 | 讨论不存在 |
| 422 | 验证错误 | Pydantic 验证失败 |
| 500 | 服务器内部错误 | 数据库连接失败 |
| 501 | 未实现 | 邮箱验证功能 |

---

## 5. API 接口详情

---

### 5.1 认证接口

**Base Path**: `/api/auth`

#### 5.1.1 用户注册

**接口**: `POST /api/auth/register`

**说明**: 注册新用户账号

**认证**: 不需要

**请求参数**:

```json
{
  "email": "user@example.com",
  "name": "张三",
  "bio": "产品经理",
  "password": "Password123!"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱地址 |
| name | string | 否 | 用户名称 |
| bio | string | 否 | 个人简介 |
| password | string | 是 | 密码（8-72 字符） |

**响应示例**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "bio": "产品经理",
  "email_verified": false,
  "auth_provider": "email",
  "avatar_url": null,
  "created_at": "2026-02-03T10:30:00Z",
  "last_login_at": null
}
```

**错误响应**:

- `400`: 邮箱已存在
- `422`: 参数验证失败

---

#### 5.1.2 用户登录

**接口**: `POST /api/auth/login`

**说明**: 使用邮箱和密码登录

**认证**: 不需要

**请求参数**:

```json
{
  "email": "user@example.com",
  "password": "Password123!"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |

**响应示例**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "张三",
    "bio": "产品经理",
    "email_verified": false,
    "auth_provider": "email",
    "avatar_url": null,
    "created_at": "2026-02-03T10:30:00Z",
    "last_login_at": "2026-02-03T10:30:00Z"
  }
}
```

**错误响应**:

- `401`: 邮箱或密码错误

---

#### 5.1.3 用户登出

**接口**: `POST /api/auth/logout`

**说明**: 登出当前用户（客户端应删除 Token）

**认证**: 需要

**请求头**:

```
Authorization: Bearer <access_token>
```

**响应示例**:

```json
{
  "message": "Successfully logged out"
}
```

---

#### 5.1.4 获取当前用户信息

**接口**: `GET /api/auth/me`

**说明**: 获取当前登录用户的详细信息

**认证**: 需要

**响应示例**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "bio": "产品经理",
  "email_verified": false,
  "auth_provider": "email",
  "avatar_url": null,
  "created_at": "2026-02-03T10:30:00Z",
  "last_login_at": "2026-02-03T10:30:00Z"
}
```

---

#### 5.1.5 验证邮箱（未实现）

**接口**: `POST /api/auth/verify-email`

**说明**: 验证用户邮箱地址

**认证**: 不需要

**请求参数**:

```
?token=verification_token_string
```

**响应**: 501 Not Implemented

---

#### 5.1.6 忘记密码（未实现）

**接口**: `POST /api/auth/forgot-password`

**说明**: 请求密码重置邮件

**认证**: 不需要

**请求参数**:

```json
{
  "email": "user@example.com"
}
```

**响应**: 501 Not Implemented

---

#### 5.1.7 重置密码（未实现）

**接口**: `POST /api/auth/reset-password`

**说明**: 使用 Token 重置密码

**认证**: 不需要

**请求参数**:

```json
{
  "token": "reset_token_string",
  "new_password": "NewPassword123!"
}
```

**响应**: 501 Not Implemented

---

### 5.2 用户接口

**Base Path**: `/api/users`

#### 5.2.1 获取当前用户信息

**接口**: `GET /api/users/me`

**说明**: 获取当前用户的 Profile

**认证**: 需要

**响应示例**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "张三",
  "bio": "产品经理",
  "email_verified": false,
  "auth_provider": "email",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2026-02-03T10:30:00Z",
  "last_login_at": "2026-02-03T10:30:00Z"
}
```

---

#### 5.2.2 更新当前用户信息

**接口**: `PATCH /api/users/me`

**说明**: 更新当前用户的 Profile

**认证**: 需要

**请求参数**:

```json
{
  "name": "李四",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "bio": "高级产品经理"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 用户名称 |
| avatar_url | string | 否 | 头像 URL |
| bio | string | 否 | 个人简介 |

**响应示例**: 同 GET /api/users/me

**错误响应**:

- `404`: 用户不存在

---

#### 5.2.3 删除当前用户账号

**接口**: `DELETE /api/users/me`

**说明**: 软删除当前用户账号

**认证**: 需要

**响应**: 204 No Content

---

### 5.3 API 密钥接口

**Base Path**: `/api/users/me/api-keys`

#### 5.3.1 获取所有 API 密钥

**接口**: `GET /api/users/me/api-keys`

**说明**: 获取当前用户的所有 LLM API 密钥

**认证**: 需要

**响应示例**:

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "provider": "openai",
    "key_name": "My OpenAI Key",
    "api_base_url": "https://api.openai.com/v1",
    "default_model": "gpt-4",
    "is_active": true,
    "created_at": "2026-02-03T10:30:00Z",
    "last_used_at": "2026-02-03T12:00:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "provider": "anthropic",
    "key_name": "Claude Key",
    "api_base_url": null,
    "default_model": "claude-3-sonnet",
    "is_active": true,
    "created_at": "2026-02-03T11:00:00Z",
    "last_used_at": null
  }
]
```

---

#### 5.3.2 创建 API 密钥

**接口**: `POST /api/users/me/api-keys`

**说明**: 创建新的 LLM API 密钥（密钥将被加密存储）

**认证**: 需要

**请求参数**:

```json
{
  "provider": "openai",
  "key_name": "My GPT-4 Key",
  "api_key": "sk-...abcdefghijklmnopqrstuvwxyz",
  "api_base_url": "https://api.openai.com/v1",
  "default_model": "gpt-4"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| provider | string | 是 | LLM 提供商：`openai`, `anthropic`, `custom` |
| key_name | string | 是 | 密钥名称（1-100 字符） |
| api_key | string | 是 | 原始 API 密钥（≥10 字符） |
| api_base_url | string | 否 | 自定义 API 端点 URL |
| default_model | string | 否 | 默认模型名称 |

**响应示例**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider": "openai",
  "key_name": "My GPT-4 Key",
  "api_base_url": "https://api.openai.com/v1",
  "default_model": "gpt-4",
  "is_active": true,
  "created_at": "2026-02-03T12:30:00Z",
  "last_used_at": null
}
```

**错误响应**:

- `400`: 参数验证失败

---

#### 5.3.3 获取单个 API 密钥

**接口**: `GET /api/users/me/api-keys/{key_id}`

**说明**: 获取指定的 API 密钥详情

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| key_id | UUID | API 密钥 ID |

**响应示例**: 同 5.3.1 中的单个对象

**错误响应**:

- `404`: API 密钥不存在

---

#### 5.3.4 更新 API 密钥

**接口**: `PATCH /api/users/me/api-keys/{key_id}`

**说明**: 更新 API 密钥的元数据（不能修改实际密钥）

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| key_id | UUID | API 密钥 ID |

**请求参数**:

```json
{
  "key_name": "Updated Key Name",
  "api_base_url": "https://new-api-endpoint.com/v1",
  "default_model": "gpt-4-turbo",
  "is_active": false
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key_name | string | 否 | 新的密钥名称 |
| api_base_url | string | 否 | 新的 API 端点 URL |
| default_model | string | 否 | 新的默认模型 |
| is_active | boolean | 否 | 是否激活 |

**响应示例**: 同 5.3.1 中的单个对象

**错误响应**:

- `404`: API 密钥不存在

---

#### 5.3.5 删除 API 密钥

**接口**: `DELETE /api/users/me/api-keys/{key_id}`

**说明**: 删除指定的 API 密钥

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| key_id | UUID | API 密钥 ID |

**响应**: 204 No Content

**错误响应**:

- `404`: API 密钥不存在

---

### 5.4 议题接口

**Base Path**: `/api/topics`

#### 5.4.1 获取所有议题

**接口**: `GET /api/topics`

**说明**: 获取当前用户的所有议题

**认证**: 需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| status | string | 否 | - | 状态过滤：`draft`, `ready`, `in_discussion`, `completed` |
| skip | int | 否 | 0 | 跳过记录数（分页） |
| limit | int | 否 | 20 | 每页记录数（1-100） |

**响应示例**:

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "title": "如何提高用户留存率",
    "status": "in_discussion",
    "created_at": "2026-02-03T10:00:00Z",
    "updated_at": "2026-02-03T12:00:00Z"
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440001",
    "title": "产品定价策略讨论",
    "status": "draft",
    "created_at": "2026-02-02T15:00:00Z",
    "updated_at": "2026-02-02T15:00:00Z"
  }
]
```

---

#### 5.4.2 创建议题

**接口**: `POST /api/topics`

**说明**: 创建新议题

**认证**: 需要

**请求参数**:

```json
{
  "title": "如何提高用户留存率",
  "description": "讨论当前产品用户留存率下降的原因和解决方案",
  "context": "我们的产品是一款 SaaS 协作工具，目前月活跃用户 10 万，但次月留存率从 60% 下降到 45%。",
  "attachments": [
    {
      "filename": "retention_data.pdf",
      "url": "https://s3.../retention_data.pdf",
      "size": 1024000,
      "mime_type": "application/pdf"
    }
  ]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 议题标题（10-200 字符） |
| description | string | 否 | 议题描述（≤2000 字符） |
| context | string | 否 | 额外背景信息 |
| attachments | array | 否 | 附件元数据数组 |

**响应示例**:

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "如何提高用户留存率",
  "description": "讨论当前产品用户留存率下降的原因和解决方案",
  "context": "我们的产品是一款 SaaS 协作工具...",
  "status": "draft",
  "attachments": [
    {
      "filename": "retention_data.pdf",
      "url": "https://s3.../retention_data.pdf",
      "size": 1024000,
      "mime_type": "application/pdf"
    }
  ],
  "template_id": null,
  "created_at": "2026-02-03T13:00:00Z",
  "updated_at": "2026-02-03T13:00:00Z"
}
```

---

#### 5.4.3 获取议题详情

**接口**: `GET /api/topics/{topic_id}`

**说明**: 获取指定议题的详细信息

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| topic_id | UUID | 议题 ID |

**响应示例**: 同 5.4.2

**错误响应**:

- `404`: 议题不存在

---

#### 5.4.4 更新议题

**接口**: `PATCH /api/topics/{topic_id}`

**说明**: 更新议题信息

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| topic_id | UUID | 议题 ID |

**请求参数**:

```json
{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "context": "更新后的背景信息",
  "status": "ready"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 新标题（10-200 字符） |
| description | string | 否 | 新描述（≤2000 字符） |
| context | string | 否 | 新背景信息 |
| status | string | 否 | 新状态 |

**响应示例**: 同 5.4.2

**错误响应**:

- `400`: 议题正在讨论中，无法更新
- `404`: 议题不存在

---

#### 5.4.5 删除议题

**接口**: `DELETE /api/topics/{topic_id}`

**说明**: 删除指定议题

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| topic_id | UUID | 议题 ID |

**响应**: 204 No Content

**错误响应**:

- `400`: 议题正在讨论中，无法删除
- `404`: 议题不存在

---

#### 5.4.6 搜索议题

**接口**: `GET /api/topics/search`

**说明**: 按标题或描述搜索议题

**认证**: 需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（≥1 字符） |
| skip | int | 否 | 0 | 跳过记录数 |
| limit | int | 否 | 20 | 每页记录数（1-100） |

**响应示例**: 同 5.4.1

---

### 5.5 角色接口

**Base Path**: `/api/characters`

#### 5.5.1 获取系统角色模板

**接口**: `GET /api/characters/templates`

**说明**: 获取系统预设的角色模板（无需认证）

**认证**: 不需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | int | 否 | 0 | 跳过记录数 |
| limit | int | 否 | 100 | 每页记录数（1-200） |

**响应示例**:

```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440000",
    "name": "产品经理",
    "avatar_url": "https://example.com/avatars/pm.jpg",
    "is_template": true,
    "is_public": true,
    "config": {
      "age": 35,
      "gender": "female",
      "profession": "产品经理",
      "personality": {
        "openness": 7,
        "rigor": 8,
        "critical_thinking": 9,
        "optimism": 6
      },
      "knowledge": {
        "fields": ["产品管理", "用户体验", "市场分析"],
        "experience_years": 10,
        "representative_views": ["用户至上", "数据驱动"]
      },
      "stance": "critical_exploration",
      "expression_style": "formal",
      "behavior_pattern": "balanced"
    },
    "usage_count": 1250,
    "rating_avg": 4.5,
    "rating_count": 200
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440001",
    "name": "技术架构师",
    "avatar_url": null,
    "is_template": true,
    "is_public": true,
    "config": { ... },
    "usage_count": 980,
    "rating_avg": 4.7,
    "rating_count": 150
  }
]
```

---

#### 5.5.2 随机获取角色模板

**接口**: `GET /api/characters/templates/random`

**说明**: 随机获取指定数量的系统角色模板（用于推荐）

**认证**: 不需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| count | int | 否 | 5 | 返回数量（1-7） |

**响应示例**: 同 5.5.1

---

#### 5.5.3 获取指定角色模板

**接口**: `GET /api/characters/templates/{character_id}`

**说明**: 获取指定的系统角色模板详情

**认证**: 不需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| character_id | UUID | 角色 ID |

**响应示例**:

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "user_id": null,
  "name": "产品经理",
  "avatar_url": "https://example.com/avatars/pm.jpg",
  "is_template": true,
  "is_public": true,
  "config": { ... },
  "usage_count": 1250,
  "rating_avg": 4.5,
  "rating_count": 200,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**错误响应**:

- `404`: 角色模板不存在

---

#### 5.5.4 获取我的自定义角色

**接口**: `GET /api/characters`

**说明**: 获取当前用户创建的自定义角色

**认证**: 需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | int | 否 | 0 | 跳过记录数 |
| limit | int | 否 | 20 | 每页记录数（1-100） |

**响应示例**: 同 5.5.1

---

#### 5.5.5 创建自定义角色

**接口**: `POST /api/characters`

**说明**: 创建新的自定义角色

**认证**: 需要

**请求参数**:

```json
{
  "name": "市场营销专家",
  "avatar_url": "https://example.com/avatars/marketing.jpg",
  "config": {
    "age": 32,
    "gender": "male",
    "profession": "市场营销总监",
    "personality": {
      "openness": 9,
      "rigor": 6,
      "critical_thinking": 7,
      "optimism": 8
    },
    "knowledge": {
      "fields": ["市场营销", "品牌建设", "用户增长"],
      "experience_years": 8,
      "representative_views": ["增长至上", "品牌价值"]
    },
    "stance": "support",
    "expression_style": "casual",
    "behavior_pattern": "active"
  }
}
```

**响应示例**:

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "市场营销专家",
  "avatar_url": "https://example.com/avatars/marketing.jpg",
  "is_template": false,
  "is_public": false,
  "config": { ... },
  "usage_count": 0,
  "rating_avg": 0.0,
  "rating_count": 0,
  "created_at": "2026-02-03T14:00:00Z",
  "updated_at": "2026-02-03T14:00:00Z"
}
```

---

#### 5.5.6 获取角色详情

**接口**: `GET /api/characters/{character_id}`

**说明**: 获取指定角色的详细信息

**认证**: 需要（如果是自定义角色）

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| character_id | UUID | 角色 ID |

**响应示例**: 同 5.5.5

**错误响应**:

- `403`: 无权访问该角色
- `404`: 角色不存在

---

#### 5.5.7 更新角色

**接口**: `PATCH /api/characters/{character_id}`

**说明**: 更新自定义角色信息

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| character_id | UUID | 角色 ID |

**请求参数**:

```json
{
  "name": "更新后的角色名",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "config": { ... }
}
```

**响应示例**: 同 5.5.5

**错误响应**:

- `400`: 无法修改系统模板角色
- `403`: 无权修改该角色
- `404`: 角色不存在

---

#### 5.5.8 删除角色

**接口**: `DELETE /api/characters/{character_id}`

**说明**: 删除自定义角色

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| character_id | UUID | 角色 ID |

**响应**: 204 No Content

**错误响应**:

- `400`: 无法删除系统模板角色
- `400`: 角色正在使用中
- `403`: 无权删除该角色
- `404`: 角色不存在

---

#### 5.5.9 搜索角色

**接口**: `GET /api/characters/search`

**说明**: 搜索系统角色模板

**认证**: 不需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词（≥1 字符） |
| skip | int | 否 | 0 | 跳过记录数 |
| limit | int | 否 | 100 | 每页记录数（1-200） |

**响应示例**: 同 5.5.1

---

#### 5.5.10 智能推荐角色

**接口**: `POST /api/characters/recommend`

**说明**: 基于议题内容智能推荐合适的角色（语义相似度）

**认证**: 不需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| count | int | 否 | 5 | 推荐数量（1-20） |

**请求参数** (Body):

```json
{
  "title": "如何提高用户留存率",
  "description": "讨论当前产品用户留存率下降的原因和解决方案"
}
```

**响应示例**:

```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440000",
    "name": "产品经理",
    "avatar_url": "https://example.com/avatars/pm.jpg",
    "is_template": true,
    "is_public": true,
    "config": { ... },
    "usage_count": 1250,
    "rating_avg": 4.5,
    "rating_count": 200,
    "similarity_score": 0.87,
    "weighted_score": 0.82
  },
  {
    "id": "880e8400-e29b-41d4-a716-446655440002",
    "name": "用户体验设计师",
    "avatar_url": null,
    "is_template": true,
    "is_public": true,
    "config": { ... },
    "usage_count": 890,
    "rating_avg": 4.6,
    "rating_count": 180,
    "similarity_score": 0.84,
    "weighted_score": 0.79
  }
]
```

**错误响应**:

- `500`: 推荐服务失败

---

### 5.6 讨论接口

**Base Path**: `/api/discussions`

#### 5.6.1 获取所有讨论

**接口**: `GET /api/discussions`

**说明**: 获取当前用户的所有讨论

**认证**: 需要

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | int | 否 | 0 | 跳过记录数 |
| limit | int | 否 | 20 | 每页记录数（1-100） |

**响应示例**:

```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440000",
    "topic_id": "770e8400-e29b-41d4-a716-446655440000",
    "topic_title": "如何提高用户留存率",
    "status": "running",
    "current_round": 2,
    "max_rounds": 5,
    "created_at": "2026-02-03T14:00:00Z"
  },
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440001",
    "topic_id": "770e8400-e29b-41d4-a716-446655440001",
    "topic_title": "产品定价策略讨论",
    "status": "completed",
    "current_round": 3,
    "max_rounds": 3,
    "created_at": "2026-02-02T16:00:00Z"
  }
]
```

---

#### 5.6.2 创建讨论

**接口**: `POST /api/discussions`

**说明**: 创建新的讨论会话

**认证**: 需要

**请求参数**:

```json
{
  "topic_id": "770e8400-e29b-41d4-a716-446655440000",
  "discussion_mode": "free",
  "max_rounds": 5,
  "character_ids": [
    "880e8400-e29b-41d4-a716-446655440000",
    "880e8400-e29b-41d4-a716-446655440001",
    "880e8400-e29b-41d4-a716-446655440002"
  ]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic_id | UUID | 是 | 关联议题 ID |
| discussion_mode | string | 否 | 讨论模式：`free`, `structured`, `creative`, `consensus`（默认：`free`） |
| max_rounds | int | 否 | 最大轮次（1-10，默认：3，推荐：3-5） |
| character_ids | array | 是 | 参与角色 ID 列表（3-7 个） |

**讨论模式说明**:

| 模式 | 说明 |
|------|------|
| free | 自由讨论（角色自由发言） |
| structured | 结构化辩论（正反方） |
| creative | 创意发散（"是的，而且"） |
| consensus | 共识构建（寻找共同点） |

**响应示例**:

```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440002",
  "topic_id": "770e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "discussion_mode": "free",
  "max_rounds": 5,
  "status": "initialized",
  "current_round": 0,
  "current_phase": "opening",
  "progress_percentage": 0.0,
  "llm_provider": null,
  "llm_model": null,
  "total_tokens_used": 0,
  "estimated_cost_usd": 0.0,
  "started_at": null,
  "completed_at": null,
  "created_at": "2026-02-03T15:00:00Z",
  "updated_at": "2026-02-03T15:00:00Z"
}
```

**错误响应**:

- `400`: 议题不存在
- `400`: 角色数量不在 3-7 范围内

---

#### 5.6.3 获取讨论详情

**接口**: `GET /api/discussions/{discussion_id}`

**说明**: 获取指定讨论的详细信息

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应示例**: 同 5.6.2

**错误响应**:

- `404`: 讨论不存在

---

#### 5.6.4 删除讨论

**接口**: `DELETE /api/discussions/{discussion_id}`

**说明**: 删除指定讨论

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应**: 204 No Content

**错误响应**:

- `404`: 讨论不存在

---

#### 5.6.5 开始讨论

**接口**: `POST /api/discussions/{discussion_id}/start`

**说明**: 开始执行讨论（需要先配置 API 密钥）

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| provider_name | string | 否 | default | 使用的 API 密钥名称 |

**响应示例**: 同 5.6.2（status 变为 `running`）

**错误响应**:

- `400`: 讨论状态不是 `initialized`
- `400`: 未配置 API 密钥

---

#### 5.6.6 暂停讨论

**接口**: `POST /api/discussions/{discussion_id}/pause`

**说明**: 暂停正在运行的讨论

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应示例**: 同 5.6.2（status 变为 `paused`）

**错误响应**:

- `400`: 讨论状态不是 `running`

---

#### 5.6.7 恢复讨论

**接口**: `POST /api/discussions/{discussion_id}/resume`

**说明**: 恢复已暂停的讨论

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应示例**: 同 5.6.2（status 变为 `running`）

**错误响应**:

- `400`: 讨论状态不是 `paused`

---

#### 5.6.8 停止讨论

**接口**: `POST /api/discussions/{discussion_id}/stop`

**说明**: 停止讨论并生成报告（后台任务）

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应示例**: 同 5.6.2（status 变为 `completed`）

**错误响应**:

- `400`: 讨论已完成或失败

---

#### 5.6.9 注入问题

**接口**: `POST /api/discussions/{discussion_id}/inject-question`

**说明**: 在讨论中注入用户问题

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 要注入的问题 |

**响应示例**:

```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440000",
  "discussion_id": "aa0e8400-e29b-41d4-a716-446655440002",
  "participant_id": "00000000-0000-0000-0000-000000000000",
  "character_name": "User",
  "character_avatar_url": null,
  "content": "能否从技术角度进一步说明？",
  "phase": "debate",
  "round": 2,
  "token_count": 0,
  "is_injected_question": true,
  "metadata": null,
  "created_at": "2026-02-03T15:30:00Z"
}
```

**错误响应**:

- `400`: 讨论状态不是 `running`

---

### 5.7 消息接口

**Base Path**: `/api/discussions/{discussion_id}/messages`

#### 5.7.1 获取讨论消息

**接口**: `GET /api/discussions/{discussion_id}/messages`

**说明**: 获取指定讨论的所有消息

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | int | 否 | 0 | 跳过记录数 |
| limit | int | 否 | 100 | 每页记录数（1-500） |

**响应示例**:

```json
[
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440001",
    "discussion_id": "aa0e8400-e29b-41d4-a716-446655440002",
    "participant_id": "cc0e8400-e29b-41d4-a716-446655440000",
    "character_name": "产品经理",
    "character_avatar_url": "https://example.com/avatars/pm.jpg",
    "content": "从用户留存率下降的角度来看，我们需要先分析用户流失的具体原因...",
    "phase": "opening",
    "round": 0,
    "token_count": 156,
    "is_injected_question": false,
    "metadata": {
      "sentiment": "neutral",
      "topics": ["用户留存", "数据分析"]
    },
    "created_at": "2026-02-03T15:05:00Z"
  },
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440002",
    "discussion_id": "aa0e8400-e29b-41d4-a716-446655440002",
    "participant_id": "cc0e8400-e29b-41d4-a716-446655440001",
    "character_name": "技术架构师",
    "character_avatar_url": null,
    "content": "技术层面我们有三个潜在问题：性能瓶颈、功能复杂度、移动端体验...",
    "phase": "opening",
    "round": 0,
    "token_count": 198,
    "is_injected_question": false,
    "metadata": {
      "sentiment": "constructive",
      "topics": ["技术", "性能", "移动端"]
    },
    "created_at": "2026-02-03T15:07:00Z"
  },
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440003",
    "discussion_id": "aa0e8400-e29b-41d4-a716-446655440002",
    "participant_id": "00000000-0000-0000-0000-000000000000",
    "character_name": "User",
    "character_avatar_url": null,
    "content": "能否从成本角度分析一下？",
    "phase": "development",
    "round": 1,
    "token_count": 0,
    "is_injected_question": true,
    "metadata": null,
    "created_at": "2026-02-03T15:20:00Z"
  }
]
```

**错误响应**:

- `400`: 讨论不存在

---

### 5.8 报告接口

**Base Path**: `/api/reports`

#### 5.8.1 获取报告详情

**接口**: `GET /api/reports/{report_id}`

**说明**: 获取指定报告的详细信息

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| report_id | UUID | 报告 ID |

**响应示例**:

```json
{
  "id": "dd0e8400-e29b-41d4-a716-446655440000",
  "discussion_id": "aa0e8400-e29b-41d4-a716-446655440002",
  "overview": {
    "topic_title": "如何提高用户留存率",
    "discussion_duration_seconds": 1800,
    "total_rounds": 3,
    "total_messages": 15,
    "participant_count": 3,
    "llm_provider": "openai",
    "llm_model": "gpt-4"
  },
  "summary": "# 讨论摘要\n\n本次讨论围绕用户留存率下降的问题展开...",
  "viewpoints_summary": [
    {
      "character_id": "880e8400-e29b-41d4-a716-446655440000",
      "character_name": "产品经理",
      "stance": "critical_exploration",
      "core_arguments": [
        "需要优先解决产品易用性问题",
        "数据驱动决策是关键"
      ],
      "position_evolution": [
        {
          "round": 1,
          "position": "初步认为是功能复杂度导致"
        },
        {
          "round": 3,
          "position": "确认为移动端体验问题为主因"
        }
      ]
    }
  ],
  "consensus": {
    "agreements": [
      "用户留存率下降是多重因素导致",
      "移动端体验是首要问题",
      "需要建立完善的用户反馈机制"
    ],
    "joint_recommendations": [
      "优化移动端核心流程",
      "建立用户分层运营策略",
      "加强新用户引导"
    ],
    "supporting_arguments": [
      "移动端用户占比 65%",
      "核心流程跳出率 40%"
    ]
  },
  "controversies": [
    {
      "topic": "产品功能 vs 易用性",
      "viewpoints": {
        "产品经理": "应优先提升易用性",
        "技术架构师": "功能完整性更重要"
      },
      "unresolved": true
    }
  ],
  "insights": [
    {
      "description": "用户流失主要发生在前 3 次",
      "related_messages": [
        "bb0e8400-e29b-41d4-a716-446655440001",
        "bb0e8400-e29b-41d4-a716-446655440005"
      ]
    }
  ],
  "recommendations": [
    {
      "action": "优化移动端注册流程",
      "rationale": "注册流失率高达 60%",
      "priority": "high"
    },
    {
      "action": "增加新用户引导",
      "rationale": "功能发现率低",
      "priority": "medium"
    }
  ],
  "quality_scores": {
    "depth": 85,
    "diversity": 78,
    "constructive": 82,
    "coherence": 90,
    "overall": 84
  },
  "generation_time_ms": 3500,
  "created_at": "2026-02-03T16:00:00Z",
  "updated_at": "2026-02-03T16:00:00Z"
}
```

**错误响应**:

- `404`: 报告不存在

---

#### 5.8.2 获取讨论报告

**接口**: `GET /api/reports/discussions/{discussion_id}`

**说明**: 获取或生成指定讨论的报告

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应示例**: 同 5.8.1

**说明**:
- 如果报告已存在，直接返回
- 如果报告不存在，自动生成并返回

**错误响应**:

- `404`: 讨论不存在

---

#### 5.8.3 重新生成报告

**接口**: `POST /api/reports/discussions/{discussion_id}/regenerate`

**说明**: 重新生成指定讨论的报告

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| discussion_id | UUID | 讨论 ID |

**响应示例**: 同 5.8.1

**错误响应**:

- `400`: 讨论状态不是 `completed`
- `404`: 讨论不存在

---

## 6. 数据模型

### 6.1 用户模型

```typescript
interface User {
  id: UUID;
  email: string;
  name?: string;
  bio?: string;
  avatar_url?: string;
  email_verified: boolean;
  auth_provider: 'email' | 'keycloak';
  created_at: datetime;
  last_login_at?: datetime;
}
```

### 6.2 API 密钥模型

```typescript
interface APIKey {
  id: UUID;
  user_id: UUID;
  provider: 'openai' | 'anthropic' | 'custom';
  key_name: string;
  api_base_url?: string;
  default_model?: string;
  is_active: boolean;
  created_at: datetime;
  last_used_at?: datetime;
}
```

### 6.3 议题模型

```typescript
interface Topic {
  id: UUID;
  user_id: UUID;
  title: string;
  description?: string;
  context?: string;
  attachments?: Array<{
    filename: string;
    url: string;
    size: number;
    mime_type: string;
  }>;
  status: 'draft' | 'ready' | 'in_discussion' | 'completed';
  template_id?: UUID;
  created_at: datetime;
  updated_at: datetime;
}
```

### 6.4 角色模型

```typescript
interface Character {
  id: UUID;
  user_id?: UUID;  // null 表示系统模板
  name: string;
  avatar_url?: string;
  is_template: boolean;
  is_public: boolean;
  config: {
    age?: number;
    gender?: string;
    profession?: string;
    personality: {
      openness: number;      // 1-10
      rigor: number;         // 1-10
      critical_thinking: number;  // 1-10
      optimism: number;      // 1-10
    };
    knowledge: {
      fields: string[];
      experience_years: number;
      representative_views: string[];
    };
    stance: 'support' | 'oppose' | 'neutral' | 'critical_exploration';
    expression_style: 'formal' | 'casual' | 'technical' | 'storytelling';
    behavior_pattern: 'active' | 'passive' | 'balanced';
  };
  usage_count: number;
  rating_avg: number;  // 0-10
  rating_count: number;
  created_at: datetime;
  updated_at: datetime;
}
```

### 6.5 讨论模型

```typescript
interface Discussion {
  id: UUID;
  topic_id: UUID;
  user_id: UUID;
  discussion_mode: 'free' | 'structured' | 'creative' | 'consensus';
  max_rounds: number;
  status: 'initialized' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';
  current_round: number;
  current_phase: 'opening' | 'development' | 'debate' | 'closing';
  progress_percentage: number;  // 0-100
  llm_provider?: string;
  llm_model?: string;
  total_tokens_used: number;
  estimated_cost_usd: number;
  started_at?: datetime;
  completed_at?: datetime;
  created_at: datetime;
  updated_at: datetime;
}
```

### 6.6 消息模型

```typescript
interface Message {
  id: UUID;
  discussion_id: UUID;
  participant_id: UUID;
  character_name: string;
  character_avatar_url?: string;
  content: string;
  phase: 'opening' | 'development' | 'debate' | 'closing';
  round: number;
  token_count?: number;
  is_injected_question: boolean;
  metadata?: {
    sentiment?: string;
    topics?: string[];
    keywords?: string[];
  };
  created_at: datetime;
}
```

### 6.7 报告模型

```typescript
interface Report {
  id: UUID;
  discussion_id: UUID;
  overview?: {
    topic_title: string;
    discussion_duration_seconds: number;
    total_rounds: number;
    total_messages: number;
    participant_count: number;
    llm_provider: string;
    llm_model: string;
  };
  summary?: string;  // Markdown 格式
  viewpoints_summary?: Array<{
    character_id: UUID;
    character_name: string;
    stance: string;
    core_arguments: string[];
    position_evolution?: Array<{
      round: number;
      position: string;
    }>;
  }>;
  consensus?: {
    agreements: string[];
    joint_recommendations: string[];
    supporting_arguments: string[];
  };
  controversies?: Array<{
    topic: string;
    viewpoints: { [character_name: string]: string[] };
    unresolved: boolean;
  }>;
  insights?: Array<{
    description: string;
    related_messages: UUID[];
  }>;
  recommendations?: Array<{
    action: string;
    rationale: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  quality_scores?: {
    depth: number;       // 0-100
    diversity: number;   // 0-100
    constructive: number;  // 0-100
    coherence: number;   // 0-100
    overall: number;     // 0-100
  };
  generation_time_ms?: number;
  created_at: datetime;
  updated_at: datetime;
}
```

---

## 附录

### A. WebSocket 接口（计划中）

**连接地址**: `ws://localhost:8000/ws/discussions/{discussion_id}`

**消息格式**:

```json
{
  "type": "message" | "status_update" | "error",
  "data": { ... },
  "timestamp": "2026-02-03T10:30:00Z"
}
```

### B. 速率限制

| 端点类型 | 限制 |
|---------|------|
| 认证端点 | 5 次/分钟/IP |
| API 端点 | 60 次/分钟/用户 |
| 讨论创建 | 10 次/小时/用户 |

### C. 分页建议

- 默认每页 20 条记录
- 最大每页 100 条记录
- 使用 `skip` 和 `limit` 参数控制分页

### D. 时间格式

所有时间字段使用 ISO 8601 格式（UTC 时区）：

```
2026-02-03T10:30:00Z
```

### E. UUID 格式

所有 UUID 使用标准 RFC 4122 格式（小写，带连字符）：

```
550e8400-e29b-41d4-a716-446655440000
```

---

**文档维护**: 本文档随 API 变更持续更新

**变更历史**:

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-02-03 | 初始版本，完整 API 接口文档 |
