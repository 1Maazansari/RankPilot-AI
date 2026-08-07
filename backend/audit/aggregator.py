"""
Aggregation engine for multi-page website audits.

Converts crawler PageAnalysis objects into ScannerResponse objects,
reuses the existing SEO engine, and generates a CrawlReport.
"""

from backend.audit.adapter import page_to_scanner_response
from backend.schemas.page import PageAnalysis
from backend.schemas.crawl_report import (
    CrawlReport,
    CrawlSummary,
    PageReport,
)

from backend.seo.engine import analyze


def generate_crawl_report(
    pages: list[PageAnalysis],
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

    for page in pages:

        scanner_response = page_to_scanner_response(page)

        seo_result = analyze(scanner_response)

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

    if pages:
        average_score = round(
            total_score / len(pages),
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
    )

    return CrawlReport(
        summary=summary,
        pages=page_reports,
    )