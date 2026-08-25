import { Trophy } from "lucide-react";
import type { SEOScore, SEOIssue } from "@/types/scan";
import { SEVERITY_LABEL, SEVERITY_ORDER, SEVERITY_BADGE, severityCounts } from "./severity";

export function SeoScoreCard({ score, issues }: { score: SEOScore; issues: SEOIssue[] }) {
  const derived = severityCounts(issues);
  const counts = issues.length > 0 ? derived : score.summary;

  return (
    <section className="overflow-hidden rounded-3xl border border-border bg-white shadow-[var(--shadow-card)]">
      <div className="grid gap-8 p-6 sm:p-8 lg:grid-cols-[1.2fr_1fr] lg:items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs font-semibold text-primary">
            <Trophy className="h-3.5 w-3.5" /> SEO Score
          </div>
          <div className="mt-5 flex flex-wrap items-end gap-6">
            <div>
              <div className="flex items-baseline gap-1">
                <span className="text-6xl font-extrabold tracking-tight text-foreground sm:text-7xl">
                  {Math.round(score.score)}
                </span>
                <span className="text-2xl font-semibold text-muted-foreground">/ 100</span>
              </div>
              <div className="mt-4 h-2 w-full max-w-sm overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full rounded-full bg-[image:var(--gradient-primary)] transition-[width] duration-700"
                  style={{ width: `${Math.max(0, Math.min(100, score.score))}%` }}
                />
              </div>
            </div>
            {score.grade && (
              <div className="rounded-2xl border border-border bg-secondary/60 px-6 py-4 text-center">
                <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Grade
                </div>
                <div className="mt-1 text-4xl font-extrabold tracking-tight text-primary">
                  {score.grade}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4">
          {SEVERITY_ORDER.map((severity) => (
            <div
              key={severity}
              className="rounded-2xl border border-border bg-secondary/40 p-4 text-center"
            >
              <div className="text-3xl font-extrabold tracking-tight text-foreground">
                {counts[severity]}
              </div>
              <span
                className={`mt-2 inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${SEVERITY_BADGE[severity]}`}
              >
                {SEVERITY_LABEL[severity]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
