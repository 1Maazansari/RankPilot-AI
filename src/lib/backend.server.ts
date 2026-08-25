/**
 * Integration with the existing FastAPI backend (see backend/api/scanner.py).
 * The backend is never modified — this module only speaks its contract.
 */
import type { AnalyzeResult, Recommendation, Report, ActionPhase, AuditCheck } from "./report-types";
import type { HealthResponse, ScanResponse, AIRecommendation } from "./backend-contract";

const DEFAULT_BASE = "http://localhost:8000";

export function backendBaseUrl(): string {
  const raw = process.env["RANKPILOT_API_URL"] ?? DEFAULT_BASE;
  return raw.replace(/\/+$/, "");
}

export async function backendHealth(): Promise<
  { ok: true; base: string; health: HealthResponse } | { ok: false; base: string; message: string }
> {
  const base = backendBaseUrl();
  try {
    const res = await fetch(`${base}/health`, {
      headers: { accept: "application/json" },
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return { ok: false, base, message: `Health check returned ${res.status}` };
    return { ok: true, base, health: (await res.json()) as HealthResponse };
  } catch {
    return { ok: false, base, message: "Backend is not reachable" };
  }
}

/** Calls POST /scan exactly as implemented by the backend. */
export async function scanViaBackend(
  rawUrl: string,
): Promise<AnalyzeResult | { ok: false; code: "offline"; message: string }> {
  const base = backendBaseUrl();
  const url = /^https?:\/\//i.test(rawUrl.trim()) ? rawUrl.trim() : `https://${rawUrl.trim()}`;

  let res: Response;
  try {
    res = await fetch(`${base}/scan`, {
      method: "POST",
      headers: { "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify({ url }),
      signal: AbortSignal.timeout(60000),
    });
  } catch {
    return { ok: false, code: "offline", message: "Backend is not reachable" };
  }

  if (res.status === 404) return { ok: false, code: "offline", message: "Backend route not found" };

  if (!res.ok) {
    const detail = await safeDetail(res);
    if (res.status === 400) return { ok: false, code: "invalid_url", message: detail ?? "Invalid URL" };
    if (res.status === 503) return { ok: false, code: "unreachable", message: detail ?? "Website Unavailable" };
    if (res.status === 504 || res.status === 408)
      return { ok: false, code: "timeout", message: detail ?? "Timeout" };
    if (res.status === 429) return { ok: false, code: "blocked", message: detail ?? "Too many requests" };
    return { ok: false, code: "unknown", message: detail ?? `Backend error ${res.status}`, status: res.status };
  }

  let payload: ScanResponse;
  try {
    payload = (await res.json()) as ScanResponse;
  } catch {
    return { ok: false, code: "unknown", message: "Backend returned an unreadable response." };
  }

  return { ok: true, report: toReport(url, payload) };
}

async function safeDetail(res: Response): Promise<string | null> {
  try {
    const body = (await res.json()) as { detail?: string; error?: { message?: string } };
    return body.detail ?? body.error?.message ?? null;
  } catch {
    return null;
  }
}

function priorityLabel(p: number): Recommendation["priority"] {
  if (p <= 2) return "High";
  if (p <= 4) return "Medium";
  return "Low";
}

const CATEGORY_HINTS: [RegExp, Recommendation["category"]][] = [
  [/image|alt/i, "accessibility"],
  [/link/i, "links"],
  [/speed|performance|load/i, "performance"],
  [/title|meta|description|heading|content|h1/i, "content"],
];

function categoryFor(rec: AIRecommendation): Recommendation["category"] {
  const hay = `${rec.title} ${rec.action}`;
  for (const [re, cat] of CATEGORY_HINTS) if (re.test(hay)) return cat;
  return "technical";
}

function toReport(requestedUrl: string, payload: ScanResponse): Report {
  const { scan, seo, ai } = payload;
  const finalUrl = scan.url || requestedUrl;
  let host = finalUrl;
  try {
    host = new URL(finalUrl).hostname;
  } catch {
    /* keep raw */
  }

  const ogTitle = scan["og:title"] ?? scan.og_title ?? "";
  const title = scan.title || null;
  const metaDescription = scan.meta_description || null;

  const checks: AuditCheck[] = [
    check("title", "Title tag length", "critical", !!title && title.length >= 25 && title.length <= 65,
      title ? `"${title}" (${title.length} chars)` : "No <title> tag found"),
    check("meta", "Meta description", "critical",
      !!metaDescription && metaDescription.length >= 70 && metaDescription.length <= 165,
      metaDescription ? `${metaDescription.length} characters` : "No meta description found"),
    check("h1", "Single H1 heading", "warning", scan.h1_count === 1, `${scan.h1_count} H1 tag(s) on the page`),
    check("h2", "Subheading structure", "info", scan.h2_count > 0, `${scan.h2_count} H2 tag(s) found`),
    check("alt", "Image alt text", "warning", scan.images === 0 || scan.missing_alt === 0,
      `${scan.missing_alt} of ${scan.images} images missing alt text`),
    check("canonical", "Canonical URL", "warning", !!scan.canonical,
      scan.canonical ? scan.canonical : "No canonical link found"),
    check("viewport", "Mobile viewport", "critical", !!scan.viewport,
      scan.viewport || "Missing viewport meta tag"),
    check("lang", "HTML lang attribute", "info", !!scan.language,
      scan.language ? `Declared as "${scan.language}"` : "No lang attribute on <html>"),
    check("og", "Open Graph tags", "info", !!ogTitle, ogTitle ? "Social preview tags present" : "No Open Graph tags"),
    check("twitter", "Twitter card", "info", !!scan.twitter_card,
      scan.twitter_card || "No Twitter card meta"),
    check("robots", "robots.txt", "warning", scan.robots_found,
      scan.robots_found ? "robots.txt found" : "No robots.txt found"),
    check("sitemap", "XML sitemap", "warning", scan.sitemap_found,
      scan.sitemap_found ? "sitemap.xml found" : "No sitemap.xml found"),
    check("links", "Internal linking", "info", scan.internal_links > 0,
      `${scan.internal_links} internal links`),
    check("https", "HTTPS", "critical", finalUrl.startsWith("https://"),
      finalUrl.startsWith("https://") ? "Served over HTTPS" : "Not served over HTTPS"),
  ];

  const recommendations: Recommendation[] = [...ai.recommendations]
    .sort((a, b) => a.priority - b.priority)
    .map((r) => ({
      title: r.title,
      priority: priorityLabel(r.priority),
      reason: r.reason,
      fix: r.action,
      category: categoryFor(r),
      impact: r.impact,
      effort: r.estimated_effort,
    }));

  const bucket = (p: Recommendation["priority"]) =>
    recommendations.filter((r) => r.priority === p).map((r) => r.title).slice(0, 4);

  const actionPlan: ActionPhase[] = (
    [
      { week: "This week", items: bucket("High") },
      { week: "Next 2 weeks", items: bucket("Medium") },
      { week: "Next month", items: bucket("Low") },
    ] as ActionPhase[]
  ).map((p) => ({
    ...p,
    items: p.items.length ? p.items : ["Nothing queued — re-scan after your next deploy"],
  }));

  return {
    url: requestedUrl,
    host,
    finalUrl,
    generatedAt: new Date().toISOString(),
    source: "backend",
    grade: seo.score.grade,
    scores: { seo: seo.score.score, health: null, performance: null, accessibility: null },
    metrics: null,
    signals: {
      title,
      titleLength: title?.length ?? 0,
      metaDescription,
      metaDescriptionLength: metaDescription?.length ?? 0,
      h1Count: scan.h1_count,
      h1: null,
      imagesTotal: scan.images,
      imagesMissingAlt: scan.missing_alt,
      internalLinks: scan.internal_links,
      externalLinks: null,
      hasCanonical: !!scan.canonical,
      hasViewport: !!scan.viewport,
      hasOpenGraph: !!ogTitle,
      hasStructuredData: false,
      hasLangAttr: !!scan.language,
      isHttps: finalUrl.startsWith("https://"),
      wordCount: null,
      robotsFound: scan.robots_found,
      sitemapFound: scan.sitemap_found,
    },
    checks,
    issues: seo.score.summary,
    issueList: seo.issues.map((i) => ({
      ruleId: i.rule_id,
      severity: i.severity,
      category: i.category,
      message: i.message,
      recommendation: i.recommendation,
    })),
    recommendations,
    actionPlan,
    aiAvailable: recommendations.length > 0,
    aiNotice: recommendations.length
      ? null
      : "The AI recommendation engine returned no output — showing the SEO rule-engine findings only.",
  };
}

function check(
  id: string,
  label: string,
  severity: AuditCheck["severity"],
  passed: boolean,
  detail: string,
): AuditCheck {
  return { id, label, severity, passed, detail };
}