from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.ai import llm
from backend.ai.llm import generate_recommendations
from backend.ai.models import AIRecommendation, AIRecommendationResult
from backend.api.recommendations import router as recommendations_router
from backend.database.base import Base
from backend.database.session import get_db
from backend.models.ai_recommendation import AIRecommendation as AIRecommendationRecord
from backend.models.page import Page
from backend.models.project import Project
from backend.models.scan import Scan, ScanStatus
from backend.models.seo_issue import IssueSeverity, SEOIssue
from backend.services.multi_page_recommendation_service import (
    MultiPageRecommendationService,
    build_multi_page_prompt,
    group_scan_issues,
)


def make_session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'recommendations.db'}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def make_scan(session_factory):
    session = session_factory()
    scan = Scan(
        project=Project(name="Example", website="https://example.com"),
        status=ScanStatus.COMPLETED,
        seo_score=62,
        grade="D",
        total_pages=3,
        failed_pages=1,
        crawl_complete=False,
    )
    first = Page(scan=scan, url="https://example.com/", seo_score=60)
    second = Page(scan=scan, url="https://example.com/about", seo_score=55)
    third = Page(scan=scan, url="https://example.com/contact", seo_score=80)
    session.add_all([scan, first, second, third])
    session.flush()
    session.add_all(
        [
            SEOIssue(scan=scan, page=first, issue_type="missing_canonical", title="Missing canonical", description="Canonical URL is missing.", severity=IssueSeverity.HIGH, recommendation="Add a canonical link."),
            SEOIssue(scan=scan, page=second, issue_type="missing_canonical", title="Missing canonical", description="Canonical URL is missing.", severity=IssueSeverity.HIGH, recommendation="Add a canonical link."),
            SEOIssue(scan=scan, page=third, issue_type="missing_h2", title="Missing H2", description="H2 headings are missing.", severity=IssueSeverity.LOW, recommendation="Add H2 headings."),
            SEOIssue(scan=scan, issue_type="missing_sitemap", title="Missing sitemap", description="XML sitemap was not found.", severity=IssueSeverity.MEDIUM, recommendation="Add a sitemap."),
        ]
    )
    session.commit()
    session.refresh(scan)
    return session, scan.id


def load_scan(session, scan_id):
    # Access relationships before grouping so this helper stays independent of loader strategy.
    scan = session.get(Scan, scan_id)
    for issue in scan.seo_issues:
        _ = issue.page
    return scan


def test_groups_repeated_issues_and_prioritizes_deterministically(tmp_path):
    sessions = make_session(tmp_path)
    session, scan_id = make_scan(sessions)

    groups = group_scan_issues(load_scan(session, scan_id))

    canonical = next(group for group in groups if group.issue_type == "missing_canonical")
    assert canonical.affected_page_count == 2
    assert canonical.affected_urls == ("https://example.com/", "https://example.com/about")
    assert groups[0].issue_type == "missing_canonical"
    assert groups[-1].issue_type == "missing_h2"


def test_prompt_is_compact_and_contains_audit_scope(tmp_path):
    sessions = make_session(tmp_path)
    session, scan_id = make_scan(sessions)

    prompt = build_multi_page_prompt(load_scan(session, scan_id), group_scan_issues(load_scan(session, scan_id)))

    assert "overall_score" in prompt
    assert "missing_canonical" in prompt
    assert '"affected_page_count": 2' in prompt
    assert "1 page(s) could not be crawled" in prompt
    assert "final_url" not in prompt


def test_existing_gemini_boundary_parses_extended_recommendation(monkeypatch):
    response = type("Response", (), {"text": '''{"recommendations": [{"priority": 1, "title": "Add canonicals", "reason": "Search engines need a preferred URL.", "impact": "High", "estimated_effort": "Low", "action": "Add a canonical link.", "source_issue_type": "missing_canonical", "example": "<link rel=canonical ...>"}]}'''})()
    monkeypatch.setattr("backend.ai.llm.client.models.generate_content", lambda **_kwargs: response)

    result = generate_recommendations("test prompt")

    assert result.recommendations[0].source_issue_type == "missing_canonical"
    assert result.recommendations[0].example == "<link rel=canonical ...>"


def test_llm_failure_uses_existing_safe_fallback(monkeypatch):
    def raise_timeout(**_kwargs):
        raise TimeoutError("timeout")

    monkeypatch.setattr("backend.ai.llm.client.models.generate_content", raise_timeout)

    result = generate_recommendations("test prompt")

    assert result.recommendations == []

    # 503/UNAVAILABLE is retried once on the primary before using the Flash fallback.
    response = type("Response", (), {"text": '''{"recommendations": [{"priority": 1, "title": "Add canonicals", "reason": "Search engines need a preferred URL.", "impact": "High", "estimated_effort": "Low", "action": "Add a canonical link.", "source_issue_type": "missing_canonical"}]}'''})()
    calls = []

    def generate_content(**kwargs):
        calls.append(kwargs["model"])
        if len(calls) < 3:
            raise RuntimeError("503 UNAVAILABLE")
        return response

    monkeypatch.setattr("backend.ai.llm.client.models.generate_content", generate_content)
    monkeypatch.setattr("backend.ai.llm.time.sleep", lambda _delay: None)

    result = generate_recommendations("test prompt")

    assert calls == [llm.MODEL, llm.MODEL, llm.FALLBACK_MODEL]
    assert result.recommendations[0].title == "Add canonicals"

def test_service_persists_one_recommendation_for_a_group(tmp_path, monkeypatch):
    sessions = make_session(tmp_path)
    session, scan_id = make_scan(sessions)
    session.close()
    monkeypatch.setattr(
        "backend.services.multi_page_recommendation_service.generate_recommendations",
        lambda _prompt: AIRecommendationResult(recommendations=[
            AIRecommendation(priority=99, title="Add canonical links", reason="This tells search engines which URL to use.", impact="High", estimated_effort="Low", action="Add one canonical link to each affected page.", source_issue_type="missing_canonical", example="Use the page's preferred URL."),
        ]),
    )

    result = MultiPageRecommendationService().generate_for_scan(sessions(), scan_id)
    verification = sessions()
    records = verification.query(AIRecommendationRecord).all()

    assert result.recommendations[0].priority == 1
    assert result.recommendations[0].affected_page_count == 2
    assert len(records) == 1
    assert records[0].seo_issue.issue_type == "missing_canonical"
    assert "Affects 2 page(s)." in records[0].recommendation


def test_recommendation_endpoint_generates_for_persisted_scan(tmp_path, monkeypatch):
    sessions = make_session(tmp_path)
    session, scan_id = make_scan(sessions)
    session.close()
    app = FastAPI()
    app.include_router(recommendations_router)

    def override_db():
        db = sessions()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        "backend.services.multi_page_recommendation_service.generate_recommendations",
        lambda _prompt: AIRecommendationResult(recommendations=[
            AIRecommendation(priority=1, title="Add a sitemap", reason="It helps search engines find pages.", impact="Medium", estimated_effort="Low", action="Publish sitemap.xml.", source_issue_type="missing_sitemap"),
        ]),
    )

    with TestClient(app) as client:
        response = client.post(f"/scans/{scan_id}/recommendations")

    assert response.status_code == 200
    assert response.json()["recommendations"][0]["source_issue_type"] == "missing_sitemap"
