import logging
from urllib.parse import urljoin

import requests

from config import SCANNER_ASSET_TIMEOUT_SECONDS
from .client import session


logger = logging.getLogger(__name__)


def detect_robots_txt(url: str) -> bool:
    robots_url = urljoin(url, "/robots.txt")
    logger.debug("Checking robots.txt: url=%s", robots_url)
    try:
        response = session.get(robots_url, timeout=SCANNER_ASSET_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        logger.warning("robots.txt check failed: url=%s error=%s", robots_url, exc)
        return False

    found = response.status_code == 200
    logger.info("robots.txt check complete: found=%s status_code=%s", found, response.status_code)
    return found
