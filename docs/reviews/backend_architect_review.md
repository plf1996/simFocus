# Backend Architecture Review
## simFocus - AI Virtual Focus Group Platform

**Document Version**: v1.0
**Review Date**: 2026-01-12
**Reviewer**: Backend System Architect
**PRD Version**: v1.0 (2026-01-09)
**Document Status**: Initial Review

---

## Executive Summary

This document provides a comprehensive backend architecture review of the simFocus PRD. The platform presents an ambitious and innovative concept - orchestrating multiple AI personas to simulate focus group discussions. From a backend perspective, this system presents significant technical challenges in real-time communication, LLM orchestration, state management, and scalability.

### Overall Assessment

**Strengths:**
- Clear value proposition and well-defined user journeys
- Thoughtful feature prioritization (MVP to advanced features)
- Strong emphasis on privacy and security (user-controlled API keys)
- Realistic performance requirements and success metrics

**Critical Concerns:**
- Discussion engine complexity is underestimated
- Real-time WebSocket architecture needs careful design
- LLM API cost control and error handling need robust strategies
- State management for discussion sessions requires distributed architecture considerations
- Report generation performance targets may be unrealistic for complex discussions

**Recommendation**: Proceed with MVP development but allocate additional engineering effort for the discussion engine and real-time communication infrastructure. Consider a phased approach with initial synchronous processing before implementing complex async orchestration.

---

## 1. Backend Architecture Recommendations

### 1.1 High-Level Architecture

Based on the PRD requirements, I recommend a **microservices-inspired architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│                    (Kong / AWS API Gateway)                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
        ┌──────────────┐  ┌──────────┐  ┌──────────────┐
        │   Frontend   │  │   Auth   │  │    User      │
        │   Service    │  │ Service  │  │   Service    │
        └──────────────┘  └──────────┘  └──────────────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────┐
                    │                               │                       │
                    ▼                               ▼                       ▼
        ┌──────────────┐                 ┌──────────────┐          ┌──────────────┐
        │   Character  │                 │  Discussion  │          │   Report     │
        │   Service    │                 │   Engine     │          │   Service    │
        └──────────────┘                 └──────────────┘          └──────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
        │  LLM Orch    │          │  WebSocket   │          │    State     │
        │  Service     │          │   Handler    │          │   Store      │
        └──────────────┘          └──────────────┘          └──────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────────┐
        │         External LLM APIs               │
        │  (OpenAI, Anthropic, Custom Endpoint)   │
        └─────────────────────────────────────────┘
```

### 1.2 Technology Stack Recommendations

**Backend Framework:**
- **FastAPI** (Python) - Excellent async support, automatic OpenAPI docs, type hints
- Alternative: Flask + Quart for async if team has more Flask experience

**Database Layer:**
- **PostgreSQL** - Primary relational database (users, topics, discussions, characters)
- **Redis** - Caching, session state, rate limiting, pub/sub for WebSocket scaling
- **Vector Database** (P2): Qdrant or Weaviate for character memory and semantic search

**Message Queue:**
- **RabbitMQ** or **Redis Streams** - For background job processing
- **Celery** or **asyncio** - For async task execution

**Real-time Communication:**
- **WebSocket** - Primary protocol for discussion streaming
- **Socket.IO** or **websockets** library - For WebSocket management
- **Redis Pub/Sub** - For multi-server WebSocket scaling

**LLM Integration:**
- **LangChain** or **LlamaIndex** - For LLM orchestration and prompt management
- **Tenacity** - For retry logic with exponential backoff
- **httpx** - Async HTTP client for LLM API calls

**Infrastructure:**
- **Docker** + **Docker Compose** - Local development
- **Kubernetes** (P1/P2) - Production orchestration
- **AWS/GCP** - Cloud hosting (recommend AWS for broader service portfolio)

### 1.3 Deployment Architecture

**MVP Phase (Single Region, Single AZ):**
```
┌─────────────────────────────────────────────────┐
│              Load Balancer (ALB)                │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   FastAPI   │ │   FastAPI   │ │   FastAPI   │
│  Instance   │ │  Instance   │ │  Instance   │
└─────────────┘ └─────────────┘ └─────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │    Redis    │ │   S3/EFs    │
│  (RDS)      │ │  (ElastiCache)│  (Storage)  │
└─────────────┘ └─────────────┘ └─────────────┘
```

**Scale-out Phase (Multi-AZ with Redis Cluster):**
- Add Redis Cluster for session sharing
- Implement database read replicas
- Separate WebSocket servers from API servers
- Add CDN for static assets

---

## 2. API Design Suggestions

### 2.1 RESTful API Structure

**Base URL**: `https://api.simfocus.com/v1`

**Core Endpoints:**

```
# Authentication
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/verify-email
POST   /auth/forgot-password
POST   /auth/reset-password

# User Management
GET    /users/me
PATCH  /users/me
DELETE /users/me
GET    /users/me/api-keys
POST   /users/me/api-keys
DELETE /users/me/api-keys/{key_id}
PATCH  /users/me/api-keys/{key_id}

# Topics (议题管理)
GET    /topics
POST   /topics
GET    /topics/{topic_id}
PATCH  /topics/{topic_id}
DELETE /topics/{topic_id}
POST   /topics/{topic_id}/duplicate

# Characters (角色系统)
GET    /characters
POST   /characters
GET    /characters/{character_id}
PATCH  /characters/{character_id}
DELETE /characters/{character_id}
GET    /characters/templates
POST   /characters/from-template

# Discussions (讨论引擎)
POST   /discussions
GET    /discussions
GET    /discussions/{discussion_id}
DELETE /discussions/{discussion_id}
POST   /discussions/{discussion_id}/start
POST   /discussions/{discussion_id}/pause
POST   /discussions/{discussion_id}/resume
POST   /discussions/{discussion_id}/stop
POST   /discussions/{discussion_id}/inject-question
GET    /discussions/{discussion_id}/messages

# Reports (报告生成)
GET    /discussions/{discussion_id}/report
GET    /reports/{report_id}
GET    /reports/{report_id}/export/{format}

# Analytics (P1/P2 features)
GET    /discussions/{discussion_id}/analytics
POST   /discussions/compare

# Teams (P2 feature)
GET    /teams
POST   /teams
GET    /teams/{team_id}
PATCH  /teams/{team_id}
DELETE /teams/{team_id}
POST   /teams/{team_id}/members
DELETE /teams/{team_id}/members/{user_id}
```

