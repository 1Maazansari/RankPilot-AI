"""
HTML Fetcher for RankPilot AI.

Includes SSRF-safe redirect handling.
"""

from dataclasses import dataclass
from urllib.parse import urljoin

import requests

from backend.scanner.validators import validate_url


@dataclass
class FetchResult:
    """
    Result returned by the HTML fetcher.
    """

    url: str
    status_code: int
    html: str
    response_time: float
    content_type: str
    page_size: int


class HTMLFetcher:
    """
    Downloads webpages with SSRF-safe redirect handling.
    """

    USER_AGENT = (
        "RankPilotAI/2.0 "
        "(+https://github.com/1Maazansari/RankPilot-AI)"
    )

    MAX_REDIRECTS = 5

    REDIRECT_STATUS_CODES = {
        301,
        302,
        303,
        307,
        308,
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch(self, url: str) -> FetchResult:
        """
        Download a webpage while validating every redirect target.
        """

        # Validate the initial URL.
        current_url = validate_url(url)

        total_response_time = 0.0

        for redirect_count in range(self.MAX_REDIRECTS + 1):

            response = requests.get(
                current_url,
                headers={
                    "User-Agent": self.USER_AGENT,
                },
                timeout=self.timeout,
                allow_redirects=False,
            )

            total_response_time += response.elapsed.total_seconds()

            # -------------------------------------------------
            # Handle redirects manually.
            # -------------------------------------------------

            if response.status_code in self.REDIRECT_STATUS_CODES:

                location = response.headers.get("Location")

                if not location:
                    raise ValueError(
                        "The server returned a redirect without "
                        "a destination."
                    )

                # Convert relative redirects into absolute URLs.
                redirect_url = urljoin(
                    current_url,
                    location,
                )

                # IMPORTANT:
                # Validate the redirect BEFORE making another request.
                current_url = validate_url(redirect_url)

                if redirect_count >= self.MAX_REDIRECTS:
                    raise ValueError(
                        "Too many redirects."
                    )

                continue

            # -------------------------------------------------
            # Normal response.
            # -------------------------------------------------

            response.raise_for_status()

            return FetchResult(
                url=response.url,
                status_code=response.status_code,
                html=response.text,
                response_time=total_response_time,
                content_type=response.headers.get(
                    "Content-Type",
                    "",
                ),
                page_size=len(response.content),
            )

        raise ValueError(
            "Too many redirects."
        )