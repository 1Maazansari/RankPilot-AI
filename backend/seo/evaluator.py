"""SEO rule evaluator orchestration."""

from collections.abc import Callable

from backend.scanner.models import ScannerResponse
from backend.seo.models import SEOIssue
from backend.seo.rules import (
    check_meta_description_too_long,
    check_meta_description_too_short,
    check_missing_alt_text,
    check_missing_canonical,
    check_missing_h1,
    check_missing_h2,
    check_missing_internal_links,
    check_missing_meta_description,
    check_missing_meta_robots,
    check_missing_og_description,
    check_missing_og_title,
    check_missing_robots_txt,
    check_missing_sitemap,
    check_missing_title,
    check_multiple_h1,
    check_title_too_long,
    check_title_too_short,
)

RuleFunction = Callable[[ScannerResponse], SEOIssue | None]

SEO_RULES: list[RuleFunction] = [
    check_missing_title,
    check_title_too_short,
    check_title_too_long,
    check_missing_meta_description,
    check_meta_description_too_short,
    check_meta_description_too_long,
    check_missing_canonical,
    check_missing_meta_robots,
    check_missing_h1,
    check_multiple_h1,
    check_missing_h2,
    check_missing_alt_text,
    check_missing_internal_links,
    check_missing_robots_txt,
    check_missing_sitemap,
    check_missing_og_title,
    check_missing_og_description,
]


def evaluate(
    scan: ScannerResponse,
    excluded_rule_ids: set[str] | None = None,
) -> list[SEOIssue]:
    """Run all SEO rules and return the issues they report."""

    issues: list[SEOIssue] = []

    for rule in SEO_RULES:
        if rule.__name__.removeprefix("check_") in (excluded_rule_ids or set()):
            continue
        issue = rule(scan)

        if issue is not None:
            issues.append(issue)

    return issues
