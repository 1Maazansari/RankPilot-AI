"""LLM interface for the AI recommendation engine."""

from ai.models import AIRecommendation, AIRecommendationResult


def generate_recommendations(prompt: str) -> AIRecommendationResult:
    """
    Generate AI recommendations from a prompt.

    This is currently a placeholder implementation.
    It will later be replaced with an actual LLM (OpenAI, Ollama, Groq, etc.).
    """

    return AIRecommendationResult(
        recommendations=[
            AIRecommendation(
                priority=1,
                title="LLM Integration Pending",
                reason="The AI provider has not been connected yet.",
                impact="High",
                estimated_effort="N/A",
                action="Connect an LLM provider to generate real recommendations.",
            )
        ]
    )