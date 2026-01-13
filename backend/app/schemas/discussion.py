"""
Discussion schemas

Provides request/response schemas for discussion operations.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class DiscussionCreateRequest(BaseModel):
    """Discussion creation request."""

    topic_id: str = Field(
        ...,
        description="Topic ID to discuss"
    )
    character_ids: list[str] = Field(
        ...,
        min_length=3,
        max_length=7,
        description="Character IDs to participate (3-7 characters)"
    )
    discussion_mode: str = Field(
        default='free',
        pattern='^(free|structured|creative|consensus)$',
        description="Discussion mode"
    )
    max_rounds: int = Field(
        default=10,
        ge=5,
        le=20,
        description="Maximum discussion rounds"
    )


class DiscussionResponse(BaseModel):
    """Discussion summary response."""

    id: str = Field(
        ...,
        description="Discussion ID"
    )
    topic_id: str = Field(
        ...,
        description="Associated topic ID"
    )
    user_id: str = Field(
        ...,
        description="Creator user ID"
    )
    discussion_mode: str = Field(
        ...,
        description="Discussion mode"
    )
    max_rounds: int = Field(
        ...,
        ge=5,
        le=20,
        description="Maximum rounds"
    )
    status: str = Field(
        ...,
        description="Current status"
    )
    current_round: int = Field(
        ...,
        ge=0,
        description="Current round number"
    )
    current_phase: str = Field(
        ...,
        description="Current discussion phase"
    )
    llm_provider: str = Field(
        ...,
        description="LLM provider used"
    )
    llm_model: str = Field(
        ...,
        description="LLM model used"
    )
    total_tokens_used: int = Field(
        ...,
        ge=0,
        description="Total tokens consumed"
    )
    estimated_cost_usd: float | None = Field(
        None,
        ge=0,
        description="Estimated cost in USD"
    )
    started_at: datetime | None = Field(
        None,
        description="Start timestamp"
    )
    completed_at: datetime | None = Field(
        None,
        description="Completion timestamp"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )

    model_config = {
        "from_attributes": True
    }


class DiscussionListResponse(BaseModel):
    """Discussion list item (summary view)."""

    id: str = Field(
        ...,
        description="Discussion ID"
    )
    title: str = Field(
        ...,
        description="Topic title"
    )
    status: str = Field(
        ...,
        description="Discussion status"
    )
    discussion_mode: str = Field(
        ...,
        description="Discussion mode"
    )
    participant_count: int = Field(
        ...,
        ge=0,
        description="Number of participants"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    completed_at: datetime | None = Field(
        None,
        description="Completion timestamp"
    )


class ParticipantResponse(BaseModel):
    """Discussion participant response."""

    id: str = Field(
        ...,
        description="Participant ID"
    )
    character_id: str = Field(
        ...,
        description="Character ID"
    )
    character_name: str = Field(
        ...,
        description="Character name"
    )
    position: int | None = Field(
        None,
        description="Speaking position (for structured mode)"
    )
    stance: str | None = Field(
        None,
        description="Stance (for structured mode)"
    )
    message_count: int = Field(
        ...,
        ge=0,
        description="Number of messages sent"
    )


class MessageResponse(BaseModel):
    """Discussion message response."""

    id: str = Field(
        ...,
        description="Message ID"
    )
    participant_id: str = Field(
        ...,
        description="Sender participant ID"
    )
    character_name: str = Field(
        ...,
        description="Character name"
    )
    character_avatar: str | None = Field(
        None,
        description="Character avatar URL"
    )
    round: int = Field(
        ...,
        ge=0,
        description="Discussion round number"
    )
    phase: str = Field(
        ...,
        description="Discussion phase"
    )
    content: str = Field(
        ...,
        description="Message content"
    )
    token_count: int = Field(
        ...,
        ge=0,
        description="Approximate token count"
    )
    is_injected_question: bool = Field(
        ...,
        description="Whether this is an injected question"
    )
    created_at: datetime = Field(
        ...,
        description="Message timestamp"
    )


class DiscussionDetailResponse(DiscussionResponse):
    """Full discussion details with participants and messages."""

    topic: dict = Field(
        ...,
        description="Topic details"
    )
    participants: list[ParticipantResponse] = Field(
        ...,
        description="Discussion participants"
    )
    messages: list[MessageResponse] = Field(
        ...,
        description="Discussion messages"
    )


class InjectQuestionRequest(BaseModel):
    """Inject question into active discussion."""

    question: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Question to inject into discussion"
    )


class DiscussionControlRequest(BaseModel):
    """Discussion control request."""

    action: str = Field(
        ...,
        pattern='^(pause|resume|stop)$',
        description="Control action"
    )
