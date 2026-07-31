"""
Page repository.
"""

from backend.models.page import Page
from backend.repositories.base_repository import BaseRepository


class PageRepository(BaseRepository[Page]):
    """Repository for Page model."""

    def __init__(self):
        super().__init__(Page)