### 2.2 WebSocket API Design

**WebSocket Endpoint**: `wss://api.simfocus.com/v1/ws/discussions/{discussion_id}`

**Message Protocol (JSON):**

```javascript
// Client → Server
{
  "action": "subscribe" | "unsubscribe" | "control",
  "data": {
    "discussion_id": "uuid",
    "control_type": "pause" | "resume" | "speed" | "inject",
    "speed": 1.0 | 1.5 | 2.0 | 3.0,
    "question": "text"
  }
}

// Server → Client (Message Stream)
{
  "type": "message" | "status" | "error" | "progress",
  "data": {
    "message_id": "uuid",
    "character_id": "uuid",
    "character_name": "string",
    "content": "string",
    "round": 1,
    "phase": "opening" | "development" | "debate" | "closing",
    "timestamp": "ISO8601"
  }
}

// Server → Client (Discussion Status)
{
  "type": "status",
  "data": {
    "status": "initializing" | "running" | "paused" | "completed" | "failed",
    "current_round": 5,
    "total_rounds": 20,
    "current_phase": "development",
    "progress_percentage": 25
  }
}
```

### 2.3 API Design Best Practices

**Request/Response Format:**
```json
{
  "data": { /* actual response data */ },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601",
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100
    }
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Human-readable message",
      "field": "topic.title"
    }
  ]
}
```

**Error Codes:**
- `AUTHENTICATION_FAILED` - 401
- `AUTHORIZATION_FAILED` - 403
- `RESOURCE_NOT_FOUND` - 404
- `VALIDATION_ERROR` - 400
- `RATE_LIMIT_EXCEEDED` - 429
- `API_KEY_INVALID` - 400
- `DISCUSSION_LIMIT_REACHED` - 429
- `LLM_API_ERROR` - 502
- `INTERNAL_SERVER_ERROR` - 500

**Rate Limiting:**
- Authentication endpoints: 5 requests/minute per IP
- API mutation endpoints: 60 requests/minute per user
- Discussion creation: 10 discussions/hour per user
- WebSocket connections: 5 concurrent connections per user

---

## 3. Database Schema Recommendations

### 3.1 Core Tables

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL for OAuth-only users
    name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    auth_provider VARCHAR(50) DEFAULT 'email', -- 'email', 'google', 'github'
    provider_id VARCHAR(255), -- OAuth provider user ID
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP, -- Soft delete
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;

-- User API Keys (Encrypted storage)
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'custom'
    key_name VARCHAR(100),
    encrypted_key TEXT NOT NULL, -- AES-256 encrypted
    api_base_url TEXT, -- Custom endpoint URL
    default_model VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    UNIQUE(user_id, provider, key_name)
);

CREATE INDEX idx_api_keys_user_id ON user_api_keys(user_id);

-- Topics (议题)
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    context TEXT, -- Additional background information
    attachments JSONB, -- Array of file metadata
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'ready', 'in_discussion', 'completed'
    template_id UUID, -- If created from template
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_topics_status ON topics(status);
CREATE INDEX idx_topics_created_at ON topics(created_at DESC);

-- Characters (角色)
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL for system templates
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    is_template BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE, -- For P2 character marketplace
    -- Character configuration (JSONB for flexibility)
    config JSONB NOT NULL,
    /*
    config structure:
    {
      "age": 35,
      "gender": "female",
      "profession": "Product Manager",
      "personality": {
        "openness": 8,
        "rigor": 6,
        "critical_thinking": 9,
        "optimism": 5
      },
      "knowledge": {
        "fields": ["product_management", "ux_design"],
        "experience_years": 10,
        "representative_views": ["user-centric", "data-driven"]
      },
      "stance": "critical_exploration", -- 'support', 'oppose', 'neutral', 'critical_exploration'
      "expression_style": "formal", -- 'formal', 'casual', 'technical', 'storytelling'
      "behavior_pattern": "balanced" -- 'active', 'passive', 'balanced'
    }
    */
    usage_count INTEGER DEFAULT 0,
    rating_avg DECIMAL(3,2),
    rating_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_characters_user_id ON characters(user_id);
CREATE INDEX idx_characters_is_template ON characters(is_template) WHERE is_template = TRUE;
CREATE INDEX idx_characters_is_public ON characters(is_public) WHERE is_public = TRUE;

-- Discussions (讨论会话)
CREATE TABLE discussions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    discussion_mode VARCHAR(20) DEFAULT 'free', -- 'free', 'structured', 'creative', 'consensus'
    max_rounds INTEGER DEFAULT 20,
    status VARCHAR(20) DEFAULT 'initialized', -- 'initialized', 'running', 'paused', 'completed', 'failed', 'cancelled'
    current_round INTEGER DEFAULT 0,
    current_phase VARCHAR(20) DEFAULT 'opening', -- 'opening', 'development', 'debate', 'closing'
    llm_provider VARCHAR(50), -- Which API was used
    llm_model VARCHAR(100), -- Which model
    total_tokens_used INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10,4),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_discussions_user_id ON discussions(user_id);
CREATE INDEX idx_discussions_topic_id ON discussions(topic_id);
CREATE INDEX idx_discussions_status ON discussions(status);
CREATE INDEX idx_discussions_created_at ON discussions(created_at DESC);

