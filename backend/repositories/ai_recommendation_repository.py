"""
AI Recommendation repository.
"""

from backend.models.ai_recommendation import AIRecommendation
from backend.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class AIRecommendationRepository(BaseRepository[AIRecommendation]):
    """Repository for AIRecommendation model."""

    def __init__(self):
        super().__init__(AIRecommendation)

    def create_many(
        self,
        db: Session,
        recommendations: list[AIRecommendation],
    ) -> list[AIRecommendation]:
        """Persist recommendation records in one transaction."""
        try:
            db.add_all(recommendations)
            db.commit()
            for recommendation in recommendations:
                db.refresh(recommendation)
            return recommendations
        except Exception:
            db.rollback()
            raise
