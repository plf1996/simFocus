from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ReportOverview(BaseModel):
    topic_title: str
    discussion_duration_seconds: int
    total_rounds: int
    total_messages: int
    participant_count: int
    llm_provider: str
    llm_model: str


class ViewpointSummary(BaseModel):
    character_id: UUID
    character_name: str
    stance: str
    core_arguments: List[str]
    position_evolution: Optional[List[Dict[str, Any]]] = None


class Consensus(BaseModel):
    agreements: List[str]
    joint_recommendations: List[str]
    supporting_arguments: List[str]


class ControversyPoint(BaseModel):
    topic: str
    viewpoints: Dict[str, List[str]]  # {character_name: arguments}
    unresolved: bool


class Insight(BaseModel):
    description: str
    related_messages: List[UUID]


class Recommendation(BaseModel):
    action: str
    rationale: str
    priority: str


class QualityScores(BaseModel):
    depth: float  # 0-100
    diversity: float
    constructive: float
    coherence: float
    overall: float


class ReportResponse(BaseModel):
    id: UUID
    discussion_id: UUID
    overview: Optional[Dict[str, Any]] = None
    viewpoints_summary: Optional[List[Dict[str, Any]]] = None
    consensus: Optional[Dict[str, Any]] = None
    controversies: Optional[List[Dict[str, Any]]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    quality_scores: Optional[Dict[str, float]] = None
    generation_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
