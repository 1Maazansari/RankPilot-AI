import type {
  ActionPhase,
  AnalyzeResult,
  AuditCheck,
  Recommendation,
  Report,
} from "./report-types";

const TIMEOUT_MS = 15000;

function normalizeUrl(input: string): URL | null {
  try {
    const withProto = /^https?:\/\//i.test(input) ? input : `https://${input}`;
    const u = new URL(withProto);
    if (!u.hostname.includes(".")) return null;
    return u;
  } catch {
    return null;
  }
}

function attr(tag: string, name: string): string | null {
  const m = tag.match(new RegExp(`${name}\\s*=\\s*("([^"]*)"|'([^']*)')`, "i"));
  return m ? (m[2] ?? m[3] ?? "").trim() : null;
}

function metaContent(html: string, matcher: RegExp): string | null {
  const tags = html.match(/<meta\b[^>]*>/gi) ?? [];
  for (const tag of tags) {
    if (matcher.test(tag)) {
      const c = attr(tag, "content");
      if (c) return c;
    }
  }
  return null;
}

function clamp(n: number) {
  return Math.max(1, Math.min(100, Math.round(n)));
}

export async function analyzeWebsite(rawUrl: string): Promise<AnalyzeResult> {
  const parsed = normalizeUrl(rawUrl.trim());
  if (!parsed) {
    return { ok: false, code: "invalid_url", message: "Could not parse the supplied URL." };
  }

  const started = Date.now();
  let response: Response;
  try {
    response = await fetch(parsed.toString(), {
      redirect: "follow",
      signal: AbortSignal.timeout(TIMEOUT_MS),
      headers: {
        "user-agent":
          "Mozilla/5.0 (compatible; BrandViziBot/1.0) AppleWebKit/537.36",
        accept: "text/html,application/xhtml+xml",
      },
    });
  } catch (error) {
    const name = (error as Error)?.name ?? "";
    if (name === "TimeoutError" || name === "AbortError") {
      return { ok: false, code: "timeout", message: "The website did not respond in time." };
    }
    return { ok: false, code: "unreachable", message: "The website could not be reached." };
  }

  const ttfbMs = Date.now() - started;

  if (response.status === 403 || response.status === 401 || response.status === 429) {
    return {
      ok: false,
      code: "blocked",
      message: `The website responded with ${response.status}.`,
      status: response.status,
    };
  }
  if (!response.ok) {
    return {
      ok: false,
      code: "http_error",
      message: `The website responded with ${response.status}.`,
      status: response.status,
    };
  }

  let html: string;
  try {
    html = await response.text();
  } catch {
    return { ok: false, code: "unknown", message: "Could not read the page content." };
  }
  const loadMs = Date.now() - started;

  const finalUrl = response.url || parsed.toString();
  const host = new URL(finalUrl).hostname;
  const head = html.slice(0, 400000);

  const titleMatch = head.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1].replace(/\s+/g, " ").trim() : null;
  const metaDescription = metaContent(head, /name\s*=\s*["']description["']/i);
  const h1s = [...head.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)].map((m) =>
    m[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim(),
  );
  const imgTags = head.match(/<img\b[^>]*>/gi) ?? [];
  const imagesMissingAlt = imgTags.filter((t) => !attr(t, "alt")).length;
  const anchors = [...head.matchAll(/<a\b[^>]*href\s*=\s*("([^"]*)"|'([^']*)')/gi)].map(
    (m) => m[2] ?? m[3] ?? "",
  );
  let internalLinks = 0;
  let externalLinks = 0;
  for (const href of anchors) {
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:")) continue;
    if (/^https?:\/\//i.test(href)) {
      try {
        new URL(href).hostname === host ? internalLinks++ : externalLinks++;
      } catch {
        /* ignore */
      }
    } else internalLinks++;
  }

  const textOnly = head
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const wordCount = textOnly ? textOnly.split(" ").length : 0;

  const signals: Report["signals"] = {
    title,
    titleLength: title?.length ?? 0,
    metaDescription,
    metaDescriptionLength: metaDescription?.length ?? 0,
    h1Count: h1s.length,
    h1: h1s[0] ?? null,
    imagesTotal: imgTags.length,
    imagesMissingAlt,
    internalLinks,
    externalLinks,
    hasCanonical: /<link\b[^>]*rel\s*=\s*["']canonical["']/i.test(head),
    hasViewport: /<meta\b[^>]*name\s*=\s*["']viewport["']/i.test(head),
    hasOpenGraph: /<meta\b[^>]*property\s*=\s*["']og:/i.test(head),
    hasStructuredData: /application\/ld\+json/i.test(head),
    hasLangAttr: /<html\b[^>]*\blang\s*=/i.test(head),
    isHttps: finalUrl.startsWith("https://"),
    wordCount,
  };

  const pageWeightKb = Math.round(new TextEncoder().encode(html).length / 1024);
  const requestsHint =
    (html.match(/<script\b/gi)?.length ?? 0) +
    (html.match(/<link\b[^>]*rel\s*=\s*["']stylesheet["']/gi)?.length ?? 0) +
    imgTags.length;

  const checks: AuditCheck[] = [
    {
      id: "title",
      label: "Title tag length",
      severity: "critical",
      passed: !!title && title.length >= 25 && title.length <= 65,
      detail: title ? `"${title}" (${title.length} chars)` : "No <title> tag found",
    },
    {
      id: "meta",
      label: "Meta description",
      severity: "critical",
      passed: !!metaDescription && metaDescription.length >= 70 && metaDescription.length <= 165,
      detail: metaDescription
        ? `${metaDescription.length} characters`
        : "No meta description found",
    },
    {
      id: "h1",
      label: "Single H1 heading",
      severity: "warning",
      passed: h1s.length === 1,
      detail: `${h1s.length} H1 tag(s) on the page`,
    },
    {
      id: "alt",
      label: "Image alt text",
      severity: "warning",
      passed: imgTags.length === 0 || imagesMissingAlt === 0,
      detail: `${imagesMissingAlt} of ${imgTags.length} images missing alt text`,
    },
    {
      id: "canonical",
      label: "Canonical URL",
      severity: "warning",
      passed: signals.hasCanonical,
      detail: signals.hasCanonical ? "Canonical link present" : "No canonical link found",
    },
    {
      id: "viewport",
      label: "Mobile viewport",
      severity: "critical",
      passed: signals.hasViewport,
      detail: signals.hasViewport ? "Responsive viewport set" : "Missing viewport meta tag",
    },
    {
      id: "og",
      label: "Open Graph tags",
      severity: "info",
      passed: signals.hasOpenGraph,
      detail: signals.hasOpenGraph ? "Social preview tags present" : "No Open Graph tags",
    },
    {
      id: "schema",
      label: "Structured data",
      severity: "info",
      passed: signals.hasStructuredData,
      detail: signals.hasStructuredData ? "JSON-LD detected" : "No JSON-LD structured data",
    },
    {
      id: "https",
      label: "HTTPS",
      severity: "critical",
      passed: signals.isHttps,
      detail: signals.isHttps ? "Served over HTTPS" : "Not served over HTTPS",
    },
    {
      id: "lang",
      label: "HTML lang attribute",
      severity: "info",
      passed: signals.hasLangAttr,
      detail: signals.hasLangAttr ? "Language declared" : "No lang attribute on <html>",
    },
    {
      id: "content",
      label: "Content depth",
      severity: "warning",
      passed: wordCount >= 300,
      detail: `${wordCount} words of visible text`,
    },
    {
      id: "weight",
      label: "Page weight",
      severity: "warning",
      passed: pageWeightKb < 500,
      detail: `${pageWeightKb} KB of HTML`,
    },
    {
      id: "ttfb",
      label: "Server response time",
      severity: "critical",
      passed: ttfbMs < 800,
      detail: `${ttfbMs} ms time to first byte`,
    },
  ];

  const failed = checks.filter((c) => !c.passed);
  const issues = {
    critical: failed.filter((c) => c.severity === "critical").length,
    high: 0,
    medium: failed.filter((c) => c.severity === "warning").length,
    low: failed.filter((c) => c.severity === "info").length,
  };

  const seoChecks = checks.filter((c) =>
    ["title", "meta", "h1", "canonical", "og", "schema", "content", "lang"].includes(c.id),
  );
  const perfPenalty =
    (ttfbMs > 1500 ? 35 : ttfbMs > 800 ? 18 : ttfbMs > 400 ? 8 : 0) +
    (pageWeightKb > 1000 ? 25 : pageWeightKb > 500 ? 12 : 0) +
    (requestsHint > 80 ? 15 : requestsHint > 40 ? 7 : 0);
  const a11yPenalty =
    (imgTags.length ? (imagesMissingAlt / imgTags.length) * 45 : 0) +
    (signals.hasLangAttr ? 0 : 12) +
    (signals.hasViewport ? 0 : 15);

  const scores = {
    seo: clamp((seoChecks.filter((c) => c.passed).length / seoChecks.length) * 100),
    health: clamp(100 - (issues.critical * 12 + issues.medium * 6 + issues.low * 2)),
    performance: clamp(100 - perfPenalty),
    accessibility: clamp(100 - a11yPenalty),
  };

  const fallback = fallbackAdvice(failed, signals, ttfbMs, pageWeightKb);
  const ai = await generateAiAdvice({ host, finalUrl, signals, checks, scores, ttfbMs, pageWeightKb });

  const report: Report = {
    url: rawUrl,
    host,
    finalUrl,
    generatedAt: new Date().toISOString(),
    source: "builtin" as const,
    grade: null,
    scores,
    metrics: { ttfbMs, loadMs, pageWeightKb, requestsHint },
    signals,
    checks,
    issues,
    issueList: [],
    recommendations: ai?.recommendations?.length ? ai.recommendations : fallback.recommendations,
    actionPlan: ai?.actionPlan?.length ? ai.actionPlan : fallback.actionPlan,
    aiAvailable: !!ai,
    aiNotice: ai
      ? null
      : "AI explanations are temporarily unavailable — showing rule-based guidance from the raw audit instead.",
  };

  return { ok: true, report };
}

function fallbackAdvice(
  failed: AuditCheck[],
  signals: Report["signals"],
  ttfbMs: number,
  pageWeightKb: number,
): { recommendations: Recommendation[]; actionPlan: ActionPhase[] } {
  const map: Record<string, Recommendation> = {
    title: {
      title: "Title tag needs work",
      priority: "High",
      category: "content",
      reason:
        "The title tag is the single strongest on-page ranking signal and the headline searchers see in results.",
      fix: "Write a 50–60 character title that leads with the primary keyword, then the brand name.",
    },
    meta: {
      title: "Meta description missing or off-length",
      priority: "High",
      category: "content",
      reason:
        "Without a well-sized description, Google auto-generates a snippet that usually converts worse.",
      fix: "Add a unique 140–160 character description with the main keyword and a clear value proposition.",
    },
    h1: {
      title: `Page has ${signals.h1Count} H1 headings`,
      priority: "Medium",
      category: "content",
      reason: "Exactly one H1 gives crawlers an unambiguous statement of page topic.",
      fix: "Keep one descriptive H1 and demote the rest to H2/H3.",
    },
    alt: {
      title: `${signals.imagesMissingAlt} images missing alt text`,
      priority: "Medium",
      category: "accessibility",
      reason: "Alt text drives image search traffic and is required for screen-reader users.",
      fix: "Describe each meaningful image in 5–12 words; use empty alt for decorative images.",
    },
    canonical: {
      title: "No canonical URL declared",
      priority: "Medium",
      category: "technical",
      reason: "Canonicals prevent duplicate-content dilution across parameter and variant URLs.",
      fix: "Add <link rel=\"canonical\"> pointing at the preferred absolute URL of each page.",
    },
    viewport: {
      title: "Missing mobile viewport tag",
      priority: "High",
      category: "technical",
      reason: "Google indexes mobile-first; without a viewport the page is treated as non-responsive.",
      fix: 'Add <meta name="viewport" content="width=device-width, initial-scale=1"> to the head.',
    },
    og: {
      title: "No Open Graph tags",
      priority: "Low",
      category: "content",
      reason: "Social shares render as bare links, reducing referral click-through.",
      fix: "Add og:title, og:description and og:image to every template.",
    },
    schema: {
      title: "No structured data",
      priority: "Low",
      category: "technical",
      reason: "JSON-LD unlocks rich results such as ratings, FAQs and breadcrumbs.",
      fix: "Add Organization plus page-appropriate JSON-LD (Article, Product, FAQPage).",
    },
    https: {
      title: "Site is not served over HTTPS",
      priority: "High",
      category: "technical",
      reason: "HTTPS is a confirmed ranking signal and browsers flag insecure pages.",
      fix: "Install a TLS certificate and 301 all HTTP traffic to HTTPS.",
    },
    lang: {
      title: "HTML lang attribute missing",
      priority: "Low",
      category: "accessibility",
      reason: "Language declaration helps screen readers and international targeting.",
      fix: 'Set <html lang="en"> (or the correct locale).',
    },
    content: {
      title: `Thin content (${signals.wordCount} words)`,
      priority: "Medium",
      category: "content",
      reason: "Pages with little unique text struggle to rank for competitive queries.",
      fix: "Expand to 600+ words of genuinely useful copy covering related subtopics.",
    },
    weight: {
      title: `Heavy HTML payload (${pageWeightKb} KB)`,
      priority: "Medium",
      category: "performance",
      reason: "Large documents delay parsing and push out Largest Contentful Paint.",
      fix: "Trim inline scripts/styles, paginate long lists, and defer non-critical markup.",
    },
    ttfb: {
      title: `Slow server response (${ttfbMs} ms)`,
      priority: "High",
      category: "performance",
      reason: "Time to first byte gates every other paint metric and directly affects rankings.",
      fix: "Add edge caching/CDN, enable compression, and cache expensive database queries.",
    },
  };

  const recommendations = failed.map((c) => map[c.id]).filter(Boolean).slice(0, 8);
  if (!recommendations.length) {
    recommendations.push({
      title: "No blocking issues detected",
      priority: "Low",
      category: "content",
      reason: "Your page passed every automated check in this audit.",
      fix: "Focus next on content depth, internal linking and earning quality backlinks.",
    });
  }

  const byPriority = (p: Recommendation["priority"]) =>
    recommendations.filter((r) => r.priority === p).map((r) => r.title);

  return {
    recommendations,
    actionPlan: [
      { week: "This week", items: byPriority("High").slice(0, 4) },
      { week: "Next 2 weeks", items: byPriority("Medium").slice(0, 4) },
      { week: "Next month", items: byPriority("Low").slice(0, 4) },
    ].map((p) => ({ ...p, items: p.items.length ? p.items : ["Nothing queued — re-scan after your next deploy"] })),
  };
}

type AiInput = {
  host: string;
  finalUrl: string;
  signals: Report["signals"];
  checks: AuditCheck[];
  scores: Report["scores"];
  ttfbMs: number;
  pageWeightKb: number;
};

async function generateAiAdvice(
  input: AiInput,
): Promise<{ recommendations: Recommendation[]; actionPlan: ActionPhase[] } | null> {
  const key = process.env["LOVABLE_API_KEY"];
  if (!key) return null;

  const prompt = `You are a senior technical SEO consultant. Audit data for ${input.finalUrl}:

SCORES: ${JSON.stringify(input.scores)}
SIGNALS: ${JSON.stringify(input.signals)}
FAILED CHECKS: ${JSON.stringify(input.checks.filter((c) => !c.passed))}
TTFB: ${input.ttfbMs}ms, HTML weight: ${input.pageWeightKb}KB

Return JSON only, shape:
{"recommendations":[{"title":string,"priority":"High"|"Medium"|"Low","category":"content"|"performance"|"technical"|"links"|"accessibility","reason":string,"fix":string}],"actionPlan":[{"week":"This week","items":[string]},{"week":"Next 2 weeks","items":[string]},{"week":"Next month","items":[string]}]}

Rules: 5-7 recommendations grounded strictly in the data above (quote real values). "reason" = why it matters in plain English (1-2 sentences). "fix" = concrete, specific steps (1-2 sentences). Action plan items are short imperative tasks, 3-4 per phase.`;

  try {
    const res = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      signal: AbortSignal.timeout(30000),
      headers: { "Content-Type": "application/json", "Lovable-API-Key": key },
      body: JSON.stringify({
        model: "openai/gpt-5.6-sol",
        reasoning_effort: "none",
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: "You are a precise technical SEO expert. Reply with JSON only." },
          { role: "user", content: prompt },
        ],
      }),
    });
    if (!res.ok) {
      console.error("AI gateway error", res.status, await res.text());
      return null;
    }
    const json = (await res.json()) as { choices?: { message?: { content?: string } }[] };
    const content = json.choices?.[0]?.message?.content;
    if (!content) return null;
    const parsed = JSON.parse(content) as {
      recommendations?: Recommendation[];
      actionPlan?: ActionPhase[];
    };
    if (!Array.isArray(parsed.recommendations) || !parsed.recommendations.length) return null;
    return {
      recommendations: parsed.recommendations.slice(0, 8),
      actionPlan: Array.isArray(parsed.actionPlan) ? parsed.actionPlan.slice(0, 3) : [],
    };
  } catch (error) {
    console.error("AI advice failed", error);
    return null;
  }
}

export async function copilotReply(
  question: string,
  context: string,
): Promise<{ ok: true; reply: string } | { ok: false; message: string }> {
  const key = process.env["LOVABLE_API_KEY"];
  if (!key) return { ok: false, message: "The AI copilot is not configured right now." };
  try {
    const res = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      signal: AbortSignal.timeout(30000),
      headers: { "Content-Type": "application/json", "Lovable-API-Key": key },
      body: JSON.stringify({
        model: "openai/gpt-5.6-sol",
        reasoning_effort: "none",
        messages: [
          {
            role: "system",
            content: `You are BrandVizi Copilot, an expert SEO assistant inside an SEO audit product. Answer in 2-5 short sentences, concrete and jargon-light. Ground answers in the user's audit data when available.\n\nAUDIT CONTEXT:\n${context || "No audit has been run yet in this session."}`,
          },
          { role: "user", content: question },
        ],
      }),
    });
    if (res.status === 429)
      return { ok: false, message: "Too many requests right now — give it a few seconds and try again." };
    if (res.status === 402)
      return { ok: false, message: "AI credits are exhausted for this workspace. Add credits to continue." };
    if (!res.ok) return { ok: false, message: "The AI copilot is temporarily unavailable." };
    const json = (await res.json()) as { choices?: { message?: { content?: string } }[] };
    const reply = json.choices?.[0]?.message?.content?.trim();
    if (!reply) return { ok: false, message: "The AI copilot returned an empty response." };
    return { ok: true, reply };
  } catch {
    return { ok: false, message: "The AI copilot timed out. Please try again." };
  }
}