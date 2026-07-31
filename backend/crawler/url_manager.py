"""
URL management utilities for RankPilot AI.
"""

from urllib.parse import urljoin, urlparse, urlunparse


class URLManager:
    """Utility class for URL operations."""

    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalize a URL by:
        - Removing fragments
        - Removing trailing slash (except root)
        """
        parsed = urlparse(url)

        parsed = parsed._replace(fragment="")

        normalized = urlunparse(parsed)

        if normalized.endswith("/") and parsed.path not in ("", "/"):
            normalized = normalized[:-1]

        return normalized

    @staticmethod
    def to_absolute(base_url: str, url: str) -> str:
        """
        Convert relative URL into absolute URL.
        """
        return urljoin(base_url, url)

    @staticmethod
    def get_domain(url: str) -> str:
        """
        Return domain name.
        """
        return urlparse(url).netloc.lower()

    @staticmethod
    def is_internal(base_url: str, target_url: str) -> bool:
        """
        Check whether target URL belongs to the same domain.
        """
        return (
            URLManager.get_domain(base_url)
            == URLManager.get_domain(target_url)
        )

    @staticmethod
    def remove_query(url: str) -> str:
        """
        Remove query parameters.
        """
        parsed = urlparse(url)
        parsed = parsed._replace(query="")
        return urlunparse(parsed)

    @staticmethod
    def is_http(url: str) -> bool:
        """
        Check if URL uses HTTP or HTTPS.
        """
        scheme = urlparse(url).scheme.lower()
        return scheme in ("http", "https")