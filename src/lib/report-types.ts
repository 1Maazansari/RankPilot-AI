export type Priority = "High" | "Medium" | "Low";

export type Recommendation = {
  title: string;
  priority: Priority;
  reason: string;
  fix: string;
  category: "content" | "performance" | "technical" | "links" | "accessibility";
  /** Backend AI engine extras (backend/ai/models.py) */
  impact?: string;
  effort?: string;
};

export type ActionPhase = { week: string; items: string[] };

export type AuditCheck = {
  id: string;
  label: string;
  severity: "critical" | "warning" | "info";
  passed: boolean;
  detail: string;
};

export type Report = {
  url: string;
  host: string;
  finalUrl: string;
  generatedAt: string;
  /** "backend" = FastAPI POST /scan. "builtin" = in-app crawler fallback. */
  source: "backend" | "builtin";
  grade: string | null;
  scores: {
    seo: number;
    health: number | null;
    performance: number | null;
    accessibility: number | null;
  };
  metrics: { ttfbMs: number; loadMs: number; pageWeightKb: number; requestsHint: number } | null;
  signals: {
    title: string | null;
    titleLength: number;
    metaDescription: string | null;
    metaDescriptionLength: number;
    h1Count: number;
    h1: string | null;
    imagesTotal: number;
    imagesMissingAlt: number;
    internalLinks: number;
    externalLinks: number | null;
    hasCanonical: boolean;
    hasViewport: boolean;
    hasOpenGraph: boolean;
    hasStructuredData: boolean;
    hasLangAttr: boolean;
    isHttps: boolean;
    wordCount: number | null;
    robotsFound?: boolean;
    sitemapFound?: boolean;
  };
  checks: AuditCheck[];
  issues: { critical: number; high: number; medium: number; low: number };
  /** Raw SEO rule-engine issues (backend/seo/models.py). Empty for builtin runs. */
  issueList: {
    ruleId: string;
    severity: "critical" | "high" | "medium" | "low";
    category: string;
    message: string;
    recommendation: string;
  }[];
  recommendations: Recommendation[];
  actionPlan: ActionPhase[];
  aiAvailable: boolean;
  aiNotice: string | null;
};

export type AnalyzeErrorCode =
  | "invalid_url"
  | "unreachable"
  | "timeout"
  | "http_error"
  | "blocked"
  | "unknown";

export type AnalyzeResult =
  | { ok: true; report: Report }
  | { ok: false; code: AnalyzeErrorCode; message: string; status?: number };

export const ERROR_COPY: Record<AnalyzeErrorCode, { title: string; body: string }> = {
  invalid_url: {
    title: "That URL doesn't look right",
    body: "Enter a full website address, including the domain — for example https://yoursite.com.",
  },
  unreachable: {
    title: "We couldn't reach that website",
    body: "The domain didn't respond. Check the spelling, or confirm the site is online and publicly accessible.",
  },
  timeout: {
    title: "The website took too long to respond",
    body: "We waited 15 seconds without a full response. This usually means the server is slow or under load — try again shortly.",
  },
  http_error: {
    title: "The website returned an error",
    body: "The server responded with an error status, so there was no page for us to audit.",
  },
  blocked: {
    title: "The website blocked our crawler",
    body: "This site rejects automated requests. Allowlist the RankX crawler or try a different page.",
  },
  unknown: {
    title: "Something went wrong during the audit",
    body: "The analysis failed unexpectedly. Please try again — if it keeps happening, try another page on the site.",
  },
};

const KEY = "rankpilot:report:";

export function cacheReport(url: string, report: Report) {
  try {
    sessionStorage.setItem(KEY + url, JSON.stringify(report));
  } catch {
    /* storage unavailable */
  }
}

export function readCachedReport(url: string): Report | null {
  try {
    const raw = sessionStorage.getItem(KEY + url);
    return raw ? (JSON.parse(raw) as Report) : null;
  } catch {
    return null;
  }
}