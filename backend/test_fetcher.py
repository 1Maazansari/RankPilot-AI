"""
Test HTML Fetcher.
"""

from backend.crawler.fetcher import HTMLFetcher


def test_fetcher():

    fetcher = HTMLFetcher()

    result = fetcher.fetch("https://openai.com")

    print("=" * 60)
    print("RankPilot Fetcher Test")
    print("=" * 60)

    print("URL:", result.url)
    print("Status:", result.status_code)
    print("Response Time:", result.response_time)
    print("Content-Type:", result.content_type)
    print("HTML Length:", len(result.html))

    print("\nFirst 200 Characters:\n")
    print(result.html[:200])

    print("\n✅ Fetcher working successfully!")


if __name__ == "__main__":
    test_fetcher()