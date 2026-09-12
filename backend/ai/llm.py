"""
Gemini LLM infrastructure.

This module provides:
1. The existing SEO recommendation generation flow.
2. A generic JSON generation function for the multi-agent system.
3. Bounded retry and fallback handling for temporary Gemini failures.
"""

import json
import logging
import time
from typing import Any

from google import genai

from backend.ai.models import AIRecommendation, AIRecommendationResult
from backend.ai.prompts import SYSTEM_PROMPT
from backend.core.config import settings


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = settings.GEMINI_API_KEY
MODEL = settings.GEMINI_MODEL
FALLBACK_MODEL = settings.GEMINI_FALLBACK_MODEL

TRANSIENT_RETRY_DELAY_SECONDS = 0.8

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")


client = genai.Client(api_key=API_KEY)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# ============================================================
# ERROR HANDLING
# ============================================================

def _get_status_code(error: Exception) -> int | None:
    """
    Extract an HTTP/status code from a Gemini exception.

    Gemini exceptions can expose the status code through
    different attributes depending on the SDK/version.
    """

    status_code = getattr(error, "status_code", None)

    if status_code is None:
        status_code = getattr(error, "code", None)

    try:
        return int(status_code) if status_code is not None else None
    except (TypeError, ValueError):
        return None


def _is_retryable_error(error: Exception) -> bool:
    """
    Return True for temporary Gemini failures that are safe
    to retry or route to the fallback model.

    Currently handled:
    - HTTP 429 Too Many Requests
    - HTTP 503 Service Unavailable
    - Gemini UNAVAILABLE errors
    - Gemini RESOURCE_EXHAUSTED / rate-limit errors
    """

    status_code = _get_status_code(error)
    message = str(error).lower()

    retryable_status_codes = {
        429,
        503,
    }

    retryable_messages = (
        "429",
        "too many requests",
        "rate limit",
        "rate-limit",
        "resource exhausted",
        "resource_exhausted",
        "503",
        "service unavailable",
        "unavailable",
    )

    if status_code in retryable_status_codes:
        return True

    return any(
        phrase in message
        for phrase in retryable_messages
    )


# Backward-compatible helper name.
def _is_unavailable_error(error: Exception) -> bool:
    """
    Backward-compatible alias for the previous helper.

    Temporary 429 and 503 Gemini failures are now both
    considered recoverable/unavailable conditions.
    """

    return _is_retryable_error(error)


# ============================================================
# GEMINI REQUEST
# ============================================================

def _generate_content(
    prompt: str,
    model: str,
):
    """
    Send a request to Gemini using the specified model.
    """

    logger.info(
        "Sending Gemini request using model: %s",
        model,
    )

    return client.models.generate_content(
        model=model,
        contents=prompt,
    )


# ============================================================
# RETRY + FALLBACK
# ============================================================

def _generate_with_fallback(
    prompt: str,
):
    """
    Generate content using the primary model with bounded
    retry and fallback behavior.

    Flow:

        Primary model
             ↓
        Retry primary once
             ↓
        Fallback model
             ↓
        Return None if everything fails

    This prevents temporary Gemini rate limits or outages
    from crashing the BrandVizi AI pipeline.

    Returns:
        Gemini response object or None.
    """

    # --------------------------------------------------------
    # 1. Primary model - first attempt
    # --------------------------------------------------------

    try:

        return _generate_content(
            prompt,
            MODEL,
        )

    except Exception as primary_error:

        if not _is_retryable_error(primary_error):

            logger.exception(
                "Gemini primary model failed with a non-retryable error."
            )

            return None

        status_code = _get_status_code(primary_error)

        logger.warning(
            "Gemini primary model failed temporarily "
            "(status=%s). Retrying once.",
            status_code,
        )

    # --------------------------------------------------------
    # 2. Primary model - retry
    # --------------------------------------------------------

    try:

        time.sleep(
            TRANSIENT_RETRY_DELAY_SECONDS
        )

        return _generate_content(
            prompt,
            MODEL,
        )

    except Exception as retry_error:

        if not _is_retryable_error(retry_error):

            logger.exception(
                "Gemini primary model retry failed "
                "with a non-retryable error."
            )

            return None

        status_code = _get_status_code(retry_error)

        logger.warning(
            "Gemini primary model retry failed "
            "(status=%s). Trying fallback model.",
            status_code,
        )

    # --------------------------------------------------------
    # 3. Fallback model
    # --------------------------------------------------------

    # Avoid making a useless second request when both
    # configuration values point to the same model.
    if FALLBACK_MODEL == MODEL:

        logger.warning(
            "Gemini fallback model is the same as the primary model. "
            "No separate fallback is available."
        )

        return None

    try:

        return _generate_content(
            prompt,
            FALLBACK_MODEL,
        )

    except Exception as fallback_error:

        status_code = _get_status_code(
            fallback_error
        )

        if _is_retryable_error(fallback_error):

            logger.warning(
                "Gemini fallback model is also temporarily "
                "unavailable (status=%s).",
                status_code,
            )

        else:

            logger.exception(
                "Gemini fallback model failed."
            )

        return None


