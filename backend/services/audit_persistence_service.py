"""Transactional persistence for completed website audits."""

from datetime import datetime, timezone
from urllib.parse import urlsplit

from sqlalchemy.orm import Session

from backend.models.page import Page
from backend.models.project import Project
from backend.models.scan import Scan, ScanStatus
from backend.models.seo_issue import IssueSeverity, SEOIssue
from backend.schemas.crawl_report import CrawlExecution, CrawlReport


class AuditPersistenceService:
    """Maps a crawl report to the existing Project/Scan/Page issue graph."""

    def persist(
        self,
        db: Session,
        *,
        requested_url: str,
        max_pages: int,
        crawl: CrawlExecution,
        report: CrawlReport,
        duration_seconds: float | None = None,
    ) -> Scan:
        """Persist one complete audit atomically and return its scan record."""
        try:
            project = self._get_or_create_project(db, requested_url)
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            scan = Scan(
                project=project,
                status=ScanStatus.COMPLETED,
                requested_url=requested_url,
                max_pages=max_pages,
                total_pages=report.summary.total_pages,
                failed_pages=report.summary.failed_pages,
                crawl_complete=report.summary.crawl_complete,
                seo_score=report.summary.average_score,
                grade=report.summary.grade,
                duration_seconds=duration_seconds,
                started_at=now,
                completed_at=now,
            )
            db.add(scan)
            db.flush()

            for analysis, page_report in zip(crawl.pages, report.pages, strict=True):
                page = Page(
                    scan=scan,
                    url=analysis.url,
                    final_url=analysis.final_url,
                    canonical_url=analysis.canonical_url,
                    title=analysis.title,
                    meta_description=analysis.meta_description,
                    robots_meta=analysis.robots_meta,
                    language=analysis.language,
                    charset=analysis.charset,
                    status_code=analysis.status_code,
                    response_time=analysis.response_time,
                    page_size=analysis.page_size,
                    word_count=analysis.word_count,
                    h1_count=analysis.h1_count,
                    h2_count=analysis.h2_count,
                    image_count=analysis.image_count,
                    missing_alt_count=analysis.missing_alt_count,
                    internal_links=analysis.internal_links,
                    external_links=analysis.external_links,
                    is_indexable=analysis.is_indexable,
                    has_https=analysis.has_https,
                    has_open_graph=analysis.has_open_graph,
                    has_twitter_card=analysis.has_twitter_card,
                    has_schema_markup=analysis.has_schema_markup,
                    seo_score=page_report.score,
                )
                db.add(page)
                db.flush()
                for issue in page_report.issues:
                    db.add(self._issue(issue, scan=scan, page=page))

            for issue in report.site_issues:
                db.add(self._issue(issue, scan=scan))

            db.commit()
            db.refresh(scan)
            return scan
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _get_or_create_project(db: Session, requested_url: str) -> Project:
        parts = urlsplit(requested_url)
        website = f"{parts.scheme}://{parts.netloc}"
        project = db.query(Project).filter(Project.website == website).one_or_none()
        if project is None:
            project = Project(name=parts.netloc, website=website)
            db.add(project)
            db.flush()
        return project

    @staticmethod
    def _issue(issue, *, scan: Scan, page: Page | None = None) -> SEOIssue:
        return SEOIssue(
            scan=scan,
            page=page,
            issue_type=issue.rule_id,
            title=issue.rule_id.replace("_", " ").title(),
            description=issue.message,
            severity=IssueSeverity(issue.severity),
            recommendation=issue.recommendation,
        )
