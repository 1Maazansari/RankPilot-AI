"""AI recommendation engine."""

from scanner.models import ScannerResponse
from seo.engine import SEOAnalysisResult

from ai.llm import generate_recommendations
from ai.models import AIRecommendationResult
from ai.prompts import SYSTEM_PROMPT


def analyze_ai(
    scan: ScannerResponse,
    seo: SEOAnalysisResult,
) -> AIRecommendationResult:
    """
    Generate AI-powered SEO recommendations.
    """

    prompt = f"""
{SYSTEM_PROMPT}

Website:
{scan.model_dump_json(indent=2)}

SEO Analysis:
{seo.model_dump_json(indent=2)}
"""

    return generate_recommendations(prompt)