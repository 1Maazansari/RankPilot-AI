"""Core SEO score calculation logic."""

from backend.score.constants import (
    MAX_SCORE,
    CRITICAL_PENALTY,
    HIGH_PENALTY,
    MEDIUM_PENALTY,
    LOW_PENALTY,
    GRADE_A,
    GRADE_B,
    GRADE_C,
    GRADE_D,
)
from backend.score.models import ScoreResult, ScoreSummary
from backend.seo.models import SEOIssue, Severity


def calculate_score(issues: list[SEOIssue]) -> ScoreResult:
    """
    Calculate the SEO score based on issue severity.
    """

    critical = 0
    high = 0
    medium = 0
    low = 0

    for issue in issues:
        if issue.severity == Severity.CRITICAL:
            critical += 1
        elif issue.severity == Severity.HIGH:
            high += 1
        elif issue.severity == Severity.MEDIUM:
            medium += 1
        elif issue.severity == Severity.LOW:
            low += 1

    penalty = (
        critical * CRITICAL_PENALTY
        + high * HIGH_PENALTY
        + medium * MEDIUM_PENALTY
        + low * LOW_PENALTY
    )

    score = max(0, min(MAX_SCORE, MAX_SCORE - penalty))

    if score >= GRADE_A:
        grade = "A"
    elif score >= GRADE_B:
        grade = "B"
    elif score >= GRADE_C:
        grade = "C"
    elif score >= GRADE_D:
        grade = "D"
    else:
        grade = "F"

    summary = ScoreSummary(
        critical=critical,
        high=high,
        medium=medium,
        low=low,
    )

    return ScoreResult(
        score=score,
        grade=grade,
        summary=summary,
    )