"""Thin orchestration layer for SEO analysis."""

from pydantic import BaseModel

from scanner.models import ScannerResponse
from seo.evaluator import evaluate
from seo.models import SEOIssue


class SEOAnalysisResult(BaseModel):
    """SEO analysis output returned by the rule engine."""

    issues: list[SEOIssue]


def analyze(scan: ScannerResponse) -> SEOAnalysisResult:
    """Evaluate SEO rules for a scanner response."""
    issues = evaluate(scan)
    return SEOAnalysisResult(issues=issues)
