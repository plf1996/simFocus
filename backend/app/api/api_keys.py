from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from typing import Any

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyUpdate,
    APIKeyResponse
)
from app.services.api_key_service import APIKeyService


router = APIRouter(prefix="/api/users/me/api-keys", tags=["API Keys"])


@router.get("", response_model=List[APIKeyResponse])
async def get_api_keys(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all API keys for current user"""
    service = APIKeyService(db)
    api_keys = await service.get_user_api_keys(current_user.id)
    return [APIKeyResponse.model_validate(key) for key in api_keys]


@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key"""
    service = APIKeyService(db)
    try:
        api_key = await service.create_api_key(current_user.id, api_key_data)
        return APIKeyResponse.model_validate(api_key)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific API key"""
    service = APIKeyService(db)
    api_key = await service.get_api_key_by_id(key_id, current_user.id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return APIKeyResponse.model_validate(api_key)


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: UUID,
    api_key_data: APIKeyUpdate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update API key metadata (cannot change actual key)"""
    service = APIKeyService(db)
    api_key = await service.update_api_key(key_id, current_user.id, api_key_data)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return APIKeyResponse.model_validate(api_key)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    service = APIKeyService(db)
    success = await service.delete_api_key(key_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
