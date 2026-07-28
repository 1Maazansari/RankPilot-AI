"""
Central logging configuration for RankPilot AI.

Provides a reusable logger for the entire backend.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.config import settings

# ------------------------------------------------------------------
# Create logs directory if it doesn't exist
# ------------------------------------------------------------------
LOG_DIR = Path("backend/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "rankpilot.log"

# ------------------------------------------------------------------
# Log format
# ------------------------------------------------------------------
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ------------------------------------------------------------------
# Configure root logger only once
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Example:
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)