import json
import logging
from google import genai

from backend.ai.models import (
    AIRecommendation,
    AIRecommendationResult,
)
from backend.ai.prompts import SYSTEM_PROMPT
from backend.core.config import settings

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

API_KEY = settings.GEMINI_API_KEY
MODEL = settings.GEMINI_MODEL

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

logging.basicConfig(level=logging.INFO)

def generate_recommendations(prompt: str) -> AIRecommendationResult:
    """
    Generate AI-powered SEO recommendations using Gemini.
    """

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
        )

        text = response.text.strip()

        # Remove accidental markdown formatting
        if text.startswith("```"):
            text = (
                text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        data = json.loads(text)

        recommendations = [
            AIRecommendation(**item)
            for item in data["recommendations"]
        ]

        return AIRecommendationResult(
            recommendations=recommendations
        )

    except json.JSONDecodeError:

        logging.exception("Gemini returned invalid JSON.")

        return AIRecommendationResult(
            recommendations=[
                AIRecommendation(
                    priority=1,
                    title="Invalid AI Response",
                    reason="Gemini returned malformed JSON.",
                    impact="High",
                    estimated_effort="N/A",
                    action="Retry the request.",
                )
            ]
        )

    except Exception as e:

        logging.exception(e)

        error = str(e).lower()

        if "api key" in error:
            reason = "Invalid Gemini API Key."
        elif "quota" in error:
            reason = "Gemini quota exceeded."
        elif "404" in error:
            reason = "Requested Gemini model not found."
        elif "timeout" in error:
            reason = "Gemini request timed out."
        else:
            reason = str(e)

        return AIRecommendationResult(
            recommendations=[
                AIRecommendation(
                    priority=1,
                    title="Gemini Error",
                    reason=reason,
                    impact="High",
                    estimated_effort="N/A",
                    action="Check Gemini configuration and retry.",
                )
            ]
        )
