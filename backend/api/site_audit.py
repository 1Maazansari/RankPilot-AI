"""
API endpoint for full website (multi-page) SEO audits.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from backend.audit.aggregator import generate_crawl_report
from backend.crawler.crawler import WebsiteCrawler
from backend.schemas.crawl_report import CrawlReport

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/site-audit",
    tags=["Site Audit"],
)


class SiteAuditRequest(BaseModel):
    url: HttpUrl
    max_pages: int = 20


@router.post(
    "",
    response_model=CrawlReport,
    status_code=status.HTTP_200_OK,
)
def site_audit(request: SiteAuditRequest) -> CrawlReport:
    """
    Perform a multi-page SEO audit.
    """

    try:
        crawler = WebsiteCrawler(
            max_pages=request.max_pages,
        )

        pages = crawler.crawl(
            str(request.url),
        )

        report = generate_crawl_report(
            pages,
        )

        return report

    except Exception as exc:
        logger.exception("Site audit failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc