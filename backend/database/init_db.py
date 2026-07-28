"""
Initialize database tables.
"""

from backend.database.base import Base
from backend.database.session import engine

# Import models here
# Example:
# from backend.models.project import Project


def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_database()