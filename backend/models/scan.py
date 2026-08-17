"""
Scan model for RankPilot AI.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base



class ScanStatus(str, Enum):
    """Status of a scan."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Scan(Base):
    """Represents a scan performed on a project."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    status: Mapped[ScanStatus] = mapped_column(
        SQLEnum(ScanStatus),
        default=ScanStatus.PENDING,
        nullable=False,
    )

    seo_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    requested_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    max_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failed_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    crawl_complete: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    grade: Mapped[str | None] = mapped_column(String(2), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationship with Project
    project = relationship(
        "Project",
        back_populates="scans",
    )
    # Relationship with Pages
    pages = relationship(
        "Page",
        back_populates="scan",
        cascade="all, delete-orphan",
    )
    seo_issues = relationship(
        "SEOIssue",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Scan(id={self.id}, "
            f"project_id={self.project_id}, "
            f"status='{self.status.value}')>"
        )
