import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { SEOIssue } from "@/types/scan";
import { SEVERITY_COLOR, SEVERITY_LABEL, SEVERITY_ORDER, severityCounts } from "./severity";

export function IssuesSeverityChart({ issues }: { issues: SEOIssue[] }) {
  const counts = severityCounts(issues);
  const data = SEVERITY_ORDER.map((severity) => ({
    name: SEVERITY_LABEL[severity],
    value: counts[severity],
    fill: SEVERITY_COLOR[severity],
  }));
  const max = Math.max(1, ...data.map((d) => d.value));

  return (
    <div
      className="h-64 w-full"
      role="img"
      aria-label={data.map((d) => `${d.name}: ${d.value}`).join(", ")}
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 12, right: 8, bottom: 4, left: -20 }}>
          <XAxis
            dataKey="name"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <YAxis
            allowDecimals={false}
            domain={[0, max]}
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <Tooltip
            cursor={{ fill: "rgba(37,99,235,0.06)" }}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid #e2e8f0",
              fontSize: 12,
              boxShadow: "0 8px 24px -12px rgba(15,23,42,0.25)",
            }}
          />
          <Bar dataKey="value" name="Issues" radius={[8, 8, 0, 0]} maxBarSize={64}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
