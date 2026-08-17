"""
Initialize the database.
"""

from sqlalchemy import inspect, text

from backend.database.base import Base
from backend.database.session import engine

# Import all models
from backend.models.project import Project
from backend.models.scan import Scan
from backend.models.page import Page
from backend.models.seo_issue import SEOIssue
from backend.models.ai_recommendation import AIRecommendation


def _upgrade_sqlite_schema() -> None:
    """Upgrade development databases created before audit persistence existed."""
    inspector = inspect(engine)
    columns = {
        table: {column["name"] for column in inspector.get_columns(table)}
        for table in inspector.get_table_names()
    }
    additions = {
        "scans": {
            "requested_url": "VARCHAR(1000)", "max_pages": "INTEGER",
            "total_pages": "INTEGER", "failed_pages": "INTEGER",
            "crawl_complete": "BOOLEAN", "grade": "VARCHAR(2)",
            "duration_seconds": "FLOAT",
        },
        "pages": {
            "final_url": "VARCHAR(1000)", "canonical_url": "VARCHAR(1000)",
            "robots_meta": "VARCHAR(255)", "language": "VARCHAR(20)",
            "charset": "VARCHAR(50)", "response_time": "FLOAT",
            "page_size": "INTEGER", "h1_count": "INTEGER DEFAULT 0",
            "h2_count": "INTEGER DEFAULT 0", "image_count": "INTEGER DEFAULT 0",
            "missing_alt_count": "INTEGER DEFAULT 0", "internal_links": "INTEGER DEFAULT 0",
            "external_links": "INTEGER DEFAULT 0", "has_https": "BOOLEAN DEFAULT 1",
            "has_open_graph": "BOOLEAN DEFAULT 0", "has_twitter_card": "BOOLEAN DEFAULT 0",
            "has_schema_markup": "BOOLEAN DEFAULT 0", "seo_score": "FLOAT",
        },
    }
    with engine.begin() as connection:
        for table, expected in additions.items():
            for column, type_sql in expected.items():
                if column not in columns.get(table, set()):
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_sql}"))

        if "scan_id" not in columns.get("seo_issues", set()):
            connection.execute(text("PRAGMA foreign_keys=OFF"))
            connection.execute(text("""
                CREATE TABLE seo_issues_upgrade (
                    id INTEGER NOT NULL PRIMARY KEY, scan_id INTEGER NOT NULL,
                    page_id INTEGER, issue_type VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL, description TEXT NOT NULL,
                    severity VARCHAR(8) NOT NULL, recommendation TEXT,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY(scan_id) REFERENCES scans (id),
                    FOREIGN KEY(page_id) REFERENCES pages (id)
                )
            """))
            connection.execute(text("""
                INSERT INTO seo_issues_upgrade
                (id, scan_id, page_id, issue_type, title, description, severity, recommendation, created_at)
                SELECT seo_issues.id, pages.scan_id, seo_issues.page_id,
                       seo_issues.issue_type, seo_issues.title, seo_issues.description,
                       seo_issues.severity, seo_issues.recommendation, seo_issues.created_at
                FROM seo_issues JOIN pages ON pages.id = seo_issues.page_id
            """))
            connection.execute(text("DROP TABLE seo_issues"))
            connection.execute(text("ALTER TABLE seo_issues_upgrade RENAME TO seo_issues"))
            connection.execute(text("PRAGMA foreign_keys=ON"))


def init_database() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "sqlite":
        _upgrade_sqlite_schema()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()