-- Discussion Participants (讨论参与者)
CREATE TABLE discussion_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discussion_id UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id),
    position INTEGER NOT NULL, -- Order for structured debates
    stance VARCHAR(20), -- For structured mode: 'pro', 'con', 'neutral'
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(discussion_id, character_id)
);

CREATE INDEX idx_participants_discussion_id ON discussion_participants(discussion_id);

-- Discussion Messages (讨论消息)
CREATE TABLE discussion_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discussion_id UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    participant_id UUID NOT NULL REFERENCES discussion_participants(id) ON DELETE CASCADE,
    round INTEGER NOT NULL,
    phase VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    is_injected_question BOOLEAN DEFAULT FALSE, -- User-injected question
    parent_message_id UUID REFERENCES discussion_messages(id), -- For threading
    metadata JSONB, -- Additional data like sentiment, topics, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    -- Full-text search
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX idx_messages_discussion_id ON discussion_messages(discussion_id);
CREATE INDEX idx_messages_discussion_round ON discussion_messages(discussion_id, round);
CREATE INDEX idx_messages_created_at ON discussion_messages(created_at);
CREATE INDEX idx_messages_tsv ON discussion_messages USING GIN(tsv);

-- Reports (报告)
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discussion_id UUID NOT NULL UNIQUE REFERENCES discussions(id) ON DELETE CASCADE,
    -- Report sections (JSONB for flexible structure)
    overview JSONB,
    viewpoints_summary JSONB, -- Array of character viewpoints
    consensus JSONB,
    controversies JSONB, -- Array of disagreement points
    insights JSONB,
    recommendations JSONB,
    full_transcript_citation TEXT, -- Reference to messages
    -- Quality metrics
    quality_scores JSONB,
    /*
    {
      "depth_score": 75,
      "diversity_score": 82,
      "constructive_score": 68,
      "coherence_score": 80
    }
    */
    generation_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_discussion_id ON reports(discussion_id);

-- Share Links (分享链接)
CREATE TABLE share_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discussion_id UUID NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slug VARCHAR(20) UNIQUE NOT NULL, -- Short URL slug
    password_hash VARCHAR(255), -- NULL if no password
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_share_links_slug ON share_links(slug);
CREATE INDEX idx_share_links_discussion_id ON share_links(discussion_id);

-- Audit Log (审计日志)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'discussion_created', 'api_key_added', etc.
    resource_type VARCHAR(50), -- 'discussion', 'topic', 'character'
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

### 3.2 Data Partitioning Strategy

**For MVP:**
- No partitioning needed
- Use indexes strategically
- Implement soft deletes for data retention

**For Scale (P1/P2):**
- Partition `discussion_messages` by `created_at` (monthly partitions)
- Partition `audit_logs` by `created_at` (monthly partitions)
- Consider time-series database for analytics if query patterns warrant it

### 3.3 Caching Strategy

**Redis Cache Layers:**

1. **Session Cache** (TTL: 24 hours)
   - Key: `session:{session_id}`
   - Value: User session data, CSRF tokens

2. **User Profile Cache** (TTL: 1 hour)
   - Key: `user:{user_id}:profile`
   - Value: User profile, preferences

3. **API Keys Cache** (TTL: 1 hour, encrypted)
   - Key: `user_api_keys:{user_id}`
   - Value: Active API keys (decrypted in memory only)

4. **Discussion State Cache** (TTL: Duration of discussion)
   - Key: `discussion_state:{discussion_id}`
   - Value: Current round, phase, active participants

5. **Character Template Cache** (TTL: 24 hours)
   - Key: `character_template:{template_id}`
   - Value: Character configuration

6. **Rate Limiting** (TTL: Window duration)
   - Key: `ratelimit:{user_id}:{endpoint}`
   - Value: Request count

---

## 4. LLM Integration Strategy

### 4.1 Multi-Provider Architecture

**Abstract LLM Interface:**

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from dataclasses import dataclass

@dataclass
class LLMMessage:
    role: str  # 'system', 'user', 'assistant'
    content: str
    metadata: Optional[dict] = None

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Optional[dict] = None

class BaseLLMProvider(ABC):
    def __init__(self, api_key: str, api_base: Optional[str] = None):
        self.api_key = api_key
        self.api_base = api_base or self.default_base_url

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
```

**Implementation Examples:**

```python
class OpenAIProvider(BaseLLMProvider):
    default_base_url = "https://api.openai.com/v1"

    async def generate(self, messages, model, temperature=0.7, max_tokens=2000, stream=False):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                tokens_used=data["usage"]["total_tokens"],
                finish_reason=data["choices"][0]["finish_reason"]
            )

class AnthropicProvider(BaseLLMProvider):
    default_base_url = "https://api.anthropic.com"

    async def generate(self, messages, model, temperature=0.7, max_tokens=2000, stream=False):
        # Anthropic-specific implementation
        # Note: Anthropic requires different message format
        pass
```

### 4.2 Prompt Engineering Architecture

**Prompt Template System:**

```python
class PromptTemplate:
    def __init__(self, template_name: str, version: str = "v1"):
        self.template_name = template_name
        self.version = version
        self._load_template()

    def _load_template(self):
        # Load from database or file system
        # Support A/B testing different prompt versions
        pass

    def format(self, **kwargs) -> str:
        pass

