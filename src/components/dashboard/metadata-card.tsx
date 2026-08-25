import { FileText } from "lucide-react";
import type { ScannerResponse } from "@/types/scan";
import { DashboardSection } from "./section";

const NOT_FOUND = "Not Found";

function value(input?: string): string {
  const trimmed = input?.trim();
  return trimmed ? trimmed : NOT_FOUND;
}

function Row({ label, content }: { label: string; content: string }) {
  const missing = content === NOT_FOUND;
  return (
    <div className="rounded-2xl border border-border bg-secondary/40 p-4">
      <dt className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </dt>
      <dd
        className={`mt-2 break-words text-sm ${
          missing ? "italic text-muted-foreground" : "text-foreground"
        }`}
      >
        {content}
      </dd>
    </div>
  );
}

export function MetadataCard({ scan }: { scan: ScannerResponse }) {
  return (
    <DashboardSection
      icon={FileText}
      title="Metadata"
      description="Head tags returned by the scanner."
    >
      <dl className="grid gap-4 md:grid-cols-2">
        <Row label="Title" content={value(scan.title)} />
        <Row label="Meta Description" content={value(scan.meta_description)} />
        <Row label="Canonical URL" content={value(scan.canonical)} />
        <Row label="Meta Robots" content={value(scan.meta_robots)} />
        <Row label="Language" content={value(scan.language)} />
        <Row label="Charset" content={value(scan.charset)} />
        <Row label="Viewport" content={value(scan.viewport)} />
        <Row label="Favicon" content={value(scan.favicon)} />
      </dl>
    </DashboardSection>
  );
}
