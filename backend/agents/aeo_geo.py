"""
BrandVizi AEO/GEO Agent.

This module contains the AEO/GEO specialist node used by the
BrandVizi LangGraph workflow.

AEO = Answer Engine Optimization
GEO = Generative Engine Optimization

Responsibilities:
- Analyze verified SEO evidence from the deterministic SEO engine.
- Reason about answer-engine and generative-search implications.
- Identify opportunities for better machine understanding.
- Provide practical implementation recommendations.
- Generate code suggestions where appropriate.
- Keep every finding traceable to deterministic evidence
  or to actual scan evidence (source_rule_id: null).
"""

import logging
from typing import Any

from pydantic import ValidationError

from backend.agents.prompts import (
    AEO_GEO_SYSTEM_PROMPT,
    build_aeo_geo_prompt,
)
from backend.agents.schemas import (
    AgentAnalysis,
    AgentFinding,
    CodeSuggestion,
)
from backend.agents.state import AgentState
from backend.ai.llm import generate_json


logger = logging.getLogger(__name__)


# ============================================================
# AEO / GEO CATEGORIES
# ============================================================

AEO_GEO_CATEGORIES = {
    "aeo_geo",
    "aeo",
    "geo",
    "schema",
    "structured_data",
    "technical",
    "metadata",
    "headings",
    "content",
    "social",
}


# ============================================================
# HELPERS
# ============================================================

def _empty_analysis(summary: str) -> AgentAnalysis:
    """
    Create an empty but valid AEO/GEO analysis.
    """

    return AgentAnalysis(
        agent_name="aeo_geo",
        summary=summary,
        findings=[],
    )


