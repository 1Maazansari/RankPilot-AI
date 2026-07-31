"""
AI Recommendation model for RankPilot AI.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class AIRecommendation(Base):
    """
    Represents an AI-generated recommendation for an SEO issue.
    """

    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    seo_issue_id: Mapped[int] = mapped_column(
        ForeignKey("seo_issues.id"),
        nullable=False,
    )

    recommendation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    priority_score: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship with SEOIssue
    seo_issue = relationship(
        "SEOIssue",
        back_populates="ai_recommendations",
    )

    def __repr__(self) -> str:
        return (
            f"<AIRecommendation(id={self.id}, "
            f"priority={self.priority_score})>"
        )