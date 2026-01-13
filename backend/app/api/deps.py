"""
FastAPI dependencies

Provides common dependency functions for route handlers including
database sessions, authentication, and service layer injection.
"""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import async_session
from app.models.user import User
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.topic_service import TopicService
from app.services.character_service import CharacterService
from app.services.discussion_service import DiscussionService
from app.services.api_key_service import ApiKeyService


# Security scheme for JWT tokens
security = HTTPBearer()


async def get_db():
    """
    Get database session.

    Yields:
        Async database session
    """
    async with async_session() as session:
        yield session


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get authenticated user from JWT token.

    Args:
        token: HTTP Bearer token
        db: Database session

    Returns:
        Authenticated user object

    Raises:
        UnauthorizedException: If token is invalid
        ForbiddenException: If user not found or deleted
    """
    try:
        # Verify token and get user ID
        payload = verify_token(token.credentials, token_type="access")
        user_id = payload.get("sub")

        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        # Fetch user from database
        user = await db.get(User, user_id)

        if not user:
            raise ForbiddenException("User not found")

        if not user.is_active:
            raise ForbiddenException("User account is disabled")

        return user

    except UnauthorizedException:
        raise
    except Exception as e:
        raise UnauthorizedException(f"Authentication failed: {str(e)}")


async def get_current_user_optional(
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    Get authenticated user if token provided, otherwise None.

    Args:
        token: Optional HTTP Bearer token
        db: Database session

    Returns:
        User object if token valid, None otherwise
    """
    if not token:
        return None

    try:
        payload = verify_token(token.credentials, token_type="access")
        user_id = payload.get("sub")

        if not user_id:
            return None

        user = await db.get(User, user_id)

        if not user or not user.is_active:
            return None

        return user

    except Exception:
        return None


async def get_request_id(
    x_request_id: Annotated[str | None, Header()] = None,
) -> str:
    """
    Get or generate request ID for tracing.

    Args:
        x_request_id: Optional X-Request-ID header

    Returns:
        Request ID string
    """
    import uuid
    return x_request_id or str(uuid.uuid4())


# Service layer dependencies

async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    """
    Get authentication service instance.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    return AuthService(db)


async def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    """
    Get user service instance.

    Args:
        db: Database session

    Returns:
        UserService instance
    """
    return UserService(db)


async def get_topic_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TopicService:
    """
    Get topic service instance.

    Args:
        db: Database session

    Returns:
        TopicService instance
    """
    return TopicService(db)


async def get_character_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CharacterService:
    """
    Get character service instance.

    Args:
        db: Database session

    Returns:
        CharacterService instance
    """
    return CharacterService(db)


async def get_discussion_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiscussionService:
    """
    Get discussion service instance.

    Args:
        db: Database session

    Returns:
        DiscussionService instance
    """
    return DiscussionService(db)


async def get_api_key_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ApiKeyService:
    """
    Get API key service instance.

    Args:
        db: Database session

    Returns:
        ApiKeyService instance
    """
    return ApiKeyService(db)