# ============================================================
# JSON EXTRACTION
# ============================================================

def _extract_json(
    text: str,
) -> dict[str, Any] | None:
    """
    Safely extract a JSON object from an LLM response.

    Handles responses wrapped in markdown code fences.
    """

    if not text:
        return None

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    if text.startswith("```"):

        if text.startswith("```json"):
            text = text[len("```json"):]

        elif text.startswith("```"):
            text = text[len("```"):]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(text)

        if isinstance(data, dict):
            return data

    except json.JSONDecodeError:

        logger.warning(
            "Gemini returned invalid JSON."
        )

    return None


# ============================================================
# GENERIC JSON GENERATION
# ============================================================

def generate_json(
    prompt: str,
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """
    Generate a generic JSON object using Gemini.

    This function is intended for the BrandVizi multi-agent
    architecture.

    Args:
        prompt:
            Agent-specific instructions and input data.

        system_prompt:
            Optional system-level instructions for the agent.

    Returns:
        Parsed JSON dictionary.

        Returns an empty dictionary when:
        - Gemini is unavailable
        - Gemini is rate-limited
        - Gemini returns no text
        - Gemini returns invalid JSON
    """

    # --------------------------------------------------------
    # 1. Build complete prompt
    # --------------------------------------------------------

    if system_prompt:

        full_prompt = (
            f"{system_prompt}\n\n"
            f"{prompt}"
        )

    else:

        full_prompt = prompt

    # --------------------------------------------------------
    # 2. Generate using retry + fallback
    # --------------------------------------------------------

    response = _generate_with_fallback(
        full_prompt
    )

    # --------------------------------------------------------
    # 3. All Gemini models failed
    # --------------------------------------------------------

    if response is None:

        logger.warning(
            "Gemini generation unavailable after "
            "retry/fallback attempts."
        )

        return {}

    # --------------------------------------------------------
    # 4. Extract response text
    # --------------------------------------------------------

    try:

        text = response.text

    except AttributeError:

        logger.warning(
            "Gemini returned a response without text."
        )

        return {}

    if not text:

        logger.warning(
            "Gemini returned an empty response."
        )

        return {}

    # --------------------------------------------------------
    # 5. Parse JSON
    # --------------------------------------------------------

    data = _extract_json(text)

    if data is None:

        logger.warning(
            "Gemini JSON generation failed because "
            "the response could not be parsed."
        )

        return {}

    return data


# ============================================================
# EXISTING SEO RECOMMENDATION FLOW
# ============================================================

def generate_recommendations(
    prompt: str,
) -> AIRecommendationResult:
    """
    Generate AI-powered SEO recommendations.

    This is the existing recommendation API and is retained
    for backward compatibility with the current BrandVizi system.
    """

    # --------------------------------------------------------
    # 1. Build complete prompt
    # --------------------------------------------------------

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{prompt}"
    )

    # --------------------------------------------------------
    # 2. Generate using the same retry/fallback infrastructure
    # --------------------------------------------------------

    response = _generate_with_fallback(
        full_prompt
    )

    # --------------------------------------------------------
    # 3. Gemini unavailable
    # --------------------------------------------------------

    if response is None:

        logger.warning(
            "Gemini recommendation generation unavailable."
        )

        return AIRecommendationResult(
            recommendations=[],
        )

    # --------------------------------------------------------
    # 4. Extract response text
    # --------------------------------------------------------

    try:

        text = response.text

        if not text:
            logger.warning(
                "Gemini returned an empty recommendation response."
            )

            return AIRecommendationResult(
                recommendations=[],
            )

        text = text.strip()

    except AttributeError:

        logger.warning(
            "Gemini returned a recommendation response "
            "without text."
        )

        return AIRecommendationResult(
            recommendations=[],
        )

    # --------------------------------------------------------
    # 5. Parse JSON
    # --------------------------------------------------------

    data = _extract_json(text)

    if data is None:

        logger.warning(
            "Gemini returned unusable recommendation JSON."
        )

        return AIRecommendationResult(
            recommendations=[],
        )

    # --------------------------------------------------------
    # 6. Validate recommendations
    # --------------------------------------------------------

    try:

        raw_recommendations = data.get(
            "recommendations",
            [],
        )

        if not isinstance(
            raw_recommendations,
            list,
        ):
            raise TypeError(
                "recommendations must be a list"
            )

        recommendations = [
            AIRecommendation(**item)
            for item in raw_recommendations
            if isinstance(item, dict)
        ]

        return AIRecommendationResult(
            recommendations=recommendations,
        )

    except (
        TypeError,
        ValueError,
    ):

        logger.warning(
            "Gemini returned an unusable recommendation response."
        )

        return AIRecommendationResult(
            recommendations=[],
        )