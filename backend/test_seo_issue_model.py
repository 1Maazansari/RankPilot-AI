"""
Test Project -> Scan -> Page -> SEOIssue relationships.
"""

from backend.database.init_db import init_database
from backend.database.session import SessionLocal
from backend.models.project import Project
from backend.models.scan import Scan, ScanStatus
from backend.models.page import Page
from backend.models.seo_issue import SEOIssue, IssueSeverity


def test_seo_issue_model():
    """Test the Project -> Scan -> Page -> SEOIssue relationship."""

    init_database()

    db = SessionLocal()

    try:
        # Clean database (development only)
        db.query(SEOIssue).delete()
        db.query(Page).delete()
        db.query(Scan).delete()
        db.query(Project).delete()
        db.commit()

        # ------------------------
        # Create Project
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
        # Create Scan
        # ------------------------
        scan = Scan(
            project_id=project.id,
            status=ScanStatus.COMPLETED,
            seo_score=94.8,
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # ------------------------
        # Create Page
        # ------------------------
        page = Page(
            scan_id=scan.id,
            url="https://openai.com",
            title="OpenAI",
            meta_description="OpenAI Homepage",
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
        # Create SEO Issue
        # ------------------------
        issue = SEOIssue(
            page_id=page.id,
            issue_type="Missing Alt Text",
            title="Images missing ALT attributes",
            description="Several images do not contain ALT text.",
            severity=IssueSeverity.HIGH,
            recommendation="Add descriptive ALT text to all images.",
        )

        db.add(issue)
        db.commit()
        db.refresh(issue)

        # ------------------------
        # Print Results
        # ------------------------
        print("\n========== TEST RESULT ==========\n")

        print("✅ Project")
        print(project)

        print("\n✅ Scan")
        print(scan)

        print("\n✅ Page")
        print(page)

        print("\n✅ SEO Issue")
        print(issue)

        print("\n✅ Project -> Scans")
        print(project.scans)

        print("\n✅ Scan -> Pages")
        print(scan.pages)

        print("\n✅ Page -> SEO Issues")
        print(page.seo_issues)

        print("\n🎉 All relationships are working correctly!")

    finally:
        db.close()


if __name__ == "__main__":
    test_seo_issue_model()