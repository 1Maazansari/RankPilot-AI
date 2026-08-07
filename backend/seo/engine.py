"""Thin orchestration layer for SEO analysis."""

from pydantic import BaseModel

from backend.scanner.models import ScannerResponse
from backend.score.engine import analyze_score
from backend.score.models import ScoreResult
from backend.seo.evaluator import evaluate
from backend.seo.models import SEOIssue


class SEOAnalysisResult(BaseModel):
    """SEO analysis output returned by the rule engine."""

    issues: list[SEOIssue]
    score: ScoreResult


def analyze(scan: ScannerResponse) -> SEOAnalysisResult:
    """
    Evaluate SEO rules for a scanner response and calculate the SEO score.
    """

    issues = evaluate(scan)
    score = analyze_score(issues)

    return SEOAnalysisResult(
        issues=issues,
        score=score,
    )