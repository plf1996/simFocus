from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class TopicBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    context: Optional[str] = None


class TopicCreate(TopicBase):
    attachments: Optional[List[dict]] = None  # Array of file metadata


class TopicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    context: Optional[str] = None
    status: Optional[str] = None  # 'draft', 'ready', 'in_discussion', 'completed'


class TopicResponse(TopicBase):
    id: UUID
    user_id: UUID
    status: str
    attachments: Optional[List[dict]] = None
    template_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicListItem(BaseModel):
    id: UUID
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicWithDiscussion(TopicResponse):
    """Topic with associated discussion info"""
    discussion_id: Optional[UUID] = None
    discussion_status: Optional[str] = None
