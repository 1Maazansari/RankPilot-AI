"""
Basic integration test for the BrandVizi LangGraph workflow.

This test verifies that the graph can execute with deterministic
SEO data without requiring the real website scanner.
"""

from backend.agents.graph import brandvizi_agent_graph


def test_brandvizi_agent_graph_execution():

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

    result = brandvizi_agent_graph.invoke(
        test_state
    )

    # ---------------------------------------------------------
    # Verify all specialist outputs exist
    # ---------------------------------------------------------

    assert "technical_analysis" in result

    assert "content_analysis" in result

    assert "aeo_geo_analysis" in result

    assert "validation" in result

    # ---------------------------------------------------------
    # Verify agent identities
    # ---------------------------------------------------------

    assert (
        result["technical_analysis"]["agent_name"]
        == "technical_seo"
    )

    assert (
        result["content_analysis"]["agent_name"]
        == "content_intelligence"
    )

    assert (
        result["aeo_geo_analysis"]["agent_name"]
        == "aeo_geo"
    )

    # ---------------------------------------------------------
    # Verify validation output
    # ---------------------------------------------------------

    assert "validated_findings" in result["validation"]

    assert "rejected_findings" in result["validation"]

    assert "warnings" in result["validation"]

    print("\nBrandVizi LangGraph execution successful.")

    print(
        "\nTechnical findings:",
        len(
            result["technical_analysis"]["findings"]
        ),
    )

    print(
        "Content findings:",
        len(
            result["content_analysis"]["findings"]
        ),
    )

    print(
        "AEO/GEO findings:",
        len(
            result["aeo_geo_analysis"]["findings"]
        ),
    )

    print(
        "Validated findings:",
        len(
            result["validation"]["validated_findings"]
        ),
    )