# Backend Schemas and API Layer Implementation

## Overview

This document describes the Pydantic schemas and API layer implementation for the simFocus backend.

## Implementation Date

2026-01-13

## Phase 1: Pydantic Schemas

### Location
`backend/app/schemas/`

### Files Created

1. **common.py** - Reusable schemas
   - `PaginationParams` - Query parameters for paginated endpoints
   - `PaginatedResponse[T]` - Generic paginated response wrapper
   - `ErrorResponse` - Standard error response format
   - `MessageResponse` - Simple success message
   - `IdResponse` - Response with created resource ID

2. **auth.py** - Authentication schemas
   - `RegisterRequest` - User registration
   - `LoginRequest` - User login
   - `TokenResponse` - JWT token response
   - `RefreshTokenRequest` - Token refresh
   - `ForgotPasswordRequest` - Password reset request
   - `ResetPasswordRequest` - Password reset confirmation
   - `VerifyEmailRequest` - Email verification
   - `ChangePasswordRequest` - Password change for authenticated users

3. **user.py** - User management schemas
   - `UserResponse` - User profile response
   - `UserUpdateRequest` - Profile update
   - `UserStatsResponse` - Usage statistics
   - `APIKeyCreateRequest` - API key creation
   - `APIKeyUpdateRequest` - API key update
   - `APIKeyResponse` - API key response (without actual key)

4. **topic.py** - Topic management schemas
   - `TopicCreateRequest` - Topic creation with validation
   - `TopicUpdateRequest` - Topic update
   - `TopicResponse` - Full topic details
   - `TopicListResponse` - Summary view for lists

5. **character.py** - Character schemas with nested models
   - `PersonalityTraits` - Personality dimensions (1-10 scale)
   - `KnowledgeBackground` - Expertise and experience
   - `CharacterConfig` - Complete character configuration
   - `CharacterCreateRequest` - Character creation
   - `CharacterUpdateRequest` - Character update
   - `CharacterResponse` - Full character details
   - `CharacterTemplateResponse` - Template list item

6. **discussion.py** - Discussion management schemas
   - `DiscussionCreateRequest` - Discussion creation with validation
   - `DiscussionResponse` - Discussion summary
   - `DiscussionListResponse` - List item view
   - `ParticipantResponse` - Participant details
   - `MessageResponse` - Message details
   - `DiscussionDetailResponse` - Full discussion with messages
   - `InjectQuestionRequest` - Question injection
   - `DiscussionControlRequest` - Control commands

7. **report.py** - Report schemas
   - `ReportResponse` - Full discussion report
   - `ReportSummaryResponse` - Report summary for lists
   - `ShareLinkCreateRequest` - Share link creation
   - `ShareLinkResponse` - Share link details

### Key Features

- **Pydantic v2 syntax** with modern type hints
- **Comprehensive validation** using Field() constraints
- **Detailed documentation** with description fields
- **Generic types** for reusable patterns
- **from_attributes=True** for ORM model support

## Phase 2: API Routes

### Location
`backend/app/api/`

### Files Created

1. **deps.py** - FastAPI dependencies
   - `get_db()` - Database session dependency
   - `get_current_user()` - JWT authentication dependency
   - `get_current_user_optional()` - Optional auth
   - `get_request_id()` - Request tracing

2. **v1/auth.py** - Authentication endpoints
   - `POST /auth/register` - User registration
   - `POST /auth/login` - User login
   - `POST /auth/refresh` - Token refresh
   - `POST /auth/verify-email` - Email verification
   - `POST /auth/forgot-password` - Password reset request
   - `POST /auth/reset-password` - Password reset
   - `POST /auth/change-password` - Password change

3. **v1/users.py** - User management endpoints
   - `GET /users/me` - Get current user profile
   - `PATCH /users/me` - Update profile
   - `DELETE /users/me` - Delete account
   - `GET /users/me/stats` - Get statistics
   - `GET /users/me/api-keys` - List API keys
   - `POST /users/me/api-keys` - Add API key
   - `DELETE /users/me/api-keys/{key_id}` - Delete API key
   - `PATCH /users/me/api-keys/{key_id}` - Update API key

4. **v1/topics.py** - Topic management endpoints
   - `GET /topics` - List user topics (paginated)
   - `POST /topics` - Create topic
   - `GET /topics/{topic_id}` - Get topic details
   - `PATCH /topics/{topic_id}` - Update topic
   - `DELETE /topics/{topic_id}` - Delete topic
   - `POST /topics/{topic_id}/duplicate` - Duplicate topic

