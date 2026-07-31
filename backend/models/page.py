"""
Page model for RankPilot AI.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


class Page(Base):
    """
    Represents a webpage discovered during a scan.
    """

    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    scan_id: Mapped[int] = mapped_column(
        ForeignKey("scans.id"),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    meta_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    h1: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    canonical_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    load_time: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    word_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_indexable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship with Scan
    scan = relationship(
        "Scan",
        back_populates="pages",
    )

    # Relationship with SEO Issues
    seo_issues = relationship(
        "SEOIssue",
        back_populates="page",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Page(id={self.id}, "
            f"url='{self.url}', "
            f"status_code={self.status_code})>"
        )