"""
API endpoint for full website (multi-page) SEO audits.
"""

import logging
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from backend.audit.aggregator import generate_crawl_report
from backend.crawler.crawler import WebsiteCrawler
from backend.scanner.validators import validate_url
from backend.schemas.crawl_report import CrawlReport
from backend.database.session import get_db
from backend.services.audit_persistence_service import AuditPersistenceService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/site-audit",
    tags=["Site Audit"],
)


class SiteAuditRequest(BaseModel):
    url: HttpUrl
    max_pages: int = Field(default=20, ge=1, le=100)


@router.post(
    "",
    response_model=CrawlReport,
    status_code=status.HTTP_200_OK,
)
def site_audit(request: SiteAuditRequest, db: Session = Depends(get_db)) -> CrawlReport:
    """
    Perform a multi-page SEO audit.
    """

    try:
        started = perf_counter()
        validated_url = validate_url(str(request.url))

        crawler = WebsiteCrawler(
            max_pages=request.max_pages,
        )

        crawl = crawler.crawl_with_result(
            validated_url,
        )

        report = generate_crawl_report(
            crawl,
        )

        scan = AuditPersistenceService().persist(
            db,
            requested_url=validated_url,
            max_pages=request.max_pages,
            crawl=crawl,
            report=report,
            duration_seconds=perf_counter() - started,
        )

        report.scan_id = scan.id
        return report

    except ValueError as exc:
        logger.warning("Invalid site audit request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL",
        ) from exc

    except Exception:
        logger.exception("Site audit failed.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Site audit could not be completed.",
        )
