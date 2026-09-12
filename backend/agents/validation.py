"""
BrandVizi Validation Node.

This node validates the outputs produced by the three specialist
LangGraph agents against the deterministic SEO engine.

Validation is NOT a fourth intelligence agent.

Its purpose is to ensure that:
- AI findings are grounded in verified SEO issues or scan evidence.
- Unsupported findings are rejected.
- The final output remains traceable.
"""

from typing import Any

from backend.agents.schemas import (
    AgentFinding,
    ValidationResult,
)
from backend.agents.state import AgentState


# ============================================================
# DETERMINISTIC EVIDENCE
# ============================================================

def _collect_rule_ids(
    seo_analysis: dict[str, Any],
) -> set[str]:
    """
    Collect all deterministic SEO rule IDs detected for the
    scanned website.
    """

    issues = seo_analysis.get(
        "issues",
        [],
    )

    if not isinstance(issues, list):
        return set()

    rule_ids: set[str] = set()

    for issue in issues:

        if not isinstance(issue, dict):
            continue

        rule_id = issue.get("rule_id")

        if rule_id is not None:
            rule_ids.add(
                str(rule_id)
            )

    return rule_ids


# ============================================================
# FINDING EXTRACTION
# ============================================================

def _extract_findings(
    analysis: dict[str, Any],
) -> list[AgentFinding]:
    """
    Convert an agent's serialized findings into validated
    AgentFinding objects.
    """

    findings = analysis.get(
        "findings",
        [],
    )

    if not isinstance(findings, list):
        return []

    validated_findings: list[AgentFinding] = []

    for finding in findings:

        if not isinstance(finding, dict):
            continue

        try:

            validated_findings.append(
                AgentFinding.model_validate(
                    finding
                )
            )

        except Exception:
            # Invalid AI findings are ignored by the validator.
            continue

    return validated_findings


# ============================================================
# LANGGRAPH VALIDATION NODE
# ============================================================

def validation_node(
    state: AgentState,
) -> dict[str, Any]:
    """
    Validation node used by the BrandVizi LangGraph workflow.

    It checks findings from:

    1. Technical SEO Agent
    2. Content Intelligence Agent
    3. AEO/GEO Agent

    against deterministic SEO rule IDs and scan evidence.
    """

    # ---------------------------------------------------------
    # 1. Read deterministic SEO evidence
    # ---------------------------------------------------------

    seo_analysis = state.get(
        "seo_analysis",
        {},
    )

    valid_rule_ids = _collect_rule_ids(
        seo_analysis
    )

    # ---------------------------------------------------------
    # 2. Read specialist agent outputs
    # ---------------------------------------------------------

    analyses = [
        state.get(
            "technical_analysis",
            {}
        ),
        state.get(
            "content_analysis",
            {}
        ),
        state.get(
            "aeo_geo_analysis",
            {}
        ),
    ]

    # ---------------------------------------------------------
    # 3. Prepare validation results
    # ---------------------------------------------------------

    validated_findings: list[AgentFinding] = []

    rejected_findings: list[AgentFinding] = []

    warnings: list[str] = []

    TECHNICAL_ONLY_RULES = {
        "missing_alt_text",
        "missing_canonical",
        "missing_meta_robots",
        "missing_robots_txt",
        "missing_sitemap",
        "missing_internal_links",
        "missing_og_title",
        "missing_og_description",
    }

    # ---------------------------------------------------------
    # 4. Validate every AI finding
    # ---------------------------------------------------------

    for analysis in analyses:

        agent_name = analysis.get("agent_name", "")
        findings = _extract_findings(
            analysis
        )

        for finding in findings:

            source_rule_id = finding.source_rule_id

            # Enforce that Content Intelligence does not duplicate Technical SEO issues
            if agent_name == "content_intelligence":
                if (
                    source_rule_id in TECHNICAL_ONLY_RULES
                    or finding.category in {"images", "technical", "links", "social"}
                    or "alt text" in finding.title.lower()
                ):
                    rejected_findings.append(finding)
                    warnings.append(
                        "Rejected Content Intelligence finding that duplicates Technical SEO: "
                        f"{finding.title} (source_rule_id={source_rule_id})"
                    )
                    continue

            if source_rule_id is not None:

                if source_rule_id in valid_rule_ids:

                    validated_findings.append(
                        finding
                    )

                else:

                    rejected_findings.append(
                        finding
                    )

                    warnings.append(
                        "Rejected unsupported AI finding: "
                        f"{finding.title} "
                        f"(source_rule_id={source_rule_id})"
                    )

            else:

                if (
                    finding.title
                    and finding.explanation
                    and finding.recommendation
                ):

                    validated_findings.append(
                        finding
                    )

                else:

                    rejected_findings.append(
                        finding
                    )

                    warnings.append(
                        "Rejected evidence-derived AI finding with "
                        f"missing required fields: {finding.title}"
                    )

    # ---------------------------------------------------------
    # 5. Determine overall validation status
    # ---------------------------------------------------------

    validation_passed = (
        len(rejected_findings) == 0
    )

    # ---------------------------------------------------------
    # 6. Create structured validation result
    # ---------------------------------------------------------

    result = ValidationResult(
        valid=validation_passed,
        validated_findings=validated_findings,
        rejected_findings=rejected_findings,
        warnings=warnings,
    )

    # ---------------------------------------------------------
    # 7. Return LangGraph state update
    # ---------------------------------------------------------

    return {
        "validation": result.model_dump(),
    }
