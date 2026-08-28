import json
import logging
import time

from google import genai

from backend.ai.models import AIRecommendation, AIRecommendationResult
from backend.ai.prompts import SYSTEM_PROMPT
from backend.core.config import settings


API_KEY = settings.GEMINI_API_KEY
MODEL = settings.GEMINI_MODEL
FALLBACK_MODEL = settings.GEMINI_FALLBACK_MODEL
TRANSIENT_RETRY_DELAY_SECONDS = 0.4

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

logging.basicConfig(level=logging.INFO)


def _is_unavailable_error(error: Exception) -> bool:
    """Return true only for Gemini's temporary 503/UNAVAILABLE failures."""
    status_code = getattr(error, "status_code", None) or getattr(error, "code", None)
    message = str(error).lower()
    return status_code == 503 or "503" in message or "unavailable" in message


def _generate_content(prompt: str, model: str):
    return client.models.generate_content(
        model=model,
        contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
    )


def generate_recommendations(prompt: str) -> AIRecommendationResult:
    """Generate AI-powered SEO recommendations with bounded graceful fallback."""
    response = None
    try:
        response = _generate_content(prompt, MODEL)
    except Exception as error:
        if _is_unavailable_error(error):
            logging.warning("Gemini primary model temporarily unavailable; retrying once.")
            try:
                time.sleep(TRANSIENT_RETRY_DELAY_SECONDS)
                response = _generate_content(prompt, MODEL)
            except Exception as retry_error:
                if _is_unavailable_error(retry_error):
                    logging.warning("Gemini primary model still unavailable; trying fallback model.")
                    try:
                        response = _generate_content(prompt, FALLBACK_MODEL)
                    except Exception:
                        logging.warning("Gemini recommendation models are unavailable.")
                else:
                    logging.warning("Gemini recommendation retry failed.")
        else:
            logging.warning("Gemini recommendation request failed.")

    if response is None:
        # Preserve the response schema while allowing the UI to mark only AI as unavailable.
        return AIRecommendationResult(recommendations=[])

    try:
        text = response.text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)
        recommendations = [AIRecommendation(**item) for item in data["recommendations"]]
        return AIRecommendationResult(recommendations=recommendations)
    except (AttributeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        logging.warning("Gemini returned an unusable recommendation response.")
        return AIRecommendationResult(recommendations=[])