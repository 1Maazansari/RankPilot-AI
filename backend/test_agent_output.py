from pprint import pprint

from backend.agents.graph import brandvizi_agent_graph



test_state = {
    "scan": {
        "url": "https://example.com",
        "title": "",
        "meta_description": None,
        "canonical": None,
        "meta_robots": None,
        "language": "en",
        "charset": "UTF-8",
        "viewport": "width=device-width",
        "favicon": None,
        "h1_count": 0,
        "h2_count": 0,
        "images": [],
        "missing_alt": [],
        "internal_links": [],
        "robots_found": False,
        "sitemap_found": False,
        "og_title": None,
        "og_description": None,
        "og_image": None,
        "twitter_card": None,
        "content_evidence": {
            "word_count": 1200,
            "text_excerpt": "This is a sample article about blog SEO best practices...",
            "h1_texts": ["Blog SEO Best Practices"],
            "h2_texts": ["Keyword Research", "On-Page Optimization", "Link Building"],
            "h3_texts": ["Internal Linking Strategy", "Meta Tag Optimization"],
            "lists": [
                {"type": "ul", "item_count": 5, "excerpt": "Use descriptive titles | Write compelling meta descriptions | Optimize images"}
            ],
            "detected_questions": ["What is blog SEO?", "How do I optimize my blog?"],
            "schema": {"has_json_ld": True, "has_microdata": False, "types": ["Article"]},
        },
    },
    "seo_analysis": {
        "issues": [
            {
                "rule_id": "missing_title",
                "severity": "critical",
                "category": "metadata",
                "message": "The page is missing a title tag.",
                "recommendation": "Add a unique descriptive title tag.",
            },
            {
                "rule_id": "missing_meta_description",
                "severity": "high",
                "category": "metadata",
                "message": "The page is missing a meta description.",
                "recommendation": "Add a relevant meta description.",
            },
        ],
        "score": 45,
    },
    "errors": [],
}


result = brandvizi_agent_graph.invoke(test_state)

print("\n" + "=" * 70)
print("TECHNICAL SEO")
print("=" * 70)
pprint(result["technical_analysis"])

print("\n" + "=" * 70)
print("CONTENT INTELLIGENCE")
print("=" * 70)
pprint(result["content_analysis"])

print("\n" + "=" * 70)
print("AEO / GEO")
print("=" * 70)
pprint(result["aeo_geo_analysis"])

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)
pprint(result["validation"])

print("\n" + "=" * 70)
print("ERRORS")
print("=" * 70)
pprint(result.get("errors", []))