"""Endpoints for on-demand AI recommendations on completed audits."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.ai.models import AIRecommendationResult
from backend.database.session import get_db
from backend.services.multi_page_recommendation_service import MultiPageRecommendationService


router = APIRouter(prefix="/scans", tags=["Recommendations"])


@router.post(
    "/{scan_id}/recommendations",
    response_model=AIRecommendationResult,
    status_code=status.HTTP_200_OK,
)
def generate_recommendations_for_scan(
    scan_id: int,
    db: Session = Depends(get_db),
) -> AIRecommendationResult:
    """Generate beginner-friendly AI explanations for one persisted scan."""
    result = MultiPageRecommendationService().generate_for_scan(db, scan_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return result
