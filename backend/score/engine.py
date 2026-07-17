"""Score engine for SEO analysis."""

from seo.models import SEOIssue

from score.calculator import calculate_score
from score.models import ScoreResult


def analyze_score(issues: list[SEOIssue]) -> ScoreResult:
    """
    Generate an SEO score from a list of SEO issues.
    """
    return calculate_score(issues)