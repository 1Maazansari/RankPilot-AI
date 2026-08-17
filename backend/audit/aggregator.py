"""
Aggregation engine for multi-page website audits.

Converts crawler PageAnalysis objects into ScannerResponse objects,
reuses the existing SEO engine, and generates a CrawlReport.
"""

from backend.audit.adapter import page_to_scanner_response
from backend.schemas.crawl_report import (
    CrawlExecution,
    CrawlReport,
    CrawlSummary,
    PageReport,
)

from backend.seo.engine import analyze
from backend.seo.rules import check_missing_robots_txt, check_missing_sitemap
from backend.score.calculator import calculate_score


SITE_LEVEL_RULE_IDS = {"missing_robots_txt", "missing_sitemap"}


def generate_crawl_report(
    crawl: CrawlExecution,
) -> CrawlReport:
    """
    Generate a complete website audit report from crawled pages.
    """

    page_reports: list[PageReport] = []

    total_score = 0

    critical = 0
    high = 0
    medium = 0
    low = 0

    # -----------------------------------------
    # Analyze each crawled page
    # -----------------------------------------

    for page in crawl.pages:

        scanner_response = page_to_scanner_response(
            page,
            robots_found=crawl.robots_txt_found,
            sitemap_found=crawl.sitemap_found,
        )

        seo_result = analyze(
            scanner_response,
            excluded_rule_ids=SITE_LEVEL_RULE_IDS,
        )

        total_score += seo_result.score.score

        critical += seo_result.score.summary.critical
        high += seo_result.score.summary.high
        medium += seo_result.score.summary.medium
        low += seo_result.score.summary.low

        page_reports.append(
            PageReport(
                url=page.url,
                score=seo_result.score.score,
                grade=seo_result.score.grade,
                issues=seo_result.issues,
            )
        )

    # -----------------------------------------
    # Calculate overall score
    # -----------------------------------------

    site_issues = []
    if crawl.pages:
        site_scan = page_to_scanner_response(
            crawl.pages[0],
            robots_found=crawl.robots_txt_found,
            sitemap_found=crawl.sitemap_found,
        )
        for rule in (check_missing_robots_txt, check_missing_sitemap):
            issue = rule(site_scan)
            if issue is not None:
                site_issues.append(issue)

    site_score = calculate_score(site_issues)
    site_penalty = 100 - site_score.score

    critical += site_score.summary.critical
    high += site_score.summary.high
    medium += site_score.summary.medium
    low += site_score.summary.low

    if crawl.pages:
        average_score = round(
            max(0, total_score / len(crawl.pages) - site_penalty),
            2,
        )
    else:
        average_score = 0

    # -----------------------------------------
    # Overall Grade
    # -----------------------------------------

    if average_score >= 90:
        grade = "A"

    elif average_score >= 80:
        grade = "B"

    elif average_score >= 70:
        grade = "C"

    elif average_score >= 60:
        grade = "D"

    else:
        grade = "F"

    summary = CrawlSummary(
        total_pages=len(page_reports),
        average_score=average_score,
        grade=grade,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        crawl_complete=not crawl.failures,
        failed_pages=len(crawl.failures),
        robots_txt_found=crawl.robots_txt_found,
        sitemap_found=crawl.sitemap_found,
        sitemap_urls=crawl.sitemap_urls,
    )

    return CrawlReport(
        summary=summary,
        pages=page_reports,
        site_issues=site_issues,
        failures=crawl.failures,
    )
