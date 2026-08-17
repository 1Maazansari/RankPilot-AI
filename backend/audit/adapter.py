"""
Adapter for converting crawler PageAnalysis objects into
ScannerResponse objects so the existing SEO engine can be reused.
"""

from backend.schemas.page import PageAnalysis
from backend.scanner.models import ScannerResponse


def page_to_scanner_response(
    page: PageAnalysis,
    *,
    robots_found: bool = False,
    sitemap_found: bool = False,
) -> ScannerResponse:
    """
    Convert a crawler PageAnalysis object into the ScannerResponse
    format expected by the SEO engine.
    """

    return ScannerResponse(
        # URL
        url=page.url,

        # Basic SEO
        title=page.title or "",
        meta_description=page.meta_description or "",
        canonical=page.canonical_url or "",
        meta_robots=page.robots_meta or "",

        # Technical SEO
        language=page.language or "",
        charset=page.charset or "",
        viewport="",          # Not collected by crawler yet
        favicon="",           # Not collected by crawler yet

        # Open Graph
        og_title=page.og_title or "",
        og_description=page.og_description or "",
        og_image=page.og_image or "",
        og_url=page.og_url or "",
        og_type=page.og_type or "",

        # Twitter Cards
        twitter_card="" if not page.has_twitter_card else "present",
        twitter_title="",
        twitter_description="",
        twitter_image="",

        # Heading Analysis
        h1_count=page.h1_count,
        h2_count=page.h2_count,

        # Image Analysis
        images=page.image_count,
        missing_alt=page.missing_alt_count,

        # Link Analysis
        internal_links=page.internal_links,

        # Technical Files
        robots_found=robots_found,
        sitemap_found=sitemap_found,
    )
