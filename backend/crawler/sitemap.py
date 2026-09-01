"""Site-level sitemap discovery for crawls."""

from dataclasses import dataclass
from urllib.parse import urljoin

import requests

from backend.crawler.fetcher import HTMLFetcher
from backend.scanner.validators import validate_url


@dataclass
class SitemapInfo:
    found: bool
    urls: list[str]


def discover_sitemap(
    site_url: str,
    robots_sitemap_urls: list[str],
    timeout: int = 10,
) -> SitemapInfo:
    """Check conventional and robots.txt-declared sitemap locations once."""

    candidates = [
        urljoin(site_url, "/sitemap.xml"),
        *robots_sitemap_urls,
    ]

    found_urls = []

    for candidate in dict.fromkeys(candidates):
        try:
            safe_candidate = validate_url(candidate)

            response = requests.get(
                safe_candidate,
                headers={"User-Agent": HTMLFetcher.USER_AGENT},
                timeout=timeout,
            )

        except (requests.RequestException, ValueError):
            continue

        if response.status_code == 200:
            found_urls.append(safe_candidate)

    return SitemapInfo(
        found=bool(found_urls),
        urls=found_urls,
    )