import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

export function SeoScoreChart({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const data = [
    { name: "SEO Score", value: clamped },
    { name: "Remaining", value: 100 - clamped },
  ];

  return (
    <div className="relative h-64 w-full" role="img" aria-label={`SEO score ${clamped} out of 100`}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            innerRadius="66%"
            outerRadius="90%"
            startAngle={90}
            endAngle={-270}
            paddingAngle={clamped === 0 || clamped === 100 ? 0 : 2}
            stroke="none"
            isAnimationActive
          >
            <Cell fill="#2563eb" />
            <Cell fill="#e2e8f0" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-extrabold tracking-tight text-foreground">{clamped}%</span>
        <span className="mt-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          SEO Score
        </span>
      </div>
    </div>
  );
}
