import logging
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def count_internal_links(soup: BeautifulSoup, base_url: str) -> int:
    base_hostname = urlparse(base_url).hostname
    internal_links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()
        if not href:
            continue

        absolute_url = urljoin(base_url, href)
        absolute_url, _fragment = urldefrag(absolute_url)
        parsed = urlparse(absolute_url)

        if parsed.scheme not in {"http", "https"}:
            continue

        if parsed.hostname == base_hostname:
            internal_links.add(absolute_url)

    logger.info("Internal link count complete: internal_links=%s", len(internal_links))
    return len(internal_links)
