import { createFileRoute, useNavigate, Link, redirect } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  AlertTriangle,
  ArrowLeft,
  Bot,
  Check,
  FileText,
  Globe,
  Loader2,
  RotateCw,
  Search,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { AIChatPanel } from "@/components/ai-chat-panel";
import { scanWebsite } from "@/lib/api";
import { toApiError, type ApiError } from "@/lib/api-error";
import { saveScan } from "@/lib/scan-storage";

const searchSchema = z.object({ url: z.string().min(1) });

export const Route = createFileRoute("/analyze")({
  beforeLoad: ({ search }) => {
    if (!search.url?.trim()) {
      throw redirect({ to: "/" });
    }
  },
  validateSearch: (search) => searchSchema.parse(search),
  head: () => ({
    meta: [
      { title: "Analyzing your website — BrandVizi" },
      {
        name: "description",
        content:
          "BrandVizi is scanning your page, running the SEO rule engine and generating AI recommendations.",
      },
      { property: "og:title", content: "Analyzing your website — BrandVizi" },
      {
        property: "og:description",
        content: "Live progress while BrandVizi audits your page and builds your SEO report.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: AnalyzePage,
});

const STAGES = [
  { key: "validate", label: "Validating URL", icon: ShieldCheck, weight: 6 },
  { key: "scan", label: "Scanning Website", icon: Globe, weight: 34 },
  { key: "seo", label: "SEO Analysis", icon: Search, weight: 22 },
  { key: "ai", label: "AI Processing", icon: Bot, weight: 30 },
  { key: "report", label: "Report Generation", icon: FileText, weight: 8 },
] as const;

const STAGE_MS = [700, 4000, 3000, 5000, 1200];

function ErrorView({ error, host, onRetry }: { error: ApiError; host: string; onRetry: () => void }) {
  return (
    <main className="mx-auto flex max-w-xl flex-col items-center px-6 py-20 text-center">
      <div className="grid h-14 w-14 place-items-center rounded-2xl bg-destructive/10 text-destructive">
        <AlertTriangle className="h-7 w-7" />
      </div>
      <h1 className="mt-6 text-3xl font-bold tracking-tight">{error.title}</h1>
      <p className="mt-3 text-muted-foreground">{error.message}</p>
      <p className="mt-2 text-sm text-muted-foreground/80">{host}</p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110"
        >
          <RotateCw className="h-4 w-4" /> Try again
        </button>
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-xl border border-border bg-white px-5 py-3 text-sm font-semibold transition hover:bg-secondary"
        >
          <ArrowLeft className="h-4 w-4" /> Analyze a different URL
        </Link>
      </div>
    </main>
  );
}

function AnalyzePage() {
  const { url } = Route.useSearch();
  const navigate = useNavigate();
  const [stageIdx, setStageIdx] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<ApiError | null>(null);
  const [attempt, setAttempt] = useState(0);
  const doneRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    doneRef.current = false;
    setError(null);
    setProgress(0);
    setStageIdx(0);

    const total = STAGE_MS.reduce((sum, value) => sum + value, 0);
    const start = performance.now();
    let raf = 0;
    const tick = () => {
      if (cancelled) return;
      const elapsed = performance.now() - start;
      let acc = 0;
      let idx = STAGES.length - 1;
      let weighted = 0;
      for (let i = 0; i < STAGES.length; i++) {
        const next = acc + STAGE_MS[i];
        if (elapsed < next) {
          idx = i;
          weighted += STAGES[i].weight * ((elapsed - acc) / STAGE_MS[i]);
          break;
        }
        weighted += STAGES[i].weight;
        acc = next;
        idx = Math.min(i + 1, STAGES.length - 1);
      }
      const capped = Math.min(doneRef.current ? 100 : 94, elapsed >= total ? 94 : weighted);
      setProgress(doneRef.current ? 100 : capped);
      setStageIdx(doneRef.current ? STAGES.length : idx);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    (async () => {
      try {
        const result = await scanWebsite(url, controller.signal);
        if (cancelled) return;
        saveScan(url, result);
        doneRef.current = true;
        setProgress(100);
        setStageIdx(STAGES.length);
        setTimeout(() => {
          if (!cancelled) navigate({ to: "/dashboard" });
        }, 550);
      } catch (caught) {
        if (!cancelled) setError(toApiError(caught));
      }
    })();

    return () => {
      cancelled = true;
      controller.abort();
      cancelAnimationFrame(raf);
    };
  }, [url, navigate, attempt]);

  const host = (() => {
    try {
      return new URL(url).hostname;
    } catch {
      return url;
    }
  })();

  return (
    <div className="relative min-h-screen">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-[image:var(--gradient-primary)] shadow-[var(--shadow-glow)]">
            <Zap className="h-5 w-5 text-white" strokeWidth={2.5} />
          </div>
          <span className="text-lg font-bold tracking-tight">
            BrandVizi
          </span>
        </Link>
      </header>

      {error ? (
        <ErrorView error={error} host={host} onRetry={() => setAttempt((value) => value + 1)} />
      ) : (
        <main className="mx-auto flex max-w-2xl flex-col items-center px-6 py-16">
          <div className="mb-8 flex flex-col items-center gap-3 text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1 text-xs font-medium text-muted-foreground">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
              </span>
              Analyzing
            </div>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Auditing <span className="text-primary">{host}</span>
            </h1>
            <p className="text-sm text-muted-foreground">
              Hang tight — a full scan usually takes well under a minute.
            </p>
          </div>

          <div className="w-full rounded-3xl border border-border bg-white p-6 shadow-[var(--shadow-card)] sm:p-8">
            <div className="mb-8">
              <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
                <span>{Math.round(progress)}%</span>
                <span>{stageIdx < STAGES.length ? STAGES[stageIdx].label : "Finalizing"}</span>
              </div>
              <div
                role="progressbar"
                aria-valuenow={Math.round(progress)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label="Scan progress"
                className="h-2 overflow-hidden rounded-full bg-secondary"
              >
                <div
                  className="h-full rounded-full bg-[image:var(--gradient-primary)] transition-[width] duration-200 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <ul className="space-y-3">
              {STAGES.map((stage, index) => {
                const done = index < stageIdx;
                const active = index === stageIdx;
                const Icon = stage.icon;
                return (
                  <li
                    key={stage.key}
                    className={`flex items-center gap-4 rounded-2xl border p-4 transition-all ${
                      active
                        ? "border-primary/40 bg-accent/60"
                        : done
                          ? "border-border bg-secondary/40"
                          : "border-border/60 bg-white opacity-60"
                    }`}
                  >
                    <div
                      className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ${
                        done
                          ? "bg-[color:var(--success)]/15 text-[color:var(--success)]"
                          : active
                            ? "bg-primary/15 text-primary"
                            : "bg-secondary text-muted-foreground"
                      }`}
                    >
                      {done ? (
                        <Check className="h-5 w-5" strokeWidth={3} />
                      ) : active ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <Icon className="h-5 w-5" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-semibold">{stage.label}</div>
                      <div className="text-xs text-muted-foreground">
                        {done ? "Complete" : active ? "In progress…" : "Pending"}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        </main>
      )}
      <AIChatPanel />
    </div>
  );
}
