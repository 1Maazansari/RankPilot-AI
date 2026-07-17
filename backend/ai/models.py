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


class AIRecommendationResult(BaseModel):
    """Collection of AI-generated recommendations."""

    recommendations: list[AIRecommendation]