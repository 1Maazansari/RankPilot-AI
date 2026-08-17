"""
HTML Parser for RankPilot AI.
"""

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from backend.schemas.page import PageAnalysis


class HTMLParser:
    """
    Parses HTML pages and extracts SEO information.
    """

    def parse(
        self,
        html: str,
        url: str,
        *,
        requested_url: str | None = None,
        status_code: int | None = None,
        response_time: float | None = None,
        page_size: int | None = None,
        content_type: str | None = None,
    ) -> PageAnalysis:
        """
        Parse HTML into a PageAnalysis object.
        """

        soup = BeautifulSoup(html, "lxml")

        internal_links, external_links = self.extract_links(
            html,
            url,
        )

        robots_meta = self._get_robots_meta(soup)

        return PageAnalysis(
            url=requested_url or url,
            final_url=url,
            title=self._get_title(soup),
            meta_description=self._get_meta_description(soup),
            canonical_url=self._get_canonical(soup),
            language=self._get_language(soup),
            charset=self._get_charset(soup),
            robots_meta=robots_meta,
            status_code=status_code,
            response_time=response_time,
            page_size=page_size,
            content_type=content_type,
            word_count=self._get_word_count(soup),
            h1_count=self._get_h1_count(soup),
            h2_count=self._get_h2_count(soup),
            image_count=self._get_image_count(soup),
            missing_alt_count=self._get_missing_alt_count(soup),
            internal_links=len(internal_links),
            external_links=len(external_links),
            has_https=urlparse(url).scheme.lower() == "https",
            is_indexable=self._is_indexable(robots_meta),
            og_title=self._get_open_graph(soup, "og:title"),
            og_description=self._get_open_graph(soup, "og:description"),
            og_image=self._get_open_graph(soup, "og:image"),
            og_url=self._get_open_graph(soup, "og:url"),
            og_type=self._get_open_graph(soup, "og:type"),
            has_open_graph=self._has_open_graph(soup),
            has_twitter_card=self._has_twitter_card(soup),
            has_schema_markup=self._has_schema_markup(soup),
        )

    # ======================================================
    # Link Extraction
    # ======================================================

    def extract_links(
        self,
        html: str,
        base_url: str,
    ) -> tuple[list[str], list[str]]:
        """
        Extract internal and external links.
        """

        soup = BeautifulSoup(html, "lxml")

        internal_links = set()
        external_links = set()

        base_domain = urlparse(base_url).netloc

        for tag in soup.find_all("a", href=True):

            href = tag["href"].strip()

            if not href:
                continue

            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue

            absolute = urljoin(base_url, href)

            parsed = urlparse(absolute)

            if parsed.scheme not in ("http", "https"):
                continue

            if parsed.netloc == base_domain:
                internal_links.add(absolute)
            else:
                external_links.add(absolute)

        return (
            sorted(internal_links),
            sorted(external_links),
        )

    # ======================================================
    # Metadata
    # ======================================================

    def _get_title(self, soup: BeautifulSoup) -> str | None:
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return None

    def _get_meta_description(self, soup: BeautifulSoup) -> str | None:
        tag = soup.find("meta", attrs={"name": "description"})
        if tag:
            return tag.get("content")
        return None

    def _get_canonical(self, soup: BeautifulSoup) -> str | None:
        tag = soup.find("link", rel="canonical")
        if tag:
            return tag.get("href")
        return None

    def _get_language(self, soup: BeautifulSoup) -> str | None:
        html = soup.find("html")
        if html:
            return html.get("lang")
        return None

    def _get_charset(self, soup: BeautifulSoup) -> str | None:
        tag = soup.find("meta", charset=True)

        if tag:
            return tag.get("charset")

        tag = soup.find(
            "meta",
            attrs={
                "http-equiv": re.compile(
                    "content-type",
                    re.I,
                )
            },
        )

        if tag:
            content = tag.get("content", "").lower()

            if "charset=" in content:
                return content.split("charset=")[-1]

        return None

    def _get_robots_meta(self, soup: BeautifulSoup) -> str | None:
        tag = soup.find("meta", attrs={"name": "robots"})
        if tag:
            return tag.get("content")
        return None

    def _is_indexable(self, robots_meta: str | None) -> bool:
        if not robots_meta:
            return True

        directives = {
            directive.strip().lower()
            for directive in robots_meta.split(",")
        }
        return "noindex" not in directives and "none" not in directives

    # ======================================================
    # Content
    # ======================================================

    def _get_word_count(self, soup: BeautifulSoup) -> int:
        text = soup.get_text(separator=" ", strip=True)
        return len(text.split())

    def _get_h1_count(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("h1"))

    def _get_h2_count(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("h2"))

    # ======================================================
    # Images
    # ======================================================

    def _get_image_count(self, soup: BeautifulSoup) -> int:
        return len(soup.find_all("img"))

    def _get_missing_alt_count(self, soup: BeautifulSoup) -> int:
        count = 0

        for image in soup.find_all("img"):
            alt = image.get("alt")

            if alt is None or alt.strip() == "":
                count += 1

        return count

    # ======================================================
    # Social
    # ======================================================

    def _has_open_graph(self, soup: BeautifulSoup) -> bool:
        return (
            soup.find(
                "meta",
                attrs={"property": "og:title"},
            )
            is not None
        )

    def _get_open_graph(
        self,
        soup: BeautifulSoup,
        property_name: str,
    ) -> str | None:
        tag = soup.find(
            "meta",
            attrs={"property": property_name},
        )
        if tag is None:
            tag = soup.find(
                "meta",
                attrs={"name": property_name},
            )
        return tag.get("content") if tag else None

    def _has_twitter_card(self, soup: BeautifulSoup) -> bool:
        return (
            soup.find(
                "meta",
                attrs={"name": "twitter:card"},
            )
            is not None
        )

    # ======================================================
    # Structured Data
    # ======================================================

    def _has_schema_markup(self, soup: BeautifulSoup) -> bool:

        if soup.find(
            "script",
            attrs={
                "type": "application/ld+json",
            },
        ):
            return True

        if soup.find(attrs={"itemscope": True}):
            return True

        return False
