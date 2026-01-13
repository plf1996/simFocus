# Task Plan: simFocus MVP Development

## Goal
Build an AI-powered virtual focus group platform (simFocus) MVP that enables users to create discussion topics, configure AI characters, run multi-character discussions, and generate insight reports.

## Current Status
- **Phase**: Phase 1-3 Complete - Foundation, Core Backend, Core Frontend
- **Progress**: 75% - P0 MVP features mostly implemented
- **Last Updated**: 2026-01-12

## Completed Work
- [x] Architecture design document created (`docs/architecture_design.md`)
- [x] Project structure decision: Monorepo approach
- [x] Directory structure defined
- [x] Backend architecture design completed (`docs/backend_design.md`)
- [x] Frontend architecture design completed (`docs/frontend_design.md`)
- [x] Backend foundation implemented (config, db, security, utils)
- [x] Database models implemented (9 models with Alembic migration)
- [x] Pydantic schemas implemented (7 schema files)
- [x] API routes implemented (auth, users, topics, characters, discussions)
- [x] Service layer implemented (6 services with full business logic)
- [x] API routes connected to services (full backend integration complete)
- [x] Frontend foundation implemented (Vue 3 + Vite + TypeScript + Pinia)
- [x] Shared types defined
- [x] Pinia stores, Router, WebSocket, API services, utils completed
- [x] Common components (8): AppButton, AppInput, AppCard, AppModal, AppLoading, AppAvatar, AppSelect, AppTextarea
- [x] Layout components (4): MainLayout, AppHeader, AppSidebar, AppFooter
- [x] Auth components (3): LoginForm, RegisterForm, ForgotPassword
- [x] Topic components (4): TopicForm, TopicCard, TopicList, TopicTemplate
- [x] Character components (5): CharacterCard, CharacterSelector, CharacterEditor, CharacterPreview, CharacterLibrary
- [x] Discussion components (7): DiscussionRoom, MessageList, MessageBubble, CharacterPanel, DiscussionControls, ProgressBar, PhaseIndicator

## Technology Stack (Confirmed)
- **Frontend**: Vue 3 + TypeScript + Pinia + Socket.IO Client
- **Backend**: FastAPI + Python 3.11+
- **Database**: PostgreSQL + Redis
- **WebSocket**: Socket.IO
- **Deployment**: Docker + Docker Compose

## Phases

### [ ] Phase 1: Project Foundation Setup
**Status**: Pending
**Duration**: ~3-5 days

- [ ] Create monorepo structure
  - [ ] Backend directory structure
  - [ ] Frontend directory structure
  - [ ] Docker configuration
  - [ ] Shared types package
- [ ] Configure development environment
  - [ ] Docker Compose for local development
  - [ ] PostgreSQL + Redis containers
  - [ ] Environment configuration
- [ ] Set up version control
  - [ ] .gitignore files
  - [ ] Commit conventions
  - [ ] Pre-commit hooks (optional)

### [ ] Phase 2: Backend Core Infrastructure
**Status**: Pending
**Duration**: ~5-7 days

- [ ] Database schema implementation
  - [ ] SQLAlchemy models
  - [ ] Alembic migrations
  - [ ] Seed data (preset characters)
- [ ] Authentication system
  - [ ] JWT implementation
  - [ ] User registration/login endpoints
  - [ ] Password hashing
  - [ ] OAuth integration (Google/GitHub) - P1
- [ ] API key encryption/decryption
  - [ ] AES-256-GCM implementation
  - [ ] Secure storage service
- [ ] Base API structure
  - [ ] FastAPI app setup
  - [ ] CORS middleware
  - [ ] Request validation (Pydantic)
  - [ ] Error handlers

### [ ] Phase 3: Backend Service Layer
**Status**: Pending
**Duration**: ~7-10 days

- [ ] User Service
  - [ ] Profile management
  - [ ] API key CRUD
  - [ ] Usage statistics
- [ ] Topic Service
  - [ ] Topic CRUD operations
  - [ ] Draft management
  - [ ] Search and filtering
- [ ] Character Service
  - [ ] Character templates (50 preset)
  - [ ] Custom character CRUD
  - [ ] Character rating system
- [ ] Report Service
  - [ ] Report generation
  - [ ] Export functionality (PDF/Markdown)
- [ ] LLM Orchestrator
  - [ ] OpenAI integration
  - [ ] Anthropic integration
  - [ ] Rate limiting
  - [ ] Retry logic

