"""
Website crawler for RankPilot AI.
"""

from collections import deque

from backend.crawler.fetcher import HTMLFetcher
from backend.crawler.parser import HTMLParser
from backend.crawler.url_manager import URLManager


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

        start_url = URLManager.normalize(start_url)

        visited = set()
        queue = deque([start_url])

        pages = []

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

                print(f"✗ Failed: {current_url}")
                print(e)

        return pages