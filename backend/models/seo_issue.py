"""
SEO Issue model for RankPilot AI.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class IssueSeverity(str, Enum):
    """Severity levels for SEO issues."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SEOIssue(Base):
    """
    Represents an SEO issue detected on a page.
    """

    __tablename__ = "seo_issues"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    page_id: Mapped[int] = mapped_column(
        ForeignKey("pages.id"),
        nullable=False,
    )

    issue_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[IssueSeverity] = mapped_column(
        SQLEnum(IssueSeverity),
        nullable=False,
    )

    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship with Page
    page = relationship(
        "Page",
        back_populates="seo_issues",
    )

    ai_recommendations = relationship(
    "AIRecommendation",
    back_populates="seo_issue",
    cascade="all, delete-orphan",
)

    def __repr__(self) -> str:
        return (
            f"<SEOIssue(id={self.id}, "
            f"type='{self.issue_type}', "
            f"severity='{self.severity.value}')>"
        )