import logging

import requests
from bs4 import BeautifulSoup

from config import SCANNER_TIMEOUT_SECONDS
from .client import session
from .headings import count_h1, count_h2
from .images import count_images, count_missing_alt_text
from .links import count_internal_links
from .metadata import extract_metadata
from .models import ScannerResponse
from .robots import detect_robots_txt
from .sitemap import detect_sitemap_xml
from .validators import validate_url


logger = logging.getLogger(__name__)


class ScannerError(Exception):
    """Base scanner exception."""


class ScannerTimeoutError(ScannerError):
    """Raised when a website takes too long to respond."""


class WebsiteUnavailableError(ScannerError):
    """Raised when a website cannot be reached or returns an error."""


def scan_website(url: str) -> ScannerResponse:
    logger.info("Starting website scan")
    validated_url = validate_url(url)
    logger.debug("URL validation succeeded: url=%s", validated_url)

    html = _download_html(validated_url)
    logger.debug("Parsing HTML with lxml: url=%s", validated_url)
    soup = BeautifulSoup(html, "lxml")

    metadata = extract_metadata(soup)
    scanner_response = ScannerResponse(
        url=validated_url,
        **metadata,
        h1_count=count_h1(soup),
        h2_count=count_h2(soup),
        images=count_images(soup),
        missing_alt=count_missing_alt_text(soup),
        internal_links=count_internal_links(soup, validated_url),
        robots_found=detect_robots_txt(validated_url),
        sitemap_found=detect_sitemap_xml(validated_url),
    )
    logger.info("Website scan complete: url=%s", validated_url)
    return scanner_response


def _download_html(url: str) -> str:
    logger.debug("Downloading HTML: url=%s", url)
    try:
        response = session.get(url, timeout=SCANNER_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.Timeout as exc:
        logger.warning("Website scan timed out: url=%s", url)
        raise ScannerTimeoutError("Website took too long to respond.") from exc
    except requests.RequestException as exc:
        logger.warning("Website unavailable: url=%s error=%s", url, exc)
        raise WebsiteUnavailableError("Unable to access the website.") from exc

    response.encoding = response.apparent_encoding
    logger.info(
        "HTML download complete: url=%s status_code=%s encoding=%s",
        url,
        response.status_code,
        response.encoding,
    )
    return response.text
