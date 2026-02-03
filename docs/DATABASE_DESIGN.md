# simFocus 数据库设计文档

**版本**: v1.0
**日期**: 2026-02-03
**状态**: 详细设计文档

---

## 目录

1. [数据库概述](#1-数据库概述)
2. [PostgreSQL 数据库设计](#2-postgresql-数据库设计)
   - [2.1 扩展与初始化](#21-扩展与初始化)
   - [2.2 核心数据表](#22-核心数据表)
   - [2.3 表关系图](#23-表关系图)
   - [2.4 索引设计](#24-索引设计)
   - [2.5 约束与触发器](#25-约束与触发器)
3. [Redis 缓存设计](#3-redis-缓存设计)
   - [3.1 缓存策略](#31-缓存策略)
   - [3.2 数据结构](#32-数据结构)
   - [3.3 缓存失效策略](#33-缓存失效策略)
4. [数据生命周期管理](#4-数据生命周期管理)
5. [性能优化](#5-性能优化)
6. [备份与恢复](#6-备份与恢复)
7. [数据迁移](#7-数据迁移)

---

## 1. 数据库概述

### 1.1 数据库架构

simFocus 采用**双数据库架构**：

- **PostgreSQL 15**：主关系型数据库，存储持久化数据
- **Redis 7**：内存数据库，用于缓存、会话管理和 Pub/Sub

### 1.2 技术选型理由

| 数据库 | 用途 | 优势 |
|--------|------|------|
| PostgreSQL | 主数据存储 | ACID 合规、JSONB 灵活性、全文搜索、pgvector 支持 |
| Redis | 缓存与会话 | 高性能、数据结构丰富、Pub/Sub、原子操作 |

### 1.3 数据库连接配置

```python
# PostgreSQL (异步)
DATABASE_URL = "postgresql+asyncpg://simfocus:password@localhost:5432/simfocus"

# 连接池配置
pool_size = 10
max_overflow = 20
pool_pre_ping = True  # 自动检测连接有效性

# Redis (异步)
REDIS_URL = "redis://localhost:6379/0"
max_connections = 20
encoding = "utf-8"
decode_responses = True
```

---

## 2. PostgreSQL 数据库设计

### 2.1 扩展与初始化

#### 2.1.1 PostgreSQL 扩展

```sql
-- UUID 生成扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 全文搜索扩展（三元组索引）
CREATE EXTENSION IF NOT EXISTS pg_trgm";

-- 向量相似度搜索扩展（P2 阶段）
-- CREATE EXTENSION IF NOT EXISTS "vector";
```

#### 2.1.2 初始化数据

- **预设角色模板**：114 个系统预设角色
- **角色分类**：
  - 商业与产品 (10)
  - 医疗与健康 (8)
  - 教育与研究 (8)
  - 法律服务 (6)
  - 服务行业 (12)
  - 交通与物流 (8)
  - 建筑与工程 (8)
  - 金融服务 (8)
  - 媒体与艺术 (10)
  - 体育与娱乐 (6)
  - 公共服务 (8)
  - 农业与制造业 (6)
  - 学生与长者 (8)
  - 自由职业者与其他 (8)

---

### 2.2 核心数据表

#### 2.2.1 用户表 (users)

**用途**：存储用户账户信息和认证数据

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),              -- NULL for OAuth-only users
    name            VARCHAR(100),
    avatar_url      TEXT,
    bio             TEXT,
    email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    auth_provider   VARCHAR(50) NOT NULL DEFAULT 'email',  -- 'email', 'keycloak'
    provider_id     VARCHAR(255),             -- OAuth provider user ID
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ               -- Soft delete
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 用户邮箱 |
| password_hash | VARCHAR(255) | NULLABLE | bcrypt 哈希密码 |
| auth_provider | VARCHAR(50) | NOT NULL | 认证提供者 |
| deleted_at | TIMESTAMPTZ | NULLABLE | 软删除时间戳 |

**关系**：
- 一个用户可以有多个 API 密钥
- 一个用户可以创建多个议题
- 一个用户可以创建多个角色
- 一个用户可以发起多个讨论
- 一个用户可以创建多个分享链接
- 一个用户有多条审计日志

---

#### 2.2.2 用户 API 密钥表 (user_api_keys)

**用途**：存储用户的 LLM API 密钥（AES-256 加密）

```sql
CREATE TABLE user_api_keys (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL,      -- 'openai', 'anthropic', 'custom'
    key_name        VARCHAR(100) NOT NULL,
    encrypted_key   TEXT NOT NULL,             -- AES-256-GCM encrypted
    api_base_url    VARCHAR(500),              -- Custom endpoint URL
    default_model   VARCHAR(100),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at    TIMESTAMPTZ
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | UUID | FK → users.id | 用户 ID |
| provider | VARCHAR(50) | NOT NULL | LLM 提供商 |
| encrypted_key | TEXT | NOT NULL | 加密后的 API 密钥 |
| api_base_url | VARCHAR(500) | NULLABLE | 自定义 API 端点 |

**加密说明**：
- 算法：AES-256-GCM
- 密钥长度：32 字节
- Nonce：96 位（随机生成）
- 存储格式：Base64(nonce + ciphertext)

---

#### 2.2.3 议题表 (topics)

**用途**：存储讨论议题信息

```sql
CREATE TABLE topics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    context         TEXT,                      -- Additional background
    attachments     JSONB,                     -- Array of file metadata
    status          VARCHAR(20) NOT NULL DEFAULT 'draft',  -- 'draft', 'ready', 'in_discussion', 'completed'
    template_id     UUID,                      -- If created from template
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | UUID | FK → users.id | 创建者 ID |
| title | VARCHAR(200) | NOT NULL | 议题标题 |
| description | TEXT | NULLABLE | 议题描述 |
| attachments | JSONB | NULLABLE | 附件元数据数组 |
| status | VARCHAR(20) | NOT NULL | 议题状态 |

**attachments JSONB 结构**：
```json
[
  {
    "filename": "document.pdf",
    "url": "https://s3.../document.pdf",
    "size": 1024000,
    "mime_type": "application/pdf"
  }
]
```

---

#### 2.2.4 角色表 (characters)

**用途**：存储角色配置（系统预设 + 用户自定义）

```sql
CREATE TABLE characters (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,  -- NULL for system templates
    name            VARCHAR(100) NOT NULL,
    avatar_url      TEXT,
    is_template     BOOLEAN NOT NULL DEFAULT FALSE,
    is_public       BOOLEAN NOT NULL DEFAULT FALSE,  -- For P2 marketplace
    config          JSONB NOT NULL,           -- Character configuration
    usage_count     INTEGER NOT NULL DEFAULT 0,
    rating_avg      NUMERIC(3,2) NOT NULL DEFAULT 0.00,
    rating_count    INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | UUID | FK → users.id (NULLABLE) | 所有者 ID（NULL 表示系统模板） |
| is_template | BOOLEAN | NOT NULL | 是否为系统模板 |
| config | JSONB | NOT NULL | 角色配置 |
| usage_count | INTEGER | NOT NULL | 使用次数统计 |
| rating_avg | NUMERIC(3,2) | NOT NULL | 平均评分 |

**config JSONB 结构**：
```json
{
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
  "stance": "critical_exploration",    // 'support', 'oppose', 'neutral', 'critical_exploration'
  "expression_style": "formal",         // 'formal', 'casual', 'technical', 'storytelling'
  "behavior_pattern": "balanced"        // 'active', 'passive', 'balanced'
}
```

---

#### 2.2.5 讨论会话表 (discussions)

**用途**：存储讨论会话信息

```sql
CREATE TABLE discussions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id            UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    discussion_mode     VARCHAR(20) NOT NULL DEFAULT 'free',  -- 'free', 'structured', 'creative', 'consensus'
    max_rounds          INTEGER NOT NULL DEFAULT 10,
    status              VARCHAR(20) NOT NULL DEFAULT 'initialized',  -- 'initialized', 'running', 'paused', 'completed', 'failed', 'cancelled'
    current_round       INTEGER NOT NULL DEFAULT 0,
    current_phase       VARCHAR(20) NOT NULL DEFAULT 'opening',  -- 'opening', 'development', 'debate', 'closing'
    llm_provider        VARCHAR(50),              -- Which API was used
    llm_model           VARCHAR(100),             -- Which model
    total_tokens_used   INTEGER NOT NULL DEFAULT 0,
    estimated_cost_usd  NUMERIC(10,4) NOT NULL DEFAULT 0.0000,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| topic_id | UUID | FK → topics.id | 关联议题 |
| discussion_mode | VARCHAR(20) | NOT NULL | 讨论模式 |
| status | VARCHAR(20) | NOT NULL | 讨论状态 |
| current_phase | VARCHAR(20) | NOT NULL | 当前阶段 |

**讨论模式说明**：
- `free`：自由讨论（角色自由发言）
- `structured`：结构化辩论（正反方）
- `creative`：创意发散（"是的，而且"）
- `consensus`：共识构建（寻找共同点）

---

#### 2.2.6 讨论参与者表 (discussion_participants)

**用途**：存储讨论的参与者（角色）信息

```sql
CREATE TABLE discussion_participants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discussion_id   UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    character_id    UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    position        INTEGER NOT NULL,         -- Order for structured debates
    stance          VARCHAR(20),              -- For structured mode: 'pro', 'con', 'neutral'
    message_count   INTEGER NOT NULL DEFAULT 0,
    total_tokens    INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| discussion_id | UUID | FK → discussions.id | 所属讨论 |
| character_id | UUID | FK → characters.id | 关联角色 |
| position | INTEGER | NOT NULL | 发言顺序 |
| stance | VARCHAR(20) | NULLABLE | 立场（结构化模式） |

---

#### 2.2.7 讨论消息表 (discussion_messages)

**用途**：存储讨论中的所有消息

```sql
CREATE TABLE discussion_messages (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discussion_id       UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    participant_id      UUID NOT NULL REFERENCES discussion_participants(id) ON DELETE CASCADE,
    round               INTEGER NOT NULL,
    phase               VARCHAR(20) NOT NULL,   -- 'opening', 'development', 'debate', 'closing'
    content             TEXT NOT NULL,
    token_count         INTEGER,
    is_injected_question BOOLEAN NOT NULL DEFAULT FALSE,  -- User-injected question
    parent_message_id   UUID REFERENCES discussion_messages(id),  -- For threading
    meta_data           JSONB,                  -- Additional data (sentiment, topics, etc.)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tsv                 TSVECTOR                 -- Full-text search
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| discussion_id | UUID | FK → discussions.id | 所属讨论 |
| participant_id | UUID | FK → discussion_participants.id | 发言者 |
| round | INTEGER | NOT NULL | 轮次号 |
| phase | VARCHAR(20) | NOT NULL | 阶段 |
| tsv | TSVECTOR | NULLABLE | 全文搜索向量 |

**meta_data JSONB 结构**：
```json
{
  "sentiment": "positive",
  "topics": ["技术可行性", "成本"],
  "keywords": ["API", "成本", "时间"],
  "embedding_vector": [0.1, 0.2, ...]  // P2 功能
}
```

---

#### 2.2.8 报告表 (reports)

**用途**：存储讨论生成的报告

```sql
CREATE TABLE reports (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discussion_id           UUID NOT NULL UNIQUE REFERENCES discussions(id) ON DELETE CASCADE,
    overview                JSONB,
    summary                 TEXT,                    -- LLM-generated comprehensive summary
    viewpoints_summary      JSONB,                   -- Array of character viewpoints
    consensus               JSONB,
    controversies           JSONB,                   -- Array of disagreement points
    insights                JSONB,
    recommendations         JSONB,
    transcript              TEXT,                    -- Full discussion transcript
    full_transcript_citation JSONB,                 -- Reference to messages (deprecated)
    quality_scores          JSONB,                   -- depth, diversity, constructive, coherence
    generation_time_ms      INTEGER,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| discussion_id | UUID | UNIQUE, FK | 关联讨论（一对一） |
| summary | TEXT | NULLABLE | Markdown 格式综合摘要 |
| quality_scores | JSONB | NULLABLE | 质量评分 |

**quality_scores JSONB 结构**：
```json
{
  "depth": 85,
  "diversity": 78,
  "constructive": 82,
  "coherence": 90,
  "overall": 84
}
```

---

#### 2.2.9 分享链接表 (share_links)

**用途**：存储讨论报告的分享链接

```sql
CREATE TABLE share_links (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    discussion_id   UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slug            VARCHAR(20) UNIQUE NOT NULL,  -- Short URL slug
    password_hash   VARCHAR(255),                  -- NULL if no password
    expires_at      TIMESTAMPTZ,
    access_count    INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| discussion_id | UUID | FK → discussions.id | 关联讨论 |
| slug | VARCHAR(20) | UNIQUE, NOT NULL | 短 URL 标识 |
| password_hash | VARCHAR(255) | NULLABLE | 密码哈希（bcrypt） |
| expires_at | TIMESTAMPTZ | NULLABLE | 过期时间 |

---

#### 2.2.10 审计日志表 (audit_logs)

**用途**：记录系统关键操作

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    action          VARCHAR(100) NOT NULL,     -- 'discussion_created', 'api_key_added', etc.
    resource_type   VARCHAR(50) NOT NULL,      -- 'discussion', 'topic', 'character'
    resource_id     UUID,
    ip_address      INET,
    user_agent      TEXT,
    log_metadata    JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**字段说明**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | UUID | FK → users.id (NULLABLE) | 操作用户 |
| action | VARCHAR(100) | NOT NULL | 操作类型 |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型 |
| ip_address | INET | NULLABLE | IP 地址 |
| log_metadata | JSONB | NULLABLE | 额外元数据 |

**操作类型 (action)**：
- `user_registered`
- `user_logged_in`
- `discussion_created`
- `discussion_started`
- `discussion_completed`
- `api_key_added`
- `api_key_deleted`
- `character_created`
- `share_link_created`
- `share_link_accessed`

---

### 2.3 表关系图

```
users (1) ────< (N) user_api_keys
  │
  ├───< (N) topics (1) ────> (1) discussions (1) ────> (1) reports
  │                                   │
  │                                   ├───< (N) discussion_participants (N) ────> characters
  │                                   │                                    │
  │                                   └───< (N) discussion_messages ──────┘
  │
  ├───< (N) characters
  │
  ├───< (N) discussions
  │
  ├───< (N) share_links
  │
  └───< (N) audit_logs
```

**关系类型说明**：
- `1 ──< N`：一对多关系
- `1 ──> 1`：一对一关系
- `ON DELETE CASCADE`：级联删除
- `ON DELETE SET NULL`：置空删除

---

### 2.4 索引设计

#### 2.4.1 主键索引

所有表都使用 UUID 主键，自动创建索引。

#### 2.4.2 唯一索引

```sql
-- users 表
CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;

-- share_links 表
CREATE UNIQUE INDEX idx_share_links_slug ON share_links(slug);

-- reports 表
CREATE UNIQUE INDEX idx_reports_discussion_id ON reports(discussion_id);
```

#### 2.4.3 普通索引

```sql
-- user_api_keys 表
CREATE INDEX idx_api_keys_user_id ON user_api_keys(user_id);

-- topics 表
CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_topics_status ON topics(status);

-- characters 表
CREATE INDEX idx_characters_user_id ON characters(user_id);
CREATE INDEX idx_characters_is_template ON characters(is_template) WHERE is_template = TRUE;

-- discussions 表
CREATE INDEX idx_discussions_user_id ON discussions(user_id);
CREATE INDEX idx_discussions_status ON discussions(status);
CREATE INDEX idx_discussions_topic_id ON discussions(topic_id);

-- discussion_participants 表
CREATE INDEX idx_participants_discussion_id ON discussion_participants(discussion_id);

-- discussion_messages 表
CREATE INDEX idx_messages_discussion_id ON discussion_messages(discussion_id);
CREATE INDEX idx_messages_discussion_round ON discussion_messages(discussion_id, round);

-- share_links 表
CREATE INDEX idx_share_links_discussion_id ON share_links(discussion_id);

-- audit_logs 表
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

#### 2.4.4 全文搜索索引

```sql
-- discussion_messages 表（GIN 索引）
CREATE INDEX idx_messages_tsv ON discussion_messages USING GIN(tsv);

-- 自动更新 tsv 列的触发器
CREATE OR REPLACE FUNCTION discussion_messages_tsv_trigger() RETURNS trigger AS $$
BEGIN
  NEW.tsv := to_tsvector('simple', coalesce(NEW.content, ''));
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER discussion_messages_tsv_update
  BEFORE INSERT OR UPDATE ON discussion_messages
  FOR EACH ROW
  EXECUTE FUNCTION discussion_messages_tsv_trigger();
```

#### 2.4.5 JSONB 索引

```sql
-- characters 表（角色属性查询）
CREATE INDEX idx_characters_config ON characters USING GIN(config);

-- reports 表（报告元数据查询）
CREATE INDEX idx_reports_quality_scores ON reports USING GIN(quality_scores);

-- audit_logs 表（元数据查询）
CREATE INDEX idx_audit_logs_metadata ON audit_logs USING GIN(log_metadata);
```

---

### 2.5 约束与触发器

#### 2.5.1 外键约束

所有外键关系都定义了 `ON DELETE` 策略：
- `CASCADE`：级联删除（如删除用户时删除其所有数据）
- `SET NULL`：置空（如系统模板角色的 user_id）
- `RESTRICT`：限制删除（如删除有讨论的议题）

#### 2.5.2 检查约束

```sql
-- 检查讨论轮次范围
ALTER TABLE discussions ADD CONSTRAINT chk_discussion_rounds
  CHECK (max_rounds >= 3 AND max_rounds <= 20);

-- 检查评分范围
ALTER TABLE characters ADD CONSTRAINT chk_character_rating
  CHECK (rating_avg >= 0 AND rating_avg <= 10);

-- 检查讨论状态
ALTER TABLE discussions ADD CONSTRAINT chk_discussion_status
  CHECK (status IN ('initialized', 'running', 'paused', 'completed', 'failed', 'cancelled'));

-- 检查议题状态
ALTER TABLE topics ADD CONSTRAINT chk_topic_status
  CHECK (status IN ('draft', 'ready', 'in_discussion', 'completed'));
```

#### 2.5.3 触发器

```sql
-- 自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- 应用到需要 updated_at 的表
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_topics_updated_at BEFORE UPDATE ON topics
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_discussions_updated_at BEFORE UPDATE ON discussions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 全文搜索自动更新（已在索引部分定义）
```

---

## 3. Redis 缓存设计

### 3.1 缓存策略

#### 3.1.1 缓存层次

```
┌─────────────────────────────────────────────────────────────┐
│                     应用层                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  会话缓存     │  │  用户缓存    │  │  API 密钥    │    │
│  │  (24h TTL)   │  │  (1h TTL)    │  │  (1h TTL)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ 讨论状态     │  │  角色模板    │  │ 速率限制     │    │
│  │ (动态 TTL)   │  │  (24h TTL)   │  │ (窗口 TTL)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Redis 缓存层                              │
│  - String (JSON)                                            │
│  - Sorted Set (速率限制)                                    │
│  - Pub/Sub (WebSocket 消息广播)                            │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1.2 缓存键命名规范

```
{数据类型}:{唯一标识}:{可选标识}

示例：
- session:abc123
- user:550e8400-e29b-41d4-a716-446655440000:profile
- user_api_keys:550e8400-e29b-41d4-a716-446655440000
- discussion_state:550e8400-e29b-41d4-a716-446655440000
- character_template:11111111-0000-0000-0000-000000000001
- ratelimit:550e8400-e29b-41d4-a716-446655440000:/api/discussions
- round_summary:550e8400-e29b-41d4-a716-446655440000:5:a1b2c3d4
```

---

### 3.2 数据结构

#### 3.2.1 String (JSON 序列化)

**用途**：存储缓存对象

```python
# 缓存结构示例
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "current_round": 5,
  "max_rounds": 10,
  "current_phase": "debate",
  "progress_percentage": 45.5
}
```

**实现代码**：
```python
class CacheService:
    async def get(self, key: str) -> Optional[any]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: any, ttl: int = None) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.redis.set(key, value, ex=ttl)
```

**使用场景**：
1. **用户会话**：`session:{session_id}`
   - TTL: 24 小时
   - Value: `{user_id, email, name, created_at}`

2. **用户配置**：`user:{user_id}:profile`
   - TTL: 1 小时
   - Value: `{id, email, name, avatar_url, bio, preferences}`

3. **API 密钥**：`user_api_keys:{user_id}`
   - TTL: 1 小时（加密存储）
   - Value: `[{id, provider, key_name, encrypted_key, ...}]`

4. **讨论状态**：`discussion_state:{discussion_id}`
   - TTL: 3600s（运行中）或 86400s（已完成）
   - Value: `{id, status, current_round, max_rounds, current_phase, progress_percentage}`

5. **角色模板**：`character_template:{template_id}`
   - TTL: 24 小时
   - Value: 完整角色配置 JSON

6. **轮次摘要**：`round_summary:{discussion_id}:{round}:{hash}`
   - TTL: 1 小时
   - Value: Markdown 格式的轮次摘要

---

#### 3.2.2 Sorted Set (速率限制)

**用途**：滑动窗口速率限制

```python
class RateLimitService:
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int = 60
    ) -> tuple[bool, dict]:
        """检查请求是否允许

        Args:
            key: 唯一标识（如 user_id 或 ip）
            limit: 最大请求数
            window: 时间窗口（秒）

        Returns:
            (是否允许, 信息字典)
        """
        current_time = int(time.time())
        window_start = current_time - window

        # 使用 Redis sorted set 实现滑动窗口
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)  # 清除过期记录
        pipe.zcard(key)                               # 当前窗口计数
        pipe.zadd(key, {str(current_time): current_time})  # 添加当前请求
        pipe.expire(key, window)                      # 设置过期
        results = await pipe.execute()

        count = results[1]
        remaining = max(0, limit - count)
        reset = current_time + window

        return count < limit, {
            'limit': limit,
            'remaining': remaining,
            'reset': reset
        }
```

**使用场景**：
- **速率限制键**：`ratelimit:{user_id}:{endpoint}`
- **速率限制 IP 键**：`ratelimit:{ip_address}:{endpoint}`
- **窗口大小**：60 秒
- **限制示例**：
  - 认证端点：5 次/分钟/IP
  - API 端点：60 次/分钟/用户
  - 讨论创建：10 次/小时/用户

---

#### 3.2.3 Pub/Sub (消息广播)

**用途**：WebSocket 消息广播到多个服务器实例

```python
# 发布消息
await redis.publish(
    f"discussion:{discussion_id}:messages",
    json.dumps({
        "type": "message",
        "data": {
            "message_id": str(message.id),
            "character_id": str(character.id),
            "character_name": character.name,
            "content": content,
            "round": discussion.current_round,
            "phase": discussion.current_phase,
            "timestamp": datetime.utcnow().isoformat()
        }
    })
)

# 订阅消息
pubsub = redis.pubsub()
await pubsub.subscribe(f"discussion:{discussion_id}:messages")
async for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        # 广播到连接的客户端
        await broadcast_to_clients(data)
```

**频道命名规范**：
- `discussion:{discussion_id}:messages`：讨论消息
- `discussion:{discussion_id}:status`：讨论状态更新
- `discussion:{discussion_id}:control`：控制命令

---

### 3.3 缓存失效策略

#### 3.3.1 TTL 策略

| 缓存类型 | TTL | 失效策略 |
|---------|-----|----------|
| 会话缓存 | 24 小时 | 时间过期 |
| 用户配置 | 1 小时 | 时间过期 + 更新时失效 |
| API 密钥 | 1 小时 | 时间过期 + 更新时失效 |
| 讨论状态 | 1h/24h | 时间过期 + 状态变更时失效 |
| 角色模板 | 24 小时 | 时间过期 |
| 轮次摘要 | 1 小时 | 时间过期 |
| 速率限制 | 窗口时间 | 滑动窗口 |
| WebSocket 追踪 | 连接时长 | 连接断开时删除 |

#### 3.3.2 主动失效

```python
# 用户配置更新时失效缓存
async def update_user_profile(user_id: UUID, updates: dict):
    # 更新数据库
    await db.execute(update(User).where(User.id == user_id).values(**updates))
    await db.commit()

    # 失效缓存
    cache_key = f"user:{user_id}:profile"
    await cache.delete(cache_key)

# API 密钥更新时失效缓存
async def add_api_key(user_id: UUID, key_data: dict):
    # 更新数据库
    new_key = UserAPIKey(user_id=user_id, **key_data)
    db.add(new_key)
    await db.commit()

    # 失效缓存
    cache_key = f"user_api_keys:{user_id}"
    await cache.delete(cache_key)

# 讨论状态变更时更新缓存
async def update_discussion_state(discussion: Discussion):
    # 更新数据库
    await db.commit()

    # 更新缓存
    await _cache_discussion_state(discussion)
```

#### 3.3.3 缓存预热

```python
# 应用启动时预热关键数据
async def warmup_cache():
    # 预加载系统角色模板
    characters = await db.execute(select(Character).where(Character.is_template == True))
    for char in characters.scalars().all():
        cache_key = f"character_template:{char.id}"
        await cache.set(cache_key, char.to_dict(), ttl=86400)

    # 预加载活跃用户的配置
    active_users = await db.execute(
        select(User)
        .where(User.last_login_at > datetime.utcnow() - timedelta(days=7))
    )
    for user in active_users.scalars().all():
        cache_key = f"user:{user.id}:profile"
        await cache.set(cache_key, user.to_dict(), ttl=3600)
```

---

## 4. 数据生命周期管理

### 4.1 数据保留策略

| 数据类型 | 热存储 (0-30天) | 温存储 (31-90天) | 冷存储 (90+天) |
|---------|----------------|-----------------|----------------|
| 讨论消息 | PostgreSQL 主库 | PostgreSQL 从库 | S3 (JSON) |
| 讨论报告 | PostgreSQL 主库 | PostgreSQL 从库 | S3 (JSON) |
| 审计日志 | PostgreSQL 主库 | PostgreSQL 从库 | S3 (JSON) |
| 用户数据 | PostgreSQL 主库 | PostgreSQL 从库 | S3 (JSON) |
| 分享链接 | PostgreSQL 主库 | - | 删除 |

### 4.2 数据清理策略

#### 4.2.1 自动归档

```python
async def archive_old_discussions():
    """归档 90 天前的讨论"""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    # 1. 导出到 S3
    discussions = await db.execute(
        select(Discussion).where(Discussion.created_at < cutoff_date)
    )

    for discussion in discussions.scalars():
        # 导出讨论数据到 JSON
        data = {
            "discussion": discussion.to_dict(),
            "messages": [msg.to_dict() for msg in discussion.messages],
            "report": discussion.report.to_dict() if discussion.report else None
        }

        # 上传到 S3
        s3_key = f"archives/discussions/{discussion.id}.json"
        await s3_client.put_object(
            Bucket="simfocus-archive",
            Key=s3_key,
            Body=json.dumps(data)
        )

    # 2. 从主库删除
    await db.execute(
        delete(Discussion).where(Discussion.created_at < cutoff_date)
    )
    await db.commit()
```

#### 4.2.2 软删除清理

```python
async def cleanup_soft_deleted_users():
    """永久删除 30 天前软删除的用户"""
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    # 删除用户及其关联数据
    await db.execute(
        delete(User).where(
            and_(
                User.deleted_at < cutoff_date,
                User.deleted_at.isnot(None)
            )
        )
    )
    await db.commit()
```

#### 4.2.3 过期分享链接清理

```python
async def cleanup_expired_share_links():
    """删除过期的分享链接"""
    await db.execute(
        delete(ShareLink).where(
            and_(
                ShareLink.expires_at < datetime.utcnow(),
                ShareLink.expires_at.isnot(None)
            )
        )
    )
    await db.commit()
```

### 4.3 数据恢复

```python
async def restore_discussion_from_archive(discussion_id: UUID):
    """从归档恢复讨论"""
    # 1. 从 S3 获取数据
    response = await s3_client.get_object(
        Bucket="simfocus-archive",
        Key=f"archives/discussions/{discussion_id}.json"
    )
    data = json.loads(response['Body'].read())

    # 2. 恢复到数据库
    # 创建讨论记录
    discussion = Discussion(**data['discussion'])
    db.add(discussion)

    # 创建消息记录
    for msg_data in data['messages']:
        message = DiscussionMessage(**msg_data)
        db.add(message)

    # 创建报告记录
    if data['report']:
        report = Report(**data['report'])
        db.add(report)

    await db.commit()
```

---

## 5. 性能优化

### 5.1 数据库优化

#### 5.1.1 查询优化

```python
# 不好的查询（N+1 问题）
async def get_discussion_messages_bad(discussion_id: UUID):
    messages = await db.execute(
        select(DiscussionMessage).where(
            DiscussionMessage.discussion_id == discussion_id
        )
    )

    result = []
    for msg in messages.scalars():
        # N+1: 每条消息都查询一次数据库
        participant = await db.execute(
            select(DiscussionParticipant).where(
                DiscussionParticipant.id == msg.participant_id
            )
        )
        character = await db.execute(
            select(Character).where(Character.id == participant.scalar().character_id)
        )
        result.append({
            "message": msg,
            "character": character.scalar()
        })

    return result

# 优化后的查询（使用 JOIN）
async def get_discussion_messages_good(discussion_id: UUID):
    result = await db.execute(
        select(DiscussionMessage, DiscussionParticipant, Character)
        .join(DiscussionParticipant, DiscussionMessage.participant_id == DiscussionParticipant.id)
        .join(Character, DiscussionParticipant.character_id == Character.id)
        .where(DiscussionMessage.discussion_id == discussion_id)
        .order_by(DiscussionMessage.created_at)
    )

    return [
        {
            "message": msg,
            "character": char
        }
        for msg, _, char in result.all()
    ]
```

#### 5.1.2 批量操作

```python
# 批量插入
async def seed_characters(characters_data: list):
    db.bulk_insert_mappings(Character, characters_data)
    await db.commit()

# 批量更新
async def update_usage_counts(character_ids: list[UUID]):
    await db.execute(
        update(Character)
        .where(Character.id.in_(character_ids))
        .values(usage_count=Character.usage_count + 1)
    )
    await db.commit()
```

#### 5.1.3 连接池配置

```python
# 生产环境推荐配置
engine = create_async_engine(
    DATABASE_URL,
    echo=False,                    # 生产环境关闭 SQL 日志
    pool_size=20,                  # 增加连接池大小
    max_overflow=40,               # 增加溢出连接数
    pool_pre_ping=True,            # 连接前检查有效性
    pool_recycle=3600,             # 1 小时回收连接
    pool_timeout=30,               # 30 秒超时
    connect_args={
        "connect_timeout": 10,
        "command_timeout": 60,
    }
)
```

### 5.2 缓存优化

#### 5.2.1 缓存穿透防护

```python
async def get_character_with_cache(character_id: UUID):
    # 1. 尝试从缓存获取
    cache_key = f"character:{character_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # 2. 从数据库获取
    character = await db.get(Character, character_id)

    # 3. 缓存空值（防止缓存穿透）
    if character is None:
        await cache.set(cache_key, None, ttl=60)  # 短 TTL
        return None

    # 4. 缓存结果
    await cache.set(cache_key, character.to_dict(), ttl=3600)
    return character.to_dict()
```

#### 5.2.2 缓存雪崩防护

```python
import random

async def cache_with_jitter(key: str, value: any, base_ttl: int):
    """添加随机抖动防止缓存雪崩"""
    jitter = random.randint(0, 300)  # 0-5 分钟抖动
    ttl = base_ttl + jitter
    await cache.set(key, value, ttl=ttl)
```

#### 5.2.3 缓存预热

```python
async def warmup_character_cache():
    """预热热门角色缓存"""
    # 获取最常用的角色
    popular_characters = await db.execute(
        select(Character)
        .where(Character.is_template == True)
        .order_by(Character.usage_count.desc())
        .limit(50)
    )

    for char in popular_characters.scalars():
        cache_key = f"character_template:{char.id}"
        await cache.set(cache_key, char.to_dict(), ttl=86400)
```

---

## 6. 备份与恢复

### 6.1 备份策略

#### 6.1.1 PostgreSQL 备份

```bash
# 全量备份（每日）
pg_dump -Fc -h localhost -U simfocus simfocus > backup_$(date +%Y%m%d).dump

# 增量备份（每小时，基于 WAL 归档）
# postgresql.conf 配置:
wal_level = replica
archive_mode = on
archive_command = 'cp %p /wal_archive/%f'
```

#### 6.1.2 Redis 备份

```bash
# RDB 快照（自动）
# redis.conf 配置:
save 900 1      # 900 秒内至少 1 个 key 变化
save 300 10     # 300 秒内至少 10 个 key 变化
save 60 10000   # 60 秒内至少 10000 个 key 变化

# AOF 持久化（可选）
appendonly yes
appendfsync everysec
```

### 6.2 恢复流程

#### 6.2.1 PostgreSQL 恢复

```bash
# 从备份恢复
pg_restore -h localhost -U simfocus -d simfocus backup_20260203.dump

# 时间点恢复（PITR）
# 1. 恢复基础备份
pg_restore -h localhost -U simfocus -d simfocus backup_base.dump

# 2. 应用 WAL 日志到指定时间点
pg_ctl start -o "-recovery_target_time '2026-02-03 10:00:00'"
```

#### 6.2.2 Redis 恢复

```bash
# 从 RDB 文件恢复
cp /path/to/dump.rdb /var/lib/redis/dump.rdb
redis-server

# 从 AOF 文件恢复
cp /path/to/appendonly.aof /var/lib/redis/appendonly.aof
redis-server
```

---

## 7. 数据迁移

### 7.1 数据库迁移工具

使用 Alembic 进行数据库版本管理。

```bash
# 创建迁移
alembic revision --autogenerate -m "Add new column"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 7.2 迁移示例

#### 7.2.1 添加新字段

```python
# Alembic migration
def upgrade():
    op.add_column('discussions',
        sa.Column('new_field', sa.String(100), nullable=True)
    )

def downgrade():
    op.drop_column('discussions', 'new_field')
```

#### 7.2.2 数据迁移

```python
def upgrade():
    # 1. 添加新列
    op.add_column('users',
        sa.Column('full_name', sa.String(200), nullable=True)
    )

    # 2. 迁移数据（合并 name 和 bio）
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = COALESCE(name, '') || ' - ' || COALESCE(bio, '')"
    )

    # 3. 使新列非空
    op.alter_column('users', 'full_name', nullable=False)

def downgrade():
    op.drop_column('users', 'full_name')
```

#### 7.2.3 索引迁移

```python
def upgrade():
    # 创建新索引（CONCURRENTLY 避免锁表）
    op.execute("""
        CREATE INDEX CONCURRENTLY idx_messages_created_at
        ON discussion_messages(created_at DESC)
    """)

def downgrade():
    op.execute("DROP INDEX idx_messages_created_at")
```

---

## 附录

### A. ER 图

```
┌──────────────┐
│    users     │
├──────────────┤
│ id (PK)      │
│ email        │
│ password_hash│
│ name         │
│ ...          │
└──────┬───────┘
       │
       ├──┬──────────────────────────────────────────────────────┐
       │  │  │  │  │                                            │
       ▼  ▼  ▼  ▼  ▼                                            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ api_keys │  │ topics   │  │characters│  │discussions│  │share_links│
└──────────┘  └────┬─────┘  └──────────┘  └─────┬────┘  └──────────┘
                   │                             │
                   │                             │
                   ▼                             ▼
              ┌──────────┐              ┌───────────────────────┐
              │discussions│             │discussion_participants│
              └────┬─────┘              └───────────┬───────────┘
                   │                              │
                   │                              │
                   ▼                              ▼
              ┌───────────────────┐      ┌─────────────────┐
              │discussion_messages│      │    characters    │
              └───────────────────┘      └─────────────────┘

                   │
                   ▼
              ┌──────────┐
              │ reports  │
              └──────────┘
```

### B. 数据字典

| 表名 | 中文名 | 记录数估计 | 增长速率 |
|------|--------|-----------|----------|
| users | 用户表 | 10,000+ | 100/天 |
| user_api_keys | API 密钥表 | 20,000+ | 200/天 |
| topics | 议题表 | 50,000+ | 500/天 |
| characters | 角色表 | 114 (固定) + 用户自定义 | 10/天 |
| discussions | 讨论表 | 50,000+ | 500/天 |
| discussion_participants | 参与者表 | 200,000+ | 2,000/天 |
| discussion_messages | 消息表 | 2,000,000+ | 20,000/天 |
| reports | 报告表 | 50,000+ | 500/天 |
| share_links | 分享链接表 | 10,000+ | 100/天 |
| audit_logs | 审计日志表 | 1,000,000+ | 10,000/天 |

### C. 性能基准

| 操作 | 目标响应时间 | 实测响应时间 |
|------|-------------|-------------|
| 用户登录 | < 500ms | ~300ms |
| 创建讨论 | < 1s | ~600ms |
| 获取消息列表 | < 200ms | ~120ms |
| 实时消息推送 | < 100ms | ~50ms |
| 报告生成 | < 10s | ~6s |
| 全文搜索 | < 500ms | ~250ms |

### D. 监控指标

```sql
-- 慢查询监控
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 表大小监控
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 索引使用率
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 缓存命中率
SELECT
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit) as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS cache_hit_ratio
FROM pg_statio_user_tables;
```

---

**文档维护**：本文档随数据库架构变更持续更新

**变更历史**：

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-02-03 | 初始版本，完整数据库设计文档 |
