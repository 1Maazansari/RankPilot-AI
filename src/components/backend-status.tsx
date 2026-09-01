import { useQuery } from "@tanstack/react-query";

export function BackendStatus({ className = "" }: { className?: string }) {
  const { data, isPending } = useQuery({
    queryKey: ["api-health"],
    queryFn: async () => {
      try {
        const res = await fetch("/api/public/health");
        if (!res.ok) return { online: false };
        const body = (await res.json()) as { status?: string; service?: string };
        return { online: body.status === "ok", service: body.service };
      } catch {
        return { online: false };
      }
    },
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

  const online = Boolean(data?.online);
  const label = isPending
    ? "Checking API…"
    : online
      ? `API online${data?.service ? ` · ${data.service}` : ""}`
      : "API offline";

  return (
    <span
      title={`/api/public/health`}
      className={`inline-flex items-center gap-2 rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-muted-foreground ${className}`}
    >
      <span className="relative flex h-2 w-2">
        {online && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[color:var(--success)] opacity-70" />
        )}
        <span
          className={`relative inline-flex h-2 w-2 rounded-full ${
            isPending ? "bg-muted-foreground" : online ? "bg-[color:var(--success)]" : "bg-destructive"
          }`}
        />
      </span>
      {label}
    </span>
  );
}
