from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class MessageBase(BaseModel):
    content: str
    phase: str
    round: int


class MessageResponse(MessageBase):
    id: UUID
    discussion_id: UUID
    participant_id: UUID
    character_name: str
    character_avatar_url: Optional[str] = None
    token_count: Optional[int] = None
    is_injected_question: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageStreamChunk(BaseModel):
    """For streaming message chunks via WebSocket"""
    message_id: UUID
    character_id: UUID
    character_name: str
    content_chunk: str
    is_complete: bool = False
    timestamp: datetime
