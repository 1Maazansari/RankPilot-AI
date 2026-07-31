"""
AI Recommendation repository.
"""

from backend.models.ai_recommendation import AIRecommendation
from backend.repositories.base_repository import BaseRepository


class AIRecommendationRepository(BaseRepository[AIRecommendation]):
    """Repository for AIRecommendation model."""

    def __init__(self):
        super().__init__(AIRecommendation)