class DiscussionPromptManager:
    def __init__(self, template_store):
        self.templates = template_store

    def get_character_system_prompt(
        self,
        character: dict,
        topic: str,
        context: dict
    ) -> str:
        """Generate system prompt for a character"""
        template = self.templates.get("character_system")
        return template.format(
            character_name=character["name"],
            profession=character["profession"],
            personality=self._format_personality(character["personality"]),
            knowledge=character["knowledge"],
            stance=character["stance"],
            expression_style=character["expression_style"],
            topic=topic,
            context=context
        )

    def get_discussion_prompt(
        self,
        phase: str,
        round: int,
        topic: str,
        previous_messages: list,
        current_character: dict,
        other_characters: list
    ) -> str:
        """Generate discussion prompt based on phase and context"""
        template = self.templates.get(f"discussion_{phase}")
        return template.format(
            round=round,
            topic=topic,
            previous_summary=self._summarize_previous(previous_messages),
            current_character=current_character,
            other_characters=other_characters,
            phase_instructions=self._get_phase_instructions(phase)
        )
```

**Sample Prompt Template:**

```jinja2
# character_system_v1.j2

You are {{ character_name }}, a {{ age }}-year-old {{ profession }} with {{ experience_years }} years of experience.

## Your Personality
- Openness: {{ personality.openness }}/10
- Intellectual Rigor: {{ personality.rigor }}/10
- Critical Thinking: {{ personality.critical_thinking }}/10
- Optimism: {{ personality.optimism }}/10

## Your Knowledge Base
- Primary Fields: {{ knowledge.fields|join(', ') }}
- Representative Views: {{ knowledge.representative_views|join('; ') }}

## Your Stance on this Topic
{{ stance_description }}

## Your Expression Style
You communicate in a {{ expression_style }} manner.

## Important Guidelines
1. Stay in character at all times
2. Draw from your knowledge base but acknowledge limitations
3. Be respectful but don't shy away from disagreement
4. Support your arguments with reasoning, not just assertions
5. Reference previous points made by other participants when responding
6. Keep responses concise (100-500 words)

## The Discussion Topic
{{ topic }}

{% if context %}
## Additional Context
{{ context }}
{% endif %}

Remember: You are participating in a focus group discussion. The goal is to explore this topic from multiple perspectives, not to "win" arguments.
```

### 4.3 Error Handling and Retry Strategy

**Retry Configuration:**

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import httpx

class LLMError(Exception):
    base class for LLM errors

class RateLimitError(LLMError):
    pass

class AuthenticationError(LLMError):
    pass

class ContextLengthError(LLMError):
    pass

class LLMService:
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def call_llm_with_retry(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        try:
            return await self.provider.generate(messages, **kwargs)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Rate limit - extract retry-after
                retry_after = e.response.headers.get('Retry-After', 60)
                raise RateLimitError(f"Rate limited. Retry after {retry_after}s")

            elif e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")

            elif e.response.status_code == 400:
                error_detail = e.response.json()
                if 'context_length' in str(error_detail).lower():
                    raise ContextLengthError("Input too long")
                raise

            # Don't retry 4xx errors except 429
            if 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                raise LLMError(f"LLM API error: {e.response.status_code}")

            # Retry 5xx errors
            raise

        except Exception as e:
            raise LLMError(f"Unexpected LLM error: {str(e)}")
```

**Circuit Breaker Pattern:**

```python
from pybreaker import CircuitBreaker

llm_circuit_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60
)

@llm_circuit_breaker
async def call_llm_protected(messages, **kwargs):
    return await llm_service.call_llm_with_retry(messages, **kwargs)
```

### 4.4 Cost Management

**Token Tracking and Budgeting:**

```python
class TokenBudgetManager:
    def __init__(self, user_id: str, discussion_id: str):
        self.user_id = user_id
        self.discussion_id = discussion_id
        self.max_budget_usd = self._get_user_budget()
        self.spent_usd = 0.0

    async def check_budget(self, estimated_tokens: int) -> bool:
        estimated_cost = self._estimate_cost(estimated_tokens)
        return (self.spent_usd + estimated_cost) <= self.max_budget_usd

    async def record_usage(self, tokens_used: int, model: str):
        cost = self._calculate_cost(tokens_used, model)
        self.spent_usd += cost
        await self._persist_usage(tokens_used, model, cost)

    def _calculate_cost(self, tokens: int, model: str) -> float:
        # Pricing per 1K tokens (as of 2026)
        pricing = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.001,
            "claude-3-opus": 0.015,
            "claude-3-5-sonnet": 0.003
        }
        return (tokens / 1000) * pricing.get(model, 0.01)
```

**Optimization Strategies:**

1. **Context Window Optimization:**
   - Implement sliding window for long discussions
   - Summarize old rounds instead of including full transcript
   - Use semantic similarity to select most relevant previous messages

2. **Model Selection:**
   - Use cheaper models (GPT-3.5) for initial rounds
   - Upgrade to better models for summary/insight generation
   - Allow user to configure quality vs cost preference

3. **Caching:**
   - Cache similar discussion starts
   - Cache character introductions
   - Implement smart cache invalidation

---

## 5. Real-time Communication Approach

### 5.1 WebSocket Architecture

**Connection Management:**

```python
from fastapi import WebSocket
from typing import Dict
import asyncio

class ConnectionManager:
    def __init__(self):
        # discussion_id -> {user_id: WebSocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Redis for multi-server support
        self.redis_pubsub = None

    async def connect(self, discussion_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if discussion_id not in self.active_connections:
            self.active_connections[discussion_id] = {}
        self.active_connections[discussion_id][user_id] = websocket

        # Notify others of new participant
        await self.broadcast_to_discussion(
            discussion_id,
            {
                "type": "participant_joined",
                "data": {"user_id": user_id}
            },
            exclude_user_id=user_id
        )

    async def disconnect(self, discussion_id: str, user_id: str):
        if discussion_id in self.active_connections:
            self.active_connections[discussion_id].pop(user_id, None)

            # Notify others
            await self.broadcast_to_discussion(
                discussion_id,
                {
                    "type": "participant_left",
                    "data": {"user_id": user_id}
                }
            )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_discussion(
        self,
        discussion_id: str,
        message: dict,
        exclude_user_id: str = None
    ):
        # Local broadcast
        if discussion_id in self.active_connections:
            for user_id, connection in self.active_connections[discussion_id].items():
                if exclude_user_id and user_id == exclude_user_id:
                    continue
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to user {user_id}: {e}")

        # Redis pub/sub for multi-server
        if self.redis_pubsub:
            await self.redis_pubsub.publish(
                f"discussion:{discussion_id}",
                json.dumps(message)
            )

manager = ConnectionManager()
```

