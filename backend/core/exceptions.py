"""
Custom exceptions for RankPilot AI.

All application-specific exceptions should inherit from
RankPilotException.
"""


class RankPilotException(Exception):
    """Base exception for RankPilot AI."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationException(RankPilotException):
    """Raised when validation fails."""


class CrawlerException(RankPilotException):
    """Raised when website crawling fails."""


class SEOException(RankPilotException):
    """Raised when SEO analysis fails."""


class AIException(RankPilotException):
    """Raised when AI processing fails."""


class DatabaseException(RankPilotException):
    """Raised when database operations fail."""


class ReportException(RankPilotException):
    """Raised when report generation fails."""