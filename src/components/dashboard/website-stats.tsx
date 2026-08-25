import { Activity, Check, X } from "lucide-react";
import type { ScannerResponse } from "@/types/scan";
import { DashboardSection } from "./section";

function StatTile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-border bg-secondary/40 p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div className="mt-2 text-2xl font-bold tracking-tight text-foreground">{value}</div>
    </div>
  );
}

function BoolTile({ label, present }: { label: string; present: boolean }) {
  return (
    <div className="rounded-2xl border border-border bg-secondary/40 p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </div>
      <div
        className={`mt-2 inline-flex items-center gap-1.5 text-base font-semibold ${
          present ? "text-[color:var(--success)]" : "text-destructive"
        }`}
      >
        {present ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
        {present ? "Found" : "Missing"}
      </div>
    </div>
  );
}

export function WebsiteStats({ scan }: { scan: ScannerResponse }) {
  return (
    <DashboardSection
      icon={Activity}
      title="Website Statistics"
      description="Structural signals detected on the scanned page."
    >
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <StatTile label="H1" value={scan.h1_count} />
        <StatTile label="H2" value={scan.h2_count} />
        <StatTile label="Images" value={scan.images} />
        <StatTile label="Missing Alt" value={scan.missing_alt} />
        <StatTile label="Internal Links" value={scan.internal_links} />
        <BoolTile label="Robots.txt" present={scan.robots_found} />
        <BoolTile label="Sitemap" present={scan.sitemap_found} />
        <BoolTile label="Canonical" present={Boolean(scan.canonical?.trim())} />
      </div>
    </DashboardSection>
  );
}