**WebSocket Endpoint:**

```python
@router.websocket("/ws/discussions/{discussion_id}")
async def discussion_websocket(
    websocket: WebSocket,
    discussion_id: str,
    token: str,  # JWT token from query param
    current_user: User = Depends(verify_websocket_token)
):
    # Verify user has access to this discussion
    discussion = await discussion_service.get_discussion(discussion_id)
    if not discussion or discussion.user_id != current_user.id:
        await websocket.close(code=1003, reason="Access denied")
        return

    await manager.connect(discussion_id, str(current_user.id), websocket)

    try:
        while True:
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "subscribe":
                # Already connected, just confirm
                await manager.send_personal_message(
                    {"type": "status", "data": {"status": "subscribed"}},
                    websocket
                )

            elif action == "control":
                # Handle user controls
                control_type = data["data"]["control_type"]

                if control_type == "pause":
                    await discussion_engine.pause_discussion(discussion_id)

                elif control_type == "resume":
                    await discussion_engine.resume_discussion(discussion_id)

                elif control_type == "inject":
                    question = data["data"]["question"]
                    await discussion_engine.inject_question(
                        discussion_id,
                        question
                    )

    except WebSocketDisconnect:
        await manager.disconnect(discussion_id, str(current_user.id))
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(discussion_id, str(current_user.id))
```

### 5.2 Scaling WebSockets

**Multi-Server Architecture:**

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   (WebSocket    │
                    │    Aware)       │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │   WS     │   │   WS     │   │   WS     │
        │ Server 1 │   │ Server 2 │   │ Server 3 │
        └─────┬────┘   └─────┬────┘   └─────┬────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │  Redis Pub/Sub  │
                    │   (Topic:       │
                    │ discussion:*)   │
                    └─────────────────┘
```

**Redis Pub/Sub Implementation:**

```python
import aioredis
import json

class RedisPubSubManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.pubsub = None

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url)
        self.pubsub = self.redis.pubsub()

    async def publish(self, channel: str, message: dict):
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        await self.pubsub.subscribe(channel)

    async def listen(self, callback):
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await callback(data)
```

### 5.3 Message Flow for Discussion

**State Machine:**

```
┌─────────────┐
│ Initialized │
└──────┬──────┘
       │ User starts discussion
       ▼
┌─────────────┐
│   Running   │◄──────────────────┐
└──────┬──────┘                   │
       │                          │
       │ (Streaming messages)     │ User resumes
       │                          │
       ▼                          │
┌─────────────┐                   │
│   Paused    │───────────────────┘
└──────┬──────┘
       │ User stops / completes
       ▼
┌─────────────┐
│  Completed  │
└─────────────┘
       │
       ▼ (async)
┌─────────────┐
│ Generating  │
│   Report    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Report Ready│
└─────────────┘
```

---

## 6. Discussion Engine Implementation

### 6.1 Core Engine Architecture

```python
class DiscussionEngine:
    def __init__(
        self,
        llm_service: LLMService,
        prompt_manager: PromptTemplateManager,
        websocket_manager: ConnectionManager,
        db: Database
    ):
        self.llm = llm_service
        self.prompts = prompt_manager
        self.ws = websocket_manager
        self.db = db

    async def start_discussion(self, discussion_id: str):
        """Initialize and start a discussion"""

        # Load discussion data
        discussion = await self.db.get_discussion(discussion_id)
        topic = await self.db.get_topic(discussion.topic_id)
        participants = await self.db.get_participants(discussion_id)

        # Initialize state
        await self._initialize_discussion_state(discussion_id, participants)

        # Start the discussion loop
        asyncio.create_task(self._discussion_loop(discussion_id))

    async def _discussion_loop(self, discussion_id: str):
        """Main discussion orchestration loop"""

        state = await self._get_state(discussion_id)

        while state.status == "running" and state.current_round < state.max_rounds:
            # Check if paused
            if state.paused:
                await asyncio.sleep(1)
                continue

            # Determine phase
            phase = self._determine_phase(state.current_round, state.max_rounds)

            # Generate messages for this round
            for participant in state.participants:
                if state.paused:  # Check again for each participant
                    break

                # Skip if this participant shouldn't speak this round
                if not self._should_participant_speak(participant, state):
                    continue

                # Generate message
                message = await self._generate_message(
                    discussion_id,
                    participant,
                    phase,
                    state
                )

                # Broadcast via WebSocket
                await self.ws.broadcast_to_discussion(
                    discussion_id,
                    {
                        "type": "message",
                        "data": message
                    }
                )

                # Save to database
                await self.db.save_message(message)

                # Update state
                state.messages.append(message)
                await self._save_state(discussion_id, state)

                # Delay for pacing (except last in round)
                if participant != state.participants[-1]:
                    await asyncio.sleep(state.message_delay)

            # Move to next round
            state.current_round += 1
            await self._save_state(discussion_id, state)

            # Broadcast progress
            await self.ws.broadcast_to_discussion(
                discussion_id,
                {
                    "type": "progress",
                    "data": {
                        "current_round": state.current_round,
                        "total_rounds": state.max_rounds,
                        "progress_percentage": (state.current_round / state.max_rounds) * 100
                    }
                }
            )

        # Discussion complete
        await self._complete_discussion(discussion_id)

    async def _generate_message(
        self,
        discussion_id: str,
        participant: dict,
        phase: str,
        state: dict
    ) -> dict:
        """Generate a message for a specific participant"""

        # Build conversation history
        conversation_history = self._build_conversation_history(state)

        # Get character system prompt
        system_prompt = await self.prompts.get_character_system_prompt(
            character=participant.character,
            topic=state.topic,
            context=state.context
        )

        # Get discussion prompt
        discussion_prompt = await self.prompts.get_discussion_prompt(
            phase=phase,
            round=state.current_round,
            topic=state.topic,
            previous_messages=conversation_history,
            current_character=participant.character,
            other_characters=[p.character for p in state.participants if p.id != participant.id]
        )

        # Call LLM
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=discussion_prompt)
        ]

        response = await self.llm.call_llm_with_retry(
            messages=messages,
            model=state.model,
            temperature=participant.character.config["personality"].get("openness", 7) / 10
        )

        return {
            "id": str(uuid.uuid4()),
            "discussion_id": discussion_id,
            "participant_id": participant.id,
            "character_id": participant.character_id,
            "character_name": participant.character.name,
            "round": state.current_round,
            "phase": phase,
            "content": response.content,
            "token_count": response.tokens_used,
            "created_at": datetime.utcnow()
        }
