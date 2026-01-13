# Shared Types

TypeScript type definitions shared between frontend and backend.

## Purpose

This directory contains type definitions that are used by both the Vue 3 frontend and FastAPI backend. This ensures type consistency across the full stack and eliminates the need to duplicate type definitions.

## Structure

```
shared/types/
├── character.ts      # Character configuration types
├── discussion.ts     # Discussion state and message types
├── api.ts           # API request/response types
├── websocket.ts     # WebSocket event types
├── index.ts         # Export all types
└── README.md
```

## Usage

### Frontend (Vue 3)

```typescript
import type { CharacterConfig, DiscussionMode } from '@/types'
// The @/types alias maps to shared/types
```

### Backend (FastAPI)

```python
# Types are used for Pydantic model validation
# See backend/app/schemas/ for implementation
```

## Type Categories

### Character Types (`character.ts`)

- `CharacterConfig` - Full character configuration
- `PersonalityTraits` - Personality dimensions (1-10 scale)
- `KnowledgeBackground` - Areas of expertise
- `DiscussionStance` - Character's position on topics
- `ExpressionStyle` - How character communicates
- `BehaviorPattern` - Participation level

### Discussion Types (`discussion.ts`)

- `DiscussionMode` - Free, structured, creative, consensus
- `DiscussionStatus` - initialized, running, paused, completed, failed
- `DiscussionPhase` - opening, development, debate, closing
- `DiscussionMessage` - Individual message structure
- `Participant` - Discussion participant info

### API Types (`api.ts`)

- `ApiResponse<T>` - Generic response wrapper
- `PaginatedResponse<T>` - Paginated list response
- `PaginationParams` - Query parameters
- `ApiError` - Error response structure

### WebSocket Types (`websocket.ts`)

- `ServerToClientEvents` - Events from server
- `ClientToServerEvents` - Events from client
- `SocketEvents` - Combined event types

## Maintenance

When adding or modifying types:

1. Update the type definition in the appropriate file
2. Add JSDoc comments explaining the purpose
3. Export from `index.ts`
4. Update frontend components that use the type
5. Update backend schemas that reference the type

## Best Practices

- Use descriptive names that clearly indicate the purpose
- Add JSDoc comments for complex types
- Use union types for fixed sets of values
- Leverage TypeScript's utility types (Pick, Omit, Partial, etc.)
- Keep types minimal and focused
- Avoid any unless absolutely necessary
