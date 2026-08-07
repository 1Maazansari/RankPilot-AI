"""Independent SEO rule checks for scanner responses."""

from backend.scanner.models import ScannerResponse

from backend.seo.constants import (
    H1_MAX_COUNT,
    H1_MIN_COUNT,
    H2_MIN_COUNT,
    INTERNAL_LINK_MIN_COUNT,
    META_DESCRIPTION_MAX_LENGTH,
    META_DESCRIPTION_MIN_LENGTH,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)
from backend.seo.models import (
    Category,
    SEOIssue,
    Severity,
)


def check_missing_title(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page title is missing."""
    if scan.title:
        return None

    return SEOIssue(
        rule_id="missing_title",
        severity=Severity.CRITICAL,
        category=Category.METADATA,
        message="Page title is missing.",
        recommendation="Add a descriptive title tag for the page.",
    )


def check_title_too_short(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page title is shorter than recommended."""
    if not scan.title or len(scan.title) >= TITLE_MIN_LENGTH:
        return None

    return SEOIssue(
        rule_id="title_too_short",
        severity=Severity.MEDIUM,
        category=Category.METADATA,
        message="Page title is shorter than the recommended length.",
        recommendation="Expand the title with relevant, concise page context.",
    )


def check_title_too_long(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page title is longer than recommended."""
    if not scan.title or len(scan.title) <= TITLE_MAX_LENGTH:
        return None

    return SEOIssue(
        rule_id="title_too_long",
        severity=Severity.MEDIUM,
        category=Category.METADATA,
        message="Page title is longer than the recommended length.",
        recommendation="Shorten the title so important terms are not truncated.",
    )


def check_missing_meta_description(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the meta description is missing."""
    if scan.meta_description:
        return None

    return SEOIssue(
        rule_id="missing_meta_description",
        severity=Severity.HIGH,
        category=Category.METADATA,
        message="Meta description is missing.",
        recommendation="Add a concise meta description that summarizes the page.",
    )


def check_meta_description_too_short(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the meta description is shorter than recommended."""
    if (
        not scan.meta_description
        or len(scan.meta_description) >= META_DESCRIPTION_MIN_LENGTH
    ):
        return None

    return SEOIssue(
        rule_id="meta_description_too_short",
        severity=Severity.LOW,
        category=Category.METADATA,
        message="Meta description is shorter than the recommended length.",
        recommendation="Expand the meta description with a clear page summary.",
    )


def check_meta_description_too_long(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the meta description is longer than recommended."""
    if (
        not scan.meta_description
        or len(scan.meta_description) <= META_DESCRIPTION_MAX_LENGTH
    ):
        return None

    return SEOIssue(
        rule_id="meta_description_too_long",
        severity=Severity.LOW,
        category=Category.METADATA,
        message="Meta description is longer than the recommended length.",
        recommendation="Shorten the meta description to keep it search-friendly.",
    )


def check_missing_canonical(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the canonical URL is missing."""
    if scan.canonical:
        return None

    return SEOIssue(
        rule_id="missing_canonical",
        severity=Severity.HIGH,
        category=Category.TECHNICAL,
        message="Canonical URL is missing.",
        recommendation="Add a canonical link tag for the preferred page URL.",
    )


def check_missing_meta_robots(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the meta robots directive is missing."""
    if scan.meta_robots:
        return None

    return SEOIssue(
        rule_id="missing_meta_robots",
        severity=Severity.LOW,
        category=Category.TECHNICAL,
        message="Meta robots directive is missing.",
        recommendation="Add a meta robots directive when crawl behavior must be explicit.",
    )


def check_missing_h1(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page has fewer H1 headings than expected."""
    if scan.h1_count >= H1_MIN_COUNT:
        return None

    return SEOIssue(
        rule_id="missing_h1",
        severity=Severity.HIGH,
        category=Category.HEADINGS,
        message="H1 heading is missing.",
        recommendation="Add one clear H1 heading that describes the page topic.",
    )


def check_multiple_h1(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page has more H1 headings than expected."""
    if scan.h1_count <= H1_MAX_COUNT:
        return None

    return SEOIssue(
        rule_id="multiple_h1",
        severity=Severity.MEDIUM,
        category=Category.HEADINGS,
        message="Page has multiple H1 headings.",
        recommendation="Use a single primary H1 and move secondary headings to lower levels.",
    )


def check_missing_h2(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page has fewer H2 headings than expected."""
    if scan.h2_count >= H2_MIN_COUNT:
        return None

    return SEOIssue(
        rule_id="missing_h2",
        severity=Severity.LOW,
        category=Category.HEADINGS,
        message="H2 headings are missing.",
        recommendation="Add H2 headings to organize supporting page sections.",
    )


def check_missing_alt_text(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when images are missing alt text."""
    if scan.missing_alt == 0:
        return None

    return SEOIssue(
        rule_id="missing_alt_text",
        severity=Severity.MEDIUM,
        category=Category.IMAGES,
        message="One or more images are missing alt text.",
        recommendation="Add descriptive alt text to informative images.",
    )


def check_missing_internal_links(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the page has fewer internal links than expected."""
    if scan.internal_links >= INTERNAL_LINK_MIN_COUNT:
        return None

    return SEOIssue(
        rule_id="missing_internal_links",
        severity=Severity.MEDIUM,
        category=Category.LINKS,
        message="Internal links are missing.",
        recommendation="Add relevant internal links to help users and crawlers navigate.",
    )


def check_missing_robots_txt(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when robots.txt was not found."""
    if scan.robots_found:
        return None

    return SEOIssue(
        rule_id="missing_robots_txt",
        severity=Severity.MEDIUM,
        category=Category.TECHNICAL,
        message="robots.txt was not found.",
        recommendation="Add a robots.txt file at the site root.",
    )


def check_missing_sitemap(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when a sitemap was not found."""
    if scan.sitemap_found:
        return None

    return SEOIssue(
        rule_id="missing_sitemap",
        severity=Severity.MEDIUM,
        category=Category.TECHNICAL,
        message="XML sitemap was not found.",
        recommendation="Add an XML sitemap and reference it from robots.txt.",
    )


def check_missing_og_title(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the Open Graph title is missing."""
    if scan.og_title:
        return None

    return SEOIssue(
        rule_id="missing_og_title",
        severity=Severity.LOW,
        category=Category.SOCIAL,
        message="Open Graph title is missing.",
        recommendation="Add an og:title value for social sharing previews.",
    )


def check_missing_og_description(scan: ScannerResponse) -> SEOIssue | None:
    """Return an issue when the Open Graph description is missing."""
    if scan.og_description:
        return None

    return SEOIssue(
        rule_id="missing_og_description",
        severity=Severity.LOW,
        category=Category.SOCIAL,
        message="Open Graph description is missing.",
        recommendation="Add an og:description value for social sharing previews.",
    )
