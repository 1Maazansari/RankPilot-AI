import { z } from "zod";
import { ApiError, apiErrorFromStatus, MALFORMED_ERROR, toApiError } from "./api-error";
import type { ScanResponse } from "@/types/scan";

export const API_BASE_URL: string =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) || "http://127.0.0.1:8000";

const SCAN_TIMEOUT_MS = 120_000;

const severitySchema = z.enum(["critical", "high", "medium", "low"]);

const scanResponseSchema = z.object({
  scan: z
    .object({
      url: z.string().default(""),
      title: z.string().default(""),
      meta_description: z.string().default(""),
      canonical: z.string().default(""),
      meta_robots: z.string().default(""),
      language: z.string().default(""),
      charset: z.string().default(""),
      viewport: z.string().default(""),
      favicon: z.string().default(""),
      twitter_card: z.string().default(""),
      twitter_title: z.string().default(""),
      twitter_description: z.string().default(""),
      twitter_image: z.string().default(""),
      h1_count: z.number().default(0),
      h2_count: z.number().default(0),
      images: z.number().default(0),
      missing_alt: z.number().default(0),
      internal_links: z.number().default(0),
      robots_found: z.boolean().default(false),
      sitemap_found: z.boolean().default(false),
    })
    .passthrough(),
  seo: z.object({
    issues: z
      .array(
        z.object({
          rule_id: z.string().default(""),
          severity: severitySchema,
          category: z.string().default(""),
          message: z.string().default(""),
          recommendation: z.string().default(""),
        }),
      )
      .default([]),
    score: z.object({
      score: z.number(),
      grade: z.string().default(""),
      summary: z.object({
        critical: z.number().default(0),
        high: z.number().default(0),
        medium: z.number().default(0),
        low: z.number().default(0),
      }),
    }),
  }),
  ai: z
    .object({
      recommendations: z
        .array(
          z.object({
            priority: z.number().default(3),
            title: z.string().default(""),
            reason: z.string().default(""),
            impact: z.string().default(""),
            estimated_effort: z.string().default(""),
            action: z.string().default(""),
          }),
        )
        .default([]),
    })
    .default({ recommendations: [] }),
  media: z
    .object({
      images: z
        .array(
          z.object({
            url: z.string(),
            alt: z.string().optional(),
            width: z.number().optional(),
            height: z.number().optional(),
          }),
        )
        .optional(),
      videos: z
        .array(
          z.object({
            url: z.string(),
            poster: z.string().optional(),
            title: z.string().optional(),
          }),
        )
        .optional(),
    })
    .optional(),
});

async function readDetail(response: Response): Promise<string | undefined> {
  try {
    const body: unknown = await response.json();
    if (body && typeof body === "object" && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === "string" && detail.length < 300) return detail;
    }
  } catch {
    /* non-JSON error body */
  }
  return undefined;
}

/** POST {API_BASE_URL}/scan — single-page SEO scan. */
export async function scanWebsite(url: string, signal?: AbortSignal): Promise<ScanResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), SCAN_TIMEOUT_MS);
  const onAbort = () => controller.abort();
  signal?.addEventListener("abort", onAbort);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ url }),
      signal: controller.signal,
    });
  } catch (error) {
    throw toApiError(error);
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", onAbort);
  }

  if (!response.ok) {
    throw apiErrorFromStatus(response.status, await readDetail(response));
  }

  let json: unknown;
  try {
    json = await response.json();
  } catch {
    throw MALFORMED_ERROR();
  }

  const parsed = scanResponseSchema.safeParse(json);
  if (!parsed.success) throw MALFORMED_ERROR();
  return parsed.data as ScanResponse;
}

export interface HealthStatus {
  online: boolean;
  service?: string;
  version?: string;
}

/** GET {API_BASE_URL}/health — connection diagnostics only. */
export async function checkHealth(): Promise<HealthStatus> {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000);
    const response = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timer);
    if (!response.ok) return { online: false };
    const body = (await response.json()) as { service?: string; version?: string };
    return { online: true, service: body.service, version: body.version };
  } catch {
    return { online: false };
  }
}

export { ApiError };

export { getScanRecommendations, siteAudit } from "./site-audit";
export type { AIRecommendation, AIRecommendationResult, CrawlFailure, CrawlReport, CrawlSummary, PageReport } from "./site-audit";
