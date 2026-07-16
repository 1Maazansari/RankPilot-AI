import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def count_images(soup: BeautifulSoup) -> int:
    count = len(soup.find_all("img"))
    logger.info("Image count complete: images=%s", count)
    return count


def count_missing_alt_text(soup: BeautifulSoup) -> int:
    missing_alt = 0
    for image in soup.find_all("img"):
        alt_text = image.get("alt")
        if alt_text is None or not alt_text.strip():
            missing_alt += 1

    logger.info("Missing alt count complete: missing_alt=%s", missing_alt)
    return missing_alt
