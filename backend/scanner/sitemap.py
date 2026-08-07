import logging
from urllib.parse import urljoin

import requests

from backend.config import SCANNER_ASSET_TIMEOUT_SECONDS
from .client import session


logger = logging.getLogger(__name__)


def detect_sitemap_xml(url: str) -> bool:
    sitemap_url = urljoin(url, "/sitemap.xml")
    logger.debug("Checking sitemap.xml: url=%s", sitemap_url)
    try:
        response = session.get(sitemap_url, timeout=SCANNER_ASSET_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        logger.warning("sitemap.xml check failed: url=%s error=%s", sitemap_url, exc)
        return False

    found = response.status_code == 200
    logger.info("sitemap.xml check complete: found=%s status_code=%s", found, response.status_code)
    return found
