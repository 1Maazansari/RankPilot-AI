import logging
from typing import Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_metadata(soup: BeautifulSoup) -> dict[str, str]:
    """
    Extract all metadata required for SEO analysis.
    """

    logger.debug("Extracting page metadata")

    metadata = {
        # Basic SEO
        "title": _extract_title(soup),
        "meta_description": _extract_meta_description(soup),
        "canonical": _extract_canonical(soup),
        "meta_robots": _extract_meta_robots(soup),

        # Technical SEO
        "language": _extract_language(soup),
        "charset": _extract_charset(soup),
        "viewport": _extract_viewport(soup),
        "favicon": _extract_favicon(soup),

        # Open Graph
        "og_title": _extract_open_graph(soup, "og:title"),
        "og_description": _extract_open_graph(soup, "og:description"),
        "og_image": _extract_open_graph(soup, "og:image"),
        "og_url": _extract_open_graph(soup, "og:url"),
        "og_type": _extract_open_graph(soup, "og:type"),

        # Twitter Cards
        "twitter_card": _extract_twitter(soup, "twitter:card"),
        "twitter_title": _extract_twitter(soup, "twitter:title"),
        "twitter_description": _extract_twitter(soup, "twitter:description"),
        "twitter_image": _extract_twitter(soup, "twitter:image"),
    }

    missing = [key for key, value in metadata.items() if not value]

    logger.info(
        "Metadata extracted successfully (%d/%d fields found)",
        sum(bool(v) for v in metadata.values()),
        len(metadata),
    )

    if missing:
        logger.debug("Missing metadata fields: %s", ", ".join(missing))

    return metadata


# ---------------------------------------------------------------------
# Basic SEO
# ---------------------------------------------------------------------


def _extract_title(soup: BeautifulSoup) -> str:
    title = soup.find("title")
    return title.get_text(strip=True) if title else ""


def _extract_meta_description(soup: BeautifulSoup) -> str:
    description = _find_meta_by_name(soup, "description")
    return _content(description)


def _extract_canonical(soup: BeautifulSoup) -> str:
    canonical = soup.find(
        "link",
        rel=lambda value: value and "canonical" in str(value).lower(),
    )

    return (canonical.get("href") or "").strip() if canonical else ""


def _extract_meta_robots(soup: BeautifulSoup) -> str:
    robots = _find_meta_by_name(soup, "robots")
    return _content(robots)


# ---------------------------------------------------------------------
# Technical SEO
# ---------------------------------------------------------------------


def _extract_language(soup: BeautifulSoup) -> str:
    html = soup.find("html")
    return (html.get("lang") or "").strip() if html else ""


def _extract_charset(soup: BeautifulSoup) -> str:
    charset = soup.find("meta", attrs={"charset": True})

    if charset:
        return (charset.get("charset") or "").strip()

    content_type = soup.find(
        "meta",
        attrs={
            "http-equiv": lambda value: value
            and value.lower() == "content-type"
        },
    )

    if not content_type:
        return ""

    content = _content(content_type)

    if "charset=" in content.lower():
        return content.split("charset=")[-1].strip()

    return content


def _extract_viewport(soup: BeautifulSoup) -> str:
    viewport = _find_meta_by_name(soup, "viewport")
    return _content(viewport)


def _extract_favicon(soup: BeautifulSoup) -> str:
    favicon = soup.find(
        "link",
        rel=lambda value: value
        and any(
            icon in str(value).lower()
            for icon in (
                "icon",
                "shortcut icon",
                "apple-touch-icon",
            )
        ),
    )

    return (favicon.get("href") or "").strip() if favicon else ""


# ---------------------------------------------------------------------
# Open Graph
# ---------------------------------------------------------------------


def _extract_open_graph(soup: BeautifulSoup, property_name: str) -> str:
    tag = soup.find(
        "meta",
        attrs={
            "property": lambda value: value
            and value.lower() == property_name.lower()
        },
    )

    if not tag:
        tag = soup.find(
            "meta",
            attrs={
                "name": lambda value: value
                and value.lower() == property_name.lower()
            },
        )

    return _content(tag)


# ---------------------------------------------------------------------
# Twitter
# ---------------------------------------------------------------------


def _extract_twitter(soup: BeautifulSoup, name: str) -> str:
    tag = _find_meta_by_name(soup, name)
    return _content(tag)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _find_meta_by_name(soup: BeautifulSoup, name: str):
    return soup.find(
        "meta",
        attrs={
            "name": lambda value: value
            and value.lower() == name.lower()
        },
    )


def _content(tag: Any) -> str:
    if not tag:
        return ""

    return (tag.get("content") or "").strip()