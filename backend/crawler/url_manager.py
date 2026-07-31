"""
URL management utilities for RankPilot AI.
"""

from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)


class URLManager:
    """
    Utility class for URL operations.
    """

    # File extensions we don't want to crawl
    SKIP_EXTENSIONS = (
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".webp",
        ".ico",
        ".zip",
        ".rar",
        ".mp4",
        ".mp3",
        ".avi",
        ".mov",
        ".css",
        ".js",
    )

    # Tracking parameters to remove
    TRACKING_PARAMS = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "fbclid",
    }

    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalize URL.
        """

        parsed = urlparse(url)

        scheme = parsed.scheme.lower()

        netloc = parsed.netloc.lower()

        path = parsed.path.rstrip("/")

        if path == "":
            path = ""

        # Remove fragments
        fragment = ""

        # Remove tracking query parameters
        query = urlencode(
            [
                (k, v)
                for k, v in parse_qsl(parsed.query)
                if k not in URLManager.TRACKING_PARAMS
            ]
        )

        return urlunparse(
            (
                scheme,
                netloc,
                path,
                "",
                query,
                fragment,
            )
        )

    @staticmethod
    def to_absolute(base_url: str, url: str) -> str:
        return urljoin(base_url, url)

    @staticmethod
    def get_domain(url: str) -> str:
        return urlparse(url).netloc.lower()

    @staticmethod
    def is_internal(base_url: str, target_url: str) -> bool:
        return (
            URLManager.get_domain(base_url)
            == URLManager.get_domain(target_url)
        )

    @staticmethod
    def is_html(url: str) -> bool:
        """
        Ignore PDFs, images, videos, etc.
        """

        parsed = urlparse(url)

        path = parsed.path.lower()

        return not path.endswith(URLManager.SKIP_EXTENSIONS)