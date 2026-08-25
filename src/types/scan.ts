/**
 * Type mirror of the RankX FastAPI backend contract.
 * Field names match the backend JSON exactly. Do not rename.
 */

export type SeoSeverity = "critical" | "high" | "medium" | "low";

export interface ScannerResponse {
  url: string;
  title: string;
  meta_description: string;
  canonical: string;
  meta_robots: string;
  language: string;
  charset: string;
  viewport: string;
  favicon: string;

  "og:title"?: string;
  "og:description"?: string;
  "og:image"?: string;
  "og:url"?: string;
  "og:type"?: string;

  twitter_card: string;
  twitter_title: string;
  twitter_description: string;
  twitter_image: string;

  h1_count: number;
  h2_count: number;
  images: number;
  missing_alt: number;
  internal_links: number;
  robots_found: boolean;
  sitemap_found: boolean;
}

export interface SEOIssue {
  rule_id: string;
  severity: SeoSeverity;
  category: string;
  message: string;
  recommendation: string;
}

export interface SEOSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface SEOScore {
  score: number;
  grade: string;
  summary: SEOSummary;
}

export interface SEOAnalysis {
  issues: SEOIssue[];
  score: SEOScore;
}

export interface AIRecommendation {
  priority: number;
  title: string;
  reason: string;
  impact: string;
  estimated_effort: string;
  action: string;
}

export interface AIResult {
  recommendations: AIRecommendation[];
}

/** Optional, forward-compatible media payload. Absent in the current backend. */
export interface MediaImage {
  url: string;
  alt?: string;
  width?: number;
  height?: number;
}

export interface MediaVideo {
  url: string;
  poster?: string;
  title?: string;
}

export interface MediaResult {
  images?: MediaImage[];
  videos?: MediaVideo[];
}

export interface ScanResponse {
  scan: ScannerResponse;
  seo: SEOAnalysis;
  ai: AIResult;
  media?: MediaResult;
}

/** What the frontend persists between /analyze and /dashboard. */
export interface StoredScan {
  url: string;
  scannedAt: string;
  result: ScanResponse;
}
