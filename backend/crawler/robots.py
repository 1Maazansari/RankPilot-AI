"""Site-level robots.txt discovery for crawls."""

from dataclasses import dataclass
import re
from urllib.parse import urljoin

import requests

from backend.crawler.fetcher import HTMLFetcher


@dataclass
class RobotsInfo:
    found: bool
    sitemap_urls: list[str]


def discover_robots(url: str, timeout: int = 10) -> RobotsInfo:
    """Fetch robots.txt once and collect any declared sitemap URLs."""

    robots_url = urljoin(url, "/robots.txt")

    try:
        response = requests.get(
            robots_url,
            headers={"User-Agent": HTMLFetcher.USER_AGENT},
            timeout=timeout,
        )
    except requests.RequestException:
        return RobotsInfo(found=False, sitemap_urls=[])

    if response.status_code != 200:
        return RobotsInfo(found=False, sitemap_urls=[])

    sitemap_urls = []
    for match in re.finditer(
        r"^\s*sitemap\s*:\s*(\S+)\s*$",
        response.text,
        re.I | re.M,
    ):
        sitemap_urls.append(urljoin(robots_url, match.group(1)))

    return RobotsInfo(found=True, sitemap_urls=list(dict.fromkeys(sitemap_urls)))
