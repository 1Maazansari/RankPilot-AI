import json
import logging
import os

from dotenv import load_dotenv
from google import genai

from backend.ai.models import (
    AIRecommendation,
    AIRecommendationResult,
)

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

logging.basicConfig(level=logging.INFO)

# --------------------------------------------------
# System Prompt
# --------------------------------------------------

SYSTEM_PROMPT = """
You are RankPilot AI.

You are an expert Technical SEO Consultant.

Analyze the provided website scan and SEO issues.

Your objective is to help website owners improve SEO rankings.

Instructions:

- Prioritize recommendations from highest impact to lowest.
- Recommend ONLY fixes based on the provided scan.
- Do NOT invent issues.
- Explain WHY each issue matters.
- Provide practical implementation advice.
- Keep recommendations concise.
- Maximum 5 recommendations.

Return ONLY valid JSON.

JSON format:

{
  "recommendations": [
    {
      "priority": 1,
      "title": "...",
      "reason": "...",
      "impact": "High",
      "estimated_effort": "...",
      "action": "..."
    }
  ]
}

Rules:

- priority must be integer
- impact must be one of:
  High
  Medium
  Low

Do not return markdown.

Do not wrap JSON inside ```.

Return JSON only.
"""

# --------------------------------------------------
# Gemini Recommendation Generator
# --------------------------------------------------


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