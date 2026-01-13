# Notes: simFocus Development

## Project Reference

### Document Location
- PRD v1.1: `/root/projects/simFocus/docs/PRD_v1.1.md`
- Task Plan: `/root/projects/simFocus/task_plan.md`

### PRD Summary

**Product**: simFocus - AI Virtual Focus Group Platform

**Core Value**: Multi-perspective collision through AI character discussions

**Target Users**:
1. Product Managers - Quick product validation
2. Independent Researchers - Academic exploration
3. Startup Founders - Business model stress testing

---

## Technical Architecture Overview

### System Layers
```
Client (Vue 3 + Socket.IO)
         ↓ HTTPS/WSS
API Gateway (FastAPI + JWT)
         ↓
Services (User, Character, Topic, Discussion, Report, LLM Orchestrator)
         ↓
External APIs (OpenAI, Anthropic, Custom)
Data (PostgreSQL, Redis)
```

### Core Services
| Service | Responsibility |
|---------|----------------|
| User Service | Auth, profile, API key encryption |
| Topic Service | Topic CRUD, templates, drafts |
| Character Service | Templates, custom characters, ratings |
| Discussion Engine | Multi-character orchestration, state machine |
| LLM Orchestrator | Multi-provider abstraction, retry, rate limiting |
| Report Generator | Summary, insights, export |

---

## Database Schema Summary

### Core Tables
- `users` - User accounts and profiles
- `user_api_keys` - Encrypted API keys
- `topics` - Discussion topics
- `characters` - Character templates and custom characters
- `discussions` - Discussion sessions
- `discussion_participants` - Characters in each discussion
- `discussion_messages` - Individual messages
- `reports` - Generated reports
- `share_links` - Shared discussion links
- `audit_logs` - Audit trail

### Key Indexes
- `users(email)`
- `user_api_keys(user_id)`
- `topics(user_id, status)`
- `characters(user_id, is_template)`
- `discussions(user_id, status)`
- `discussion_messages(discussion_id, round)`
- `discussion_messages(tsv)` - Full-text search

---

## API Endpoint Summary

### Authentication
```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/verify-email
POST   /auth/forgot-password
POST   /auth/reset-password
```

### Users
```
GET    /users/me
PATCH  /users/me
GET    /users/me/api-keys
POST   /users/me/api-keys
DELETE /users/me/api-keys/{key_id}
PATCH  /users/me/api-keys/{key_id}
```

### Topics
```
GET    /topics
POST   /topics
GET    /topics/{topic_id}
PATCH  /topics/{topic_id}
DELETE /topics/{topic_id}
POST   /topics/{topic_id}/duplicate
```

### Characters
```
GET    /characters
POST   /characters
GET    /characters/{character_id}
PATCH  /characters/{character_id}
DELETE /characters/{character_id}
GET    /characters/templates
POST   /characters/from-template
POST   /characters/{character_id}/rate
```

### Discussions
```
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
```

### WebSocket
```
wss://api.simfocus.com/v1/ws/discussions/{discussion_id}?token={jwt}
```

---

## Discussion Phases

### Phase 1: Opening (1-2 rounds)
- Characters introduce themselves
- State initial positions

### Phase 2: Development (3-8 rounds)
- Characters respond to each other
- Deep arguments

### Phase 3: Debate (2-5 rounds)
- Target disagreements
- Focused交锋

### Phase 4: Closing (1-2 rounds)
- Summarize viewpoints
- Attempt consensus

---

## Character Config Structure

```json
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
  "stance": "critical_exploration",
  "expression_style": "formal",
  "behavior_pattern": "balanced"
}
```

---

## Redis Cache Keys

| Pattern | Purpose | TTL |
|---------|---------|-----|
| `session:{session_id}` | User session | 24h |
| `user:{user_id}:profile` | User profile | 1h |
| `user_api_keys:{user_id}` | API keys (encrypted) | 1h |
| `discussion_state:{discussion_id}` | Active discussion | Duration+1h |
| `character_template:{template_id}` | Character template | 24h |
| `ratelimit:{user_id}:{endpoint}` | Rate limiting | Window |
| `ws_connections:{discussion_id}:{user_id}` | WebSocket tracking | Connection |

---

## Security Requirements

- API Key Encryption: AES-256-GCM
- Transmission: HTTPS/WSS (TLS 1.3)
- JWT Token: 24-hour expiration
- Password: bcrypt hashing
- Rate limiting per endpoint

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Response Time | < 2s (excluding LLM) |
| First Message | < 10s |
| Message Generation | 5-10s |
| Report Generation | < 10s |
| API Success Rate | > 99% |
| Concurrent Users | 1000+ (MVP) |

---

## MVP Success Criteria

- 50 seed users
- Completion rate > 70%
- User satisfaction > 3.5/5
- Weekly Active Discussions: 100 (Month 1)
