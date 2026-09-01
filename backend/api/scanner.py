"""
Scanner API for RankPilot AI.
"""

import logging
import time
from collections import defaultdict
from threading import Lock

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, HttpUrl

from backend.ai.engine import analyze_ai
from backend.ai.models import AIRecommendationResult
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
    ai: AIRecommendationResult


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
        scan_result = scan_website(
            str(request.url)
        )

        seo_result = analyze(
            scan_result
        )

        ai_result = analyze_ai(
            scan_result,
            seo_result,
        )

        return ScanResponse(
            scan=scan_result,
            seo=seo_result,
            ai=ai_result,
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