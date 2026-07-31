"""
Initialize the database.
"""

from backend.database.base import Base
from backend.database.session import engine

# Import all models
from backend.models.project import Project
from backend.models.scan import Scan


def init_database() -> None:
    """
    Create all database tables.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    init_database()