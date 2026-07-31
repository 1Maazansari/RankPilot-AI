"""
Project repository.
"""

from backend.models.project import Project
from backend.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model."""

    def __init__(self):
        super().__init__(Project)