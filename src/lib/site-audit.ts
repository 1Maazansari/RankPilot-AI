import { z } from "zod";
import { API_BASE_URL } from "./api";
import { apiErrorFromStatus, MALFORMED_ERROR, toApiError } from "./api-error";

const SITE_AUDIT_TIMEOUT_MS = 300_000;
const RECOMMENDATIONS_TIMEOUT_MS = 120_000;
const severitySchema = z.enum(["critical", "high", "medium", "low"]);
const seoIssueSchema = z.object({ rule_id: z.string(), severity: severitySchema, category: z.enum(["metadata", "headings", "images", "links", "technical", "social"]), message: z.string(), recommendation: z.string() });
const crawlFailureSchema = z.object({ url: z.string(), reason: z.string() });
const crawlSummarySchema = z.object({ total_pages: z.number(), average_score: z.number(), grade: z.string(), critical: z.number(), high: z.number(), medium: z.number(), low: z.number(), crawl_complete: z.boolean(), failed_pages: z.number(), robots_txt_found: z.boolean(), sitemap_found: z.boolean(), sitemap_urls: z.array(z.string()) });
const pageReportSchema = z.object({ url: z.string(), score: z.number(), grade: z.string(), issues: z.array(seoIssueSchema) });
const crawlReportSchema = z.object({ summary: crawlSummarySchema, pages: z.array(pageReportSchema), site_issues: z.array(seoIssueSchema), failures: z.array(crawlFailureSchema), scan_id: z.number().int().nullable() });
const aiRecommendationSchema = z.object({ priority: z.number().int().min(1), title: z.string(), reason: z.string(), impact: z.string(), estimated_effort: z.string(), action: z.string(), source_issue_type: z.string().nullable(), affected_page_count: z.number().int().min(0), affected_urls: z.array(z.string()), example: z.string().nullable() });
const aiRecommendationResultSchema = z.object({ recommendations: z.array(aiRecommendationSchema) });

export type SEOIssue = z.infer<typeof seoIssueSchema>;
export type CrawlFailure = z.infer<typeof crawlFailureSchema>;
export type CrawlSummary = z.infer<typeof crawlSummarySchema>;
export type PageReport = z.infer<typeof pageReportSchema>;
export type CrawlReport = z.infer<typeof crawlReportSchema>;
export type AIRecommendation = z.infer<typeof aiRecommendationSchema>;
export type AIRecommendationResult = z.infer<typeof aiRecommendationResultSchema>;

async function readDetail(response: Response): Promise<string | undefined> {
  try {
    const body: unknown = await response.json();
    if (body && typeof body === "object" && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === "string" && detail.length < 300) return detail;
    }
  } catch { /* Non-JSON error response. */ }
  return undefined;
}

async function postJson<T>(path: string, body: unknown, schema: z.ZodType<T>, timeoutMs: number, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const onAbort = () => controller.abort();
  signal?.addEventListener("abort", onAbort);
  let response: Response;
  try {
    response = await fetch(API_BASE_URL + path, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, ...(body === undefined ? {} : { body: JSON.stringify(body) }), signal: controller.signal });
  } catch (error) {
    throw toApiError(error);
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", onAbort);
  }
  if (!response.ok) throw apiErrorFromStatus(response.status, await readDetail(response));
  let json: unknown;
  try { json = await response.json(); } catch { throw MALFORMED_ERROR(); }
  const parsed = schema.safeParse(json);
  if (!parsed.success) throw MALFORMED_ERROR();
  return parsed.data;
}

/** POST /site-audit — crawl and analyze multiple pages of a website. */
export function siteAudit(url: string, maxPages: number, signal?: AbortSignal): Promise<CrawlReport> {
  return postJson("/site-audit", { url, max_pages: maxPages }, crawlReportSchema, SITE_AUDIT_TIMEOUT_MS, signal);
}

/** POST /scans/{scan_id}/recommendations — generate recommendations for a persisted site audit. */
export function getScanRecommendations(scanId: number, signal?: AbortSignal): Promise<AIRecommendationResult> {
  return postJson("/scans/" + scanId + "/recommendations", undefined, aiRecommendationResultSchema, RECOMMENDATIONS_TIMEOUT_MS, signal);
}
