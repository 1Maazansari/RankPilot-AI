import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Download, ExternalLink, Lock, RefreshCw, Search, Sparkles } from "lucide-react";
import { SiteNav } from "@/components/site-nav";
import { AIChatPanel } from "@/components/ai-chat-panel";
import { EmptyState } from "@/components/dashboard/empty-state";
import { SeoScoreCard } from "@/components/dashboard/seo-score-card";
import { SeoAnalytics } from "@/components/dashboard/seo-analytics";
import { WebsiteStats } from "@/components/dashboard/website-stats";
import { MetadataCard } from "@/components/dashboard/metadata-card";
import { SocialPreview } from "@/components/dashboard/social-preview";
import { MediaAnalysis } from "@/components/dashboard/media-analysis";
import { SeoIssuesTable } from "@/components/dashboard/seo-issues-table";
import { AiRecommendations } from "@/components/dashboard/ai-recommendations";
import { readScan } from "@/lib/scan-storage";
import { downloadReport } from "@/lib/report-download";
import { MULTI_PAGE_LOCKED_NOTE } from "@/lib/pricing";
import type { StoredScan } from "@/types/scan";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "SEO Report Dashboard — BrandVizi" },
      {
        name: "description",
        content:
          "Your BrandVizi SEO report: score, issues by severity, metadata, media and AI recommendations for the page you scanned.",
      },
      { property: "og:title", content: "SEO Report Dashboard — BrandVizi" },
      {
        property: "og:description",
        content: "Score, issues, metadata and AI recommendations from your BrandVizi scan.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: DashboardPage,
});

function DashboardPage() {
  const [stored, setStored] = useState<StoredScan | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setStored(readScan());
    setReady(true);
  }, []);

  if (!ready) {
    return (
      <div className="min-h-screen">
        <SiteNav />
        <main className="mx-auto max-w-7xl px-6 py-16">
          <div className="h-64 animate-pulse rounded-3xl border border-border bg-secondary/50" />
        </main>
      </div>
    );
  }

  if (!stored) {
    return (
      <div className="min-h-screen">
        <SiteNav />
        <main className="mx-auto max-w-3xl px-6 py-24">
          <h1 className="sr-only">SEO Report Dashboard</h1>
          <EmptyState
            icon={Search}
            title="No scan data yet"
            description="Run a scan from the home page to generate your SEO report. Reports are kept for your current browser session only."
            action={
              <Link
                to="/"
                className="inline-flex items-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110"
              >
                <Search className="h-4 w-4" /> Scan a website
              </Link>
            }
          />
        </main>
        <AIChatPanel />
      </div>
    );
  }

  const { url, scannedAt, result } = stored;
  const { scan, seo, ai, media } = result;
  const context = `URL: ${url}. SEO score ${Math.round(seo.score.score)}/100, grade ${seo.score.grade || "n/a"}. Issues: ${seo.issues
    .slice(0, 12)
    .map((issue) => `${issue.severity}: ${issue.message}`)
    .join("; ")}`;

  return (
    <div className="min-h-screen bg-secondary/30">
      <SiteNav />

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-10 sm:py-14">
        <header className="flex flex-wrap items-start justify-between gap-6">
          <div className="min-w-0">
            <div className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs font-semibold text-primary">
              <Sparkles className="h-3.5 w-3.5" /> Single-page report
            </div>
            <h1 className="mt-3 truncate text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
              {(() => {
                try {
                  return new URL(url).hostname.replace(/^www\./, "");
                } catch {
                  return url;
                }
              })()}
            </h1>
            <p className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
              >
                {url} <ExternalLink className="h-3.5 w-3.5" />
              </a>
              <span>Scanned {new Date(scannedAt).toLocaleString()}</span>
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-white px-4 py-2.5 text-sm font-semibold text-foreground transition hover:bg-secondary"
            >
              <RefreshCw className="h-4 w-4" /> New scan
            </Link>
            <button
              type="button"
              onClick={() => downloadReport(stored)}
              className="inline-flex items-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110"
            >
              <Download className="h-4 w-4" /> Download report
            </button>
          </div>
        </header>

        <SeoScoreCard score={seo.score} issues={seo.issues} />
        <SeoAnalytics score={seo.score} issues={seo.issues} />
        <WebsiteStats scan={scan} />
        <MetadataCard scan={scan} />
        <SocialPreview scan={scan} />
        <MediaAnalysis scan={scan} media={media} />
        <SeoIssuesTable issues={seo.issues} />
        <AiRecommendations recommendations={ai.recommendations} />

        <section className="flex flex-wrap items-center justify-between gap-6 rounded-3xl border border-primary/20 bg-accent/50 p-6 sm:p-8">
          <div className="flex items-start gap-3">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white text-primary shadow-sm">
              <Lock className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-lg font-bold tracking-tight text-foreground">
                Want the whole website?
              </h2>
              <p className="mt-1 max-w-xl text-sm text-muted-foreground">{MULTI_PAGE_LOCKED_NOTE}</p>
            </div>
          </div>
          <Link
            to="/multi-page-audit"
            className="inline-flex items-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110"
          >
            Start multi-page audit
          </Link>
        </section>
      </main>

      <AIChatPanel context={context} />
    </div>
  );
}
