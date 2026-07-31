"""
Database models for RankPilot AI.
"""

from backend.models.project import Project
from backend.models.scan import Scan
from backend.models.page import Page
from backend.models.seo_issue import SEOIssue
from backend.models.ai_recommendation import AIRecommendation

__all__ = [
    "Project",
    "Scan",
    "Page",
    "SEOIssue",
    "AIRecommendation",
]