import { BarChart3 } from "lucide-react";
import type { SEOIssue, SEOScore } from "@/types/scan";
import { DashboardSection } from "./section";
import { SeoScoreChart } from "./seo-score-chart";
import { IssuesSeverityChart } from "./issues-severity-chart";

export function SeoAnalytics({ score, issues }: { score: SEOScore; issues: SEOIssue[] }) {
  return (
    <DashboardSection
      icon={BarChart3}
      title="SEO Analytics"
      description="Score breakdown and issue distribution from this scan."
    >
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-border bg-secondary/30 p-4">
          <h3 className="mb-2 text-sm font-semibold text-foreground">SEO Score</h3>
          <SeoScoreChart score={score.score} />
        </div>
        <div className="rounded-2xl border border-border bg-secondary/30 p-4">
          <h3 className="mb-2 text-sm font-semibold text-foreground">Issues by Severity</h3>
          <IssuesSeverityChart issues={issues} />
        </div>
      </div>
    </DashboardSection>
  );
}
