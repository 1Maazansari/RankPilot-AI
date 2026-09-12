/**
 * Type mirror of the BrandVizi FastAPI backend contract.
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

  /**
   * Content evidence extracted by the backend scanner.
   * Used by the Content Intelligence and AEO/GEO agents.
   */
  content_evidence?: {
    word_count: number;
    text_excerpt: string;
    h1_texts: string[];
    h2_texts: string[];
    h3_texts: string[];
    lists: Array<{
      type: string;
      item_count: number;
      excerpt: string;
    }>;
    detected_questions: string[];
    schema: {
      has_json_ld: boolean;
      has_microdata: boolean;
      types: string[];
    };
  };
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
  source_issue_type?: string;
  affected_page_count?: number;
  affected_urls?: string[];
  example?: string;
}

export interface AIResult {
  recommendations: AIRecommendation[];
}

/** Optional, forward-compatible media payload. */
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

/**
 * LangGraph multi-agent analysis types.
 * Optional for backward compatibility.
 */

export interface CodeSuggestion {
  language: string;
  code: string;
  file_hint?: string | null;
  location_hint?: string | null;
  explanation: string;
}

export interface AgentFinding {
  title: string;
  category: string;
  severity: string;
  explanation: string;
  recommendation: string;
  implementation_steps: string[];

  /**
   * Can be null for findings where no code snippet is appropriate.
   */
  code_suggestion?: CodeSuggestion | string | null;

  confidence?: number;

  /**
   * Null for evidence-derived AI findings that do not map
   * directly to a deterministic SEO rule.
   */
  source_rule_id?: string | null;
  source_message?: string | null;
}

export interface AgentAnalysis {
  agent_name: string;
  summary: string;
  findings: AgentFinding[];
}

export interface ValidationResult {
  valid: boolean;
  validated_findings: AgentFinding[];
  rejected_findings: AgentFinding[];
  warnings: string[];
}

export interface FinalAgentResult {
  technical: AgentAnalysis;
  content: AgentAnalysis;
  aeo_geo: AgentAnalysis;
  validation: ValidationResult;
}

export interface ScanResponse {
  scan: ScannerResponse;
  seo: SEOAnalysis;
  ai: AIResult;
  media?: MediaResult;
  agents?: FinalAgentResult;
}

/** What the frontend persists between /analyze and /dashboard. */
export interface StoredScan {
  url: string;
  scannedAt: string;
  result: ScanResponse;
}