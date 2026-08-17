"""
Pydantic schemas for Website Crawl Reports.
"""

from pydantic import BaseModel

from backend.seo.models import SEOIssue
from backend.schemas.page import PageAnalysis


class CrawlFailure(BaseModel):
    """A URL that could not be fetched or parsed during a crawl."""

    url: str
    reason: str


class CrawlExecution(BaseModel):
    """Crawler output plus site-wide crawl metadata."""

    pages: list[PageAnalysis]
    failures: list[CrawlFailure] = []
    robots_txt_found: bool = False
    sitemap_found: bool = False
    sitemap_urls: list[str] = []


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

    crawl_complete: bool

    failed_pages: int

    robots_txt_found: bool

    sitemap_found: bool

    sitemap_urls: list[str]


class CrawlReport(BaseModel):
    """
    Final report returned after auditing an entire website.
    """

    summary: CrawlSummary

    pages: list[PageReport]

    site_issues: list[SEOIssue]

    failures: list[CrawlFailure]
