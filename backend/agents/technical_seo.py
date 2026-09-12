"""
BrandVizi Technical SEO Agent.

This module contains the Technical SEO node used by the
BrandVizi LangGraph workflow.

Responsibilities:
- Read deterministic SEO evidence.
- Analyze verified technical SEO issues using Gemini.
- Generate practical recommendations.
- Generate code suggestions where appropriate.
- Keep every AI finding traceable to a deterministic SEO rule
  or to actual scan evidence (source_rule_id: null).
"""

from typing import Any

from pydantic import ValidationError

from backend.agents.prompts import (
    TECHNICAL_SEO_SYSTEM_PROMPT,
    build_technical_seo_prompt,
)
from backend.agents.schemas import AgentAnalysis
from backend.agents.state import AgentState
from backend.ai.llm import generate_json


# Categories handled by the Technical SEO Agent.
TECHNICAL_CATEGORIES = {
    "technical",
    "metadata",
    "headings",
    "images",
    "links",
    "social",
}


def _empty_analysis(summary: str) -> AgentAnalysis:
    """
    Create an empty but valid Technical SEO analysis.
    """

    return AgentAnalysis(
        agent_name="technical_seo",
        summary=summary,
        findings=[],
    )


def _get_verified_issues(
    seo_analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract all verified issues detected by the deterministic
    SEO engine.

    The AI agent receives all issues and independently determines
    which are relevant to its technical SEO specialization.
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


def technical_seo_node(
    state: AgentState,
) -> dict[str, Any]:
    """
    Technical SEO specialist node for LangGraph.

    Flow:

        AgentState
            ↓
        Deterministic SEO evidence
            ↓
        Technical SEO prompt
            ↓
        Gemini
            ↓
        Pydantic validation
            ↓
        Evidence validation
            ↓
        technical_analysis
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
    # 2. Extract verified technical issues
    # ---------------------------------------------------------

    verified_issues = _get_verified_issues(
        seo_analysis
    )

    # ---------------------------------------------------------
    # 3. Nothing to analyze
    # ---------------------------------------------------------

    if not verified_issues:

        analysis = _empty_analysis(
            "No verified technical SEO issues were detected "
            "by the deterministic SEO engine."
        )

        return {
            "technical_analysis": analysis.model_dump(),
        }

    # ---------------------------------------------------------
    # 4. Build grounded AI prompt
    # ---------------------------------------------------------

    prompt = build_technical_seo_prompt(
        scan=scan,
        issues=verified_issues,
    )

    # ---------------------------------------------------------
    # 5. Call Gemini through the shared LLM layer
    # ---------------------------------------------------------

    try:

        raw_result = generate_json(
            prompt=prompt,
            system_prompt=TECHNICAL_SEO_SYSTEM_PROMPT,
        )

    except Exception as exc:

        analysis = _empty_analysis(
            "Technical SEO analysis was unavailable "
            "because the AI service could not be reached."
        )

        return {
            "technical_analysis": analysis.model_dump(),
            "errors": [
                f"Technical SEO agent error: {exc}"
            ],
        }

    # ---------------------------------------------------------
    # 6. Validate Gemini's structured response
    # ---------------------------------------------------------

    try:

        analysis = AgentAnalysis.model_validate(
            raw_result
        )

    except ValidationError as exc:

        analysis = _empty_analysis(
            "Technical SEO analysis returned an invalid "
            "structured AI response."
        )

        return {
            "technical_analysis": analysis.model_dump(),
            "errors": [
                f"Technical SEO response validation error: {exc}"
            ],
        }

    # ---------------------------------------------------------
    # 7. Force correct agent identity
    # ---------------------------------------------------------

    analysis = analysis.model_copy(
        update={
            "agent_name": "technical_seo",
        }
    )

    # ---------------------------------------------------------
    # 8. Ground AI findings against deterministic evidence
    # ---------------------------------------------------------

    analysis = _validate_against_evidence(
        analysis=analysis,
        verified_issues=verified_issues,
        valid_categories=TECHNICAL_CATEGORIES,
    )

    # ---------------------------------------------------------
    # 9. Return LangGraph state update
    # ---------------------------------------------------------

    return {
        "technical_analysis": analysis.model_dump(),
    }
