"""Shared state for the BrandVizi LangGraph agent workflow."""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between BrandVizi AI agents.

    The deterministic scanner and SEO engine populate the initial
    website and SEO data. Each specialist agent then adds its own
    analysis to the state.
    """

    # ------------------------------------------------------------------
    # Input data from the existing BrandVizi scanning system
    # ------------------------------------------------------------------

    scan: dict[str, Any]

    seo_analysis: dict[str, Any]

    # ------------------------------------------------------------------
    # Specialist agent outputs
    # ------------------------------------------------------------------

    technical_analysis: dict[str, Any]

    content_analysis: dict[str, Any]

    aeo_geo_analysis: dict[str, Any]

    # ------------------------------------------------------------------
    # Validation output
    # ------------------------------------------------------------------

    validation: dict[str, Any]

    # ------------------------------------------------------------------
    # Workflow errors
    # ------------------------------------------------------------------

    errors: list[str]

    # ------------------------------------------------------------------
    # Compact content evidence extracted from the page.
    # ------------------------------------------------------------------

    content_evidence: dict[str, Any]