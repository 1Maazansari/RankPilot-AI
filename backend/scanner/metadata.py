import logging
from typing import Any

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def extract_metadata(soup: BeautifulSoup) -> dict[str, str]:
    logger.debug("Extracting page metadata")
    metadata = {
        "title": _extract_title(soup),
        "meta_description": _extract_meta_description(soup),
        "canonical": _extract_canonical(soup),
        "meta_robots": _extract_meta_robots(soup),
        "og_title": _extract_open_graph(soup, "og:title"),
        "og_description": _extract_open_graph(soup, "og:description"),
    }
    logger.info(
        "Metadata extraction complete: title=%s meta_description=%s canonical=%s "
        "meta_robots=%s og_title=%s og_description=%s",
        bool(metadata["title"]),
        bool(metadata["meta_description"]),
        bool(metadata["canonical"]),
        bool(metadata["meta_robots"]),
        bool(metadata["og_title"]),
        bool(metadata["og_description"]),
    )
    return metadata


def _extract_title(soup: BeautifulSoup) -> str:
    title = soup.find("title")
    return title.get_text(strip=True) if title else ""


def _extract_meta_description(soup: BeautifulSoup) -> str:
    description = soup.find("meta", attrs={"name": "description"})
    return _content(description)


def _extract_canonical(soup: BeautifulSoup) -> str:
    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    return (canonical.get("href") or "").strip() if canonical else ""


def _extract_meta_robots(soup: BeautifulSoup) -> str:
    robots = soup.find("meta", attrs={"name": "robots"})
    return _content(robots)


def _extract_open_graph(soup: BeautifulSoup, property_name: str) -> str:
    tag = soup.find("meta", attrs={"property": property_name})
    return _content(tag)


def _content(tag: Any) -> str:
    if not tag:
        return ""
    return (tag.get("content") or "").strip()
