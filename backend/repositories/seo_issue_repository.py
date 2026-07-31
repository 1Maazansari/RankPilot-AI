"""
SEO Issue repository.
"""

from backend.models.seo_issue import SEOIssue
from backend.repositories.base_repository import BaseRepository


class SEOIssueRepository(BaseRepository[SEOIssue]):
    """Repository for SEOIssue model."""

    def __init__(self):
        super().__init__(SEOIssue)