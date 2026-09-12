"""
Compact Content Evidence Layer for BrandVizi.

This module extracts limited page-content evidence from raw HTML
without sending the full HTML to Gemini.

The evidence includes:
- main text excerpt
- H1/H2/H3 text
- word count
- lists
- detected questions
- structured data / schema presence
"""

import json
import re
from typing import Any

from bs4 import BeautifulSoup


def extract_content_evidence(html: str) -> dict[str, Any]:
    """
    Extract compact content evidence from raw HTML.

    Args:
        html: Raw HTML string.

    Returns:
        Dictionary containing compact evidence suitable for
        Content Intelligence and AEO/GEO agents.
    """

    if not html:
        return _empty_evidence()

    soup = BeautifulSoup(html, "lxml")

    # 1. Extract schema / structured data first, before any HTML
    # transformation or tag decomposition.
    schema = _extract_schema(soup)

    # 2. Identify the primary content container to prioritize main article
    # content and reduce navigation/footer contamination.
    container = _find_main_content_container(soup)

    # 3. Clean non-content and boilerplate elements from the container.
    _clean_boilerplate(container)

    # 4. Extract visible text from cleaned content.
    visible_text = container.get_text(separator=" ", strip=True)

    # Main text excerpt: up to 1200 characters.
    text_excerpt = visible_text[:1200].strip()
    if len(visible_text) > 1200:
        text_excerpt += "..."

    # Word count based on visible article text.
    word_count = len(visible_text.split())

    # Heading texts from container; if H1 is missing in container,
    # fall back to document-level search (excluding nav/footer).
    h1_texts = _extract_heading_texts(container, "h1")
    if not h1_texts:
        h1_texts = _extract_heading_texts(soup, "h1")

    h2_texts = _extract_heading_texts(container, "h2")
    h3_texts = _extract_heading_texts(container, "h3")

    # Lists from the cleaned article content.
    lists = _extract_lists(container)

    # Detected questions from clean headings and body text.
    questions = _detect_questions(h1_texts + h2_texts + h3_texts, visible_text)

    return {
        "word_count": word_count,
        "text_excerpt": text_excerpt,
        "h1_texts": h1_texts,
        "h2_texts": h2_texts,
        "h3_texts": h3_texts,
        "lists": lists,
        "detected_questions": questions,
        "schema": schema,
    }


def _empty_evidence() -> dict[str, Any]:
    """Return an empty evidence dictionary."""
    return {
        "word_count": 0,
        "text_excerpt": "",
        "h1_texts": [],
        "h2_texts": [],
        "h3_texts": [],
        "lists": [],
        "detected_questions": [],
        "schema": {
            "has_json_ld": False,
            "has_microdata": False,
            "types": [],
        },
    }


def _find_main_content_container(soup: BeautifulSoup) -> Any:
    """
    Find the main article or page content container to avoid
    global navigation, headers, and footers.
    """
    candidates = [
        "article",
        "main",
        '[role="main"]',
        "#main-content",
        "#content",
        "#main",
        ".main-content",
        ".article-content",
        ".entry-content",
        ".post-content",
        ".post-body",
        ".blog-post",
        ".article-body",
        ".content-area",
    ]

    for selector in candidates:
        try:
            match = soup.select_one(selector)
            if match and len(match.get_text(strip=True)) >= 150:
                return match
        except Exception:
            continue

    return soup.body or soup


def _clean_boilerplate(container: Any) -> None:
    """
    Decompose non-content, navigation, footer, and boilerplate elements.
    """
    # 1. Non-content tags
    for tag in container.find_all(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "iframe",
            "form",
            "canvas",
            "template",
            "nav",
            "footer",
            "aside",
        ]
    ):
        tag.decompose()

    # 2. Elements with navigation/banner/footer/search roles
    for tag in container.find_all(
        attrs={
            "role": [
                "navigation",
                "banner",
                "contentinfo",
                "search",
                "complementary",
            ]
        }
    ):
        tag.decompose()

    # 3. Hidden elements
    for tag in container.find_all(attrs={"aria-hidden": "true"}):
        tag.decompose()

    # 4. Common navigation, cookie, modal, sharing classes and IDs
    boilerplate_pattern = re.compile(
        r"(^|\b)(cookie|consent|navbar|site-header|site-footer|modal|popup|social-share|share-buttons|breadcrumb|breadcrumbs|sidebar|pagination)(\b|$)",
        re.I,
    )
    for tag in container.find_all(attrs={"class": boilerplate_pattern}):
        tag.decompose()
    for tag in container.find_all(attrs={"id": boilerplate_pattern}):
        tag.decompose()


