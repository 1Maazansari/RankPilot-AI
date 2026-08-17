"""
Website crawler for RankPilot AI.
"""

from collections import deque
import logging

from backend.crawler.fetcher import HTMLFetcher
from backend.crawler.parser import HTMLParser
from backend.crawler.robots import discover_robots
from backend.crawler.sitemap import discover_sitemap
from backend.crawler.url_manager import URLManager
from backend.schemas.crawl_report import CrawlExecution, CrawlFailure


logger = logging.getLogger(__name__)


class WebsiteCrawler:
    """
    Crawls a website and returns parsed pages.
    """

    def __init__(self, max_pages: int = 10):
        self.max_pages = max_pages

        self.fetcher = HTMLFetcher()
        self.parser = HTMLParser()

    def crawl(self, start_url: str):
        """
        Crawl a website starting from the given URL.
        """

        return self.crawl_with_result(start_url).pages

    def crawl_with_result(self, start_url: str) -> CrawlExecution:
        """Crawl a site and return pages with site-level crawl metadata."""

        start_url = URLManager.normalize(start_url)

        robots = discover_robots(start_url, timeout=self.fetcher.timeout)
        sitemap = discover_sitemap(
            start_url,
            robots.sitemap_urls,
            timeout=self.fetcher.timeout,
        )

        visited = set()
        queue = deque([start_url])

        pages = []
        failures = []

        while queue and len(pages) < self.max_pages:

            current_url = queue.popleft()

            current_url = URLManager.normalize(current_url)

            if current_url in visited:
                continue

            visited.add(current_url)

            try:
                # ---------------------------------
                # Fetch webpage
                # ---------------------------------
                result = self.fetcher.fetch(current_url)

                # ---------------------------------
                # Parse SEO information
                # ---------------------------------
                analysis = self.parser.parse(
                    result.html,
                    result.url,
                    requested_url=current_url,
                    status_code=result.status_code,
                    response_time=result.response_time,
                    page_size=result.page_size,
                    content_type=result.content_type,
                )

                # ---------------------------------
                # Extract links
                # ---------------------------------
                internal_links, external_links = (
                    self.parser.extract_links(
                        result.html,
                        result.url,
                    )
                )

                # Update statistics
                analysis.internal_links = len(internal_links)
                analysis.external_links = len(external_links)

                # ---------------------------------
                # Add new URLs to queue
                # ---------------------------------
                for link in internal_links:

                    normalized = URLManager.normalize(link)

                    if(
                        normalized not in visited
                        and normalized not in queue
                        and URLManager.is_html(normalized)
                    ):
                        queue.append(normalized) 
                        

                # ---------------------------------
                # Save page
                # ---------------------------------
                pages.append(analysis)

                print(f"✓ Crawled: {current_url}")

            except Exception as e:

                failures.append(
                    CrawlFailure(
                        url=current_url,
                        reason="fetch_or_parse_failed",
                    )
                )

                print(f"✗ Failed: {current_url}")
                logger.warning("Failed to crawl: %s", current_url, exc_info=True)

        return CrawlExecution(
            pages=pages,
            failures=failures,
            robots_txt_found=robots.found,
            sitemap_found=sitemap.found,
            sitemap_urls=sitemap.urls,
        )
