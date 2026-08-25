import type { SeoSeverity } from "@/types/scan";

export const SEVERITY_ORDER: SeoSeverity[] = ["critical", "high", "medium", "low"];

export const SEVERITY_LABEL: Record<SeoSeverity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

/** Chart-safe hex colors (Recharts cannot read Tailwind classes). */
export const SEVERITY_COLOR: Record<SeoSeverity, string> = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#d97706",
  low: "#2563eb",
};

export const SEVERITY_BADGE: Record<SeoSeverity, string> = {
  critical: "bg-red-50 text-red-700 ring-1 ring-red-200",
  high: "bg-orange-50 text-orange-700 ring-1 ring-orange-200",
  medium: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  low: "bg-blue-50 text-blue-700 ring-1 ring-blue-200",
};

export function severityCounts(issues: { severity: SeoSeverity }[]) {
  const counts: Record<SeoSeverity, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const issue of issues) counts[issue.severity] += 1;
  return counts;
}
