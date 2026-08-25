from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.audit.aggregator import generate_crawl_report
from backend.database.base import Base
from backend.database.session import get_db
from backend.models.page import Page
from backend.models.project import Project
from backend.models.scan import Scan, ScanStatus
from backend.models.seo_issue import SEOIssue
from backend.schemas.crawl_report import CrawlExecution, CrawlFailure
from backend.schemas.page import PageAnalysis
from backend.services.audit_persistence_service import AuditPersistenceService
from backend.api.site_audit import router as site_audit_router


def make_page(url: str, **overrides) -> PageAnalysis:
    values = {
        "url": url,
        "final_url": url,
        "title": "A valid page title",
        "meta_description": "A sufficiently descriptive page summary for tests.",
        "canonical_url": url,
        "status_code": 200,
        "response_time": 0.2,
        "page_size": 1024,
        "h1_count": 1,
        "h2_count": 1,
        "internal_links": 2,
        "has_open_graph": True,
    }
    values.update(overrides)
    return PageAnalysis(**values)


def persist_audit(tmp_path, crawl: CrawlExecution):
    engine = create_engine(f"sqlite:///{tmp_path / 'audit.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    report = generate_crawl_report(crawl)
    scan = AuditPersistenceService().persist(
        session,
        requested_url="https://example.com/starting-path",
        max_pages=10,
        crawl=crawl,
        report=report,
        duration_seconds=1.25,
    )
    return session, scan, report


def test_persists_project_scan_pages_and_page_issues(tmp_path):
    crawl = CrawlExecution(
        pages=[
            make_page("https://example.com/", title=""),
            make_page("https://example.com/about", meta_description=""),
        ],
        robots_txt_found=True,
        sitemap_found=True,
    )
    session, scan, report = persist_audit(tmp_path, crawl)

    project = session.query(Project).one()
    stored_scan = session.query(Scan).one()
    pages = session.query(Page).order_by(Page.url).all()
    issues = session.query(SEOIssue).all()

    assert project.website == "https://example.com"
    assert stored_scan.project_id == project.id
    assert stored_scan.status is ScanStatus.COMPLETED
    assert stored_scan.requested_url == "https://example.com/starting-path"
    assert stored_scan.total_pages == 2
    assert stored_scan.seo_score == report.summary.average_score
    assert stored_scan.grade == report.summary.grade
    assert len(pages) == 2
    assert all(page.scan_id == scan.id for page in pages)
    assert all(issue.scan_id == scan.id for issue in issues)
    assert any(issue.page_id is not None for issue in issues)
    assert {page.seo_score for page in pages} == {item.score for item in report.pages}


def test_persists_site_issues_and_partial_crawl_metadata(tmp_path):
    crawl = CrawlExecution(
        pages=[make_page("https://example.com/")],
        failures=[CrawlFailure(url="https://example.com/broken", reason="fetch_or_parse_failed")],
        robots_txt_found=False,
        sitemap_found=False,
    )
    session, scan, report = persist_audit(tmp_path, crawl)

    site_issues = session.query(SEOIssue).filter(SEOIssue.page_id.is_(None)).all()

    assert scan.crawl_complete is False
    assert scan.failed_pages == 1
    assert scan.total_pages == 1
    assert scan.duration_seconds == 1.25
    assert {issue.issue_type for issue in site_issues} == {
        issue.rule_id for issue in report.site_issues
    }
    assert all(issue.scan_id == scan.id for issue in site_issues)


def test_site_audit_returns_existing_report_contract_after_persistence(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'endpoint.db'}")
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine)
    app = FastAPI()
    app.include_router(site_audit_router)

    def override_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    crawl = CrawlExecution(
        pages=[make_page("https://example.com/")],
        robots_txt_found=True,
        sitemap_found=True,
    )
    monkeypatch.setattr(
        "backend.api.site_audit.WebsiteCrawler.crawl_with_result",
        lambda _crawler, _url: crawl,
    )

    with TestClient(app) as client:
        response = client.post("/site-audit", json={"url": "https://example.com", "max_pages": 3})

    assert response.status_code == 200
    assert set(response.json()) == {"summary", "pages", "site_issues", "failures", "scan_id"}
    assert response.json()["scan_id"] is not None
    session = testing_session()
    assert session.query(Scan).one().max_pages == 3