```

### 6.2 Phase Management

**Phase Transitions:**

```python
class PhaseManager:
    PHASE_CONFIG = {
        "opening": {
            "rounds": (1, 2),
            "instructions": "Introduce yourself and share your initial perspective on this topic.",
            "min_rounds": 1,
            "max_rounds": 2
        },
        "development": {
            "rounds": (3, 10),
            "instructions": "Respond to previous points, deepen your arguments, and explore the topic further.",
            "min_rounds": 3,
            "max_rounds": 8
        },
        "debate": {
            "rounds": (11, 15),
            "instructions": "Identify points of disagreement and engage in constructive debate.",
            "min_rounds": 2,
            "max_rounds": 5
        },
        "closing": {
            "rounds": (16, 20),
            "instructions": "Summarize your position, identify common ground, and propose next steps.",
            "min_rounds": 1,
            "max_rounds": 2
        }
    }

    def determine_phase(self, current_round: int, max_rounds: int) -> str:
        """Determine which phase we're in based on round number"""

        # Dynamic phase allocation based on total rounds
        opening_end = max(2, int(max_rounds * 0.1))
        development_end = max(10, int(max_rounds * 0.5))
        debate_end = max(15, int(max_rounds * 0.8))

        if current_round <= opening_end:
            return "opening"
        elif current_round <= development_end:
            return "development"
        elif current_round <= debate_end:
            return "debate"
        else:
            return "closing"
```

### 6.3 Discussion Modes

**Mode Factory:**

```python
class DiscussionModeFactory:
    @staticmethod
    def create_mode(mode_type: str) -> BaseDiscussionMode:
        if mode_type == "free":
            return FreeDiscussionMode()
        elif mode_type == "structured":
            return StructuredDebateMode()
        elif mode_type == "creative":
            return CreativeDivergenceMode()
        elif mode_type == "consensus":
            return ConsensusBuildingMode()
        else:
            raise ValueError(f"Unknown discussion mode: {mode_type}")

class BaseDiscussionMode(ABC):
    @abstractmethod
    def should_participant_speak(self, participant: dict, state: dict) -> bool:
        pass

    @abstractmethod
    def get_speaking_order(self, participants: list, round: int) -> list:
        pass

class FreeDiscussionMode(BaseDiscussionMode):
    """Participants speak freely, system balances participation"""

    def should_participant_speak(self, participant: dict, state: dict) -> bool:
        # Everyone speaks each round in free mode
        return True

    def get_speaking_order(self, participants: list, round: int) -> list:
        # Rotate speaking order
        offset = (round - 1) % len(participants)
        return participants[offset:] + participants[:offset]

class StructuredDebateMode(BaseDiscussionMode):
    """Pro/con/neutral structured debate"""

    def should_participant_speak(self, participant: dict, state: dict) -> bool:
        # Alternating pro/con/neutral
        position_order = ["pro", "con", "neutral"]
        current_position = position_order[state.current_round % 3]
        return participant.stance == current_position

class CreativeDivergenceMode(BaseDiscussionMode):
    """'Yes, and' mode - no direct disagreement"""

    def get_phase_instructions(self, phase: str) -> str:
        base = super().get_phase_instructions(phase)
        return base + "\n\nIMPORTANT: Build on others' ideas. Start your responses with 'Yes, and...' or similar affirmative language. Avoid direct criticism."
```

---

## 7. Performance Optimization Suggestions

### 7.1 Database Optimization

**Indexing Strategy:**

```sql
-- Critical indexes for discussion queries
CREATE INDEX CONCURRENTLY idx_messages_discussion_round_phase
ON discussion_messages(discussion_id, round, phase);

CREATE INDEX CONCURRENTLY idx_discussions_user_status
ON discussions(user_id, status, created_at DESC);

-- Partial indexes for efficiency
CREATE INDEX idx_active_discussions
ON discussions(id, user_id, current_round)
WHERE status IN ('running', 'paused');

-- Covering index for common query pattern
CREATE INDEX idx_topics_user_status_created
ON topics(user_id, status, created_at DESC, title);
```

**Query Optimization:**

```python
# Use select/load for related data to avoid N+1
discussion = await Discussion.select(
    Discussion,
    Topic,
    User
).where(
    Discussion.id == discussion_id
).first()

# Pagination for large datasets
async def get_user_discussions(
    user_id: str,
    page: int = 1,
    per_page: int = 20
) -> PaginatedResult:
    offset = (page - 1) * per_page

    discussions = await Discussion.query.where(
        Discussion.user_id == user_id
    ).order_by(
        Discussion.created_at.desc()
    ).limit(per_page).offset(offset).gino.all()

    total = await db.func.count(Discussion.id).where(
        Discussion.user_id == user_id
    ).gino.scalar()

    return PaginatedResult(
        items=discussions,
        total=total,
        page=page,
        per_page=per_page
    )
