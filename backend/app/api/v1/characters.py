"""
Character management API routes

Provides endpoints for creating and managing AI characters.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_character_service, get_current_user_optional
from app.models.user import User
from app.schemas.character import (
    CharacterCreateRequest,
    CharacterResponse,
    CharacterTemplateResponse,
    CharacterUpdateRequest,
)
from app.schemas.common import MessageResponse
from app.services.character_service import CharacterService

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get(
    "",
    response_model=list[CharacterResponse],
    summary="List user characters",
)
async def list_characters(
    current_user: Annotated[User, Depends(get_current_user)],
    character_service: Annotated[CharacterService, Depends(get_character_service)],
):
    """
    Get all characters created by user.

    Returns both custom characters and used templates.
    """
    characters = await character_service.list_characters(
        user_id=str(current_user.id),
        include_templates=True,
        limit=100,
    )
    return characters


@router.post(
    "",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create custom character",
)
async def create_character(
    data: CharacterCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    character_service: Annotated[CharacterService, Depends(get_character_service)],
):
    """
    Create a new custom character.

    - **name**: Character display name (2-100 characters)
    - **avatar_url**: Optional avatar image URL
    - **config**: Complete character configuration
    - **is_public**: Whether to share with other users
    """
    character = await character_service.create_character(
        user_id=str(current_user.id),
        name=data.name,
        config=data.config,
        avatar_url=data.avatar_url,
        is_public=data.is_public,
    )
    return character


@router.get(
    "/templates",
    response_model=list[CharacterTemplateResponse],
    summary="List character templates",
)
async def list_character_templates(
    character_service: Annotated[CharacterService, Depends(get_character_service)],
    category: Annotated[str | None, Query(description="Filter by category")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 50,
):
    """
    Get system preset character templates.

    - **category**: Optional filter by category
    - **limit**: Maximum number of results (default 50)

    Returns system templates available for all users.
    """
    templates = await character_service.list_templates(
        category=category,
        limit=limit,
    )
    return templates


@router.get(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Get character by ID",
)
async def get_character(
    character_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    character_service: Annotated[CharacterService, Depends(get_character_service)],
):
    """
    Get character details.

    Returns full character configuration including personality traits and knowledge background.
    """
    character = await character_service.get_character(character_id=character_id)
    return character


@router.patch(
    "/{character_id}",
    response_model=CharacterResponse,
    summary="Update character",
)
async def update_character(
    character_id: str,
    data: CharacterUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    character_service: Annotated[CharacterService, Depends(get_character_service)],
):
    """
    Update character configuration.

    Only custom characters can be updated (not system templates).
    """
    character = await character_service.update_character(
        character_id=character_id,
        user_id=str(current_user.id),
        name=data.name,
        config=data.config,
        avatar_url=data.avatar_url,
        is_public=data.is_public,
    )
    return character


@router.delete(
    "/{character_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete character",
)
async def delete_character(
    character_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    character_service: Annotated[CharacterService, Depends(get_character_service)],
):
    """
    Delete character.

    Only custom characters can be deleted.
    Cannot delete characters used in active discussions.
    """
    await character_service.delete_character(
        character_id=character_id,
        user_id=str(current_user.id),
    )
    return MessageResponse(message="Character deleted successfully")


@router.post(
    "/{character_id}/rate",
    response_model=MessageResponse,
    summary="Rate character",
)
async def rate_character(
    character_id: str,
    rating: Annotated[int, Query(ge=1, le=5, description="Rating from 1 to 5")],
    current_user: Annotated[User, Depends(get_current_user)],
    character_service: Annotated[CharacterService, Depends(get_character_service)],
):
    """
    Rate character quality.

    Submit a rating from 1 to 5 stars for a character.
    Used to improve template quality.
    """
    await character_service.rate_character(
        character_id=character_id,
        user_id=str(current_user.id),
        rating=rating,
    )
    return MessageResponse(message="Character rated successfully")
