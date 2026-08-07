"""Score engine for SEO analysis."""

from backend.score.calculator import calculate_score
from backend.score.models import ScoreResult
from backend.seo.models import SEOIssue


def analyze_score(issues: list[SEOIssue]) -> ScoreResult:
    """
    Generate an SEO score from a list of SEO issues.
    """
    return calculate_score(issues)