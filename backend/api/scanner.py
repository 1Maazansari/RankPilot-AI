
"""
Scanner API for RankPilot AI.
"""

import logging
import time
from collections import defaultdict
from threading import Lock
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, HttpUrl

from backend.ai.engine import analyze_ai
from backend.ai.models import AIRecommendationResult
from backend.agents.graph import brandvizi_agent_graph
from backend.agents.schemas import FinalAgentResult
from backend.scanner.models import ScannerResponse
from backend.scanner.scanner import (
    ScannerTimeoutError,
    WebsiteUnavailableError,
    scan_website,
)
from backend.seo.engine import (
    SEOAnalysisResult,
    analyze,
)


logger = logging.getLogger(__name__)

router = APIRouter(tags=["scanner"])


# =========================================================
# MVP RATE LIMITING
# =========================================================

RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = Lock()


def check_rate_limit(client_ip: str) -> bool:
    """
    Allow a maximum of 10 scan requests per IP
    within a rolling 60-second window.
    """

    now = time.monotonic()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    with _rate_limit_lock:
        timestamps = _rate_limit_store[client_ip]

        # Remove expired requests.
        timestamps[:] = [
            timestamp
            for timestamp in timestamps
            if timestamp > window_start
        ]

        # Block if the client has reached the limit.
        if len(timestamps) >= RATE_LIMIT_REQUESTS:
            return False

        # Record this request.
        timestamps.append(now)

    return True


# =========================================================
# REQUEST / RESPONSE MODELS
# =========================================================


class ScanRequest(BaseModel):
    url: HttpUrl


class ScanResponse(BaseModel):
    scan: ScannerResponse
    seo: SEOAnalysisResult

    # Existing AI recommendation response.
    # Kept for frontend/backward compatibility.
    ai: AIRecommendationResult

    # New LangGraph multi-agent analysis.
    agents: FinalAgentResult


# =========================================================
# LANGGRAPH HELPERS
# =========================================================


def _model_dump(value: Any) -> dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary.

    Supports the current Pydantic v2 models used by BrandVizi.
    """
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return value

    raise TypeError(
        f"Expected a Pydantic model or dict, got {type(value).__name__}"
    )


def run_agent_analysis(
    scan_result: ScannerResponse,
    seo_result: SEOAnalysisResult,
) -> FinalAgentResult:
    """
    Run the BrandVizi LangGraph multi-agent workflow.

    Pipeline:
        Technical SEO
              ↓
        Content Intelligence
              ↓
        AEO/GEO
              ↓
        Validation
    """

    initial_state = {
        "scan": _model_dump(scan_result),
        "seo_analysis": _model_dump(seo_result),
        "errors": [],
    }

    graph_result = brandvizi_agent_graph.invoke(
        initial_state
    )

    # -----------------------------------------------------
    # Defensive validation of graph output
    # -----------------------------------------------------

    try:
        return FinalAgentResult(
            technical=graph_result.get(
                "technical_analysis",
                {
                    "agent_name": "technical_seo",
                    "summary": "Technical SEO analysis unavailable.",
                    "findings": [],
                },
            ),
            content=graph_result.get(
                "content_analysis",
                {
                    "agent_name": "content_intelligence",
                    "summary": "Content Intelligence analysis unavailable.",
                    "findings": [],
                },
            ),
            aeo_geo=graph_result.get(
                "aeo_geo_analysis",
                {
                    "agent_name": "aeo_geo",
                    "summary": "AEO/GEO analysis unavailable.",
                    "findings": [],
                },
            ),
            validation=graph_result.get(
                "validation",
                {
                    "valid": False,
                    "validated_findings": [],
                    "rejected_findings": [],
                    "warnings": [
                        "LangGraph validation output was unavailable."
                    ],
                },
            ),
        )

    except Exception:
        logger.exception(
            "Failed to validate LangGraph output"
        )

        raise


# =========================================================
# SCAN ENDPOINT
# =========================================================


@router.post(
    "/scan",
    response_model=ScanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid URL",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit exceeded",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Website unavailable",
        },
        status.HTTP_504_GATEWAY_TIMEOUT: {
            "description": "Website timeout",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Unexpected error",
        },
    },
)
def scan(
    request: ScanRequest,
    http_request: Request,
) -> ScanResponse:

    # -----------------------------------------------------
    # Rate limiting
    # -----------------------------------------------------

    client_ip = (
        http_request.client.host
        if http_request.client
        else "unknown"
    )

    if not check_rate_limit(client_ip):
        logger.warning(
            "Rate limit exceeded for scanner client=%s",
            client_ip,
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Too many scan requests. "
                "Please try again later."
            ),
        )

    # -----------------------------------------------------
    # Scan
    # -----------------------------------------------------

    try:
        # =================================================
        # STEP 1 — WEBSITE SCANNER
        # =================================================

        scan_result = scan_website(
            str(request.url)
        )

        # =================================================
        # STEP 2 — DETERMINISTIC SEO ENGINE
        # =================================================

        seo_result = analyze(
            scan_result
        )

        # =================================================
        # STEP 3 — EXISTING AI RECOMMENDATION ENGINE
        # =================================================
        #
        # Kept intentionally for backward compatibility
        # with the existing BrandVizi frontend/API.
        #
        # The deterministic SEO engine remains the factual
        # source of truth for this layer.
        #

        ai_result = analyze_ai(
            scan_result,
            seo_result,
        )

        # =================================================
        # STEP 4 — LANGGRAPH MULTI-AGENT SYSTEM
        # =================================================
        #
        # Technical SEO
        #       ↓
        # Content Intelligence
        #       ↓
        # AEO/GEO
        #       ↓
        # Validation
        #

        agent_result = run_agent_analysis(
            scan_result,
            seo_result,
        )

        # =================================================
        # STEP 5 — FINAL RESPONSE
        # =================================================

        return ScanResponse(
            scan=scan_result,
            seo=seo_result,
            ai=ai_result,
            agents=agent_result,
        )

    # -----------------------------------------------------
    # Invalid URL
    # -----------------------------------------------------

    except ValueError as exc:
        logger.warning(
            "Invalid scanner request: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL",
        ) from exc

    # -----------------------------------------------------
    # Website unavailable
    # -----------------------------------------------------

    except WebsiteUnavailableError as exc:
        logger.warning(
            "Website unavailable during scan: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Website Unavailable",
        ) from exc

    # -----------------------------------------------------
    # Timeout
    # -----------------------------------------------------

    except ScannerTimeoutError as exc:
        logger.warning(
            "Website timeout during scan: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout",
        ) from exc

    # -----------------------------------------------------
    # Unexpected error
    # -----------------------------------------------------

    except Exception:
        logger.exception(
            "Unexpected scanner API error"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected Error",
        )
