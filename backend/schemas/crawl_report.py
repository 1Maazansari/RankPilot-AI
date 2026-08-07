"""
Pydantic schemas for Website Crawl Reports.
"""

from pydantic import BaseModel

from backend.seo.models import SEOIssue


class PageReport(BaseModel):
    """
    SEO analysis result for a single crawled page.
    """

    url: str

    score: float

    grade: str

    issues: list[SEOIssue]


class CrawlSummary(BaseModel):
    """
    Overall summary of a website audit.
    """

    total_pages: int

    average_score: float

    grade: str

    critical: int

    high: int

    medium: int

    low: int


class CrawlReport(BaseModel):
    """
    Final report returned after auditing an entire website.
    """

    summary: CrawlSummary

    pages: list[PageReport]