```

### 7.2 Caching Layers

**Multi-level Caching:**

```python
class CacheStrategy:
    def __init__(self, redis: Redis, local_cache: TTLCache):
        self.redis = redis
        self.local = local_cache  # L1 cache (in-memory)

    async def get(self, key: str):
        # L1: Local cache (fastest)
        if key in self.local:
            return self.local[key]

        # L2: Redis cache (fast)
        value = await self.redis.get(key)
        if value:
            self.local[key] = value
            return json.loads(value)

        return None

    async def set(self, key: str, value: any, ttl: int = 3600):
        # Set both layers
        self.local[key] = value
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
```

**Cache Invalidation Strategy:**

```python
class DiscussionCache:
    def __init__(self, cache: CacheStrategy):
        self.cache = cache

    async def get_discussion(self, discussion_id: str) -> Optional[dict]:
        return await self.cache.get(f"discussion:{discussion_id}")

    async def invalidate_discussion(self, discussion_id: str):
        # Invalidate discussion and related caches
        await self.cache.redis.delete(f"discussion:{discussion_id}")
        await self.cache.redis.delete(f"discussion:{discussion_id}:messages")
        await self.cache.redis.delete(f"discussion:{discussion_id}:participants")
        await self.cache.redis.delete(f"user:discussions:{user_id}")  # List cache
```

### 7.3 Async Task Processing

**Background Job Architecture:**

```python
from celery import Celery

celery_app = Celery(
    'simfocus',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task(bind=True, max_retries=3)
def generate_report_task(self, discussion_id: str):
    """Generate report asynchronously"""
    try:
        report = report_service.generate_discussion_report(discussion_id)
        # Notify user via WebSocket or email
        websocket_manager.broadcast_to_discussion(
            discussion_id,
            {"type": "report_ready", "data": {"report_id": report.id}}
        )
        return report.id
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise self.retry(exc=e, countdown=60)

# Usage in API
@router.post("/discussions/{discussion_id}/stop")
async def stop_discussion(discussion_id: str):
    # Stop discussion synchronously
    await discussion_engine.stop(discussion_id)

    # Start report generation asynchronously
    generate_report_task.delay(discussion_id)

    return {"status": "Report generation started"}
```

### 7.4 Connection Pooling

**Database Connection Pool:**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/simfocus",
    pool_size=20,          # Number of connections to maintain
    max_overflow=10,       # Additional connections under load
    pool_timeout=30,       # Wait time for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Test connections before use
    echo=False
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**HTTP Client Pooling:**

```python
import httpx

# Global async HTTP client with connection pooling
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(60.0, connect=10.0),
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=5.0
    )
)
```

---

## 8. Identified Risks and Mitigations

### 8.1 Technical Risks

| Risk | Severity | Probability | Impact | Mitigation Strategy |
|------|----------|-------------|--------|---------------------|
| **LLM API rate limiting** | High | High | Discussion failures | Implement exponential backoff, support multiple providers, queue requests intelligently |
| **High token consumption costs** | High | Medium | Budget overruns | Implement token budgeting, optimize prompts, use cheaper models for initial rounds, cache similar discussions |
| **WebSocket connection drops** | Medium | High | Poor UX | Auto-reconnect with state recovery, heartbeat/ping mechanism, queue messages during disconnect |
| **Discussion quality degradation** | High | Medium | User churn | A/B test prompts, collect quality feedback, implement quality scoring, allow regeneration |
| **Database write bottlenecks** | Medium | Medium | Slow performance | Batch writes, use connection pooling, consider time-series DB for messages at scale |
| **Memory leaks in long discussions** | Medium | Low | Server crashes | Monitor memory usage, implement sliding window for context, periodic restarts |
| **Concurrent discussion limits** | Medium | Medium | Poor scalability | Horizontal scaling, stateless design where possible, Redis for shared state |

### 8.2 Security Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **API key exposure** | Critical | AES-256 encryption at rest, never log keys, use HSM for production, brief TTL in cache |
| **Injection attacks** | High | Parameterized queries, input validation, output encoding, WAF |
| **WebSocket hijacking** | Medium | Token-based auth, origin validation, rate limiting per connection |
| **DDoS on discussion endpoint** | Medium | Rate limiting, IP blocking, CAPTCHA for abuse detection |
| **Data breach** | Critical | Encryption at rest and in transit, regular security audits, minimal data collection |

### 8.3 Business Logic Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Characters speaking out of turn** | Poor UX | Strict state management, validation before sending messages |
| **Infinite discussion loops** | API cost overrun | Hard max round limit, timeout guards, manual kill switch |
| **Report generation failure** | User frustration | Retry with backoff, partial reports, error messages with next steps |
| **User abuse (inappropriate content)** | Legal/Reputation | Content moderation, user reporting, automated filtering, ban system |

### 8.4 Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Database connection exhaustion** | Outage | Pool sizing monitoring, circuit breakers, graceful degradation |
| **Redis failure** | WebSocket disconnect, cache miss | Redis Sentinel/Cluster, fallback to direct DB, read-through cache |
| **LLM provider outage** | Complete service failure | Multi-provider support, graceful degradation message, queue for retry |
| **Deployment downtime** | User churn | Blue-green deployments, health checks, auto-rollback |

---

## 9. Monitoring and Observability

### 9.1 Key Metrics to Track

**Application Metrics:**
- Discussion success rate (completed vs failed)
- Average discussion duration
- Message generation latency (p50, p95, p99)
- LLM API error rate (by provider)
- Token consumption (per user, per discussion)
- WebSocket connection duration
- Database query performance
- Cache hit rates

**Business Metrics:**
- Discussions created per day
- User retention (discussion repeat rate)
- Report generation success rate
- Character usage statistics
- API provider distribution

**Infrastructure Metrics:**
- CPU/memory utilization
- Database connection pool usage
- Redis memory usage
- Network I/O
- Disk usage

### 9.2 Logging Strategy

```python
import structlog

