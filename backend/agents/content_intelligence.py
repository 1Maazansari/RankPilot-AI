"""
BrandVizi Content Intelligence Agent.

This module contains the Content Intelligence node used by the
BrandVizi LangGraph workflow.

Responsibilities:
- Read verified SEO evidence from the deterministic SEO engine.
- Analyze content-related implications using Gemini.
- Provide practical content recommendations.
- Generate implementation guidance where appropriate.
- Keep every AI finding traceable to deterministic evidence
  or to actual scan evidence (source_rule_id: null).
"""

import logging
from typing import Any

from pydantic import ValidationError

from backend.agents.prompts import (
    CONTENT_INTELLIGENCE_SYSTEM_PROMPT,
    build_content_intelligence_prompt,
)
from backend.agents.schemas import AgentAnalysis
from backend.agents.state import AgentState
from backend.ai.llm import generate_json


logger = logging.getLogger(__name__)


# ============================================================
# CONTENT CATEGORIES AND BOUNDARIES
# ============================================================

CONTENT_CATEGORIES = {
    "content",
    "headings",
    "metadata",
}

# Technical SEO rules that Content Intelligence must NEVER analyze or produce
# findings for. These belong strictly to the Technical SEO specialist.
EXCLUDED_TECHNICAL_RULES = {
    "missing_alt_text",
    "missing_canonical",
    "missing_meta_robots",
    "missing_robots_txt",
    "missing_sitemap",
    "missing_internal_links",
    "missing_og_title",
    "missing_og_description",
}

DISALLOWED_CONTENT_CATEGORIES = {
    "images",
    "technical",
    "links",
    "social",
}


# ============================================================
# HELPERS
# ============================================================

def _empty_analysis(summary: str) -> AgentAnalysis:
    """
    Create an empty but valid Content Intelligence analysis.
    """

    return AgentAnalysis(
        agent_name="content_intelligence",
        summary=summary,
        findings=[],
    )


