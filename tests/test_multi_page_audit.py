from datetime import timedelta

import pytest
import requests
from pydantic import ValidationError

from backend.api.site_audit import SiteAuditRequest
from backend.audit.adapter import page_to_scanner_response
from backend.audit.aggregator import generate_crawl_report
from backend.crawler.crawler import WebsiteCrawler
from backend.crawler.fetcher import FetchResult
from backend.crawler.parser import HTMLParser
from backend.crawler.robots import RobotsInfo, discover_robots
from backend.crawler.sitemap import discover_sitemap
from backend.schemas.crawl_report import CrawlExecution
from backend.schemas.page import PageAnalysis


class StubResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text


def page(url: str, **overrides) -> PageAnalysis:
    values = {
        "url": url,
        "final_url": url,
        "title": "A valid page title",
        "meta_description": "A sufficiently descriptive page summary for tests.",
        "canonical_url": url,
        "h1_count": 1,
        "h2_count": 1,
        "internal_links": 1,
        "og_title": "Open Graph title",
        "og_description": "Open Graph description",
    }
    values.update(overrides)
    return PageAnalysis(**values)


def test_robots_meta_does_not_imply_robots_txt():
    scan = page_to_scanner_response(
        page("https://example.com", robots_meta="noindex"),
    )

    assert scan.robots_found is False


def test_sitemap_discovery_uses_robots_declaration_once(monkeypatch):
    requested_urls = []

    def fake_get(url, **_kwargs):
        requested_urls.append(url)
        if url.endswith("/robots.txt"):
            return StubResponse(200, "Sitemap: https://example.com/sitemaps/main.xml")
        if url.endswith("/sitemap.xml"):
            return StubResponse(404)
        if url.endswith("/sitemaps/main.xml"):
            return StubResponse(200)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("backend.crawler.robots.requests.get", fake_get)
    monkeypatch.setattr("backend.crawler.sitemap.requests.get", fake_get)

    robots = discover_robots("https://example.com")
    sitemap = discover_sitemap("https://example.com", robots.sitemap_urls)

    assert robots.found is True
    assert sitemap.found is True
    assert sitemap.urls == ["https://example.com/sitemaps/main.xml"]
    assert requested_urls.count("https://example.com/robots.txt") == 1
    assert requested_urls.count("https://example.com/sitemap.xml") == 1


def test_site_level_robots_and_sitemap_issues_are_not_repeated_per_page():
    crawl = CrawlExecution(
        pages=[page("https://example.com"), page("https://example.com/about")],
        robots_txt_found=False,
        sitemap_found=False,
    )

    report = generate_crawl_report(crawl)

    assert {issue.rule_id for issue in report.site_issues} == {
        "missing_robots_txt",
        "missing_sitemap",
    }
    assert all(
        "missing_robots_txt" not in {issue.rule_id for issue in item.issues}
        and "missing_sitemap" not in {issue.rule_id for issue in item.issues}
        for item in report.pages
    )


def test_open_graph_fetch_metadata_https_and_indexability_are_preserved():
    analysis = HTMLParser().parse(
        """
        <html><head>
          <meta name="robots" content="noindex, follow">
          <meta property="og:title" content="RankPilot">
          <meta property="og:description" content="SEO auditing">
        </head><body><h1>Page</h1></body></html>
        """,
        "http://example.com/final",
        requested_url="http://example.com/requested",
        status_code=200,
        response_time=0.25,
        page_size=1234,
        content_type="text/html; charset=utf-8",
    )

    scan = page_to_scanner_response(analysis)

    assert analysis.url == "http://example.com/requested"
    assert analysis.final_url == "http://example.com/final"
    assert analysis.status_code == 200
    assert analysis.response_time == 0.25
    assert analysis.page_size == 1234
    assert analysis.content_type == "text/html; charset=utf-8"
    assert analysis.has_https is False
    assert analysis.is_indexable is False
    assert scan.og_title == "RankPilot"
    assert scan.og_description == "SEO auditing"


def test_https_is_detected_from_final_url():
    analysis = HTMLParser().parse("<html></html>", "https://example.com")

    assert analysis.has_https is True
    assert analysis.is_indexable is True


@pytest.mark.parametrize("max_pages", [0, -1, 101])
def test_site_audit_max_pages_has_safe_bounds(max_pages):
    with pytest.raises(ValidationError):
        SiteAuditRequest(url="https://example.com", max_pages=max_pages)


def test_partial_crawl_failures_are_reported(monkeypatch):
    monkeypatch.setattr(
        "backend.crawler.crawler.discover_robots",
        lambda *_args, **_kwargs: RobotsInfo(found=True, sitemap_urls=[]),
    )
    monkeypatch.setattr(
        "backend.crawler.crawler.discover_sitemap",
        lambda *_args, **_kwargs: type("Sitemap", (), {"found": True, "urls": ["https://example.com/sitemap.xml"]})(),
    )

    def fake_fetch(url):
        if url == "https://example.com":
            return FetchResult(
                url=url,
                status_code=200,
                html='<a href="/broken">Broken</a><h1>Home</h1>',
                response_time=0.1,
                content_type="text/html",
                page_size=45,
            )
        raise requests.RequestException("network failure")

    crawler = WebsiteCrawler(max_pages=2)
    monkeypatch.setattr(crawler.fetcher, "fetch", fake_fetch)

    crawl = crawler.crawl_with_result("https://example.com")
    report = generate_crawl_report(crawl)

    assert len(crawl.pages) == 1
    assert crawl.failures[0].url == "https://example.com/broken"
    assert report.summary.crawl_complete is False
    assert report.summary.failed_pages == 1
    assert report.failures[0].reason == "fetch_or_parse_failed"
