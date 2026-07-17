"""Pydantic models for SEO rule engine results."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Severity(StrEnum):
    """Severity levels for SEO issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(StrEnum):
    """SEO rule categories."""

    METADATA = "metadata"
    HEADINGS = "headings"
    IMAGES = "images"
    LINKS = "links"
    TECHNICAL = "technical"
    SOCIAL = "social"


class SEOIssue(BaseModel):
    """A single SEO issue reported by a rule."""

    model_config = ConfigDict(use_enum_values=True)

    rule_id: str
    severity: Severity
    category: Category
    message: str
    recommendation: str
