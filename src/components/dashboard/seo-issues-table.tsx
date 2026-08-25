import { useMemo, useState } from "react";
import { ListChecks, ArrowUpDown, PartyPopper } from "lucide-react";
import type { SEOIssue, SeoSeverity } from "@/types/scan";
import { DashboardSection } from "./section";
import { EmptyState } from "./empty-state";
import { SEVERITY_BADGE, SEVERITY_LABEL, SEVERITY_ORDER } from "./severity";

const RANK: Record<SeoSeverity, number> = { critical: 0, high: 1, medium: 2, low: 3 };

export function SeoIssuesTable({ issues }: { issues: SEOIssue[] }) {
  const [severity, setSeverity] = useState<string>("all");
  const [category, setCategory] = useState<string>("all");
  const [ascending, setAscending] = useState(true);

  const categories = useMemo(
    () => Array.from(new Set(issues.map((issue) => issue.category).filter(Boolean))).sort(),
    [issues],
  );

  const rows = useMemo(() => {
    const filtered = issues.filter(
      (issue) =>
        (severity === "all" || issue.severity === severity) &&
        (category === "all" || issue.category === category),
    );
    return [...filtered].sort((a, b) =>
      ascending ? RANK[a.severity] - RANK[b.severity] : RANK[b.severity] - RANK[a.severity],
    );
  }, [issues, severity, category, ascending]);

  if (issues.length === 0) {
    return (
      <DashboardSection icon={ListChecks} title="SEO Issues">
        <EmptyState icon={PartyPopper} title="No SEO issues found!" description="This page passed every rule in the RankX SEO engine." />
      </DashboardSection>
    );
  }

  const selectClass =
    "rounded-xl border border-border bg-white px-3 py-2 text-sm text-foreground outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/10";

  return (
    <DashboardSection
      icon={ListChecks}
      title="SEO Issues"
      description={`${issues.length} finding${issues.length === 1 ? "" : "s"} from the SEO rule engine.`}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <label className="sr-only" htmlFor="severity-filter">Filter by severity</label>
          <select
            id="severity-filter"
            value={severity}
            onChange={(event) => setSeverity(event.target.value)}
            className={selectClass}
          >
            <option value="all">All severities</option>
            {SEVERITY_ORDER.map((value) => (
              <option key={value} value={value}>{SEVERITY_LABEL[value]}</option>
            ))}
          </select>
          <label className="sr-only" htmlFor="category-filter">Filter by category</label>
          <select
            id="category-filter"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className={selectClass}
          >
            <option value="all">All categories</option>
            {categories.map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => setAscending((value) => !value)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-white px-3 py-2 text-sm font-medium text-foreground transition hover:bg-secondary"
          >
            <ArrowUpDown className="h-4 w-4" />
            {ascending ? "Most severe first" : "Least severe first"}
          </button>
        </div>
      }
    >
      {rows.length === 0 ? (
        <EmptyState compact title="No issues match these filters." />
      ) : (
        <>
          {/* Desktop table */}
          <div className="hidden overflow-x-auto rounded-2xl border border-border lg:block">
            <table className="w-full min-w-[840px] border-collapse text-left text-sm">
              <thead className="bg-secondary/60">
                <tr>
                  <th scope="col" className="px-4 py-3 font-semibold text-muted-foreground">Severity</th>
                  <th scope="col" className="px-4 py-3 font-semibold text-muted-foreground">Category</th>
                  <th scope="col" className="px-4 py-3 font-semibold text-muted-foreground">Issue</th>
                  <th scope="col" className="px-4 py-3 font-semibold text-muted-foreground">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((issue, index) => (
                  <tr key={`${issue.rule_id}-${index}`} className="border-t border-border align-top">
                    <td className="px-4 py-4">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${SEVERITY_BADGE[issue.severity]}`}>
                        {SEVERITY_LABEL[issue.severity]}
                      </span>
                    </td>
                    <td className="px-4 py-4 capitalize text-muted-foreground">{issue.category || "—"}</td>
                    <td className="px-4 py-4 text-foreground">{issue.message}</td>
                    <td className="px-4 py-4 text-muted-foreground">{issue.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile cards */}
          <ul className="space-y-3 lg:hidden">
            {rows.map((issue, index) => (
              <li key={`${issue.rule_id}-m-${index}`} className="rounded-2xl border border-border bg-secondary/30 p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${SEVERITY_BADGE[issue.severity]}`}>
                    {SEVERITY_LABEL[issue.severity]}
                  </span>
                  {issue.category && (
                    <span className="rounded-full bg-white px-2.5 py-0.5 text-xs font-medium capitalize text-muted-foreground ring-1 ring-border">
                      {issue.category}
                    </span>
                  )}
                </div>
                <p className="mt-3 text-sm font-medium text-foreground">{issue.message}</p>
                <p className="mt-2 text-sm text-muted-foreground">{issue.recommendation}</p>
              </li>
            ))}
          </ul>
        </>
      )}
    </DashboardSection>
  );
}