def _get_verified_issues(
    seo_analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract all verified issues detected by the deterministic
    SEO engine.

    The AEO/GEO agent receives all issues and independently
    determines which are relevant to its specialization.
    """

    issues = seo_analysis.get("issues", [])

    if not isinstance(issues, list):
        return []

    verified_issues: list[dict[str, Any]] = []

    for issue in issues:

        if not isinstance(issue, dict):
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
    the structured CodeSuggestion format expected by our
    Pydantic schema.

    It does not create new findings or change the evidence
    used by the agent.
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

        # Gemini returned code directly as a string.
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
                    "metadata",
                    "headings",
                    "technical",
                    "social",
                    "aeo_geo",
                    "aeo",
                    "geo",
                    "schema",
                    "structured_data",
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
                    "AEO/GEO agent and normalized into "
                    "the BrandVizi structured schema."
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
    """

    verified_rule_ids = {
        str(issue.get("rule_id"))
        for issue in verified_issues
        if issue.get("rule_id") is not None
    }

    validated_findings: list[Any] = []

    for finding in analysis.findings:

        source_rule_id = finding.source_rule_id

        if source_rule_id is not None:

            if source_rule_id in verified_rule_ids:
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

def aeo_geo_node(
    state: AgentState,
) -> dict[str, Any]:
    """
    AEO/GEO specialist node for LangGraph.

    Flow:

        AgentState
            ↓
        Deterministic SEO evidence
            ↓
        AEO/GEO prompt
            ↓
        Gemini
            ↓
        Response normalization
            ↓
        Pydantic validation
            ↓
        Evidence validation
            ↓
        aeo_geo_analysis
    """

    # ---------------------------------------------------------
    # 1. Read shared LangGraph state
    # ---------------------------------------------------------

    scan = state.get("scan", {})

    seo_analysis = state.get(
        "seo_analysis",
        {},
    )

    # ---------------------------------------------------------
    # 2. Extract verified AEO/GEO evidence and content evidence
    # ---------------------------------------------------------

    verified_issues = _get_verified_issues(
        seo_analysis
    )

    content_evidence = scan.get("content_evidence", {})
    detected_questions = content_evidence.get("detected_questions", [])
    schema_info = content_evidence.get("schema", {})
    schema_types = [str(t).lower() for t in schema_info.get("types", [])]
    has_faq_schema = any("faq" in t or "qapage" in t for t in schema_types)

    has_content_evidence = bool(
        content_evidence.get("text_excerpt")
        or detected_questions
        or content_evidence.get("h1_texts")
    )

    # Helper to construct guaranteed evidence-derived finding
    def _create_faq_schema_finding() -> AgentFinding:
        q_sample = detected_questions[:3]
        faq_items = []
        for q in q_sample:
            faq_items.append(
                '    {\n'
                '      "@type": "Question",\n'
                f'      "name": "{q}",\n'
                '      "acceptedAnswer": {\n'
                '        "@type": "Answer",\n'
                '        "text": "Direct, concise answer extracted from page content."\n'
                '      }\n'
                '    }'
            )
        faq_json = (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "FAQPage",\n'
            '  "mainEntity": [\n'
            + ",\n".join(faq_items)
            + '\n  ]\n'
            '}\n'
            '</script>'
        )

        return AgentFinding(
            title="Detected Questions Present Without FAQ Structured Data",
            category="aeo_geo",
            severity="medium",
            explanation=(
                f"The page content contains {len(detected_questions)} detected questions "
                f"({', '.join(detected_questions[:2])}), but the schema evidence indicates "
                "no FAQPage or QAPage structured data is implemented. Without structured data, "
                "answer engines and generative search tools cannot reliably parse and extract "
                "direct question-and-answer pairs for AI summaries."
            ),
            recommendation=(
                "Implement FAQPage JSON-LD schema markup mapping the detected questions to "
                "their corresponding answers within the text to enhance answer engine visibility."
            ),
            implementation_steps=[
                f"Review the detected questions: {', '.join(detected_questions[:3])}.",
                "Extract concise, direct factual answers from the surrounding content.",
                "Construct and inject a FAQPage JSON-LD script into the page template or document head.",
            ],
            code_suggestion=CodeSuggestion(
                language="html",
                code=faq_json,
                file_hint="HTML head or page template",
                location_hint="Inside the <head> element",
                explanation="Structured FAQPage JSON-LD enables answer engines to identify direct answers to user queries.",
            ),
            confidence=0.88,
            source_rule_id=None,
            source_message=None,
        )

    # ---------------------------------------------------------
    # 3. Nothing relevant to analyze
    # ---------------------------------------------------------

    if not verified_issues and not has_content_evidence:

        analysis = _empty_analysis(
            "No verified SEO evidence requiring AEO/GEO "
            "analysis was detected."
        )

        return {
            "aeo_geo_analysis": analysis.model_dump(),
        }

    # ---------------------------------------------------------
    # 4. Build grounded AEO/GEO prompt
    # ---------------------------------------------------------

    prompt = build_aeo_geo_prompt(
        scan=scan,
        issues=verified_issues,
    )

    # ---------------------------------------------------------
    # 5. Call Gemini through shared LLM layer
    # ---------------------------------------------------------

    try:

        raw_result = generate_json(
            prompt=prompt,
            system_prompt=AEO_GEO_SYSTEM_PROMPT,
        )

    except Exception as exc:

        logger.exception(
            "AEO/GEO Gemini call failed."
        )

        fallback_findings = []
        if detected_questions and not has_faq_schema:
            fallback_findings.append(_create_faq_schema_finding())

        summary = (
            "The page contains detected questions that can be formatted as FAQPage structured data for answer engines."
            if fallback_findings
            else "AEO/GEO analysis was unavailable because the AI service could not be reached."
        )

        analysis = AgentAnalysis(
            agent_name="aeo_geo",
            summary=summary,
            findings=fallback_findings,
        )

        return {
            "aeo_geo_analysis": analysis.model_dump(),
            "errors": [
                f"AEO/GEO agent error: {exc}"
            ] if not fallback_findings else [],
        }

    # ---------------------------------------------------------
    # 6. Log raw Gemini response for debugging
    # ---------------------------------------------------------

    logger.info(
        "AEO/GEO raw Gemini response: %r",
        raw_result,
    )

    # ---------------------------------------------------------
    # 7. Normalize Gemini response
    # ---------------------------------------------------------

    raw_result = _normalize_code_suggestions(
        raw_result
    )

    # ---------------------------------------------------------
    # 8. Validate Gemini structured response
    # ---------------------------------------------------------

    try:

        analysis = AgentAnalysis.model_validate(
            raw_result
        )

    except ValidationError as exc:

        logger.exception(
            "AEO/GEO response validation failed. "
            "Raw normalized Gemini response: %r",
            raw_result,
        )

        fallback_findings = []
        if detected_questions and not has_faq_schema:
            fallback_findings.append(_create_faq_schema_finding())

        analysis = AgentAnalysis(
            agent_name="aeo_geo",
            summary=(
                "AEO/GEO Agent returned an invalid response, but evidence-derived opportunities were identified."
                if fallback_findings
                else "AEO/GEO Agent returned an invalid structured AI response."
            ),
            findings=fallback_findings,
        )

        return {
            "aeo_geo_analysis": analysis.model_dump(),
            "errors": [
                f"AEO/GEO response validation error: {exc}"
            ] if not fallback_findings else [],
        }

    # ---------------------------------------------------------
    # 9. Force correct agent identity
    # ---------------------------------------------------------

    analysis = analysis.model_copy(
        update={
            "agent_name": "aeo_geo",
        }
    )

    # ---------------------------------------------------------
    # 10. Ground findings against deterministic evidence
    # ---------------------------------------------------------

    analysis = _validate_against_evidence(
        analysis=analysis,
        verified_issues=verified_issues,
        valid_categories=AEO_GEO_CATEGORIES,
    )

    # ---------------------------------------------------------
    # 10b. Ensure structured finding when supported by
    #      detected_questions + schema evidence (source_rule_id: null)
    # ---------------------------------------------------------

    if detected_questions and not has_faq_schema:
        has_question_schema_finding = any(
            finding.source_rule_id is None
            and (
                "question" in finding.title.lower()
                or "faq" in finding.title.lower()
                or "schema" in finding.title.lower()
                or "structured data" in finding.title.lower()
            )
            for finding in analysis.findings
        )

        if not has_question_schema_finding:
            derived_finding = _create_faq_schema_finding()
            analysis = analysis.model_copy(
                update={
                    "findings": [*analysis.findings, derived_finding],
                }
            )

    # ---------------------------------------------------------
    # 11. Return LangGraph state update
    # ---------------------------------------------------------

    return {
        "aeo_geo_analysis": analysis.model_dump(),
    }
