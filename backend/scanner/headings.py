import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def count_h1(soup: BeautifulSoup) -> int:
    count = len(soup.find_all("h1"))
    logger.info("Heading count complete: h1_count=%s", count)
    return count


def count_h2(soup: BeautifulSoup) -> int:
    count = len(soup.find_all("h2"))
    logger.info("Heading count complete: h2_count=%s", count)
    return count