5. **v1/characters.py** - Character management endpoints
   - `GET /characters` - List user characters
   - `POST /characters` - Create custom character
   - `GET /characters/templates` - List system templates
   - `GET /characters/{character_id}` - Get character details
   - `PATCH /characters/{character_id}` - Update character
   - `DELETE /characters/{character_id}` - Delete character
   - `POST /characters/{character_id}/rate` - Rate character

6. **v1/discussions.py** - Discussion management endpoints
   - `GET /discussions` - List user discussions
   - `POST /discussions` - Create discussion
   - `GET /discussions/{discussion_id}` - Get discussion details
   - `DELETE /discussions/{discussion_id}` - Delete discussion
   - `POST /discussions/{discussion_id}/start` - Start discussion
   - `POST /discussions/{discussion_id}/pause` - Pause discussion
   - `POST /discussions/{discussion_id}/resume` - Resume discussion
   - `POST /discussions/{discussion_id}/stop` - Stop discussion
   - `POST /discussions/{discussion_id}/inject-question` - Inject question
   - `GET /discussions/{discussion_id}/messages` - Get messages

### Key Features

- **Dependency injection** for authentication and database
- **Proper status codes** (201, 202, etc.)
- **Comprehensive docstrings** for all endpoints
- **Type hints** with Annotated types
- **Tagged routes** for API documentation
- **TODO comments** for implementation guidance

## Design Patterns

### Request Validation
- All request bodies use Pydantic schemas
- Field-level validation constraints
- Clear error messages on validation failure

### Response Formatting
- Consistent response structure across endpoints
- Proper HTTP status codes
- Resource representation without sensitive data

### Authentication
- JWT-based authentication via HTTPBearer
- Protected routes use `Depends(get_current_user)`
- User data available in all protected endpoints

### Pagination
- `PaginationParams` for query parameters
- `PaginatedResponse[T]` generic wrapper
- Consistent pagination interface

### Error Handling
- Custom exceptions in `app.core.exceptions`
- Standardized error response format
- Request ID tracking for debugging

## Integration Points

### With Models
All response schemas have `from_attributes = True` to support ORM model conversion:
```python
user = await db.get(User, user_id)
return UserResponse.model_validate(user)
```

### With Security
Authentication uses `app.core.security` functions:
- `verify_token()` - JWT validation
- Token creation via `create_access_token()` and `create_refresh_token()`

### With Database
Database session dependency provides async SQLAlchemy session:
```python
async def endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(query)
    return result.scalars().all()
```

## Next Steps

### Implementation Priority

1. **Service Layer** - Implement business logic in `app/services/`
2. **Repository Layer** - Create data access layer (optional)
3. **Error Handlers** - Implement global exception handlers
4. **Testing** - Write unit and integration tests
5. **Documentation** - Set up automatic OpenAPI documentation

### Missing Components

The following components are stubbed with `raise NotImplementedError`:

- All authentication logic (register, login, token refresh)
- All CRUD operations (create, read, update, delete)
- Discussion engine orchestration
- Report generation
- API key encryption/decryption
- Email sending (verification, password reset)

### Integration Checklist

- [ ] Set up database connection pool
- [ ] Configure JWT secret key and settings
- [ ] Set up encryption keys for API keys
- [ ] Configure email service for notifications
- [ ] Set up Redis for caching
- [ ] Configure rate limiting
- [ ] Set up CORS middleware
- [ ] Configure WebSocket support
- [ ] Set up request ID middleware
- [ ] Configure logging

## File Structure

```
backend/app/
├── schemas/
│   ├── __init__.py
│   ├── common.py
│   ├── auth.py
│   ├── user.py
│   ├── topic.py
│   ├── character.py
│   ├── discussion.py
│   └── report.py
├── api/
│   ├── __init__.py
│   ├── deps.py
│   └── v1/
│       ├── __init__.py
│       ├── auth.py
│       ├── users.py
│       ├── topics.py
│       ├── characters.py
│       └── discussions.py
```

## Notes

- All code and comments are in English as required
- Pydantic v2 syntax with modern type hints
- Database models use SQLAlchemy 2.0 async
- Security module already implements JWT and encryption
- Exception classes defined in `app.core.exceptions`
- Follows backend design document specifications

## Testing Syntax

All files have been checked for syntax errors:
```bash
python3 -m py_compile backend/app/schemas/*.py
python3 -m py_compile backend/app/api/v1/*.py backend/app/api/deps.py
```

All files pass syntax validation.