def _get_verified_issues(
    seo_analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract verified issues relevant to content intelligence.

    Filters out purely technical SEO issues (such as missing_alt_text,
    canonicalization, sitemaps, robots directives, etc.) to prevent
    Content Intelligence from duplicating Technical SEO findings.
    """

    issues = seo_analysis.get("issues", [])

    if not isinstance(issues, list):
        return []

    verified_issues: list[dict[str, Any]] = []

    for issue in issues:

        if not isinstance(issue, dict):
            continue

        rule_id = str(issue.get("rule_id", ""))
        category = str(issue.get("category", "")).lower()

        if rule_id in EXCLUDED_TECHNICAL_RULES or category in DISALLOWED_CONTENT_CATEGORIES:
            continue

        verified_issues.append(issue)

    return verified_issues


def _normalize_code_suggestions(
    raw_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize Gemini's code_suggestion output before
    Pydantic validation.

    Gemini may occasionally return:

        "code_suggestion": "<title>...</title>"

    instead of:

        "code_suggestion": {
            "language": "html",
            "code": "<title>...</title>",
            "explanation": "...",
        }

    This helper converts the shorthand string form into
    the structured CodeSuggestion format expected by the
    BrandVizi schema.

    It does not create new findings or change their
    deterministic evidence.
    """

    if not isinstance(raw_result, dict):
        return raw_result

    findings = raw_result.get("findings")

    if not isinstance(findings, list):
        return raw_result

    normalized_findings: list[Any] = []

    for finding in findings:

        if not isinstance(finding, dict):
            normalized_findings.append(finding)
            continue

        normalized_finding = dict(finding)

        code_suggestion = normalized_finding.get(
            "code_suggestion"
        )

        # Already correctly structured.
        if isinstance(code_suggestion, dict):
            normalized_findings.append(
                normalized_finding
            )
            continue

        # No code suggestion.
        if code_suggestion is None:
            normalized_findings.append(
                normalized_finding
            )
            continue

        # Gemini returned the code directly as a string.
        if isinstance(code_suggestion, str):

            category = str(
                normalized_finding.get(
                    "category",
                    "",
                )
            ).lower()

            language = (
                "html"
                if category in {
                    "content",
                    "headings",
                    "metadata",
                }
                else "text"
            )

            normalized_finding[
                "code_suggestion"
            ] = {
                "language": language,
                "code": code_suggestion,
                "file_hint": None,
                "location_hint": None,
                "explanation": (
                    "Code suggestion returned by the "
                    "Content Intelligence Agent and "
                    "normalized into the BrandVizi "
                    "structured schema."
                ),
            }

        normalized_findings.append(
            normalized_finding
        )

    return {
        **raw_result,
        "findings": normalized_findings,
    }


def _validate_against_evidence(
    analysis: AgentAnalysis,
    verified_issues: list[dict[str, Any]],
    valid_categories: set[str],
) -> AgentAnalysis:
    """
    Validate AI findings against deterministic evidence and
    available scan evidence.

    Rule-backed findings must match a verified deterministic SEO rule.
    Evidence-derived findings (source_rule_id: null) must have an
    appropriate category and required fields.

    Strictly filters out technical SEO issues like missing_alt_text
    to avoid duplicating Technical SEO findings.
    """

    verified_rule_ids = {
        str(issue.get("rule_id"))
        for issue in verified_issues
        if issue.get("rule_id") is not None
    }

    validated_findings: list[Any] = []

    for finding in analysis.findings:

        source_rule_id = finding.source_rule_id

        # Strictly reject any technical SEO issues (such as missing_alt_text)
        if source_rule_id in EXCLUDED_TECHNICAL_RULES:
            continue

        if finding.category in DISALLOWED_CONTENT_CATEGORIES:
            continue

        title_lower = finding.title.lower()
        if "alt text" in title_lower or "alt attribute" in title_lower:
            continue

        if source_rule_id is not None:

            if source_rule_id in verified_rule_ids and finding.category in valid_categories:
                validated_findings.append(finding)

        else:

            if finding.category in valid_categories:
                if (
                    finding.title
                    and finding.explanation
                    and finding.recommendation
                ):
                    validated_findings.append(finding)

    return analysis.model_copy(
        update={
            "findings": validated_findings,
        }
    )


# ============================================================
# LANGGRAPH NODE
# ============================================================

def content_intelligence_node(
    state: AgentState,
) -> dict[str, Any]:
    """
    Content Intelligence specialist node for LangGraph.

    Flow:

        AgentState
            ↓
        Deterministic SEO evidence
            ↓
        Content Intelligence prompt
            ↓
        Gemini
            ↓
        Response normalization
            ↓
        Pydantic validation
            ↓
        Evidence validation
            ↓
        content_analysis
    """

    # ---------------------------------------------------------
    # 1. Read shared LangGraph state
    # ---------------------------------------------------------

    scan = state.get(
        "scan",
        {},
    )

    seo_analysis = state.get(
        "seo_analysis",
        {},
    )

    # ---------------------------------------------------------
    # 2. Extract verified content issues
    # ---------------------------------------------------------

    verified_issues = _get_verified_issues(
        seo_analysis
    )

    content_evidence = scan.get(
        "content_evidence",
        {},
    )

    has_content_evidence = bool(
        content_evidence.get("text_excerpt")
        or content_evidence.get("h1_texts")
        or content_evidence.get("h2_texts")
    )

    # ---------------------------------------------------------
    # 3. Nothing to analyze
    # ---------------------------------------------------------

    if not verified_issues and not has_content_evidence:

        analysis = _empty_analysis(
            "No verified content-related SEO issues or content "
            "evidence were available for analysis."
        )

        return {
            "content_analysis": analysis.model_dump(),
        }

    # ---------------------------------------------------------
    # 4. Build grounded AI prompt
    # ---------------------------------------------------------

    prompt = build_content_intelligence_prompt(
        scan=scan,
        issues=verified_issues,
    )

    # ---------------------------------------------------------
    # 5. Call Gemini through shared LLM layer
    # ---------------------------------------------------------

    try:

        raw_result = generate_json(
            prompt=prompt,
            system_prompt=CONTENT_INTELLIGENCE_SYSTEM_PROMPT,
        )

    except Exception as exc:

        logger.exception(
            "Content Intelligence Gemini call failed."
        )

        analysis = _empty_analysis(
            "Content Intelligence analysis was unavailable "
            "because the AI service could not be reached."
        )

        return {
            "content_analysis": analysis.model_dump(),
            "errors": [
                f"Content Intelligence agent error: {exc}"
            ],
        }

    # ---------------------------------------------------------
    # 6. Log raw Gemini response for debugging
    # ---------------------------------------------------------

    logger.info(
        "Content Intelligence raw Gemini response: %r",
        raw_result,
    )

    # ---------------------------------------------------------
    # 7. Normalize Gemini response
    # ---------------------------------------------------------

    raw_result = _normalize_code_suggestions(
        raw_result
    )

    # ---------------------------------------------------------
    # 8. Validate structured Gemini response
    # ---------------------------------------------------------

    try:

        analysis = AgentAnalysis.model_validate(
            raw_result
        )

    except ValidationError as exc:

        logger.exception(
            "Content Intelligence response validation failed. "
            "Raw normalized Gemini response: %r",
            raw_result,
        )

        analysis = _empty_analysis(
            "Content Intelligence Agent returned an invalid "
            "structured AI response."
        )

        return {
            "content_analysis": analysis.model_dump(),
            "errors": [
                f"Content Intelligence response validation error: {exc}"
            ],
        }

    # ---------------------------------------------------------
    # 9. Force correct agent identity
    # ---------------------------------------------------------

    analysis = analysis.model_copy(
        update={
            "agent_name": "content_intelligence",
        }
    )

    # ---------------------------------------------------------
    # 10. Ground AI findings against deterministic evidence
    # ---------------------------------------------------------

    analysis = _validate_against_evidence(
        analysis=analysis,
        verified_issues=verified_issues,
        valid_categories=CONTENT_CATEGORIES,
    )

    # ---------------------------------------------------------
    # 11. Return LangGraph state update
    # ---------------------------------------------------------

    return {
        "content_analysis": analysis.model_dump(),
    }
