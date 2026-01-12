# Product Requirements Document (PRD)
# AI Virtual Focus Group Platform - simFocus

**Document Version**: v1.1
**Date**: 2026-01-12
**Status**: Technical Review Completed
**Product Owner**: AI Product Manager

---

## Change Summary (v1.0 → v1.1)

This version incorporates comprehensive technical reviews from software architecture, backend, and frontend experts. Key updates include:

### Architecture & Design
- **Added Section 4.1**: System Architecture with high-level component diagram and technology stack justification
- **Added Section 4.2**: Data Architecture with detailed database schema and caching strategy
- **Added Section 4.3**: API Design specifications for REST and WebSocket protocols
- **Enhanced Section 5.2**: Expanded security implementation details with encryption specifications

### Technical Clarifications
- Defined LLM provider abstraction layer for multi-vendor support
- Specified WebSocket scaling strategy using Redis Pub/Sub
- Added discussion state machine for session management
- Clarified error handling and retry mechanisms
- Specified performance optimization strategies

### Risk Mitigations
- Identified technical risks with WebSocket connection instability
- Added mitigation strategies for LLM API rate limiting
- Defined data retention and archival policies
- Specified monitoring and observability requirements

### Open Questions
- **Added Appendix D**: Unresolved items requiring product/technical team decisions

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Target Users](#2-target-users)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
   - 4.1 [Core Function Modules](#41-core-function-modules)
   - 4.2 [System Architecture](#42-system-architecture) **[NEW]**
   - 4.3 [Data Architecture](#43-data-architecture) **[NEW]**
   - 4.4 [API Design](#44-api-design) **[NEW]**
   - 4.5 [Enhanced Function Modules](#45-enhanced-function-modules)
   - 4.6 [Functional Interaction Flows](#46-functional-interaction-flows)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Feature Prioritization](#6-feature-prioritization)
7. [Success Metrics](#7-success-metrics)
8. [Competitive Analysis](#8-competitive-analysis)
9. [Future Planning](#9-future-planning)
10. [Risks and Dependencies](#10-risks-and-dependencies)
11. [Appendices](#appendices)
   - Appendix A: Glossary
   - Appendix B: Reference Documents
   - Appendix C: Contact Information
   - Appendix D: Open Questions **[NEW]**

---

## 1. Product Overview

### 1.1 Product Positioning

**simFocus** is an AI-powered virtual focus group platform that simulates multi-character discussions in real-time, enabling users to rapidly obtain diverse perspectives, deep insights, and creative inspiration to support decision-making and problem-solving.

### 1.2 Core Value Propositions

- **Multi-Perspective Collision**: Obtain 3-7 different character viewpoints in a single discussion, saving time compared to individual consultations
- **Real-Time Observation Experience**: Watch the formation, collision, and evolution of viewpoints throughout the process, not just receive conclusions
- **Intelligent Character System**: Support custom character creation or AI automatic generation of optimal discussion participants
- **Deep Thinking Externalization**: Visualize and structure complex argumentation processes
- **Privacy and Control**: Users provide their own API keys, data is stored locally, fully controlling discussion content

### 1.3 Product Goals

**Short-term Goals (3-6 months)**:
- Complete MVP core feature development, supporting basic multi-character discussion workflow
- Validate product-market fit, acquire first 100 seed users
- Establish stable character generation and discussion driving mechanisms

**Medium-term Goals (6-12 months)**:
- Optimize discussion quality to achieve 80% effectiveness of real focus groups
- Expand to enterprise users, launch team collaboration version
- Build character library ecosystem, support user sharing and reuse of quality character configurations

**Long-term Goals (12+ months)**:
- Become a standard thinking assistance tool for knowledge workers, product teams, and research institutions
- Support multi-language and multi-cultural background character discussions
- Explore real-time interaction, voice discussions and other richer interaction forms

### 1.4 Target Market

**Primary Market**:
- Individual knowledge workers (independent developers, freelancers, researchers)
- Product teams (product managers, UX researchers, market researchers)
- Education sector (students, teachers, academic researchers)
- Creative industries (designers, copywriters, marketers)

**Geographic Scope**: Initially focus on Chinese users, later expand to global market

---

## 2. Target Users

### 2.1 User Personas

#### Primary User Group 1: Product Manager - Xiao Zhang

**Basic Information**:
- Age: 28
- Occupation: Internet company product manager
- Experience: 4 years

**Use Scenarios**:
- Before requirement review, quickly verify feasibility of product ideas
- When designing features, simulate reactions and needs of different user roles
- During competitive analysis, evaluate competitor strategies from multiple angles

**Core Needs**:
- Rapidly obtain diverse perspectives, avoid thinking blind spots
- Save time costs of organizing real user research
- Obtain structured argumentation process for team reporting

**Pain Points**:
- Team internal discussions prone to groupthink
- Organizing real focus groups is time-consuming and expensive (recruitment, venue, gifts)
- Difficult to quickly obtain expert-level opinions

#### Primary User Group 2: Independent Researcher - Professor Li

**Basic Information**:
- Age: 45
- Occupation: Associate Professor, Philosophy Department
- Experience: 15 years

**Use Scenarios**:
- When writing academic papers, simulate peer review opinions
- Exploring philosophical topics, obtain perspectives from different schools of thought
- Preparing lectures, designing classroom discussion topics

**Core Needs**:
- Simulate deep speculation processes of multiple experts
- Explore multiple dimensions and possibilities of topics
- Generate teaching cases and discussion materials

**Pain Points**:
- Difficult to find experts from different fields for cross-disciplinary discussions
- Long cycle and high cost of academic exchanges
- Need to quickly verify rationality of arguments

#### Primary User Group 3: Startup Founder - Mr. Wang

**Basic Information**:
- Age: 35
- Occupation: Early-stage startup founder
- Experience: 10 years

**Use Scenarios**:
- Business model validation, simulate multiple perspectives of investors, users, employees
- Before decision-making, quickly obtain "devil's advocate" opposing views
- Strategic planning, simulate market reactions and competitive landscape

**Core Needs**:
- Rapid stress testing of business ideas
- Discover decision blind spots and potential risks
- Obtain simulated feedback from different stakeholders

**Pain Points**:
- Small team size, lack of diverse viewpoints
- High cost of consulting services
- Urgent decision-making timeline, need rapid validation

### 2.2 User Segmentation

| User Type | Usage Frequency | Willingness to Pay | Key Feature Requirements |
|-----------|-----------------|-------------------|------------------------|
| Individual User (Light) | 1-3 times/month | Low | Basic discussions, free character library |
| Individual User (Heavy) | 2-5 times/week | Medium | Custom characters, history, export |
| Enterprise Team | 5-10 times/week | High | Collaboration, enterprise character library, data management |
| Education Institution | 10+ times/month | Medium-High | Teaching mode, batch discussions, student management |

---

## 3. User Stories

### 3.1 Core User Journeys

**Journey 1: Rapid Product Feedback**

> As a product manager, I want to quickly understand market reaction to new features so I can make adjustments before development.

**Steps**:
1. Login to platform, click "Create New Discussion"
2. Enter topic: "We plan to add AI recommendation feature to e-commerce App, users upload product photos and automatically recommend similar products"
3. Select "Auto Generate Characters"
4. System recommends character configuration: product manager, UI designer, technical engineer, regular user, data privacy expert
5. Click "Start Discussion"
6. Watch 5 characters debate feature value, technical feasibility, user experience, privacy risks in real-time
7. After 15 minutes, discussion ends, view auto-generated report
8. Report shows: high feature value but privacy risks need attention, recommend local AI solution
9. Export PDF report, share with team

**Journey 2: Academic Topic Deep Dive**

> As a philosophy researcher, I want to explore "Whether AI has consciousness" to obtain perspectives from different schools of thought.

**Steps**:
1. Create discussion, enter topic: "Discuss possibility of AI consciousness from functionalism, dualism, and physicalism perspectives"
2. Select "Custom Characters"
3. Manually define three characters:
   - Character 1: Functionalist, emphasizing computational theory of mind
   - Character 2: Dualist, insisting on mind-body dualism
   - Character 3: Physicalist, believing consciousness is physical process emergence
4. Start discussion, watch deep speculation and debate among three parties
5. Discover Character 2's "qualia" question triggers intense debate
6. View discussion report, extract core controversy points and arguments from all sides
7. Save discussion record as writing material

**Journey 3: Startup Idea Stress Test**

> As a startup founder, I want to test new business model risks and opportunities to improve business plan.

**Steps**:
1. Enter topic: "I want to build an elderly door-to-door service platform, featuring 2-hour response"
2. Select character template: "Startup Review Committee" (preset configuration)
3. Characters include: angel investor, industry expert, financial advisor, target user representative, competitor
4. Start discussion
5. During observation, discover "2-hour response" difficult to achieve in tier 3-4 cities
6. Pause discussion, insert guiding question: "What if implemented in phases, starting from tier-1 cities?"
7. Characters adjust discussion direction, explore phased strategy
8. Final report recommends: first establish benchmark in tier-1 cities, validate model then expand
9. Adjust business plan based on discussion results

### 3.2 Key User Story Mapping

| Epic | User Story | Priority | Acceptance Criteria |
|------|-----------|----------|---------------------|
| Topic Management | As a user, I can create and edit discussion topics to start new discussions | P0 | Topic text supports 10-2000 characters; support saving drafts |
| Character Creation | As a user, I can customize character background, stance, personality to obtain specific perspectives | P0 | Support setting 5 dimensions: occupation, age, personality, stance, expression style |
| Character Generation | As a user, I can let system automatically generate characters based on topic to quickly start discussion | P0 | System can recommend 3-7 character configurations based on topic type |
| Real-time Observation | As a user, I can watch character discussion process in real-time to understand viewpoint formation and evolution | P0 | Discussion content displays in real-time, support scrolling for history |
| Discussion Control | As a user, I can pause, continue, accelerate during discussion to control viewing pace | P1 | Support pause/continue; support 2x, 3x accelerated playback |
| Interactive Guidance | As a user, I can insert guiding questions during discussion to adjust direction | P1 | After inserting question, characters can respond and adjust discussion direction |
| Report Generation | As a user, I can obtain structured report after discussion ends to quickly get core insights | P0 | Report contains: viewpoint summary, consensus conclusions, controversy points, recommendations |
| History Query | As a user, I can view and manage historical discussion records to review past discussions | P0 | Support search by time, topic keywords; support viewing complete discussion replay |
| Export Sharing | As a user, I can export discussion report as PDF/Markdown to share with team | P1 | Exported report format beautiful, contains complete discussion process and summary |
| User System | As a new user, I can quickly register and login platform to start using | P0 | Support email registration; support third-party login (Google/GitHub) |

---

## 4. Functional Requirements

### 4.1 Core Function Modules

#### Module 1: User System (User System)

**Feature 1.1: User Registration and Login**

**Requirement Description**:
- Support email + password registration
- Support email verification (prevent abuse)
- Support third-party login (Google, GitHub)
- Support password recovery
- Remember login status (optional)

**Business Rules**:
- Email format must be valid
- Password strength requirement: at least 8 characters, including letters and numbers
- Same IP address maximum 3 account registrations in 24 hours (anti-abuse)
- Unverified email users cannot create discussions

**Interface Requirements**:
- Clean registration/login form
- Clear error prompts
- Third-party login buttons clearly visible

---

**Feature 1.2: User Personal Center**

**Requirement Description**:
- View and edit personal profile (nickname, avatar, bio)
- Manage LLM API keys
- View usage statistics (discussion count, usage duration)
- Manage subscription plans (if paid version launched)

**Business Rules**:
- API keys encrypted storage
- Support multiple API key management (OpenAI, Claude, local models, etc.)
- Personal profile optional, not mandatory

---

#### Module 2: Topic Management (Topic Management)

**Feature 2.1: Create Discussion Topic**

**Requirement Description**:
- Provide topic input box
- Support rich text editing (bold, lists, links)
- Support adding background description, context information
- Support uploading relevant attachments (images, documents)
- Support setting expected discussion duration (10/20/30/60 minutes)

**Input Specifications**:
- Topic title: 10-200 characters
- Topic description: 0-2000 characters (optional)
- Attachments: maximum 5 files, single file not exceeding 10MB

**Business Rules**:
- Topic can be saved as draft after submission
- Drafts do not consume API quota
- Topic cannot be modified after official discussion starts

---

**Feature 2.2: Topic Template Library**

**Requirement Description**:
- Provide preset topic templates
- Support user saving custom templates
- Support quickly creating discussions from templates

**Preset Template Categories**:
- Product Review
- Creative Ideation
- Academic Seminar
- Decision Support
- Problem Solving

**Business Rules**:
- Each template contains: topic framework, recommended character configuration, discussion guiding questions
- Users can modify based on template to create new discussion

---

**Feature 2.3: Historical Topic Management**

**Requirement Description**:
- View historical discussion list
- Filter by time, status
- Search topic keywords
- Delete or archive old discussions

**Business Rules**:
- Retain historical discussion records for at least 90 days
- Deleted discussions enter recycle bin, permanently deleted after 30 days
- Support batch operations (batch delete, batch archive)

---

#### Module 3: Character System (Character System)

**Feature 3.1: Custom Character Creation**

**Requirement Description**:
- Provide character configuration form
- Support setting multi-dimensional character traits
- Support saving custom character templates
- Support importing characters from character library

**Character Configuration Dimensions**:
- **Basic Information**: Name, age, gender, occupation/identity
- **Personality Traits**: Openness, rigor, critical thinking, optimism (1-10 score)
- **Knowledge Background**: Professional field, experience years, representative views
- **Discussion Stance**: Support/oppose/neutral/critical exploration
- **Expression Style**: Formal/casual/technical/storytelling
- **Behavior Pattern**: Active speaking/passive response/balanced

**Business Rules**:
- Single discussion can configure 3-7 characters
- Character names cannot be duplicated in single discussion
- Support character preview, view character profile and sample speech

---

**Feature 3.2: Intelligent Character Recommendation**

**Requirement Description**:
- System automatically recommends character configurations based on topic content
- Provide multiple recommendation options for user selection
- Users can adjust based on recommended options

**Recommendation Logic**:
- Analyze topic type (product, academic, business, creative, etc.)
- Identify key stakeholders (users, developers, decision makers, etc.)
- Match preset character templates
- Generate 3 recommendation options (conservative, balanced, exploratory)

**Example**:
- Topic: "Develop an AI writing assistant"
- Recommendation Option 1 (product-oriented): product manager, UI designer, target user, technical lead
- Recommendation Option 2 (business-oriented): investor, market expert, competitor, potential customer
- Recommendation Option 3 (exploratory): sci-fi writer, ethicist, futurist, ordinary user

---

**Feature 3.3: Character Library Management**

**Requirement Description**:
- System presets 100+ quality character templates
- Support user searching and browsing character library
- Support user favoriting and rating characters
- Support user sharing custom characters to community (future feature)

**Character Library Categories**:
- By occupation: product manager, engineer, designer, market expert, investor, etc.
- By thinking style: critical thinker, innovator, conservative, optimist, etc.
- By user persona: youth, enterprise customer, technical expert, ordinary user, etc.
- By academic field: philosopher, economist, psychologist, sociologist, etc.

**Business Rules**:
- Preset characters carefully designed and tested to ensure discussion quality
- Users can rate and comment on characters
- High-rated characters displayed first

---

#### Module 4: Discussion Engine (Discussion Engine)

**Feature 4.1: Multi-Character Discussion Drive**

**Requirement Description**:
- System drives multiple virtual characters to discuss around topic
- Characters can respond, question, supplement, revise viewpoints
- Discussion has clear logical structure and progressive depth
- Avoid repetition and invalid dialogue

**Discussion Phase Control**:
1. **Opening Phase** (1-2 rounds): Characters introduce themselves, state initial positions
2. **Development Phase** (3-8 rounds): Characters respond to each other, deep arguments
3. **Debate Phase** (2-5 rounds): Target disagreements for交锋
4. **Closing Phase** (1-2 rounds): Summarize viewpoints, attempt consensus or clarify differences

**Quality Assurance Mechanisms**:
- Each character speech length controlled at 100-500 words
- Character speeches must reference previous points, avoid monologue
- System detects repetitive content, guides characters to new angles
- Avoid single character dominance, balance character speech counts

**Business Rules**:
- Single discussion total rounds: 10-20 rounds (user configurable)
- Each round speech interval: 2-5 seconds (simulating real discussion rhythm)
- Discussion duration: user preset (default 20 minutes)

---

**Feature 4.2: Discussion Mode Configuration**

**Requirement Description**:
- Support multiple discussion modes
- Users can choose appropriate mode based on needs

**Discussion Mode Types**:

**Mode A: Free Discussion Mode (default)**
- Characters speak freely, respond to each other
- System maintains speech balance and logical coherence
- Applicable to: Open topic exploration

**Mode B: Structured Debate Mode**
- Divided into pro, con, neutral sides
- Each round system specifies speaking character
- Applicable to: Binary opposition topics (e.g., "Should we do X")

**Mode C: Creative Divergence Mode**
- Based on "yes, and" principle
- Characters continue innovation based on others' viewpoints
- Prohibit direct negation, only extension
- Applicable to: Creative ideation, solution design

**Mode D: Consensus Building Mode**
- Goal is finding common ground
- Characters actively compromise and integrate viewpoints
- Applicable to: Team decision-making, conflict resolution

---

**Feature 4.3: Real-Time Observation Interaction**

**Requirement Description**:
- User watches discussion as "observer"
- Interface uses chat dialogue form
- Displays character avatar, name, speech content
- Supports scrolling to view historical messages

**Interface Elements**:
- Discussion area: displays character dialogue
- Character list: displays current all characters and speech status
- Discussion progress bar: displays current round and estimated remaining time
- Control buttons: pause, continue, insert question, end discussion

**Interaction Features**:
- New messages automatically scroll to visible area (if user viewing history)
- Slight animation effect when character speaking
- Support clicking character avatar to view character details

---

**Feature 4.4: Discussion Process Control**

**Requirement Description**:
- Users can intervene during discussion
- Support pause, continue, accelerate
- Support inserting guiding questions
- Support ending discussion early

**Control Function Details**:

**Pause/Continue**:
- After pause, stop generating new messages
- Users can view historical messages, take notes
- After continue, discussion seamlessly resumes

**Accelerated Playback**:
- Support 1.5x, 2x, 3x acceleration
- Reduce message interval time
- Does not affect message content quality

**Insert Guiding Question**:
- Users can input questions at any time
- System adds question to next discussion round
- Characters respond to guiding question
- Use: Adjust discussion direction, deepen specific topics

**End Discussion**:
- Manually end discussion
- System immediately generates report (based on discussed content)
- Prompt user confirmation if discussion less than 5 rounds

---

#### Module 5: Report Generation (Report Generation)

**Feature 5.1: Discussion Summary Report**

**Requirement Description**:
- Automatically generate structured report after discussion ends
- Report contains complete discussion process and core insights
- Support online viewing and export

**Report Structure**:

**1. Discussion Overview**
- Topic title and description
- Participant character list
- Discussion duration, round statistics
- Discussion timestamp

**2. Viewpoint Summary**
- Organize main viewpoints by character
- Each character's core arguments and supporting data
- Character position evolution trajectory (if changed)

**3. Consensus Conclusions**
- Viewpoints characters agree on
- Jointly recognized recommendations or solutions
- Key arguments supporting consensus

**4. Controversy Points**
- Main disagreement points between characters
- Opposing viewpoints and arguments from all sides
- Unresolved controversial questions

**5. Insights and Recommendations**
- Key insights extracted by system
- Actionable next step recommendations
- Potential risks and opportunity points

**6. Discussion Record**
- Complete discussion dialogue record
- Chronologically ordered
- Support keyword highlighting

**Business Rules**:
- Report generation time < 10 seconds
- Report length: 1000 words for simple topics, 3000-5000 words for complex topics
- Support report updates (if user continues discussion)

---

**Feature 5.2: Report Visualization**

**Requirement Description**:
- Present discussion results in chart form
- Improve information absorption efficiency

**Visualization Elements**:

**Viewpoint Distribution Chart**:
- Display position distribution of each character (support/oppose/neutral)
- Use radar chart to display character scores on multiple dimensions

**Controversy Heatmap**:
- Mark high-frequency controversy points in discussion
- Display discussion heat of each controversy point

**Position Evolution Chart**:
- Display character position changes over time (if any)
- Present with line chart or Sankey diagram

**Keyword Cloud**:
- Extract high-frequency keywords from discussion
- Display core concepts and themes

**Business Rules**:
- Visualization charts can be exported as images
- Chart color scheme beautiful, support dark mode

---

**Feature 5.3: Report Export and Sharing**

**Requirement Description**:
- Support multiple format report export
- Support generating share links
- Support embedding external systems

**Export Formats**:
- PDF (suitable for printing and sharing)
- Markdown (suitable for developers)
- Plain text (suitable for further editing)
- JSON (suitable for API integration)

**Sharing Features**:
- Generate read-only share link
- Support setting access password
- Support setting link validity period (1 day/7 days/30 days/permanent)
- Support viewing link access statistics

**Embedding Features** (Enterprise Edition):
- Provide embed code
- Support embedding Notion, Confluence and other knowledge bases
- Support embedding enterprise internal systems

---

#### Module 6: API Management (API Management)

**Feature 6.1: LLM API Configuration**

**Requirement Description**:
- Users provide their own LLM API keys
- Support multiple mainstream LLM providers
- Flexibly switch between different models

**Supported API Providers**:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- Other OpenAI-compatible APIs (e.g., locally deployed models)

**Configuration Items**:
- API Key
- API Base URL (optional, for proxy or local models)
- Model Name (e.g., gpt-4, claude-3-5-sonnet-20241022)
- Temperature Parameter (0.0-1.0, controls creativity, default 0.7)
- Max Token Count (automatically suggested based on model)

**Business Rules**:
- API keys encrypted storage (AES-256)
- API keys only used for user's own discussions
- Do not cache API key plaintext on server
- Provide API usage statistics (call count, Token consumption)

---

**Feature 6.2: API Usage Monitoring**

**Requirement Description**:
- Real-time monitoring of API call status
- Display API usage and costs
- Exception situation prompts

**Monitoring Metrics**:
- Successful call count
- Failed call count and error reasons
- Token consumption statistics
- Estimated cost (based on vendor pricing)

**Exception Handling**:
- Prompt user when API key invalid or expired
- Advance warning when API quota insufficient
- Automatically retry when network error (maximum 3 times)
- Prompt user to check network or switch model when timeout

---

### 4.2 System Architecture

#### 4.2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Frontend (Vue 3 + Pinia + Socket.IO)              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTPS/WSS
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Gateway (FastAPI)                         │ │
│  │  - Authentication (JWT)                                    │ │
│  │  - Rate Limiting                                           │ │
│  │  - Request Routing                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                 │                                │
│           ┌─────────────────────┼─────────────────────┐         │
│           ▼                     ▼                     ▼         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │  REST API      │  │   WebSocket    │  │ Background     │    │
│  │  Endpoints     │  │   Handler      │  │ Workers        │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  User        │  │  Character   │  │  Discussion          │ │
│  │  Service     │  │  Service     │  │  Engine Service      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Topic       │  │  Report      │  │  LLM Orchestrator    │ │
│  │  Service     │  │  Generator   │  │  Service             │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  OpenAI API  │  │  Anthropic   │  │  OpenAI-Compatible   │ │
│  │  (User Key)  │  │  API         │  │  APIs                │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ PostgreSQL   │  │    Redis     │  │  Vector DB           │ │
│  │ (Primary DB) │  │ (Cache +     │  │  (Character Memory)  │ │
│  │              │  │  Pub/Sub)    │  │  - P2 Feature        │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2.2 Core Components and Responsibilities

**1. API Gateway**
- **Responsibility**: Entry point for all client requests, handles authentication, rate limiting, and routing
- **Key Features**:
  - JWT token verification
  - Per-endpoint rate limiting (using Redis)
  - Request/response logging
  - CORS handling

**2. REST API Endpoints**
- **Responsibility**: Handle stateless HTTP requests for CRUD operations
- **Key Endpoints**:
  - Authentication: `/api/auth/*`
  - Users: `/api/users/*`
  - Topics: `/api/topics/*`
  - Characters: `/api/characters/*`
  - Discussions: `/api/discussions/*`
  - Reports: `/api/reports/*`

**3. WebSocket Handler**
- **Responsibility**: Manage real-time bidirectional communication for active discussions
- **Key Features**:
  - Connection lifecycle management
  - Message broadcasting to discussion participants
  - Control command handling (pause, resume, inject question)
  - Automatic reconnection support
  - Redis Pub/Sub integration for horizontal scaling

**4. Background Workers**
- **Responsibility**: Execute async tasks that don't block main request flow
- **Key Tasks**:
  - Report generation after discussion completion
  - Email notifications
  - Data archival jobs
  - Analytics processing

**5. Discussion Engine Service** (Most Critical Component)
- **Responsibility**: Orchestrate multi-character discussions, manage state machine
- **Key Responsibilities**:
  - Coordinate multiple LLM API calls
  - Manage discussion phases (opening, development, debate, closing)
  - Handle streaming responses for real-time delivery
  - Implement discussion modes (free, structured, creative, consensus)
  - Persist discussion state for recovery
  - Error handling and retry logic

**6. LLM Orchestrator Service**
- **Responsibility**: Abstract and manage multiple LLM provider integrations
- **Key Features**:
  - Provider-agnostic interface
  - Automatic retry with exponential backoff
  - Rate limiting per provider
  - Cost tracking and budget management
  - Fallback mechanisms
  - Token usage optimization

**7. User Service**
- **Responsibility**: User authentication, profile management, API key storage
- **Key Features**:
  - Registration/login (email + OAuth)
  - API key encryption/decryption (AES-256)
  - User preferences management
  - Usage statistics tracking

**8. Character Service**
- **Responsibility**: Character template management and configuration
- **Key Features**:
  - CRUD for custom characters
  - Preset character library (100+ templates)
  - Character recommendation algorithm
  - Character rating and popularity tracking

**9. Report Generator Service**
- **Responsibility**: Generate structured insights from completed discussions
- **Key Features**:
  - Multi-section report generation (overview, viewpoints, consensus, controversies)
  - Visualization data preparation
  - Export to multiple formats (PDF, Markdown, JSON)
  - Asynchronous generation with status tracking

**10. Topic Service**
- **Responsibility**: Topic CRUD operations and template management
- **Key Features**:
  - Topic creation and editing
  - Template library management
  - Draft saving and retrieval
  - Search and filtering

#### 4.2.3 Technology Stack Justification

**Backend - FastAPI**
- **Why**: Native async/await support for concurrent LLM calls, automatic OpenAPI docs, type hints with Pydantic
- **WebSocket Support**: Built-in WebSocket handling for real-time discussions
- **Performance**: Comparable to Node.js for I/O-bound workloads with better maintainability

**Frontend - Vue 3**
- **Why**: Composition API superior for complex state management, smaller bundle size than React, excellent TypeScript support
- **State Management**: Pinia provides simpler API than Vuex with better TypeScript support
- **Real-time**: Socket.IO client with automatic reconnection and fallback to polling

**Database - PostgreSQL**
- **Why**: ACID compliance for transactional data, JSONB for flexible character configurations, pgvector extension for future vector similarity
- **Full-text Search**: Built-in tsvector for efficient message search
- **Reliability**: Proven track record, excellent tooling

**Cache - Redis**
- **Why**: Fast in-memory caching for active discussion state, pub/sub for WebSocket scaling, rate limiting
- **Session Management**: Store active discussion sessions with TTL
- **Scalability**: Enables horizontal scaling of WebSocket servers

**Vector Database (P2)**
- **Options**: Qdrant or Weaviate for character memory retrieval
- **Use Case**: Enable characters to remember and reference past discussions
- **Timing**: P2 feature, not needed for MVP

**Infrastructure**
- **Docker + Docker Compose**: Local development environment setup
- **Nginx**: Reverse proxy with WebSocket support
- **Prometheus + Grafana**: Monitoring and metrics visualization
- **ELK Stack**: Log aggregation and analysis

---

### 4.3 Data Architecture

#### 4.3.1 Database Schema Overview

**Core Tables**

```sql
-- Users Table
users (
    id: UUID (PK)
    email: VARCHAR(255) UNIQUE
    password_hash: VARCHAR(255) -- NULL for OAuth-only users
    name: VARCHAR(100)
    avatar_url: TEXT
    bio: TEXT
    email_verified: BOOLEAN
    auth_provider: VARCHAR(50) -- 'email', 'google', 'github'
    provider_id: VARCHAR(255) -- OAuth provider user ID
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
    last_login_at: TIMESTAMP
    deleted_at: TIMESTAMP -- Soft delete
)

-- User API Keys (Encrypted storage)
user_api_keys (
    id: UUID (PK)
    user_id: UUID (FK → users.id)
    provider: VARCHAR(50) -- 'openai', 'anthropic', 'custom'
    key_name: VARCHAR(100)
    encrypted_key: TEXT -- AES-256 encrypted
    api_base_url: TEXT -- Custom endpoint URL
    default_model: VARCHAR(100)
    is_active: BOOLEAN
    created_at: TIMESTAMP
    last_used_at: TIMESTAMP
)

-- Topics (议题)
topics (
    id: UUID (PK)
    user_id: UUID (FK → users.id)
    title: VARCHAR(200)
    description: TEXT
    context: TEXT -- Additional background information
    attachments: JSONB -- Array of file metadata
    status: VARCHAR(20) -- 'draft', 'ready', 'in_discussion', 'completed'
    template_id: UUID -- If created from template
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
)

-- Characters (角色)
characters (
    id: UUID (PK)
    user_id: UUID (FK → users.id) -- NULL for system templates
    name: VARCHAR(100)
    avatar_url: TEXT
    is_template: BOOLEAN
    is_public: BOOLEAN -- For P2 character marketplace
    config: JSONB -- Character configuration (see structure below)
    usage_count: INTEGER
    rating_avg: DECIMAL(3,2)
    rating_count: INTEGER
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
)

-- Discussions (讨论会话)
discussions (
    id: UUID (PK)
    topic_id: UUID (FK → topics.id)
    user_id: UUID (FK → users.id)
    discussion_mode: VARCHAR(20) -- 'free', 'structured', 'creative', 'consensus'
    max_rounds: INTEGER
    status: VARCHAR(20) -- 'initialized', 'running', 'paused', 'completed', 'failed', 'cancelled'
    current_round: INTEGER
    current_phase: VARCHAR(20) -- 'opening', 'development', 'debate', 'closing'
    llm_provider: VARCHAR(50) -- Which API was used
    llm_model: VARCHAR(100) -- Which model
    total_tokens_used: INTEGER
    estimated_cost_usd: DECIMAL(10,4)
    started_at: TIMESTAMP
    completed_at: TIMESTAMP
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
)

-- Discussion Participants (讨论参与者)
discussion_participants (
    id: UUID (PK)
    discussion_id: UUID (FK → discussions.id)
    character_id: UUID (FK → characters.id)
    position: INTEGER -- Order for structured debates
    stance: VARCHAR(20) -- For structured mode: 'pro', 'con', 'neutral'
    message_count: INTEGER
    total_tokens: INTEGER
    created_at: TIMESTAMP
)

-- Discussion Messages (讨论消息)
discussion_messages (
    id: UUID (PK)
    discussion_id: UUID (FK → discussions.id)
    participant_id: UUID (FK → discussion_participants.id)
    round: INTEGER
    phase: VARCHAR(20)
    content: TEXT
    token_count: INTEGER
    is_injected_question: BOOLEAN -- User-injected question
    parent_message_id: UUID (FK → discussion_messages.id) -- For threading
    metadata: JSONB -- Additional data like sentiment, topics, etc.
    created_at: TIMESTAMP
    tsv: TSVECTOR -- Full-text search
)

-- Reports (报告)
reports (
    id: UUID (PK)
    discussion_id: UUID (FK → discussions.id) UNIQUE
    overview: JSONB
    viewpoints_summary: JSONB -- Array of character viewpoints
    consensus: JSONB
    controversies: JSONB -- Array of disagreement points
    insights: JSONB
    recommendations: JSONB
    full_transcript_citation: TEXT -- Reference to messages
    quality_scores: JSONB -- depth, diversity, constructive, coherence
    generation_time_ms: INTEGER
    created_at: TIMESTAMP
    updated_at: TIMESTAMP
)

-- Share Links (分享链接)
share_links (
    id: UUID (PK)
    discussion_id: UUID (FK → discussions.id)
    user_id: UUID (FK → users.id)
    slug: VARCHAR(20) UNIQUE -- Short URL slug
    password_hash: VARCHAR(255) -- NULL if no password
    expires_at: TIMESTAMP
    access_count: INTEGER
    created_at: TIMESTAMP
)

-- Audit Log (审计日志)
audit_logs (
    id: UUID (PK)
    user_id: UUID (FK → users.id)
    action: VARCHAR(100) -- 'discussion_created', 'api_key_added', etc.
    resource_type: VARCHAR(50) -- 'discussion', 'topic', 'character'
    resource_id: UUID
    ip_address: INET
    user_agent: TEXT
    metadata: JSONB
    created_at: TIMESTAMP
)
```

**Character Config JSONB Structure**:
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
  "stance": "critical_exploration", // 'support', 'oppose', 'neutral', 'critical_exploration'
  "expression_style": "formal", // 'formal', 'casual', 'technical', 'storytelling'
  "behavior_pattern": "balanced" // 'active', 'passive', 'balanced'
}
```

**Key Indexes**:
```sql
-- Performance-critical indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_api_keys_user_id ON user_api_keys(user_id);
CREATE INDEX idx_topics_user_id ON topics(user_id);
CREATE INDEX idx_topics_status ON topics(status);
CREATE INDEX idx_characters_user_id ON characters(user_id);
CREATE INDEX idx_characters_is_template ON characters(is_template) WHERE is_template = TRUE;
CREATE INDEX idx_discussions_user_id ON discussions(user_id);
CREATE INDEX idx_discussions_status ON discussions(status);
CREATE INDEX idx_messages_discussion_id ON discussion_messages(discussion_id);
CREATE INDEX idx_messages_discussion_round ON discussion_messages(discussion_id, round);
CREATE INDEX idx_messages_tsv ON discussion_messages USING GIN(tsv);
CREATE INDEX idx_reports_discussion_id ON reports(discussion_id);
```

#### 4.3.2 Caching Strategy

**Redis Cache Layers**:

1. **Session Cache** (TTL: 24 hours)
   - Key: `session:{session_id}`
   - Value: User session data, JWT tokens, CSRF tokens
   - Use: Authentication state, quick user data lookup

2. **User Profile Cache** (TTL: 1 hour)
   - Key: `user:{user_id}:profile`
   - Value: User profile, preferences, permissions
   - Invalidation: On user profile update

3. **API Keys Cache** (TTL: 1 hour, encrypted)
   - Key: `user_api_keys:{user_id}`
   - Value: Active API keys (decrypted only in memory)
   - Use: Frequent LLM API calls without DB queries
   - Invalidation: On API key update

4. **Discussion State Cache** (TTL: Duration of discussion + 1 hour)
   - Key: `discussion_state:{discussion_id}`
   - Value: Current round, phase, active participants, conversation summary
   - Use: Real-time discussion orchestration, state recovery after failure
   - Invalidation: On discussion completion

5. **Character Template Cache** (TTL: 24 hours)
   - Key: `character_template:{template_id}`
   - Value: Character configuration JSON
   - Use: Quick character loading for library browsing
   - Invalidation: On character template update

6. **Rate Limiting** (TTL: Window duration)
   - Key: `ratelimit:{user_id}:{endpoint}`
   - Value: Request count in current window
   - Use: Per-user, per-endpoint rate limiting

7. **WebSocket Connection Tracking** (TTL: Connection duration)
   - Key: `ws_connections:{discussion_id}:{user_id}`
   - Value: Connection metadata, server instance ID
   - Use: Multi-server WebSocket message routing

**Cache Invalidation Strategy**:

- **Write-through**: Write to both cache and database synchronously for critical data
- **Write-back**: Write to cache first, asynchronously persist to database for high-frequency data (discussion state)
- **Time-based expiration**: TTL-based eviction for less critical data
- **Event-based invalidation**: Publish invalidation events on data updates

#### 4.3.3 Data Retention Policy

**Hot Storage (0-30 days)**: PostgreSQL primary database
- All recent discussions, messages, reports
- Active user data
- Real-time analytics data

**Warm Storage (31-90 days)**: PostgreSQL read replica
- Older discussions moved to read replica
- Compressed message archives
- Aggregated analytics

**Cold Storage (90+ days)**: S3-compatible object storage (JSON format)
- Archived discussions exported as JSON
- Compliance requirements (data export requests)
- Long-term analytics data lake

**Automated Cleanup**:
```python
# Daily job to archive old discussions
async def cleanup_old_discussions():
    cutoff_90_days = datetime.utcnow() - timedelta(days=90)

    # Export to cold storage
    await archive_to_s3(
        cutoff_date=cutoff_90_days,
        destination="s3://simfocus-archive/discussions/"
    )

    # Delete from primary DB
    await delete_discussions_older_than(cutoff_90_days)
```

---

### 4.4 API Design

#### 4.4.1 REST API Structure

**Base URL**: `https://api.simfocus.com/v1`

**Core Endpoint Categories**:

**Authentication**
```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/verify-email
POST   /auth/forgot-password
POST   /auth/reset-password
```

**User Management**
```
GET    /users/me
PATCH  /users/me
DELETE /users/me
GET    /users/me/api-keys
POST   /users/me/api-keys
DELETE /users/me/api-keys/{key_id}
PATCH  /users/me/api-keys/{key_id}
```

**Topics (议题管理)**
```
GET    /topics
POST   /topics
GET    /topics/{topic_id}
PATCH  /topics/{topic_id}
DELETE /topics/{topic_id}
POST   /topics/{topic_id}/duplicate
```

**Characters (角色系统)**
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

**Discussions (讨论引擎)**
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

**Reports (报告生成)**
```
GET    /discussions/{discussion_id}/report
GET    /reports/{report_id}
GET    /reports/{report_id}/export/{format}
```

**Analytics (P1/P2 features)**
```
GET    /discussions/{discussion_id}/analytics
POST   /discussions/compare
```

**Share Links**
```
POST   /discussions/{discussion_id}/share
GET    /share/{slug}
DELETE /share/{slug}
```

#### 4.4.2 WebSocket Protocol

**WebSocket Endpoint**: `wss://api.simfocus.com/v1/ws/discussions/{discussion_id}?token={jwt_token}`

**Connection Flow**:
1. Client connects with JWT token in query parameter
2. Server verifies token and discussion access permission
3. Server sends connection confirmation
4. Bi-directional message exchange begins
5. Client or server can close connection

**Message Protocol (JSON)**:

**Client → Server Messages**:
```javascript
// Subscribe to discussion updates
{
  "action": "subscribe",
  "data": {
    "discussion_id": "uuid"
  }
}

// Control commands
{
  "action": "control",
  "data": {
    "control_type": "pause" | "resume" | "speed" | "inject",
    "speed": 1.0 | 1.5 | 2.0 | 3.0,
    "question": "text"
  }
}

// Heartbeat (client-side ping)
{
  "action": "ping"
}
```

**Server → Client Messages**:
```javascript
// New character message (streaming)
{
  "type": "message",
  "data": {
    "message_id": "uuid",
    "character_id": "uuid",
    "character_name": "string",
    "content": "string",
    "round": 1,
    "phase": "opening" | "development" | "debate" | "closing",
    "timestamp": "ISO8601",
    "is_streaming": true
  }
}

// Message complete (final)
{
  "type": "message_complete",
  "data": {
    "message_id": "uuid",
    "token_count": 123
  }
}

// Discussion status update
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

// Character thinking indicator
{
  "type": "character_thinking",
  "data": {
    "character_id": "uuid",
    "character_name": "string"
  }
}

// Error notification
{
  "type": "error",
  "data": {
    "code": "LLM_API_ERROR",
    "message": "Human-readable error message",
    "retryable": true
  }
}

// Pong response to heartbeat
{
  "type": "pong"
}
```

#### 4.4.3 Error Handling

**Standard Error Response Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": {
      "field": "topic.title",
      "reason": "Title must be between 10-200 characters"
    },
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

**Error Code Categories**:

**Authentication Errors** (401):
- `AUTH_001`: Invalid or expired token
- `AUTH_002`: Token missing
- `AUTH_003`: Invalid credentials

**Authorization Errors** (403):
- `AUTHZ_001`: Insufficient permissions
- `AUTHZ_002`: Resource access denied
- `AUTHZ_003`: Discussion ownership required

**Validation Errors** (400):
- `VALIDATION_001`: Invalid input format
- `VALIDATION_002`: Missing required field
- `VALIDATION_003`: Value out of range

**Resource Errors** (404):
- `RESOURCE_001`: Resource not found
- `RESOURCE_002`: Resource already deleted

**API Key Errors** (400):
- `API_KEY_001`: Invalid API key
- `API_KEY_002`: API key quota exceeded
- `API_KEY_003`: API key rate limited

**Discussion Errors** (400):
- `DISCUSSION_001`: Discussion not found
- `DISCUSSION_002`: Discussion already started
- `DISCUSSION_003`: Discussion failed to start
- `DISCUSSION_004`: Maximum concurrent discussions reached

**LLM API Errors** (502):
- `LLM_001`: LLM API error
- `LLM_002`: LLM timeout
- `LLM_003`: LLM rate limited
- `LLM_004`: LLM context length exceeded

**Rate Limiting** (429):
- `RATE_LIMIT_001`: Too many requests
- `RATE_LIMIT_002`: Discussion creation limit exceeded

**Server Errors** (500):
- `SERVER_001`: Internal server error
- `SERVER_002`: Database connection error
- `SERVER_003`: Service temporarily unavailable

#### 4.4.4 Rate Limiting Strategy

**Endpoint-Specific Limits**:
- Authentication endpoints: 5 requests/minute per IP
- API mutation endpoints: 60 requests/minute per user
- Discussion creation: 10 discussions/hour per user
- Character creation: 100 characters/hour per user
- WebSocket connections: 5 concurrent connections per user

**Implementation**:
- Token bucket algorithm using Redis
- Sliding window for precision
- Per-user and per-IP limits
- Rate limit headers in response:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1641234567
  ```

---

### 4.5 Enhanced Function Modules

#### Module 7: Discussion Analysis and Optimization (Discussion Analytics)

**Feature 7.1: Discussion Quality Scoring**

**Requirement Description**:
- System automatically evaluates discussion quality
- Provides multi-dimensional scoring and suggestions

**Scoring Dimensions**:
- **Depth Score** (0-100): Logical depth and thoroughness of arguments
- **Diversity Score** (0-100): Viewpoint diversity and differentiation
- **Constructive Score** (0-100): Actionability and practicality of conclusions
- **Coherence Score** (0-100): Logical coherence and structural clarity of discussion

**Improvement Suggestions**:
- Provide specific suggestions for low-score dimensions
- Example: "Diversity score is low, suggest adding critical characters"
- Or: "Constructive score is low, suggest guiding characters to propose specific recommendations in closing phase"

---

**Feature 7.2: Comparative Analysis**

**Requirement Description**:
- Support multiple discussions of same topic with different character configurations
- Compare and analyze differences between multiple discussions

**Comparison Dimensions**:
- Viewpoint differences comparison
- Conclusion differences comparison
- Impact of character configuration on discussion results

**Application Scenarios**:
- Verify robustness of conclusion (whether different character combinations yield similar results)
- Explore perspective differences among different stakeholders
- Find better character configuration schemes

---

#### Module 8: Collaboration and Sharing (Collaboration)

**Feature 8.1: Team Workspaces**

**Requirement Description**:
- Support creating team spaces
- Team members share discussion records
- Unified management of API keys (enterprise version)

**Feature Details**:
- Team member invitation and management
- Team discussion library sharing
- Team character library sharing
- Team usage statistics

**Permission Management**:
- Owner: Full control permissions
- Admin: Manage discussions and members
- Member: View and create discussions
- Guest: Only view specified discussions

---

**Feature 8.2: Comments and Annotations**

**Requirement Description**:
- Support adding comments on discussion reports
- Team members can collaborative annotation

**Feature Details**:
- Add comments to specific speeches
- @mention other members
- Comment notifications
- Comment export

---

#### Module 9: Advanced Character System (Advanced Characters)

**Feature 9.1: Character Evolution Learning**

**Requirement Description**:
- Characters "learn" and evolve based on historical discussions
- Characters retain conversation memory (within same discussion series)

**Application Scenarios**:
- When continuously discussing multiple topics of same project, characters "remember" previous discussion content
- Characters reference previous viewpoints in later discussions
- Simulate real long-term collaborative relationships

**Technical Implementation**:
- Use vector database to store character historical speeches
- Retrieve relevant history when generating new replies
- Maintain character consistency through Prompt Engineering

---

**Feature 9.2: Real Person Simulation**

**Requirement Description**:
- Create virtual characters based on real person's speech materials
- Simulate thinking patterns of historical figures, experts, opinion leaders

**Application Scenarios**:
- Academic discussion: Simulate philosophers like Aristotle, Kant, Wittgenstein
- Business analysis: Simulate entrepreneurs like Musk, Buffett, Jobs
- Historical research: Simulate historical figures' views on modern topics

**Implementation**:
- User uploads representative text of real person (works, speeches, interviews)
- System analyzes text to extract thinking patterns and expression style
- Generate character configuration

**Notes**:
- Clearly label as "simulated character" to avoid misleading
- Respect portrait rights and reputation rights of characters

---

#### Module 10: Intelligent Assistance (AI Assistance)

**Feature 10.1: Topic Intelligent Analysis**

**Requirement Description**:
- After user enters topic, system automatically analyzes topic characteristics
- Recommend best discussion strategies

**Analysis Dimensions**:
- Topic type recognition (product decision, academic exploration, creative ideation, etc.)
- Key stakeholder identification
- Potential controversy point prediction
- Recommended discussion mode
- Recommended character configuration
- Suggested discussion guiding questions

**Output Example**:
```
Topic Analysis Results:
- Topic type: Product decision category
- Complexity: Medium
- Recommended discussion mode: Structured debate mode
- Recommended characters: Product manager, target user, technical lead, market expert, competitor representative
- Estimated discussion duration: 20 minutes
- Potential controversy points: Technical feasibility vs user needs
```

---

**Feature 10.2: Discussion Guidance Assistant**

**Requirement Description**:
- AI assistant provides guidance suggestions during discussion
- Help users optimize discussion quality

**Assistance Functions**:
- Suggest guiding questions when discussion deadlocks
- Prompt user to focus when certain viewpoints ignored
- Suggest adjusting direction when discussion deviates from topic
- Real-time analyze discussion quality, provide improvement suggestions

**Interaction**:
- Display suggestions in sidebar
- Users can selectively adopt
- Don't disturb main discussion flow

---

### 4.6 Functional Interaction Flows

#### Flow 1: Create and Start Discussion

```
1. User logs into platform
2. Click "Create New Discussion"
3. Enter topic content
4. Select character configuration method (custom/auto-generate)
5. If selecting custom:
   a. Create or select characters (3-7)
   b. Configure character traits
   c. Preview characters
6. If selecting auto-generate:
   a. System analyzes topic
   b. Display 3 recommendation options
   c. User selects option (optional adjustment)
7. Select discussion mode (default free discussion)
8. Set discussion duration (default 20 minutes)
9. Confirm API configuration (prompt if not configured)
10. Click "Start Discussion"
11. Enter real-time observation interface
```

#### Flow 2: Watch Discussion and Interact

```
1. Observation interface loads, displays character list and discussion area
2. Characters begin taking turns speaking
3. New messages display in real-time
4. User can at any time:
   - Pause/continue discussion
   - Adjust playback speed
   - View character details
   - Insert guiding question
   - End discussion
5. Discussion auto-ends or user manually ends
6. Auto-navigate to report page
```

#### Flow 3: View and Use Report

```
1. Report page loads
2. Display discussion overview and summary
3. User can:
   - Read complete report
   - View visualization charts
   - Search keywords
   - Copy content
   - Export report (PDF/Markdown/JSON)
   - Generate share link
   - Return to modify character configuration and re-discuss
4. Save to history
```

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

| Metric | Requirement | Description |
|-------|-------------|-------------|
| Response Time | < 2 seconds | Time from user action to interface response (excluding LLM API calls) |
| First Message Latency | < 10 seconds | Time from discussion start to first message display |
| Message Generation Speed | 5-10 seconds/message | Average generation time for character speeches |
| Report Generation Time | < 10 seconds | Time from discussion end to report display |
| Concurrent Users | 1000+ | Simultaneous online users (MVP phase) |
| API Request Success Rate | > 99% | LLM API call success rate (including retries) |

**Performance Optimization Strategy**:
- Frontend uses WebSocket for real-time communication
- LLM API calls use connection pooling and async processing
- Static assets use CDN acceleration
- Implement request caching and deduplication

---

### 5.2 Security and Privacy

#### 5.2.1 Data Security

**API Key Encryption**:
- User API keys encrypted storage using AES-256-GCM
- 32-byte master key stored in environment variable (not in code)
- Different encryption keys per deployment (dev/staging/prod)
- Master key rotation annually with re-encryption
- Consider AWS KMS or HashiCorp Vault for production

**Implementation**:
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class APIKeyEncryption:
    def __init__(self, master_key: bytes):
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

**Transmission Security**:
- All communications use HTTPS/WSS encryption (TLS 1.3)
- JWT tokens for authentication with short expiration (24 hours)
- Sensitive fields encrypted in database

**Data Storage Security**:
- Database regular backups (daily full, hourly incremental)
- Sensitive operation logging
- Database encryption at rest

#### 5.2.2 Privacy Protection

**Data Minimization**:
- User discussion content private by default, not used for AI training
- Don't share user data without authorization
- Support user exporting and deleting personal data

**Compliance**:
- Comply with GDPR, CCPA and other privacy regulations
- Provide data portability (export in JSON format)
- Provide right to be forgotten (complete deletion)
- Maintain consent records

**User Control**:
- Users can access all their data
- Users can delete their discussions
- Users can export all their data
- Clear privacy policy and terms of service

#### 5.2.3 Access Control

**Authentication**:
- JWT-based authentication
- OAuth 2.0 integration for third-party login
- Multi-factor authentication (P2 feature)

**Authorization**:
- Users can only access their own discussion records
- Team function supports fine-grained permission control
- Share links support password protection and validity period

**Session Management**:
- JWT token expiration after 24 hours
- Refresh token mechanism
- Session invalidation on logout

#### 5.2.4 Content Moderation

**Multi-layer Content Moderation**:
1. **Local keyword filtering** (fast): Block obviously inappropriate topics
2. **Regex pattern matching**: Detect structured harmful content
3. **LLM-based moderation** (optional, slower): nuanced policy evaluation

**User Reporting**:
- In-app reporting mechanism
- Review queue for reported content
- Account suspension for repeated violations

#### 5.2.5 Security Auditing

**Regular Security Measures**:
- Quarterly security scans and penetration testing
- Dependency library vulnerability scanning (Dependabot, Snyk)
- Security event response mechanism
- Security logging for audit trails

**Audit Logging**:
- All authentication events
- All authorization failures
- All API key operations
- All discussion creation/deletion
- IP address and user agent logging

---

### 5.3 Availability Requirements

**System Availability**:
- Availability target: 99.5% (monthly downtime < 3.6 hours)
- Planned maintenance notified 24 hours in advance
- Implement health checks and auto-recovery

**Fault Tolerance**:
- API call failure automatic retry (max 3 times)
- Discussion interruption support resume from breakpoint
- Database master-slave replication and failover
- Redis clustering for cache high availability

**Disaster Recovery**:
- Database backups stored in multiple geographic regions
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 5 minutes

---

### 5.4 Compatibility Requirements

**Browser Support**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Device Support**:
- Desktop (primary): 1920x1080 and above resolution
- Tablet (secondary): iPad and above size
- Mobile (secondary): Responsive design, simplified features

**LLM API Compatibility**:
- OpenAI API format
- Anthropic API format
- OpenAI-compatible third-party APIs (e.g., LocalAI, Ollama)

---

### 5.5 Accessibility

**Accessibility Design**:
- Comply with WCAG 2.1 AA level standards
- Support keyboard navigation
- Support screen readers
- Color contrast compliance
- Provide text size adjustment

**Internationalization**:
- Initial support for Chinese
- Reserved multi-language extension architecture
- Support UTF-8 encoding
- Date, time, number format localization

---

### 5.6 Maintainability

**Code Quality**:
- Code comment coverage > 30%
- Unit test coverage > 70%
- Use code quality check tools (ESLint, Prettier)
- Regular code review

**Monitoring and Logging**:
- Real-time application performance monitoring
- Error log centralized collection
- User behavior analysis (anonymized)
- API call statistics and cost tracking

**Documentation**:
- API documentation (if providing public API)
- Deployment documentation
- Troubleshooting manual
- User manual and help center

---

## 6. Feature Prioritization

### 6.1 Prioritization Framework (RICE Model)

| Feature Module | Reach (Users) | Impact | Confidence | Effort | RICE Score | Priority |
|----------------|--------------|--------|------------|--------|------------|----------|
| User registration/login | 100% | 3 (huge) | 100% | 3 person-weeks | 100 | P0 |
| Topic input | 100% | 3 (huge) | 100% | 2 person-weeks | 150 | P0 |
| Custom character creation | 100% | 3 (huge) | 90% | 4 person-weeks | 67.5 | P0 |
| Intelligent character recommendation | 80% | 2 (large) | 70% | 6 person-weeks | 18.7 | P1 |
| Multi-character discussion drive | 100% | 3 (huge) | 80% | 10 person-weeks | 24 | P0 |
| Real-time observation | 100% | 3 (huge) | 95% | 3 person-weeks | 95 | P0 |
| Report generation | 100% | 3 (huge) | 90% | 5 person-weeks | 54 | P0 |
| History query | 90% | 2 (large) | 100% | 2 person-weeks | 90 | P0 |
| API management | 100% | 3 (huge) | 100% | 2 person-weeks | 150 | P0 |
| Discussion control (pause/accelerate) | 60% | 1 (medium) | 95% | 2 person-weeks | 28.5 | P1 |
| Interactive guidance (insert question) | 40% | 2 (large) | 80% | 3 person-weeks | 21.3 | P1 |
| Discussion quality scoring | 30% | 1 (medium) | 60% | 4 person-weeks | 4.5 | P2 |
| Report export | 70% | 2 (large) | 100% | 2 person-weeks | 70 | P1 |
| Team collaboration | 20% | 2 (large) | 70% | 8 person-weeks | 3.5 | P2 |
| Character library | 80% | 1 (medium) | 80% | 3 person-weeks | 21.3 | P1 |

**RICE Score Calculation Formula**: (Reach × Impact × Confidence) / Effort

### 6.2 MVP Feature Scope (P0)

**MVP (Minimum Viable Product) Must Include**:

1. **User System**
   - Email registration/login
   - Personal center (manage API keys)

2. **Topic Management**
   - Create topic
   - Topic list

3. **Character System**
   - Custom character creation (basic version)
   - Preset character library (50 characters)

4. **Discussion Engine**
   - Multi-character free discussion mode
   - Real-time observation interface
   - Basic discussion control (start, pause, end)

5. **Report Generation**
   - Discussion summary report (basic version)
   - Online report viewing

6. **History Records**
   - View historical discussions
   - View historical reports

7. **API Management**
   - Configure LLM API
   - API usage monitoring

**MVP Excludes** (deferred to later iterations):
- Intelligent character recommendation (use preset templates instead)
- Advanced discussion control (accelerated playback, insert question)
- Discussion quality scoring
- Team collaboration
- Report export (online viewing only)

---

### 6.3 Feature Iteration Roadmap

#### V1.0 - MVP (Launch: Month 3)

**Goal**: Verify core value, achieve end-to-end discussion workflow

**Features**:
- All P0 features online
- Support 1 LLM API provider (OpenAI)
- Single-user mode
- Basic UI/UX

**Success Criteria**:
- At least 50 seed users
- Completion rate > 70% (from creating topic to viewing report)
- User satisfaction > 3.5/5

---

#### V1.1 - Enhanced Experience (Launch: Month 4)

**Goal**: Improve user experience and discussion quality

**New Features**:
- Support multiple LLM APIs (Anthropic, local models)
- Intelligent character recommendation
- Advanced discussion control (accelerate, insert question)
- Topic template library
- Character preview function

**Optimizations**:
- Discussion quality improvement
- Report content optimization
- UI/UX improvements

---

#### V1.2 - Content and Sharing (Launch: Month 5)

**Goal**: Enhance content value and dissemination capability

**New Features**:
- Expand character library to 100+ characters
- Report export (PDF, Markdown)
- Share link function
- Discussion comparative analysis
- Topic search and filtering

---

#### V2.0 - Collaboration and Intelligence (Launch: Month 8)

**Goal**: Expand team scenarios, improve intelligence level

**New Features**:
- Team workspaces
- Team character library
- Comments and annotations
- Discussion quality scoring
- Topic intelligent analysis
- Discussion guidance assistant

---

#### V2.1 - Advanced Features (Launch: Month 10)

**Goal**: Differentiated features, enhance competitiveness

**New Features**:
- Character evolution learning
- Multiple discussion modes (debate, consensus, creative divergence)
- Enhanced report visualization
- Custom themes (UI themes)

---

#### V3.0 - Ecosystem (Launch: Month 12+)

**Goal**: Build ecosystem, expand boundaries

**New Features**:
- Character marketplace (user sharing and trading characters)
- API open platform
- Plugin system
- Mobile App
- Voice discussions
- Real-time multi-person interaction

---

## 7. Success Metrics

### 7.1 North Star Metric

**Core Value Metric**: **Weekly Active Discussions (WAD)**

**Definition**: Number of discussions created and completed per week

**Goals**:
- 1 month after V1.0 launch: 100 discussions/week
- 3 months after V1.0 launch: 500 discussions/week
- 6 months after V1.0 launch: 2000 discussions/week

**Rationale**:
- Directly reflects core value usage of product
- More reflective of product real value than user count
- Highly correlated with business value

---

### 7.2 Process Metrics

**User Activation**:
- **Registration conversion rate**: Visitor → Registered user > 15%
- **First discussion completion rate**: Complete first discussion within 7 days of registration > 40%
- **API configuration rate**: Configure API key within 7 days of registration > 60%

**User Retention**:
- **Day 1 retention rate** > 40%
- **Day 7 retention rate** > 25%
- **Day 30 retention rate** > 15%

**User Engagement**:
- **Weekly discussion frequency**: Active users average > 2 discussions/week
- **Discussion completion rate**: From creation to viewing report > 70%
- **Average discussion duration**: 15-25 minutes (reflects content quality)

**Feature Penetration**:
- **Custom character usage rate** > 30%
- **Intelligent recommendation usage rate** > 40%
- **Report view completeness** > 60%

---

### 7.3 Outcome Metrics

**User Satisfaction**:
- **NPS (Net Promoter Score)** > 30
- **User rating** > 4.0/5
- **Customer Satisfaction (CSAT)** > 80%

**Discussion Quality** (subjective assessment):
- **Discussion usefulness** > 80% (user feedback)
- **Report quality rating** > 4.0/5
- **Character realism rating** > 3.5/5

**Business Metrics** (if launching paid version):
- **Paid conversion rate** > 5%
- **ARPU (Average Revenue Per User)** > $10/month
- **CAC (Customer Acquisition Cost) < LTV (User Lifetime Value) × 0.3**

---

### 7.4 Reverse Metrics

**Metrics to Monitor and Reduce**:
- **API call failure rate** < 1%
- **Discussion interruption rate** < 5% (exit before completion)
- **Report generation failure rate** < 0.5%
- **User complaint rate** < 2%
- **Negative feedback ratio** < 10%

---

### 7.5 Data Collection Plan

**Event Tracking Design**:

**User Behavior Events**:
- Page view (page_view)
- Button click (button_click)
- Discussion creation (discussion_create)
- Discussion completion (discussion_complete)
- Report viewing (report_view)
- Report export (report_export)

**Business Events**:
- API call success/failure (api_call_success/fail)
- Character creation/selection (character_create/select)
- Discussion control operation (discussion_control)
- Share link generation/access (share_link_generate/access)

**Performance Events**:
- Page load time (page_load_time)
- API response time (api_response_time)
- Message generation time (message_generation_time)

**User Feedback Collection**:
- Satisfaction survey popup after discussion ends
- In-app feedback entry
- Regular user interviews (5-10 people monthly)
- NPS survey (quarterly)

---

## 8. Competitive Analysis

### 8.1 Direct Competitors

Currently no identical products in market, but tools with similar features:

#### Competitor 1: ChatGPT + Custom Instructions

**Product Description**: OpenAI's ChatGPT supports custom instructions, can simulate different roles

**Strengths**:
- Powerful language model
- Flexible custom instructions
- Huge user base

**Weaknesses**:
- Need to manually simulate multiple characters (no automatic multi-character interaction)
- No structured discussion workflow
- No professional report generation
- No observation experience

**Our Differentiation**:
- Specially designed multi-character discussion engine
- Automated discussion workflow control
- Structured report generation
- Real-time observation experience

---

#### Competitor 2: Character.ai

**Product Description**: Platform for creating and chatting with virtual characters

**Strengths**:
- Rich character library
- Realistic character dialogue
- Active community

**Weaknesses**:
- Mainly for entertainment and companionship
- Doesn't support multi-character simultaneous discussion
- No topic-driven discussion
- No professional report generation

**Our Differentiation**:
- Focus on productive use scenarios (decision-making, research, creativity)
- Multi-character collaborative discussion
- Topic-driven rather than character-driven
- Professional-level report output

---

#### Competitor 3: C-3 - AI Roleplayer

**Product Description**: Tool for AI role-playing thought experiments

**Strengths**:
- Supports multi-character scenarios
- Applicable to strategic planning

**Weaknesses**:
- Relatively single function
- Simple character configuration
- No observation mode
- No report generation

**Our Differentiation**:
- More complete character system (multi-dimensional configuration)
- Real-time observation experience
- Automatic report generation
- More rich discussion modes

---

### 8.2 Indirect Competitors

#### Competitor 4: Traditional Focus Group Services

**Product Description**: Offline or online real user focus group services

**Strengths**:
- Real human feedback
- Rich non-verbal information
- Professional moderator guidance

**Weaknesses**:
- High cost ($5000-$20000 per session)
- Long cycle (recruitment, execution, analysis)
- Difficult to conduct frequently
- Limited sample size

**Our Differentiation**:
- Very low cost (only API fees)
- Fast (20 minutes vs weeks)
- Can conduct anytime
- Simulate expert-level participants

**Positioning Relationship**: We're not a replacement, but a complement
- Used as pre-research before real focus groups
- Used for early rapid iteration
- Used when budget is limited

---

#### Competitor 5: Online Survey Tools (SurveyMonkey, Wenjuanxing)

**Product Description**: Online questionnaire platforms

**Strengths**:
- Low cost
- Large sample size
- Structured data

**Weaknesses**:
- Only get preset question answers
- Cannot explore deeply
- Cannot observe thinking process
- Lack interaction and collision

**Our Differentiation**:
- Deep exploration rather than shallow answers
- Viewpoint collision rather than unidirectional feedback
- Observe thinking process rather than just get conclusions

---

### 8.3 Competitive Strategy

**Differentiation Positioning**:
- **Not positioned as chatbot**, but **thinking assistance tool**
- **Not positioned as entertainment tool**, but **productivity tool**
- **Not replacing human discussion**, but **rapid pre-research and divergence**

**Core Competitive Advantages**:
1. **Professionalism**: Designed for productive scenarios, output structured reports
2. **Efficiency**: 20 minutes to obtain multi-perspective deep discussion
3. **Flexibility**: Custom characters or intelligent recommendation
4. **Privacy**: User's own API, data localization

**Market Entry Strategy**:
1. **Seed User Strategy**: Focus on product managers, researchers and other early adopters
2. **Content Marketing**: Share high-quality discussion cases and reports
3. **Community Building**: Build user community, share character configurations and best practices
4. **Product-Led Growth**: Achieve viral spread through share links

---

## 9. Future Planning

### 9.1 Short-term Planning (3-6 months)

**V1.0 - MVP Launch**
- Complete core feature development
- Recruit 100 seed users
- Collect user feedback and iterate rapidly

**V1.1 - Experience Optimization**
- Optimize discussion quality
- Expand character library
- Improve UI/UX

**V1.2 - Content Expansion**
- Topic template library
- Report export functionality
- Sharing functionality

**Key Milestones**:
- Month 3: V1.0 launch
- Month 4: Achieve 100 weekly active discussions
- Month 6: Achieve 500 weekly active discussions

---

### 9.2 Medium-term Planning (6-12 months)

**V2.0 - Collaboration Version**
- Team workspaces
- Enterprise features
- Subscription model

**V2.1 - Intelligence Upgrade**
- Discussion quality scoring
- Intelligent character recommendation
- Topic intelligent analysis

**V2.5 - Mobile**
- Mobile web optimization
- Native app planning

**Key Milestones**:
- Month 8: Launch team collaboration version
- Month 10: Achieve 2000 weekly active discussions
- Month 12: Achieve profitability

---

### 9.3 Long-term Vision (12+ months)

**V3.0 - Ecosystem**
- Open API platform
- Plugin marketplace
- Character marketplace

**V3.5 - Multi-modal Interaction**
- Voice discussions
- Video virtual avatars
- Real-time multi-person interaction

**V4.0 - AI Evolution**
- Character self-learning
- Cross-discussion knowledge transfer
- Personalized character assistants

**Vision**: Become a standard thinking assistance tool for knowledge workers, like calculators to mathematics, simFocus to thinking and decision-making.

---

### 9.4 Potential Expansion Directions

**Industry Verticalization**:
- Product R&D dedicated version
- Academic research dedicated version
- Creative design dedicated version
- Education training dedicated version

**Technology Exploration**:
- Integrate knowledge graphs (like GraphDB mentioned by user)
- Multi-modal input (images, documents, video)
- Real-time web information retrieval
- Expert system integration

**Business Model Exploration**:
- Freemium model (basic free, advanced paid)
- Enterprise subscription
- API billing
- Character marketplace transaction commission

---

## 10. Risks and Dependencies

### 10.1 Product Risks

**Risk 1: Discussion Quality Below Expectations**

**Description**: AI character discussion quality below user expectations, cannot provide real value

**Impact**: High - Directly affects core value and user retention

**Probability**: Medium

**Mitigation Measures**:
- Carefully design prompt engineering
- Optimize character configuration logic
- Add discussion quality scoring and feedback mechanism
- Continuously collect user feedback and iterate
- Set reasonable user expectations (marketing materials state AI limitations)

**Contingency Plan**:
- Provide "dissatisfied re-discussion" function
- Manual review and optimize high-frequency used characters

---

**Risk 2: Users Don't Understand Product Value**

**Description**: Users think directly asking ChatGPT is enough, don't understand multi-character discussion value

**Impact**: High - Affects user acquisition and conversion

**Probability**: Medium-High

**Mitigation Measures**:
- Clear value proposition communication
- Provide high-quality example discussions and reports
- Product guidance flow (onboarding)
- Comparative demonstration (single AI vs multi-AI discussion)
- Free trial, let users experience firsthand

---

**Risk 3: LLM API Costs Too High**

**Description**: Single discussion API cost exceeds user's willingness to pay range

**Impact**: Medium - Affects pricing and profitability

**Probability**: Medium

**Mitigation Measures**:
- Optimize prompts, reduce token consumption
- Support cheaper models (like GPT-3.5)
- Support local models (user hardware already paid)
- Intelligent caching (reuse similar discussions)
- Tiered pricing (basic version uses cheap models, advanced version uses GPT-4)

---

### 10.2 Technical Risks

**Risk 4: LLM API Instability**

**Description**: Third-party API rate limiting, downtime or changes

**Impact**: High - Directly affects user experience

**Probability**: Medium

**Mitigation Measures**:
- Support multiple API providers (reduce single point dependency)
- Implement retry and degradation mechanisms
- Monitor API status, advance warning
- Encourage users to configure multiple APIs as backup
- Cache common discussion patterns

---

**Risk 5: Discussion Fluency and Coherence Insufficient**

**Description**: Character dialogue unnatural, lacks logical coherence

**Impact**: High - Affects user experience

**Probability**: Medium

**Mitigation Measures**:
- Optimize discussion driving algorithm
- Add context memory mechanism
- Use stronger models (Claude, GPT-4)
- Set character behavior rules and constraints
- Continuous testing and optimization

---

**Risk 6: Response Speed Too Slow**

**Description**: Character reply generation time too long, affects observation experience

**Impact**: Medium - Affects user experience

**Probability**: Medium

**Mitigation Measures**:
- Optimize prompt length
- Use faster models
- Parallel process multiple characters
- Implement streaming output (gradual display)
- Provide playback speed control

---

### 10.3 Business Risks

**Risk 7: User Acquisition Cost Too High**

**Description**: CAC too high, cannot sustainably grow

**Impact**: High - Affects profitability

**Probability**: Medium

**Mitigation Measures**:
- Product-Led Growth (PLG) strategy
- Content marketing (cases, blogs, social media)
- Community building (word-of-mouth spread)
- Free trial reduce conversion threshold
- Partner channels

---

**Risk 8: Commercialization Difficulties**

**Description**: Users unwilling to pay, commercialization blocked

**Impact**: High - Affects long-term sustainability

**Probability**: Medium

**Mitigation Measures**:
- Freemium model (basic functions free)
- Enterprise subscription (B2B easier to monetize)
- Pay-per-use (single discussion payment)
- API platform model (third-party integration)
- Data insight service (anonymized data analysis)

---

### 10.4 Legal and Compliance Risks

**Risk 9: User-Generated Inappropriate Content**

**Description**: Users use platform to generate illegal, harmful content

**Impact**: Medium - Legal and reputation risk

**Probability**: Low

**Mitigation Measures**:
- User agreement explicitly prohibits
- Content moderation mechanism (report generation after check)
- Sensitive word filtering
- User reporting mechanism
- Comply with regulatory requirements

---

**Risk 10: Data Privacy Violations**

**Description**: User data leakage or violating privacy regulations

**Impact**: High - Legal and reputation risk

**Probability**: Low

**Mitigation Measures**:
- Encrypt stored user data
- Comply with GDPR, CCPA and other regulations
- Provide data export and deletion functions
- Regular security audits
- Transparent privacy policy

---

### 10.5 External Dependencies

**Key Dependencies**:

1. **LLM API Providers** (OpenAI, Anthropic, etc.)
   - Dependency: Core functionality relies on their APIs
   - Risk: API changes, rate limiting, price adjustments
   - Mitigation: Support multiple providers, maintain flexibility

2. **Cloud Service Providers** (AWS, Azure, etc.)
   - Dependency: Infrastructure hosting
   - Risk: Service interruption, price adjustments
   - Mitigation: Multi-cloud strategy, containerized deployment

3. **Third-party Authentication Services** (Google, GitHub OAuth)
   - Dependency: User registration and login
   - Risk: Service changes
   - Mitigation: Keep email registration as alternative

---

## Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| simFocus | AI Virtual Focus Group Platform product name |
| Topic (议题) | Discussion theme or question submitted by user |
| Character (角色) | Virtual discussion participant played by AI |
| Character Profile (角色配置) | Parameter set defining character traits |
| Observation Mode (观摩模式) | Mode where user watches character discussion in real-time |
| Report (报告) | Structured summary generated after discussion ends |
| API Key (API密钥) | Authentication credential for user accessing LLM services |
| Discussion (讨论) | Complete workflow from creating topic to generating report |
| Round (轮次) | Each character speaking once is called a round |
| Consensus (共识) | Viewpoints characters agree on |
| Controversy Point (争议点) | Viewpoints where characters disagree |

---

### Appendix B: Reference Documents

**Product References**:
- "Inspired: How to Create Tech Products Customers Love" - Marty Cagan
- "The Lean Startup" - Eric Ries
- "The Design of Everyday Things" - Don Norman

**Technical References**:
- OpenAI API documentation
- Anthropic Claude API documentation
- Prompt engineering best practices

**Competitive Research**:
- Character.ai product analysis
- ChatGPT custom features research
- Traditional focus group methodology

---

### Appendix C: Contact Information

**Product Team**:
- Product Owner: [TBD]
- Technical Lead: [TBD]
- Design Lead: [TBD]

**Feedback Channels**:
- User feedback email: feedback@simfocus.com
- Product community: community.simfocus.com
- GitHub Issues: github.com/simfocus/simfocus/issues

---

### Appendix D: Open Questions

**Questions Requiring Product/Technical Team Decisions**:

#### D.1 Architecture & Design

1. **Discussion Recovery**: If user's connection drops mid-discussion, should the discussion:
   - Continue running server-side?
   - Pause and wait for reconnection?
   - Allow state recovery on reconnect?
   - **Status**: Unresolved - Affects UX and backend architecture

2. **Multi-user Observation**: Should future versions allow multiple users to observe same discussion simultaneously (e.g., team watching together)?
   - **Status**: Unresolved - Affects WebSocket permissions and scaling strategy

3. **Discussion Forking**: Should users be able to "fork" a discussion at any point and explore different directions with same characters?
   - **Status**: Unresolved - Affects data model and backend complexity

4. **Character Identity Consistency**: How should characters maintain consistency if same character used across multiple discussions by same user?
   - **Status**: Unresolved - Affects character memory architecture (P2 feature)

#### D.2 Performance & Scaling

5. **First Message Latency Breakdown**: For "first message" requirement of <10 seconds, does this include:
   - Time to load discussion page?
   - Time to connect WebSocket?
   - Time to generate first character's message?
   - **Status**: Unresolved - Affects performance targets and optimization strategy

6. **Concurrent Discussion Limits**: What is expected maximum number of simultaneous discussions a single user might run?
   - **Status**: Unresolved - Affects rate limiting and infrastructure planning

7. **Message Persistence Strategy**: Should messages be persisted to database immediately or batched for performance?
   - **Status**: Unresolved - Affects database write performance and data durability

#### D.3 Product & UX

8. **Discussion Interruption Behavior**: If user inserts a question, should characters:
   - Finish current round first?
   - Interrupt immediately?
   - Insert at natural break point?
   - **Status**: Unresolved - Affects discussion engine logic

9. **Character Avatar System**: Are dynamic character avatars (AI-generated) planned or static images only?
   - **Status**: Unresolved - Affects frontend implementation and storage

10. **Mobile Experience Scope**: For mobile "secondary" support, should it be:
    - Read-only observation of desktop-initiated discussions?
    - Full discussion creation capability?
    - Notification-driven when discussion updates?
    - **Status**: Unresolved - Affects mobile development scope

#### D.4 Data & Privacy

11. **Data Analytics Permissions**: Can anonymized usage data be collected for product improvement:
    - Discussion topics?
    - Character configurations used?
    - Completion rates?
    - **Status**: Unresolved - Affects privacy policy and analytics implementation

12. **API Key Sharing**: Should users be able to:
    - Share API keys within a team?
    - Set spending limits per discussion?
    - Configure fallback keys?
    - **Status**: Unresolved - Affects API key management features

#### D.5 Technical Implementation

13. **Vector Database Timing**: Is vector database (for character memory) planned for:
    - MVP (P0)?
    - P1 iteration?
    - P2 (character evolution)?
    - **Status**: Unresolved - Affects infrastructure setup and development timeline

14. **Streaming vs Batch Display**: Should character responses:
    - Stream token-by-token (more engaging)?
    - Show after completion (simpler)?
    - Configurable per user?
    - **Status**: Unresolved - Affects frontend WebSocket handling and UX

15. **Deployment Target**: Where will application be deployed:
    - User's local machine?
    - Cloud provider (which one)?
    - Self-hosted by users?
    - **Status**: Unresolved - Affects infrastructure decisions and cost model

---

**Document Change History**:

| Version | Date | Reviser | Change Description |
|---------|------|---------|-------------------|
| v1.0 | 2026-01-09 | AI Product Manager | Initial version |
| v1.1 | 2026-01-12 | Product Manager | Technical review completed, added system architecture, data architecture, API design, enhanced security section, open questions appendix |

---

**Document Review Status**:
- [x] Product team review
- [x] Technical team review
- [ ] Design team review
- [ ] Stakeholder review
- [ ] Approved

---

*This PRD document is the guiding document for simFocus product development, all functional requirements based on v1.1 MVP version planning. As product iterates and user feedback collected, this document will continue to update and improve.*
