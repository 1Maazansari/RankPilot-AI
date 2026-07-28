"""
Security utilities for RankPilot AI.

Provides helper functions for validating and normalizing URLs
before they are processed by the crawler.

Future responsibilities:
- JWT authentication
- API key validation
- Password hashing
- OAuth helpers
"""

from urllib.parse import urlparse, urlunparse

import validators

from core.exceptions import ValidationException


ALLOWED_SCHEMES = {"http", "https"}


def normalize_url(url: str) -> str:
    """
    Normalize a URL.

    - Removes leading/trailing spaces
    - Adds https:// if no scheme exists
    - Removes trailing slash
    """

    if not url:
        return ""

    url = url.strip()

    parsed = urlparse(url)

    # URL already has a scheme
    if parsed.scheme:
        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            return url

        return urlunparse(
            parsed._replace(path=parsed.path.rstrip("/"))
        )

    # Add HTTPS if missing
    url = f"https://{url}"

    parsed = urlparse(url)

    return urlunparse(
        parsed._replace(path=parsed.path.rstrip("/"))
    )


def is_safe_url(url: str) -> bool:
    """
    Allow only HTTP and HTTPS URLs.
    """

    parsed = urlparse(url)

    return parsed.scheme.lower() in ALLOWED_SCHEMES


from urllib.parse import urlparse
import validators


def is_valid_url(url: str) -> bool:
    """
    Validate that the URL is syntactically correct and
    uses an allowed scheme.
    """

    parsed = urlparse(url)

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False

    return validators.url(url) is True


def validate_url(url: str) -> str:
    """
    Normalize and validate a URL.

    Returns
    -------
    str
        Normalized URL

    Raises
    ------
    ValidationException
        If URL is invalid or unsafe.
    """

    if not url or not url.strip():
        raise ValidationException("URL cannot be empty.")

    raw = url.strip()

    parsed = urlparse(raw)

    # Reject dangerous schemes immediately
    if parsed.scheme and parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValidationException(
            f"Unsupported URL scheme: {parsed.scheme}"
        )

    normalized = normalize_url(raw)

    if not is_safe_url(normalized):
        raise ValidationException("Unsafe URL.")

    if not is_valid_url(normalized):
        raise ValidationException("Invalid URL.")

    return normalized