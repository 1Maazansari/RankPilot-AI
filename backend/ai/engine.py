"""
AI recommendation engine.
"""

from backend.ai.llm import generate_recommendations
from backend.ai.models import AIRecommendationResult
from backend.scanner.models import ScannerResponse
from backend.seo.engine import SEOAnalysisResult


def analyze_ai(
    scan: ScannerResponse,
    seo: SEOAnalysisResult,
) -> AIRecommendationResult:
    """
    Generate AI-powered SEO recommendations.
    """

    prompt = f"""
Website:
{scan.model_dump_json(indent=2)}

SEO Analysis:
{seo.model_dump_json(indent=2)}
"""

    return generate_recommendations(prompt)
