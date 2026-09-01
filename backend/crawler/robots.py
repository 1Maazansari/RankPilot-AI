"""Site-level robots.txt discovery for crawls."""

from dataclasses import dataclass
import re
from urllib.parse import urljoin

import requests

from backend.crawler.fetcher import HTMLFetcher
from backend.scanner.validators import validate_url


@dataclass
class RobotsInfo:
    found: bool
    sitemap_urls: list[str]


def discover_robots(url: str, timeout: int = 10) -> RobotsInfo:
    """Fetch robots.txt once and collect any declared sitemap URLs."""

    try:
        robots_url = validate_url(urljoin(url, "/robots.txt"))

        response = requests.get(
            robots_url,
            headers={"User-Agent": HTMLFetcher.USER_AGENT},
            timeout=timeout,
        )

    except (requests.RequestException, ValueError):
        return RobotsInfo(found=False, sitemap_urls=[])

    if response.status_code != 200:
        return RobotsInfo(found=False, sitemap_urls=[])

    sitemap_urls = []

    for match in re.finditer(
        r"^\s*sitemap\s*:\s*(\S+)\s*$",
        response.text,
        re.I | re.M,
    ):
        sitemap_url = urljoin(robots_url, match.group(1))

        try:
            sitemap_url = validate_url(sitemap_url)
        except ValueError:
            continue

        sitemap_urls.append(sitemap_url)

    return RobotsInfo(
        found=True,
        sitemap_urls=list(dict.fromkeys(sitemap_urls)),
    )