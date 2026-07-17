"""Thin orchestration layer for SEO analysis."""

from pydantic import BaseModel

from scanner.models import ScannerResponse
from score.engine import analyze_score
from score.models import ScoreResult
from seo.evaluator import evaluate
from seo.models import SEOIssue


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