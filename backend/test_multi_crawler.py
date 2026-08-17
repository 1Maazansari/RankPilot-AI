from backend.crawler.crawler import WebsiteCrawler


def main():
    url = "https://www.art.yale.edu/"

    crawler = WebsiteCrawler(max_pages=5)

    print("\n" + "=" * 70)
    print("RANKPILOT AI - MULTI PAGE CRAWLER TEST")
    print("=" * 70)

    pages = crawler.crawl(url)

    print("\n" + "=" * 70)
    print(f"CRAWL COMPLETE")
    print(f"TOTAL PAGES: {len(pages)}")
    print("=" * 70)

    for index, page in enumerate(pages, start=1):

        print("\n" + "-" * 70)
        print(f"PAGE {index}")
        print("-" * 70)

        print(f"URL              : {page.url}")
        print(f"Title            : {page.title}")
        print(f"Meta Description  : {page.meta_description}")
        print(f"Canonical         : {page.canonical_url}")
        print(f"Robots Meta       : {page.robots_meta}")
        print(f"Language          : {page.language}")
        print(f"Word Count        : {page.word_count}")

        print(f"H1 Count          : {page.h1_count}")
        print(f"H2 Count          : {page.h2_count}")

        print(f"Images            : {page.image_count}")
        print(f"Missing ALT       : {page.missing_alt_count}")

        print(f"Internal Links    : {page.internal_links}")
        print(f"External Links    : {page.external_links}")

        print(f"Open Graph        : {page.has_open_graph}")
        print(f"Twitter Card      : {page.has_twitter_card}")
        print(f"Schema Markup     : {page.has_schema_markup}")


if __name__ == "__main__":
    main()