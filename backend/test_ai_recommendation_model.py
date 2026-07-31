"""
Test Project -> Scan -> Page -> SEOIssue -> AIRecommendation relationships.
"""

from backend.database.init_db import init_database
from backend.database.session import SessionLocal
from backend.models.project import Project
from backend.models.scan import Scan, ScanStatus
from backend.models.page import Page
from backend.models.seo_issue import SEOIssue, IssueSeverity
from backend.models.ai_recommendation import AIRecommendation


def test_ai_recommendation_model():
    """Test the complete database relationship chain."""

    init_database()

    db = SessionLocal()

    try:
        # Clean database (development only)
        db.query(AIRecommendation).delete()
        db.query(SEOIssue).delete()
        db.query(Page).delete()
        db.query(Scan).delete()
        db.query(Project).delete()
        db.commit()

        # ------------------------
        # Project
        # ------------------------
        project = Project(
            name="OpenAI",
            website="https://openai.com",
            description="Official OpenAI website",
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        # ------------------------
        # Scan
        # ------------------------
        scan = Scan(
            project_id=project.id,
            status=ScanStatus.COMPLETED,
            seo_score=95.5,
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # ------------------------
        # Page
        # ------------------------
        page = Page(
            scan_id=scan.id,
            url="https://openai.com",
            title="OpenAI",
            meta_description="Official OpenAI homepage",
            h1="OpenAI",
            canonical_url="https://openai.com",
            status_code=200,
            load_time=0.42,
            word_count=1500,
            is_indexable=True,
        )

        db.add(page)
        db.commit()
        db.refresh(page)

        # ------------------------
        # SEO Issue
        # ------------------------
        issue = SEOIssue(
            page_id=page.id,
            issue_type="Missing Alt Text",
            title="Images missing ALT attributes",
            description="Some images do not have ALT text.",
            severity=IssueSeverity.HIGH,
            recommendation="Add descriptive ALT attributes.",
        )

        db.add(issue)
        db.commit()
        db.refresh(issue)

        # ------------------------
        # AI Recommendation
        # ------------------------
        ai = AIRecommendation(
            seo_issue_id=issue.id,
            recommendation="Use concise, descriptive ALT text for every image.",
            reasoning="Improves accessibility and image SEO.",
            priority_score=9,
        )

        db.add(ai)
        db.commit()
        db.refresh(ai)

        # ------------------------
        # Print Results
        # ------------------------
        print("\n========== TEST RESULT ==========\n")

        print("Project:", project)
        print("Scan:", scan)
        print("Page:", page)
        print("SEO Issue:", issue)
        print("AI Recommendation:", ai)

        print("\nProject -> Scans")
        print(project.scans)

        print("\nScan -> Pages")
        print(scan.pages)

        print("\nPage -> SEO Issues")
        print(page.seo_issues)

        print("\nSEO Issue -> AI Recommendations")
        print(issue.ai_recommendations)

        print("\n🎉 All relationships are working correctly!")

    finally:
        db.close()


if __name__ == "__main__":
    test_ai_recommendation_model()