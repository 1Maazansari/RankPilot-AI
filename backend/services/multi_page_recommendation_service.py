"""AI recommendation orchestration for persisted multi-page scans."""

from collections import defaultdict
from dataclasses import dataclass
import json

from sqlalchemy.orm import Session, selectinload

from backend.ai.llm import generate_recommendations
from backend.ai.models import AIRecommendation, AIRecommendationResult
from backend.models.ai_recommendation import AIRecommendation as AIRecommendationRecord
from backend.models.page import Page
from backend.models.scan import Scan
from backend.models.seo_issue import SEOIssue
from backend.repositories.ai_recommendation_repository import AIRecommendationRepository


SEVERITY_WEIGHTS = {"critical": 4, "high": 3, "medium": 2, "low": 1}
CATEGORY_WEIGHTS = {
    "technical": 6,
    "metadata": 5,
    "headings": 4,
    "links": 3,
    "images": 2,
    "social": 1,
}


@dataclass(frozen=True)
class GroupedIssue:
    """A repeated SEO issue condensed into one deterministic recommendation input."""

    issue_type: str
    severity: str
    category: str
    message: str
    default_action: str | None
    issues: tuple[SEOIssue, ...]
    affected_urls: tuple[str, ...]
    priority_score: int

    @property
    def affected_page_count(self) -> int:
        return len(self.affected_urls)

    @property
    def is_site_level(self) -> bool:
        return any(issue.page_id is None for issue in self.issues)


def category_for_issue(issue_type: str) -> str:
    """Recover the deterministic rule category from the persisted rule identifier."""
    if issue_type in {"missing_canonical", "missing_meta_robots", "missing_robots_txt", "missing_sitemap"}:
        return "technical"
    if issue_type.startswith(("missing_title", "title_", "missing_meta_description", "meta_description_")):
        return "metadata"
    if issue_type in {"missing_h1", "multiple_h1", "missing_h2"}:
        return "headings"
    if issue_type == "missing_alt_text":
        return "images"
    if issue_type == "missing_internal_links":
        return "links"
    if issue_type.startswith(("missing_og_", "missing_twitter_")):
        return "social"
    return "technical"


def group_scan_issues(scan: Scan) -> list[GroupedIssue]:
    """Group matching persisted findings and apply a transparent priority order."""
    grouped: dict[str, list[SEOIssue]] = defaultdict(list)
    for issue in scan.seo_issues:
        grouped[issue.issue_type].append(issue)

    results = []
    for issue_type, issues in grouped.items():
        ordered_issues = tuple(sorted(issues, key=lambda issue: issue.id))
        urls = tuple(sorted({issue.page.url for issue in ordered_issues if issue.page is not None}))
        severity = ordered_issues[0].severity.value
        category = category_for_issue(issue_type)
        average_page_gap = 0
        page_scores = [issue.page.seo_score for issue in ordered_issues if issue.page and issue.page.seo_score is not None]
        if page_scores:
            average_page_gap = round(100 - (sum(page_scores) / len(page_scores)))
        priority_score = (
            SEVERITY_WEIGHTS[severity] * 100
            + len(urls) * 10
            + CATEGORY_WEIGHTS[category]
            + average_page_gap
            + (50 if any(issue.page_id is None for issue in ordered_issues) else 0)
        )
        results.append(
            GroupedIssue(
                issue_type=issue_type,
                severity=severity,
                category=category,
                message=ordered_issues[0].description,
                default_action=ordered_issues[0].recommendation,
                issues=ordered_issues,
                affected_urls=urls,
                priority_score=priority_score,
            )
        )
    return sorted(results, key=lambda group: (-group.priority_score, group.issue_type))


