"""
Repository layer.
"""

from backend.repositories.project_repository import ProjectRepository
from backend.repositories.scan_repository import ScanRepository
from backend.repositories.page_repository import PageRepository
from backend.repositories.seo_issue_repository import SEOIssueRepository
from backend.repositories.ai_recommendation_repository import AIRecommendationRepository

__all__ = [
    "ProjectRepository",
    "ScanRepository",
    "PageRepository",
    "SEOIssueRepository",
    "AIRecommendationRepository",
]