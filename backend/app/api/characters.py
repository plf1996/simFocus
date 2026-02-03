from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any
from uuid import UUID
from typing import Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

if False:
    from app.models.user import User

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListItem
)
from app.services.character_service import CharacterService
from app.services.embedding_service import (
    get_embedding_service,
    build_character_text,
    build_topic_text,
    compute_weighted_score
)
from app.models.character import Character


router = APIRouter(prefix="/api/characters", tags=["Characters"])


@router.get("/templates", response_model=List[CharacterListItem])
async def get_character_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get system template characters (no auth required)"""
    service = CharacterService(db)
    characters = await service.get_template_characters(skip, limit)
    return [CharacterListItem.model_validate(char) for char in characters]


@router.get("/templates/random", response_model=List[CharacterListItem])
async def get_random_templates(
    count: int = Query(5, ge=1, le=7),
    db: AsyncSession = Depends(get_db)
):
    """Get random template characters for recommendations"""
    service = CharacterService(db)
    characters = await service.get_random_templates(count)
    return [CharacterListItem.model_validate(char) for char in characters]


@router.get("/templates/{character_id}", response_model=CharacterResponse)
async def get_template_character(
    character_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template character"""
    service = CharacterService(db)
    character = await service.get_character_by_id(character_id)

    if not character or not character.is_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template character not found"
        )

    return CharacterResponse.model_validate(character)


@router.get("", response_model=List[CharacterListItem])
async def get_my_characters(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get custom characters for current user"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    service = CharacterService(db)
    characters = await service.get_user_characters(current_user.id, skip, limit)
    return [CharacterListItem.model_validate(char) for char in characters]


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_data: CharacterCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a custom character"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    service = CharacterService(db)
    character = await service.create_character(current_user.id, character_data)
    return CharacterResponse.model_validate(character)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific custom character"""
    service = CharacterService(db)
    character = await service.get_character_by_id(character_id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    # Check if user owns this character
    if character.user_id != current_user.id and not character.is_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this character"
        )

    return CharacterResponse.model_validate(character)


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: UUID,
    character_data: CharacterUpdate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a custom character"""
    service = CharacterService(db)
    try:
        character = await service.update_character(character_id, current_user.id, character_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    return CharacterResponse.model_validate(character)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a custom character"""
    service = CharacterService(db)
    try:
        success = await service.delete_character(character_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )


@router.get("/search", response_model=List[CharacterListItem])
async def search_characters(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Search template characters"""
    service = CharacterService(db)
    characters = await service.search_characters(query, skip, limit)
    return [CharacterListItem.model_validate(char) for char in characters]


@router.post("/recommend", response_model=List[CharacterListItem])
async def recommend_characters(
    topic: Dict[str, str] = Body(..., description="Topic with title and description"),
    count: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Recommend characters based on topic content using semantic similarity

    Args:
        topic: Dictionary with 'title' and 'description' fields
        count: Number of recommendations to return (max 20)

    Returns:
        List of recommended characters sorted by similarity
    """
    try:
        # Get embedding service
        embedding_service = get_embedding_service()

        # Build topic text and encode (using enhanced mode)
        topic_text = build_topic_text(topic, enhanced=True)
        topic_embedding = await embedding_service.encode_text(topic_text)

        # Fetch all template characters
        result = await db.execute(
            select(Character).where(Character.is_template == True)
        )
        characters = result.scalars().all()

        if not characters:
            return []

        # Build character texts
        character_dicts = []
        for char in characters:
            char_dict = {
                "id": str(char.id),
                "name": char.name,
                "config": char.config,
                "avatar_url": char.avatar_url,
                "is_template": char.is_template,
                "is_public": char.is_public,
                "usage_count": char.usage_count or 0,
                "rating_avg": char.rating_avg or 0.0,
                "rating_count": char.rating_count or 0
            }
            character_dicts.append(char_dict)

        # Build character texts for embedding (using enhanced mode)
        character_texts = [build_character_text(c, enhanced=True) for c in character_dicts]

        # Encode all characters in batch
        character_embeddings = await embedding_service.encode_texts_batch(character_texts)

        # Debug: log embedding dimensions
        logger.info(f"Topic embedding shape: {topic_embedding.shape}")
        logger.info(f"Character embeddings shape: {character_embeddings.shape}")
        logger.info(f"Service embedding_dim: {embedding_service.embedding_dim}")

        # Compute semantic similarities
        similarities = embedding_service.compute_similarities(
            topic_embedding,
            character_embeddings
        )

        # Debug: log similarity stats
        logger.info(f"Similarities computed: {len(similarities)} values")
        logger.info(f"Similarity range: [{similarities.min():.4f}, {similarities.max():.4f}]")
        logger.info(f"Top 5 similarities: {sorted(similarities, reverse=True)[:5]}")

        # Compute weighted scores (semantic similarity + popularity + rating)
        weighted_scores = []
        for i, char_dict in enumerate(character_dicts):
            semantic_sim = float(similarities[i])
            weighted_score = compute_weighted_score(
                semantic_sim,
                char_dict,
                weights={"similarity": 0.7, "usage_count": 0.2, "rating": 0.1}
            )
            weighted_scores.append((i, weighted_score, semantic_sim))

        # Sort by weighted score (descending)
        weighted_scores.sort(key=lambda x: x[1], reverse=True)

        # Get top N characters
        recommended_characters = []
        for idx, weighted_score, semantic_sim in weighted_scores[:count]:
            char_dict = character_dicts[idx].copy()
            char_dict["similarity_score"] = semantic_sim
            char_dict["weighted_score"] = weighted_score
            recommended_characters.append(char_dict)

        # Convert to response models
        return [
            CharacterListItem(
                id=UUID(char["id"]),
                name=char["name"],
                avatar_url=char.get("avatar_url"),
                is_template=char["is_template"],
                is_public=char["is_public"],
                config=char["config"],
                usage_count=char["usage_count"],
                rating_avg=char["rating_avg"],
                rating_count=char["rating_count"],
                similarity_score=float(char["similarity_score"]) if char.get("similarity_score") is not None else None,
                weighted_score=float(char["weighted_score"]) if char.get("weighted_score") is not None else None
            )
            for char in recommended_characters
        ]

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
