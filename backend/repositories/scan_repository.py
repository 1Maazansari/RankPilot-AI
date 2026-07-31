"""
Scan repository.
"""

from backend.models.scan import Scan
from backend.repositories.base_repository import BaseRepository


class ScanRepository(BaseRepository[Scan]):
    """Repository for Scan model."""

    def __init__(self):
        super().__init__(Scan)