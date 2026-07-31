"""
HTML Fetcher for RankPilot AI.
"""

from dataclasses import dataclass

import requests


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


class HTMLFetcher:
    """
    Downloads webpages.
    """

    USER_AGENT = (
        "RankPilotAI/2.0 (+https://github.com/1Maazansari/RankPilot-AI)"
    )

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch(self, url: str) -> FetchResult:
        """
        Download webpage.
        """

        response = requests.get(
            url,
            headers={
                "User-Agent": self.USER_AGENT,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        return FetchResult(
            url=response.url,
            status_code=response.status_code,
            html=response.text,
            response_time=response.elapsed.total_seconds(),
            content_type=response.headers.get("Content-Type", ""),
        )