logger = structlog.get_logger()

# Structured logging with context
logger.info(
    "discussion_started",
    discussion_id=discussion.id,
    user_id=discussion.user_id,
    participant_count=len(participants),
    mode=discussion.discussion_mode,
    model=discussion.llm_model
)

logger.error(
    "llm_api_error",
    discussion_id=discussion_id,
    provider="openai",
    error_type="rate_limit_error",
    retry_attempt=attempt,
    error_message=str(e)
)
```

### 9.3 Distributed Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

def generate_message(discussion_id, participant):
    with tracer.start_as_current_span("generate_message") as span:
        span.set_attribute("discussion_id", discussion_id)
        span.set_attribute("participant_id", participant.id)

        with tracer.start_as_current_span("llm_api_call"):
            # LLM call
            pass
```

---

## 10. Questions for Clarification

### 10.1 Product Requirements

1. **Discussion Duration**: The PRD mentions 10-20 rounds but also time limits (10-60 minutes). Which is the primary constraint? Should discussions stop based on rounds or time?

2. **Multi-user Observation**: Should multiple users be able to watch the same discussion simultaneously (e.g., team members)? This affects WebSocket architecture and permissions.

3. **Discussion Reuse**: Can users "rerun" the same discussion with the same characters? This affects caching strategy.

4. **Character Personality Consistency**: How strict should the system be about maintaining character personality across rounds? This affects prompt complexity and token usage.

5. **Real Intervention vs Simulation**: When users "inject" a question, should characters respond naturally or is this a moderator intervention?

### 10.2 Technical Requirements

6. **LLM Provider Priority**: For MVP, should we prioritize OpenAI, Anthropic, or support both equally from day one?

7. **Streaming vs Batch**: Should messages stream character-by-character (like ChatGPT) or appear all at once? This affects UX and LLM API usage.

8. **Report Generation Timing**: Should reports generate immediately after discussion completes, or can this be a background job? The 10-second requirement may be difficult for long discussions.

9. **Vector Database Timing**: For the P2 character memory feature, do we need vector database from MVP or can we add it later?

10. **Cost Monitoring**: Should users get real-time cost warnings during discussions, or only at the end?

### 10.3 Operational Requirements

11. **Data Retention**: The PRD says 90 days for history, but what about actual discussion messages? Should they be deleted or archived?

12. **Geographic Distribution**: Should we plan for multi-region deployment from the start, or is single-region acceptable for MVP?

13. **Support Contact**: For technical issues with discussions, should there be a way for users to share discussion state with support?

14. **Analytics Data**: Can we use anonymized discussion data for product improvement, or must everything be deleted on user request?

15. **Rate Limiting Strategy**: Should rate limits be per-user, per-API-key, or both?

---

## 11. MVP Implementation Recommendations

### 11.1 Simplified MVP Architecture

For MVP, consider this simplified approach:

```
┌─────────────────────────────────────────────┐
│           Single FastAPI Application        │
│  (Auth + Topics + Characters + Discussions) │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌───────────┐ ┌──────────┐ ┌──────────┐
│PostgreSQL │ │  Redis   │ │ OpenAI   │
│           │ │          │ │   API    │
└───────────┘ └──────────┘ └──────────┘
```

**MVP Simplifications:**
1. Single LLM provider (OpenAI GPT-3.5-turbo or GPT-4)
2. Synchronous discussion generation (no WebSocket streaming for MVP)
3. Basic report generation (no visualizations)
4. No team features
5. No character memory
6. Simple round-robin discussion mode

### 11.2 MVP Development Priority Order

**Phase 1 (Weeks 1-2): Foundation**
- Database schema and migrations
- Authentication system
- Basic CRUD for users, topics, characters
- API key management

**Phase 2 (Weeks 3-4): Discussion Engine**
- LLM provider abstraction
- Prompt template system
- Basic discussion loop
- Message generation and storage

**Phase 3 (Weeks 5-6): Real-time and Reporting**
- WebSocket implementation
- Discussion controls (start/pause/stop)
- Basic report generation
- Frontend integration

**Phase 4 (Weeks 7-8): Polish and Testing**
- Error handling and retry logic
- Cost tracking
- Performance optimization
- End-to-end testing

### 11.3 Technical Debt to Accept for MVP

1. No caching (add in P1)
2. No message queue (add in P1 when adding async report generation)
3. Simple retry logic (enhance in P1)
4. No distributed tracing (add in P2)
5. Basic monitoring (add in P1)

---

## 12. Conclusion

The simFocus PRD describes an innovative product with significant backend complexity. The discussion engine is the most technically challenging component and deserves focused engineering effort.

### Critical Success Factors:

1. **Robust LLM Integration**: Multi-provider support, comprehensive error handling, and cost management
2. **Scalable Real-time Communication**: WebSocket architecture that can scale horizontally
3. **State Management**: Clear discussion state machine with recovery mechanisms
4. **Performance**: Meeting the latency requirements through caching and async processing
5. **Security**: Protecting user API keys and preventing abuse

### Recommended Next Steps:

1. **Technical Spike**: Prototype the discussion engine with a simple 2-character, 5-round discussion
2. **Performance Testing**: Validate LLM API latency and streaming behavior
3. **Cost Analysis**: Model the per-discussion API costs for different configurations
4. **Architecture Review**: Review this document with the engineering team and adjust based on team expertise
5. **Proof of Concept**: Build a minimal end-to-end demo before full MVP development

The proposed architecture is designed to support the MVP while providing a clear path to scale. By following the recommendations in this review, the team can build a robust, scalable backend for the simFocus platform.

---

**Document End**

For questions or clarifications regarding this review, please contact the backend architecture team.