### [ ] Phase 4: Discussion Engine (Core)
**Status**: Pending
**Duration**: ~10-14 days

- [ ] Discussion state machine
  - [ ] Status transitions
  - [ ] Phase management (opening/development/debate/closing)
- [ ] WebSocket handler
  - [ ] Connection management
  - [ ] Message broadcasting
  - [ ] Control command handling
- [ ] Discussion Engine Service
  - [ ] Multi-character coordination
  - [ ] Prompt engineering system
  - [ ] Streaming response handling
  - [ ] State persistence and recovery
- [ ] Redis integration
  - [ ] Session caching
  - [ ] Pub/Sub for WebSocket scaling

### [ ] Phase 5: Frontend Foundation
**Status**: Pending
**Duration**: ~5-7 days

- [ ] Vue 3 project setup
  - [ ] Vite configuration
  - [ ] TypeScript setup
  - [ ] ESLint + Prettier
- [ ] State management (Pinia)
  - [ ] User store
  - [ ] Topic store
  - [ ] Character store
  - [ ] Discussion store
- [ ] Routing (Vue Router)
  - [ ] Public routes
  - [ ] Protected routes
- [ ] UI component library
  - [ ] Select: Element Plus / Naive UI / PrimeVue
  - [ ] Design system setup
- [ ] WebSocket client
  - [ ] Socket.IO integration
  - [ ] Reconnection handling

### [ ] Phase 6: Frontend Core Features
**Status**: Pending
**Duration**: ~10-14 days

- [ ] Authentication pages
  - [ ] Login
  - [ ] Register
  - [ ] Forgot password
- [ ] User dashboard
  - [ ] Topic list
  - [ ] Discussion history
  - [ ] API key management
- [ ] Topic creation
  - [ ] Topic form
  - [ ] Character selection
  - [ ] Discussion mode selection
- [ ] Discussion room (real-time)
  - [ ] Message display
  - [ ] Character list
  - [ ] Progress indicator
  - [ ] Control buttons (pause/resume/stop)
- [ ] Report view
  - [ ] Report display
  - [ ] Visualization charts
  - [ ] Export functionality

### [ ] Phase 7: Integration & Testing
**Status**: Pending
**Duration**: ~5-7 days

- [ ] End-to-end testing
  - [ ] Create discussion flow
  - [ ] Run discussion flow
  - [ ] View report flow
- [ ] API testing
  - [ ] Unit tests for services
  - [ ] Integration tests
- [ ] Performance testing
  - [ ] WebSocket concurrent connections
  - [ ] API response times
- [ ] Bug fixes and optimizations

### [ ] Phase 8: Deployment & Documentation
**Status**: Pending
**Duration**: ~3-5 days

- [ ] Production deployment setup
  - [ ] Docker production configuration
  - [ ] Nginx reverse proxy
  - [ ] Environment variables
- [ ] Documentation
  - [ ] API documentation
  - [ ] Deployment guide
  - [ ] User guide
- [ ] MVP release preparation

---

## Key Questions
1. Should we use a monorepo or separate repos for frontend/backend?
   - Decision pending - affects project structure
2. Which UI component library for Vue 3?
   - Options: Element Plus, Naive UI, PrimeVue
3. Should OAuth be included in MVP or deferred to P1?
   - PRD says P1, email auth sufficient for MVP
4. Deployment target for MVP?
   - Affects infrastructure decisions

## Decisions Made
- Frontend: Vue 3 + TypeScript + Pinia
- Backend: FastAPI + Python
- Database: PostgreSQL + Redis
- WebSocket: Socket.IO
- Monorepo approach: TBD (recommend monorepo for tighter coordination)

## Errors Encountered
- None yet - project not started

## Open Technical Questions (from PRD Appendix D)
- Discussion recovery behavior on connection drop
- Message persistence strategy (immediate vs batch)
- Streaming vs batch display for character responses
- Vector database timing (MVP vs P1 vs P2)

## MVP Feature Scope Confirmation
**P0 (Must Have)**:
- User registration/login (email only)
- API key management
- Topic creation
- Custom character creation
- Preset character library (50)
- Multi-character free discussion mode
- Real-time observation interface
- Discussion summary report
- History records

**Deferred to P1**:
- Intelligent character recommendation
- Advanced discussion controls (accelerate, inject question)
- Report export (PDF/Markdown)
- OAuth login

**Deferred to P2**:
- Discussion quality scoring
- Team collaboration
- Character memory (vector DB)