def _extract_heading_texts(
    container: Any,
    tag: str,
    limit: int = 10,
) -> list[str]:
    """Extract visible text from heading tags within container."""
    texts: list[str] = []
    for element in container.find_all(tag, limit=limit):
        text = element.get_text(strip=True)
        if text:
            texts.append(text)
    return texts


def _extract_lists(container: Any, limit: int = 10) -> list[dict[str, Any]]:
    """
    Extract compact list evidence, excluding navigation and social links.

    Returns a list of dicts with:
    - type: "ul" or "ol"
    - item_count: number of items
    - excerpt: first few item texts joined
    """
    lists: list[dict[str, Any]] = []
    social_keywords = re.compile(
        r"facebook|twitter|linkedin|pinterest|share on", re.I
    )

    for list_tag in container.find_all(["ul", "ol"], limit=limit * 2):
        classes = " ".join(list_tag.get("class", []))
        ids = str(list_tag.get("id", ""))
        if re.search(
            r"share|social|nav|menu|pagination|breadcrumb",
            f"{classes} {ids}",
            re.I,
        ):
            continue

        items = [
            li.get_text(strip=True)
            for li in list_tag.find_all("li", limit=6)
            if li.get_text(strip=True)
        ]
        if not items:
            continue

        if all(social_keywords.search(item) for item in items):
            continue

        lists.append(
            {
                "type": list_tag.name,
                "item_count": len(list_tag.find_all("li")),
                "excerpt": " | ".join(items[:3]),
            }
        )
        if len(lists) >= limit:
            break

    return lists


def _detect_questions(
    headings: list[str],
    body_text: str,
    limit: int = 20,
) -> list[str]:
    """
    Detect question-like strings from headings and body text.

    Uses simple heuristics:
    - Ends with '?'
    - Starts with common question words
    """
    question_words = re.compile(
        r"^(what|how|why|when|where|who|which|can|is|are|do|does|did|will|would|should|may|might)\b",
        re.IGNORECASE,
    )

    candidates: list[str] = []

    for text in headings:
        if text.endswith("?") or question_words.match(text):
            candidates.append(text)

    # Also scan first 800 chars of body text for question sentences.
    for sentence in re.split(r"(?<=[.!?])\s+", body_text[:800]):
        sentence = sentence.strip()
        if sentence.endswith("?") and len(sentence) < 200:
            candidates.append(sentence)

    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for q in candidates:
        if q not in seen:
            seen.add(q)
            unique.append(q)

    return unique[:limit]


def _extract_schema(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Extract structured data / schema evidence from the page.

    Returns a compact dict with:
    - has_json_ld: bool
    - has_microdata: bool
    - types: list of schema.org type names detected
    """
    types: list[str] = []

    # JSON-LD
    json_ld_scripts = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    )
    has_json_ld = bool(json_ld_scripts)

    for script in json_ld_scripts:
        text = script.get_text(strip=True)
        if not text:
            continue
        try:
            data = json.loads(text)

            def _collect_types(obj: Any) -> None:
                if isinstance(obj, dict):
                    t = obj.get("@type")
                    if t:
                        if isinstance(t, list):
                            types.extend([str(x) for x in t])
                        elif isinstance(t, str):
                            types.append(t)
                    for v in obj.values():
                        _collect_types(v)
                elif isinstance(obj, list):
                    for item in obj:
                        _collect_types(item)

            _collect_types(data)
        except Exception:
            matches = re.findall(r'"@type"\s*:\s*"([^"]+)"', text)
            types.extend(matches)
            if not matches and '"@context"' in text and "schema.org" in text:
                types.append("unknown")

    # Microdata / itemscope
    microdata_items = soup.find_all(attrs={"itemscope": True})
    has_microdata = bool(microdata_items)
    for item in microdata_items:
        itemtype = item.get("itemtype")
        if isinstance(itemtype, str):
            match = re.search(r"schema\.org/([^/]+)$", itemtype)
            if match:
                types.append(match.group(1))

    return {
        "has_json_ld": has_json_ld,
        "has_microdata": has_microdata,
        "types": list(dict.fromkeys(types)),  # deduplicate preserving order
    }
