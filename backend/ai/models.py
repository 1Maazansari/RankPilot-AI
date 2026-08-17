"""Pydantic models for AI recommendations."""

from pydantic import BaseModel, Field


class AIRecommendation(BaseModel):
    """A single AI-generated SEO recommendation."""

    priority: int = Field(..., ge=1)
    title: str
    reason: str
    impact: str
    estimated_effort: str
    action: str
    source_issue_type: str | None = None
    affected_page_count: int = Field(default=0, ge=0)
    affected_urls: list[str] = Field(default_factory=list)
    example: str | None = None


class AIRecommendationResult(BaseModel):
    """Collection of AI-generated recommendations."""

    recommendations: list[AIRecommendation]
