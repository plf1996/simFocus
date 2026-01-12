# Software Architecture Review
# AI Virtual Focus Group Platform - simFocus

**Document Version**: v1.0
**Review Date**: 2026-01-12
**Reviewer**: Software Architect
**Reviewed Document**: PRD v1.0 (2026-01-09)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Recommendations](#architecture-recommendations)
3. [Technology Stack Suggestions](#technology-stack-suggestions)
4. [Scalability Considerations](#scalability-considerations)
5. [Data Architecture Recommendations](#data-architecture-recommendations)
6. [Security Architecture Considerations](#security-architecture-considerations)
7. [Integration Patterns](#integration-patterns)
8. [Identified Risks and Mitigations](#identified-risks-and-mitigations)
9. [Questions for Clarification](#questions-for-clarification)
10. [Recommendations for MVP](#recommendations-for-mvp)

---

## Executive Summary

This review examines the Product Requirements Document (PRD) for simFocus, an AI-powered virtual focus group platform, from a software architecture perspective. The platform aims to enable multi-character AI-driven discussions with real-time observation capabilities.

### Overall Assessment

**Strengths:**
- Well-defined product scope with clear user personas and use cases
- Thoughtful prioritization using RICE framework
- Strong privacy-first approach (user-provided API keys)
- Clear phased delivery roadmap

**Critical Architecture Gaps:**
- No system architecture design or component interaction patterns defined
- Technology stack mentioned but not justified with architectural reasoning
- Missing data architecture design for discussion state management
- No clear strategy for real-time WebSocket scaling
- Absence of error handling and recovery strategies
- Limited discussion on API abstraction layer for multiple LLM providers

**Recommendation Priority:**
The PRD should be supplemented with a dedicated System Architecture Document (SAD) and Data Architecture Document (DAD) before implementation begins.

---

## Architecture Recommendations

### 1. Overall System Architecture

The PRD lacks a comprehensive system architecture design. Based on the requirements, the following architecture pattern is recommended:

```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
|   Web Client      |<--->|   API Gateway     |<--->|   LLM Provider    |
|  (Vue.js + WS)    |     |  (FastAPI + Auth) |     |   (User's Key)    |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
                                |    ^
                                v    |
                       +-------------------+
                       |                   |
                       |  Core Services    |
                       |                   |
                       +-------------------+
                          |         |
          +---------------+---------+---------------+
          |               |         |               |
+-------------------+ +-----------+ +-----------+ +-------------------+
|                   | |           | |           | |                   |
| Discussion Engine | | Character | |  Report   | |   User & API      |
|   Service         | |  Service  | | Generator | |   Management      |
|                   | |           | |           | |                   |
+-------------------+ +-----------+ +-----------+ +-------------------+
          |               |         |               |
          +---------------+---------+---------------+
                          |
                +-------------------+
                |                   |
                |  Data Layer       |
                |                   |
                +-------------------+
           |            |            |
+------------------+ +----------+ +------------------+
|                  | |          | |                  |
|   PostgreSQL     | |  Redis   | |  Vector DB       |
| (Relational)     | | (Cache)  | | (Character Mem)  |
|                  | |          | |                  |
+------------------+ +----------+ +------------------+
```

### 2. Core Component Architecture

#### 2.1 Discussion Engine Service (Most Critical)

**Responsibilities:**
- Orchestrate multi-character conversations
- Manage discussion state machine (phases: opening, developing, debating, concluding)
- Coordinate LLM API calls across multiple characters
- Handle streaming responses for real-time delivery

**Key Design Considerations:**
- Must be stateful for active discussions
- Requires robust error handling for LLM API failures
- Needs discussion state persistence for recovery

**Recommended Pattern:** Actor Model with discussion session actors

```python
# Pseudocode for Discussion Engine Architecture
class DiscussionSession:
    """
    Manages a single discussion session with state persistence
    """
    def __init__(self, discussion_id, config):
        self.state = DiscussionState(
            phase=Phase.OPENING,
            current_round=0,
            characters=[],
            conversation_history=[],
            metadata={}
        )
        self.character_clients = self._init_character_clients(config)

    async def run_discussion(self):
        """Main discussion orchestration loop"""
        while not self._is_complete():
            await self._run_round()
            await self._persist_state()

    async def _run_round(self):
        """Execute a single discussion round"""
        for character in self._determine_speaking_order():
            response = await self._generate_character_response(character)
            await self._broadcast_message(response)
```

#### 2.2 LLM Abstraction Layer

**Critical Need:** The PRD mentions supporting multiple LLM providers (OpenAI, Anthropic, OpenAI-compatible). An abstraction layer is essential.

```python
# Recommended LLM Provider Abstraction
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMRequest:
    messages: List[dict]
    temperature: float
    max_tokens: int
    stream: bool

@dataclass
class LLMResponse:
    content: str
    tokens_used: int
    model: str

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI implementation"""

class AnthropicProvider(LLMProvider):
    """Anthropic implementation"""

class OpenAICompatibleProvider(LLMProvider):
    """For local models, Ollama, etc."""

# Factory pattern
class LLMProviderFactory:
    @staticmethod
    def create(provider_type: str, config: dict) -> LLMProvider:
        # Returns appropriate provider instance
```

### 2.3 Real-time Communication Layer

**Requirement Analysis:**
- Real-time message streaming (5-10 seconds per message)
- Multiple concurrent discussions per user (potential future requirement)
- Pause/resume/seek controls

**Recommended Architecture:**

```
WebSocket Server (FastAPI + WebSocket)
    |
    +-- Connection Manager (per discussion session)
    |
    +-- Message Queue (Redis Pub/Sub for horizontal scaling)
    |
    +-- State Synchronization (Redis for active session state)
```

### 2.4 Report Generation Service

**Design Recommendation:**
- Separate async service that processes completed discussions
- Uses structured prompting for consistent report sections
- Implements template-based rendering for different formats (PDF, MD, JSON)

---

## Technology Stack Suggestions

### 3.1 Backend - FastAPI (Confirmed in CLAUDE.md)

**Justification:**
- Native async/await support for concurrent LLM calls
- Built-in WebSocket support
- Automatic API documentation (OpenAPI)
- Type hints for better code quality
- Pydantic for data validation

**Recommended Key Libraries:**

| Component | Library | Purpose |
|-----------|---------|---------|
| Web Framework | FastAPI | API and WebSocket server |
| ORM | SQLAlchemy 2.0 | Database access with async support |
| Validation | Pydantic v2 | Request/response validation |
| Async Runtime | asyncio | Core async support |
| Task Queue | Celery / dramatiq | Background jobs (report generation) |
| Caching | Redis | Session cache, pub/sub |
| HTTP Client | httpx | Async HTTP for LLM APIs |
| Vector DB | pgvector / Qdrant | Character memory retrieval |

### 3.2 Frontend - Vue.js 3 (Confirmed in CLAUDE.md)

**Justification:**
- Composition API for better code organization
- Pinia for state management (simpler than Vuex)
- Excellent TypeScript support
- Smaller bundle size compared to React

**Recommended Key Libraries:**

| Component | Library | Purpose |
|-----------|---------|---------|
| Framework | Vue 3 | Core framework |
| State | Pinia | Client state management |
| Router | Vue Router | Navigation |
| UI Components | Element Plus / Naive UI | Component library |
| WebSocket | Native WebSocket API | Real-time communication |
| HTTP Client | axios | REST API calls |
| Markdown | markdown-it | Report rendering |
| PDF Export | jsPDF | PDF generation |

### 3.3 Database Architecture

**PostgreSQL as Primary Database:**

**Justification:**
- ACID compliance for transactional data
- JSONB for flexible character configurations
- Full-text search capabilities
- pgvector extension for vector similarity (character memory)
- Proven reliability

**Recommended Schema Design:**

```sql
-- Core tables
users (id, email, password_hash, created_at, updated_at)
api_keys (id, user_id, provider, encrypted_key, created_at)
discussions (id, user_id, topic, status, config_jsonb, created_at, completed_at)
discussion_participants (id, discussion_id, character_config_jsonb, order_index)
discussion_messages (id, discussion_id, participant_id, round_number, content, metadata_jsonb, created_at)
reports (id, discussion_id, content_jsonb, format, created_at)
character_templates (id, name, category, config_jsonb, is_system)

-- Indexes
CREATE INDEX idx_discussions_user_id ON discussions(user_id);
CREATE INDEX idx_discussions_status ON discussions(status);
CREATE INDEX idx_messages_discussion_id ON discussion_messages(discussion_id);
CREATE INDEX idx_messages_created_at ON discussion_messages(created_at);
```

**Redis for Caching:**

**Use Cases:**
1. Active discussion session state
2. WebSocket connection tracking
3. Pub/sub for message broadcasting
4. Rate limiting
5. API key caching (encrypted)

### 3.4 Infrastructure Recommendations

| Component | Recommendation | Notes |
|-----------|---------------|-------|
| Containerization | Docker + Docker Compose | Local development |
| Reverse Proxy | Nginx | WebSocket support |
| Process Manager | systemd / supervisord | Production |
| Monitoring | Prometheus + Grafana | Metrics |
| Logging | ELK Stack or Loki | Log aggregation |
| CI/CD | GitHub Actions | Automated testing and deployment |

---

## Scalability Considerations

### 4.1 Current Requirements vs. Future Scale

**PRD Performance Targets:**
- Concurrent users: 1000+ (MVP)
- Response time: < 2s (excluding LLM API)
- Discussion completion: > 70%

**Bottleneck Analysis:**

| Component | Bottleneck Risk | Mitigation |
|-----------|-----------------|------------|
| WebSocket Connections | High (1000+ concurrent) | Connection pooling, Redis pub/sub for horizontal scaling |
| LLM API Calls | High (external dependency) | Request queuing, rate limiting, retry logic |
| Database Writes | Medium (message storage) | Batch writes, async persistence |
| Report Generation | Medium (CPU intensive) | Async worker pool, queue-based processing |

### 4.2 Horizontal Scaling Strategy

**Stateless Components (Easy to Scale):**
- API Gateway / REST endpoints
- Report Generation Service (queue-based)
- Static Assets (CDN)

**Stateful Components (Requires Strategy):**
- Discussion Engine Service
- WebSocket Server

**Recommended Approach for Stateful Services:**

1. **Sticky Sessions + Multiple Instances:**
   - Use nginx with ip_hash for WebSocket routing
   - Each discussion session pinned to specific backend instance
   - Limit: Maximum sessions per instance = memory / session_size

2. **Redis-backed State:**
   - Store discussion state in Redis
   - Any backend instance can handle any discussion
   - Enables true horizontal scaling

```python
# Redis-backed session management
class RedisBackedDiscussionSession:
    def __init__(self, discussion_id: str, redis_client):
        self.discussion_id = discussion_id
        self.redis = redis_client
        self.key = f"discussion:{discussion_id}"

    async def load_state(self) -> DiscussionState:
        data = await self.redis.get(self.key)
        return DiscussionState.model_validate_json(data)

    async def save_state(self, state: DiscussionState):
        await self.redis.setex(
            self.key,
            86400,  # 24 hours
            state.model_dump_json()
        )
```

### 4.3 LLM API Rate Limiting

**Challenge:** Multiple providers have different rate limits

**Recommended Solution:**

```python
class RateLimiter:
    """
    Multi-provider rate limiting with token bucket algorithm
    """
    def __init__(self):
        self.buckets = {
            'openai': TokenBucket(capacity=3000, refill_rate=60),  # GPT-4
            'anthropic': TokenBucket(capacity=5000, refill_rate=50),  # Claude
            'default': TokenBucket(capacity=1000, refill_rate=10)
        }

    async def acquire(self, provider: str, tokens: int):
        bucket = self.buckets.get(provider, self.buckets['default'])
        await bucket.acquire(tokens)
```

### 4.4 Caching Strategy

**Cache-able Data:**
1. Character templates (static, long cache)
2. User profile (moderate changes)
3. Completed discussion metadata (immutable)
4. API key validation status (short cache)

**Non-cacheable:**
1. Active discussion state
2. Real-time messages
3. User's own API keys

---

## Data Architecture Recommendations

### 5.1 Discussion State Management

**Critical Missing Design:** How to manage discussion state across phases and potential interruptions

**Recommended State Machine:**

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class DiscussionStatus(Enum):
    DRAFT = "draft"
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DiscussionPhase(Enum):
    OPENING = "opening"       # Round 1-2
    DEVELOPING = "developing" # Round 3-8
    DEBATING = "debating"     # Round 9-13
    CONCLUDING = "concluding" # Round 14-15

@dataclass
class DiscussionState:
    discussion_id: str
    status: DiscussionStatus
    phase: DiscussionPhase
    current_round: int
    total_rounds: int
    current_speaker_index: int
    conversation_history: List[ConversationMessage]
    last_message_at: Optional[datetime]
    error_count: int
    retry_count: int

    def can_transition_to(self, new_status: DiscussionStatus) -> bool:
        # Define valid state transitions
        valid_transitions = {
            DiscussionStatus.DRAFT: [DiscussionStatus.INITIALIZING],
            DiscussionStatus.INITIALIZING: [DiscussionStatus.IN_PROGRESS, DiscussionStatus.FAILED],
            DiscussionStatus.IN_PROGRESS: [DiscussionStatus.PAUSED, DiscussionStatus.COMPLETED, DiscussionStatus.FAILED],
            DiscussionStatus.PAUSED: [DiscussionStatus.IN_PROGRESS, DiscussionStatus.CANCELLED],
        }
        return new_status in valid_transitions.get(self.status, [])
```

### 5.2 Message Flow Architecture

**Real-time Message Flow:**

```
1. Discussion Engine generates message for Character A
2. Message persisted to database (async)
3. Message published to Redis Pub/Sub: discussion:{id}
4. WebSocket server receives via Pub/Sub subscription
5. WebSocket server pushes to connected client
6. Client renders message with typing animation
```

**Why Redis Pub/Sub:**
- Decouples message generation from delivery
- Enables horizontal scaling of WebSocket servers
- Multiple clients can observe same discussion (future feature)

### 5.3 Character Memory Architecture

**PRD mentions:** "Character evolution learning" (P2 feature)

**Recommended Implementation:**

```python
class CharacterMemory:
    """
    Vector-based memory retrieval for character consistency
    """
    def __init__(self, vector_db_client):
        self.db = vector_db_client
        self.collection = "character_memories"

    async def store_memory(
        self,
        discussion_id: str,
        character_id: str,
        content: str,
        metadata: dict
    ):
        embedding = await self._embed(content)
        await self.db.insert(
            collection=self.collection,
            documents=[{
                "discussion_id": discussion_id,
                "character_id": character_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata
            }]
        )

    async def retrieve_relevant(
        self,
        character_id: str,
        current_context: str,
        limit: int = 5
    ) -> List[str]:
        """Retrieve relevant past statements for context"""
        query_embedding = await self._embed(current_context)
        results = await self.db.search(
            collection=self.collection,
            vector=query_embedding,
            filter={"character_id": character_id},
            limit=limit
        )
        return [r["content"] for r in results]
```

### 5.4 Data Retention Strategy

**PRD Requirement:** "Retain discussion records for at least 90 days"

**Recommended Implementation:**

1. **Hot Storage (0-30 days):** PostgreSQL primary database
2. **Warm Storage (31-90 days):** PostgreSQL with read replica
3. **Cold Storage (90+ days):** Archive to S3-compatible storage (JSON format)

**Automated Cleanup:**
```python
async def cleanup_old_discussions():
    """Run daily to archive/delete old discussions"""
    cutoff_90_days = datetime.utcnow() - timedelta(days=90)

    # Archive to cold storage
    await archive_to_s3(
        cutoff_date=cutoff_90_days,
        destination="s3://simfocus-archive/discussions/"
    )

    # Delete from primary DB
    await delete_discussions_older_than(cutoff_90_days)
```

---

## Security Architecture Considerations

### 6.1 API Key Security (Critical)

**PRD Requirement:** "User-provided API keys, AES-256 encrypted storage"

**Security Architecture:**

```
Client Side
    |
    | (HTTPS only)
    v
Server Side
    |
    +-- API Key Encryption Service
    |   |
    |   +-- Input: User's API key (plaintext)
    |   +-- Encryption: AES-256-GCM
    |   +-- Key: Application secret (stored in env variable, not in code)
    |   +-- Output: Encrypted key (stored in DB)
    |
    v
Database (Encrypted at rest)
```

**Implementation Recommendation:**

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class APIKeyEncryption:
    """
    Service for encrypting/decrypting user API keys
    """
    def __init__(self, master_key: bytes):
        """
        Args:
            master_key: 32-byte key from environment variable
        """
        if len(master_key) != 32:
            raise ValueError("Master key must be 32 bytes")
        self.cipher = AESGCM(master_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt API key, return base64-encoded result"""
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = self.cipher.encrypt(nonce, plaintext.encode(), None)
        return base64.b64encode(nonce + ciphertext).decode()

    def decrypt(self, encrypted: str) -> str:
        """Decrypt encrypted API key"""
        data = base64.b64decode(encrypted)
        nonce, ciphertext = data[:12], data[12:]
        return self.cipher.decrypt(nonce, ciphertext, None).decode()
```

**Security Best Practices:**
1. Master key stored as environment variable, never in code
2. Different encryption keys per deployment (dev/staging/prod)
3. Rotate master keys annually with re-encryption
4. Log decryption operations (without logging the actual keys)
5. Consider using AWS KMS / HashiCorp Vault for production

### 6.2 Authentication & Authorization

**Recommended Implementation:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT-based authentication
class AuthService:
    def create_access_token(self, user_id: str) -> str:
        """Create JWT with short expiration"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def verify_token(self, token: str) -> str:
        """Verify and return user_id"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload["user_id"]
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

# WebSocket authentication
async def verify_ws_token(token: str) -> str:
    """Verify WebSocket connection token"""
    return AuthService().verify_token(token)

# Discussion ownership check
async def verify_discussion_access(
    discussion_id: str,
    user_id: str
) -> bool:
    """Verify user owns the discussion"""
    discussion = await get_discussion(discussion_id)
    return discussion.user_id == user_id
```

### 6.3 Content Moderation

**PRD Risk:** "User-generated inappropriate content"

**Recommended Architecture:**

```python
class ContentModerationService:
    """
    Multi-layer content moderation
    """
    def __init__(self):
        self.local_filters = self._load_local_filters()
        self.llm_moderator = None  # Optional LLM-based moderation

    async def check_topic(self, topic: str) -> ModerationResult:
        """Check topic before discussion starts"""
        # Layer 1: Local keyword filter (fast)
        if self._has_blocked_keywords(topic):
            return ModerationResult(blocked=True, reason="blocked_keyword")

        # Layer 2: Regex patterns
        if self._matches_blocked_patterns(topic):
            return ModerationResult(blocked=True, reason="pattern_match")

        # Layer 3: Optional LLM-based moderation (slower)
        if self.llm_moderator:
            result = await self.llm_moderator.check(topic)
            return result

        return ModerationResult(blocked=False)

    async def check_discussion_output(self, messages: List[str]):
        """Check generated messages for policy violations"""
        # Implement post-generation moderation
        pass
```

### 6.4 Rate Limiting

**Recommended Strategy:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Different limits for different endpoints
@app.post("/api/discussions/start")
@limiter.limit("10/hour")  # Start 10 discussions per hour
async def start_discussion(...):
    pass

@app.post("/api/characters")
@limiter.limit("100/hour")  # Create 100 characters per hour
async def create_character(...):
    pass

# WebSocket: limit concurrent discussions per user
class ConcurrentDiscussionLimiter:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.redis = Redis()

    async def acquire(self, user_id: str) -> bool:
        key = f"active_discussions:{user_id}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, 3600)  # 1 hour timeout
        return count <= self.max_concurrent

    async def release(self, user_id: str):
        key = f"active_discussions:{user_id}"
        await self.redis.decr(key)
```

---

## Integration Patterns

### 7.1 Frontend-Backend Integration

**Recommended API Structure:**

```
REST API (Stateless operations)
├── POST   /api/auth/register
├── POST   /api/auth/login
├── POST   /api/auth/logout
├── GET    /api/discussions
├── POST   /api/discussions
├── GET    /api/discussions/:id
├── PUT    /api/discussions/:id
├── DELETE /api/discussions/:id
├── GET    /api/discussions/:id/report
├── GET    /api/characters
├── POST   /api/characters
├── GET    /api/users/me
└── PUT    /api/users/me

WebSocket (Stateful operations)
├── WS /ws/discussions/:id
│   ├── connect (token)
│   ├── message (server → client: new character message)
│   ├── status (server → client: phase/round updates)
│   ├── pause (client → server)
│   ├── resume (client → server)
│   ├── insert_question (client → server)
│   └── error (server → client)
```

### 7.2 Error Handling Pattern

**Recommended Structure:**

```python
from pydantic import BaseModel

class APIError(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class ErrorCode:
    # Authentication errors
    INVALID_TOKEN = "AUTH_001"
    EXPIRED_TOKEN = "AUTH_002"

    # API Key errors
    INVALID_API_KEY = "API_KEY_001"
    API_KEY_QUOTA_EXCEEDED = "API_KEY_002"
    API_KEY_RATE_LIMITED = "API_KEY_003"

    # Discussion errors
    DISCUSSION_NOT_FOUND = "DISCUSSION_001"
    DISCUSSION_ALREADY_STARTED = "DISCUSSION_002"
    DISCUSSION_FAILED = "DISCUSSION_003"

    # LLM errors
    LLM_API_ERROR = "LLM_001"
    LLM_TIMEOUT = "LLM_002"
    LLM_RATE_LIMITED = "LLM_003"

# Exception handler
@app.exception_handler(DiscussionException)
async def discussion_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
```

### 7.3 LLM API Integration Pattern

**Recommended Abstraction with Retry Logic:**

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    """
    Robust LLM client with retry, timeout, and fallback
    """
    def __init__(self, provider: LLMProvider, api_key: str):
        self.provider = provider
        self.api_key = api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        timeout: float = 30.0
    ) -> str:
        try:
            return await asyncio.wait_for(
                self._do_generate(prompt),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"LLM call timed out after {timeout}s")
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise

    async def generate_stream(self, prompt: str):
        """Stream response for real-time display"""
        async for chunk in self.provider.stream(prompt):
            yield chunk
```

---

## Identified Risks and Mitigations

### 8.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **WebSocket connection instability** | High | Medium | Implement auto-reconnect with state resync; fallback to polling; use heartbeat/ping |
| **LLM API rate limiting during multi-character discussions** | High | Medium | Implement token bucket rate limiting; stagger character calls; support multiple providers |
| **Discussion state loss during server restart** | Medium | Low | Persist state to Redis after each round; implement recovery on restart |
| **Memory leaks from long-running discussion sessions** | Medium | Medium | Set session timeout; implement periodic state cleanup; monitor memory usage |
| **Slow report generation blocking user** | Medium | Medium | Make report generation async; send notification when ready; show loading state |

### 8.2 Architecture-Specific Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Monolithic Discussion Engine** | Single service handling all discussion logic may become bottleneck | Design for eventual microservices; keep clear boundaries; use async patterns |
| **Tight coupling to specific LLM providers** | Provider API changes could break system | Use abstraction layer; version API integrations; support OpenAI-compatible fallback |
| **No horizontal scaling for WebSocket** | Single-server WebSocket limits concurrent users | Use Redis Pub/Sub for message distribution; implement sticky sessions with health checks |
| **Database connection pool exhaustion** | High concurrent discussions may exhaust connections | Use connection pooling (SQLAlchemy); set appropriate pool size; use pgbouncer if needed |
| **Character prompt injection** | Malicious users could craft topics to bypass character constraints | Sanitize user input; use system/user message separation; validate character outputs |

### 8.3 Data Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Loss of discussion data** | High | Regular database backups; write-ahead logging; replicate to read replica |
| **API key exposure in logs** | Critical | Never log API keys; use structured logging with sanitization; audit log output |
| **Unauthorized access to discussions** | High | Implement proper ownership checks; use UUIDs instead of sequential IDs; audit access patterns |
| **GDPR compliance issues** | High | Implement data export; implement data deletion; maintain consent records |

---

## Questions for Clarification

### 9.1 Architecture & Design

1. **Discussion Recovery:** If a user's connection drops mid-discussion, should the discussion:
   - Continue running server-side?
   - Pause and wait for reconnection?
   - Allow state recovery on reconnect?

2. **Multi-user Observation:** Should future versions allow multiple users to observe the same discussion simultaneously (e.g., team watching together)?

3. **Discussion Forking:** Should users be able to "fork" a discussion at any point and explore different directions with the same characters?

4. **Character Identity:** How should characters maintain consistency if the same character is used across multiple discussions by the same user?

### 9.2 Performance & Scaling

5. **Acceptable Latency:** For the "first message" requirement of <10 seconds, does this include the time for:
   - Loading the discussion page?
   - Connecting WebSocket?
   - Generating the first character's message?

6. **Concurrent Discussions:** What is the expected maximum number of simultaneous discussions a single user might run?

7. **Message Persistence:** Should messages be persisted to database immediately or batched for performance?

### 9.3 Product & UX

8. **Discussion Interruption:** If a user inserts a question, should characters:
   - Finish current round first?
   - Interrupt immediately?
   - Insert at natural break point?

9. **Character Avatars:** Are dynamic character avatars (AI-generated) planned or static images only?

10. **Mobile Experience:** For the mobile "secondary" support, should it be:
    - Read-only observation of desktop-initiated discussions?
    - Full discussion creation capability?
    - Notification-driven when discussion updates?

### 9.4 Data & Privacy

11. **Data Analytics:** Can anonymized usage data be collected for product improvement?
    - Discussion topics?
    - Character configurations used?
    - Completion rates?

12. **API Key Storage:** Should users be able to:
    - Share API keys within a team?
    - Set spending limits per discussion?
    - Configure fallback keys?

### 9.5 Technical Implementation

13. **Vector Database:** Is the vector database (for character memory) planned for:
    - MVP (P0)?
    - P1 iteration?
    - P2 (character evolution)?

14. **Streaming vs Batch:** Should character responses:
    - Stream token-by-token (more engaging)?
    - Show after completion (simpler)?
    - Configurable per user?

15. **Deployment Target:** Where will the application be deployed:
    - User's local machine?
    - Cloud provider (which one)?
    - Self-hosted by users?

---

## Recommendations for MVP

### 10.1 MVP Architecture Simplification

For MVP (V1.0), recommend simplified architecture:

```
Single Deployment Unit
├── FastAPI Application
│   ├── REST API endpoints
│   ├── WebSocket server
│   ├── Discussion Engine (in-memory)
│   └── Background tasks
├── PostgreSQL Database
└── Redis (optional, can start without)
```

**Rationale:**
- Minimize infrastructure complexity
- Single server can handle 1000 concurrent users with proper optimization
- Add Redis Pub/Sub for WebSocket scaling when needed (post-MVP)

### 10.2 MVP Feature Prioritization

Based on architectural complexity, recommend adjusting priorities:

| Feature | Current Priority | Recommended Priority | Reason |
|---------|------------------|---------------------|--------|
| Real-time streaming | P0 | P0 | Core experience |
| Pause/resume | P1 | P0 | Simple to implement with in-memory state |
| Insert question | P1 | P1 | Moderate complexity |
| Accelerate playback | P1 | P2 | Requires caching completed discussion |
| Character memory (vector DB) | P2 | P2 | Complex infrastructure |
| Multiple LLM providers | P1 | P0 | Requires abstraction layer anyway |
| Report export PDF | P1 | P2 | PDF generation is complex |
| Report export Markdown | P1 | P1 | Simple to implement |
| Share links | P1 | P2 | Requires public view infrastructure |

### 10.3 MVP Technical Decisions

**Make These Decisions Before Implementation:**

1. **Discussion State Persistence:** In-memory for MVP, with Redis fallback
2. **Message Delivery:** WebSocket primary, HTTP polling fallback
3. **Character Prompt Strategy:** Single prompt with full conversation history
4. **Rate Limiting:** In-memory for MVP, Redis for production
5. **Database Migrations:** Alembic for PostgreSQL schema management

### 10.4 Post-MVP Evolution Path

```
Phase 1 (MVP)
└── Single server, in-memory state

Phase 2 (V1.1)
├── Add Redis for state persistence
├── Add rate limiting
└── Implement LLM provider abstraction

Phase 3 (V1.2)
├── Add Redis Pub/Sub for WebSocket scaling
├── Separate report generation worker
└── Add monitoring stack

Phase 4 (V2.0)
├── Microservice considerations
├── Vector database for character memory
└── Team collaboration features
```

---

## Conclusion

The simFocus PRD presents a well-structured product vision with clear user needs and feature prioritization. However, from a software architecture perspective, several critical design decisions need to be made before implementation:

**Immediate Next Steps:**
1. Design the system architecture with clear component boundaries
2. Implement the LLM provider abstraction layer first
3. Design the discussion state machine and persistence strategy
4. Plan the WebSocket scaling approach
5. Define the API key security implementation

**Critical Success Factors:**
- Robust error handling for LLM API failures
- Smooth real-time user experience despite LLM latency
- Clean abstraction for multi-provider support
- Secure API key handling

**Architecture Documents Needed:**
1. System Architecture Document (SAD)
2. Data Architecture Document (DAD)
3. API Specification (OpenAPI)
4. Security Architecture Document

The technology choices (Vue.js 3 + FastAPI + PostgreSQL) are appropriate for this use case and should provide a solid foundation for building the product.

---

*This review was prepared based on PRD v1.0 dated 2026-01-09. All recommendations should be validated with the product and engineering teams before implementation.*
