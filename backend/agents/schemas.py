"""
Pydantic schemas for the BrandVizi LangGraph agent system.
"""

from pydantic import BaseModel, Field


class CodeSuggestion(BaseModel):
    """AI-generated implementation code for a verified SEO issue."""

    language: str
    code: str
    file_hint: str | None = None
    location_hint: str | None = None
    explanation: str


class AgentFinding(BaseModel):
    """A single finding produced by a specialized AI agent."""

    title: str
    category: str
    severity: str
    explanation: str
    recommendation: str
    implementation_steps: list[str]
    code_suggestion: CodeSuggestion | None = None

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the finding is correctly reasoned from verified evidence.",
    )

    source_rule_id: str | None = Field(
        default=None,
        description="Exact deterministic SEO rule_id this finding is based on.",
    )

    source_message: str | None = Field(
        default=None,
        description="Original deterministic SEO issue message.",
    )


class AgentAnalysis(BaseModel):
    """Complete analysis returned by one specialized AI agent."""

    agent_name: str
    summary: str
    findings: list[AgentFinding]


class ValidationResult(BaseModel):
    """Result of validating AI-generated findings against deterministic evidence."""

    valid: bool

    validated_findings: list[AgentFinding]

    rejected_findings: list[AgentFinding]

    warnings: list[str]


class FinalAgentResult(BaseModel):
    """Final combined result of the BrandVizi AI agent workflow."""

    technical: AgentAnalysis

    content: AgentAnalysis

    aeo_geo: AgentAnalysis

    validation: ValidationResult