def build_multi_page_prompt(scan: Scan, groups: list[GroupedIssue]) -> str:
    """Build a compact, deterministic input for the existing Gemini boundary."""
    grouped_issues = []
    for index, group in enumerate(groups[:12], start=1):
        grouped_issues.append(
            {
                "deterministic_priority": index,
                "issue_type": group.issue_type,
                "severity": group.severity,
                "category": group.category,
                "affected_page_count": group.affected_page_count,
                "site_level": group.is_site_level,
                "affected_urls": list(group.affected_urls[:5]),
                "additional_affected_pages": max(0, group.affected_page_count - 5),
                "lowest_affected_page_score": min(
                    (issue.page.seo_score for issue in group.issues if issue.page and issue.page.seo_score is not None),
                    default=None,
                ),
                "message": group.message,
                "suggested_fix": group.default_action,
            }
        )
    failures = []
    if scan.failed_pages:
        failures.append(f"{scan.failed_pages} page(s) could not be crawled.")
    payload = {
        "overall_score": scan.seo_score,
        "grade": scan.grade,
        "crawl_summary": {
            "pages_audited": scan.total_pages,
            "crawl_complete": scan.crawl_complete,
            "failed_pages": scan.failed_pages,
        },
        "crawl_failures": failures,
        "grouped_issues": grouped_issues,
    }
    return (
        "Create recommendations only for the grouped issues below. Keep their "
        "deterministic_priority order; do not calculate or alter SEO scores. "
        "Use source_issue_type exactly as provided.\n\n"
        f"MULTI_PAGE_AUDIT:\n{json.dumps(payload)}"
    )


class MultiPageRecommendationService:
    """Generates and persists recommendations without changing audit creation."""

    def generate_for_scan(self, db: Session, scan_id: int) -> AIRecommendationResult | None:
        scan = (
            db.query(Scan)
            .options(
                selectinload(Scan.seo_issues).selectinload(SEOIssue.page),
                selectinload(Scan.pages),
            )
            .filter(Scan.id == scan_id)
            .one_or_none()
        )
        if scan is None:
            return None

        groups = group_scan_issues(scan)
        if not groups:
            return AIRecommendationResult(recommendations=[])

        generated = generate_recommendations(build_multi_page_prompt(scan, groups))
        normalized = self._normalize(generated, groups)
        self._replace_persisted(db, scan, normalized, groups)
        return AIRecommendationResult(recommendations=normalized)

    @staticmethod
    def _normalize(
        generated: AIRecommendationResult,
        groups: list[GroupedIssue],
    ) -> list[AIRecommendation]:
        by_type = {group.issue_type: group for group in groups}
        selected: dict[str, AIRecommendation] = {}
        for index, recommendation in enumerate(generated.recommendations[:5]):
            fallback = groups[min(index, len(groups) - 1)]
            group = by_type.get(recommendation.source_issue_type, fallback)
            if group.issue_type in selected:
                continue
            selected[group.issue_type] = (
                recommendation.model_copy(
                    update={
                        "source_issue_type": group.issue_type,
                        "affected_page_count": group.affected_page_count,
                        "affected_urls": list(group.affected_urls[:5]),
                    }
                )
            )
        return [
            selected[group.issue_type].model_copy(update={"priority": priority})
            for priority, group in enumerate(groups, start=1)
            if group.issue_type in selected
        ]

    @staticmethod
    def _replace_persisted(
        db: Session,
        scan: Scan,
        recommendations: list[AIRecommendation],
        groups: list[GroupedIssue],
    ) -> None:
        by_type = {group.issue_type: group for group in groups}
        issue_ids = [issue.id for issue in scan.seo_issues]
        try:
            if issue_ids:
                db.query(AIRecommendationRecord).filter(
                    AIRecommendationRecord.seo_issue_id.in_(issue_ids)
                ).delete(synchronize_session=False)
            records = []
            for recommendation in recommendations:
                group = by_type[recommendation.source_issue_type]
                records.append(
                    AIRecommendationRecord(
                        seo_issue_id=group.issues[0].id,
                        recommendation=MultiPageRecommendationService._stored_action(recommendation),
                        reasoning=(
                            f"Why it matters: {recommendation.reason}\n"
                            f"Impact: {recommendation.impact}\n"
                            f"Effort: {recommendation.estimated_effort}"
                        ),
                        priority_score=recommendation.priority,
                    )
                )
            AIRecommendationRepository().create_many(db, records)
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _stored_action(recommendation: AIRecommendation) -> str:
        scope = f"Affects {recommendation.affected_page_count} page(s)."
        urls = ", ".join(recommendation.affected_urls)
        example = f" Example: {recommendation.example}" if recommendation.example else ""
        return f"{recommendation.action}\n{scope}{(' URLs: ' + urls) if urls else ''}{example}"
