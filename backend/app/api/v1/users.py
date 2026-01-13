"""
User management API routes

Provides endpoints for user profile management and API key operations.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_user,
    get_user_service,
    get_api_key_service,
)
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.user import (
    APIKeyCreateRequest,
    APIKeyResponse,
    APIKeyUpdateRequest,
    UserResponse,
    UserStatsResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get authenticated user's profile information.

    Returns email, name, avatar, bio, and account metadata.
    """
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update user profile",
)
async def update_user_profile(
    data: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Update user profile information.

    Allows updating name, avatar URL, and bio.
    """
    updated_user = await user_service.update_profile(
        user_id=str(current_user.id),
        name=data.name,
        avatar_url=data.avatar_url,
        bio=data.bio,
    )
    return updated_user


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete user account",
)
async def delete_user_account(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Permanently delete user account and all associated data.

    This operation cannot be undone. All data including topics,
    discussions, characters, and API keys will be deleted.
    """
    await user_service.delete_account(
        user_id=str(current_user.id),
        password=None,  # OAuth users can delete without password
    )
    return MessageResponse(message="Account deleted successfully")


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Get user statistics",
)
async def get_user_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Get user usage statistics.

    Returns totals for discussions, topics, characters, tokens used,
    and estimated costs.
    """
    stats = await user_service.get_statistics(user_id=str(current_user.id))
    return stats


@router.get(
    "/me/api-keys",
    response_model=list[APIKeyResponse],
    summary="List user API keys",
)
async def list_api_keys(
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """
    Get all API keys for current user.

    Returns list without the actual key values for security.
    """
    api_keys = await api_key_service.list_api_keys(user_id=str(current_user.id))
    return api_keys


@router.post(
    "/me/api-keys",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add new API key",
)
async def create_api_key(
    data: APIKeyCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """
    Add a new LLM API key.

    The key will be encrypted using AES-256-GCM before storage.
    Supports OpenAI, Anthropic, and custom API endpoints.
    """
    api_key = await api_key_service.create_api_key(
        user_id=str(current_user.id),
        provider=data.provider,
        key_name=data.key_name,
        api_key=data.api_key,
        api_base_url=data.api_base_url,
        default_model=data.default_model,
    )
    return api_key


@router.delete(
    "/me/api-keys/{key_id}",
    response_model=MessageResponse,
    summary="Delete API key",
)
async def delete_api_key(
    key_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """
    Delete an API key.

    Permanently removes the API key from user's account.
    """
    await api_key_service.delete_api_key(
        user_id=str(current_user.id),
        api_key_id=key_id,
    )
    return MessageResponse(message="API key deleted successfully")


@router.patch(
    "/me/api-keys/{key_id}",
    response_model=APIKeyResponse,
    summary="Update API key",
)
async def update_api_key(
    key_id: str,
    data: APIKeyUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """
    Update API key metadata.

    Allows updating key name, API base URL, default model, and active status.
    Does not allow updating the actual key value (create new key for that).
    """
    updated_key = await api_key_service.update_api_key(
        user_id=str(current_user.id),
        api_key_id=key_id,
        key_name=data.key_name,
        is_active=data.is_active,
        default_model=data.default_model,
    )
    return updated_key
