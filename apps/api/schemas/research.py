"""
Pydantic schemas for API request/response models.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Request Models ──────────────────────────────────────────

class ResearchRequest(BaseModel):
    """Request body for starting a new research run."""
    question: str = Field(..., min_length=5, max_length=2000, description="The research question")
    depth: str = Field("standard", pattern="^(quick|standard|deep)$")
    sources: list[str] = Field(default=["web"], description="Source types to search")
    max_sources: int = Field(20, ge=5, le=50)
    require_citation_verification: bool = True
    allow_autonomous_research: bool = True


# ── Response Models ─────────────────────────────────────────

class ResearchResponse(BaseModel):
    """Response after creating a research run."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    status: str
    created_at: datetime


class ClaimResponse(BaseModel):
    """A single claim with its verdict and confidence."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    verdict: str
    confidence: float
    evidence_span: Optional[str] = None
    source_id: Optional[UUID] = None
    created_at: datetime


class SourceResponse(BaseModel):
    """A discovered source with metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    source_type: Optional[str] = None
    published_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    created_at: datetime


class EventResponse(BaseModel):
    """An agent execution event."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agent_name: str
    event_type: str
    data: dict
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    created_at: datetime


class ResearchDetailResponse(ResearchResponse):
    """Full research run details with claims and sources."""
    model_config = ConfigDict(from_attributes=True)

    depth: Optional[str] = None
    config: Optional[dict] = None
    result: Optional[dict] = None
    stats: Optional[dict] = None
    updated_at: Optional[datetime] = None
