/**
 * Type mirror of the FastAPI backend contract shipped in the project ZIP.
 * Source of truth: backend/api/scanner.py, backend/scanner/models.py,
 * backend/seo/models.py, backend/score/models.py, backend/ai/models.py
 *
 * Nothing here may diverge from the backend — it is a read-only contract.
 */

export type ScannerResponse = {
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
  og_title?: string;
  og_description?: string;
  og_image?: string;
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
};

export type SeoSeverity = "critical" | "high" | "medium" | "low";
export type SeoCategory =
  | "metadata"
  | "headings"
  | "images"
  | "links"
  | "technical"
  | "social";

export type SEOIssue = {
  rule_id: string;
  severity: SeoSeverity;
  category: SeoCategory;
  message: string;
  recommendation: string;
};

export type ScoreResult = {
  score: number;
  grade: string;
  summary: { critical: number; high: number; medium: number; low: number };
};

export type SEOAnalysisResult = { issues: SEOIssue[]; score: ScoreResult };

export type AIRecommendation = {
  priority: number;
  title: string;
  reason: string;
  impact: string;
  estimated_effort: string;
  action: string;
};

export type ScanResponse = {
  scan: ScannerResponse;
  seo: SEOAnalysisResult;
  ai: { recommendations: AIRecommendation[] };
};

/** GET /health */
export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};