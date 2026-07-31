"""
Test the BaseRepository and ProjectRepository.
"""

from backend.database.init_db import init_database
from backend.database.session import SessionLocal
from backend.models.project import Project
from backend.repositories.project_repository import ProjectRepository


def test_project_repository():
    """Test CRUD operations using ProjectRepository."""

    init_database()

    db = SessionLocal()
    repo = ProjectRepository()

    try:
        # Clean existing data
        db.query(Project).delete()
        db.commit()

        print("=" * 60)
        print("      RankPilot AI - Repository Layer Tests")
        print("=" * 60)

        # -----------------------------
        # CREATE
        # -----------------------------
        print("\n[1] CREATE")

        project = Project(
            name="OpenAI",
            website="https://openai.com",
            description="Official OpenAI website",
        )

        project = repo.create(db, project)

        print("✅ Created:", project)

        # -----------------------------
        # GET BY ID
        # -----------------------------
        print("\n[2] GET BY ID")

        fetched = repo.get_by_id(db, project.id)

        print("✅ Retrieved:", fetched)

        # -----------------------------
        # GET ALL
        # -----------------------------
        print("\n[3] GET ALL")

        projects = repo.get_all(db)

        print(f"✅ Total Projects: {len(projects)}")

        for p in projects:
            print("   ", p)

        # -----------------------------
        # UPDATE
        # -----------------------------
        print("\n[4] UPDATE")

        fetched.description = "Updated by Repository Test"

        updated = repo.update(db, fetched)

        print("✅ Updated:", updated)

        # -----------------------------
        # DELETE
        # -----------------------------
        print("\n[5] DELETE")

        repo.delete(db, updated)

        remaining = repo.get_all(db)

        print(f"✅ Remaining Projects: {len(remaining)}")

        print("\n🎉 Repository Layer Working Successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    test_project_repository()