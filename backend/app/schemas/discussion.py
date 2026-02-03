from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class DiscussionBase(BaseModel):
    topic_id: UUID
    discussion_mode: str = Field(default="free", description="'free', 'structured', 'creative', 'consensus'")
    max_rounds: int = Field(default=3, ge=1, le=10, description="Number of discussion rounds (recommended: 3-5)")


class DiscussionCreate(DiscussionBase):
    character_ids: List[UUID] = Field(..., min_length=3, max_length=7, description="3-7 characters required")


class DiscussionUpdate(BaseModel):
    status: Optional[str] = None
    max_rounds: Optional[int] = Field(None, ge=5, le=30)


class DiscussionResponse(DiscussionBase):
    id: UUID
    user_id: UUID
    status: str
    current_round: int
    current_phase: str
    progress_percentage: float = 0.0
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    total_tokens_used: int
    estimated_cost_usd: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiscussionListItem(BaseModel):
    id: UUID
    topic_id: UUID
    topic_title: str
    status: str
    current_round: int
    max_rounds: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiscussionControl(BaseModel):
    action: str = Field(..., description="'pause', 'resume', 'stop', 'inject_question'")
    speed: Optional[float] = Field(None, ge=1.0, le=3.0, description="Playback speed multiplier")
    question: Optional[str] = Field(None, description="Question to inject (for action='inject_question')")


class DiscussionStatus(BaseModel):
    status: str
    current_round: int
    total_rounds: int
    current_phase: str
    progress_percentage: float
