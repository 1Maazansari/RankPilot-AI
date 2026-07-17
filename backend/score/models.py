"""Pydantic models for SEO score results."""

from pydantic import BaseModel


class ScoreSummary(BaseModel):
    """Counts of SEO issues grouped by severity."""

    critical: int
    high: int
    medium: int
    low: int


class ScoreResult(BaseModel):
    """Final SEO score result and severity summary."""

    score: int
    grade: str
    summary: ScoreSummary
