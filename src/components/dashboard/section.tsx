import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export function DashboardSection({
  id,
  icon: Icon,
  title,
  description,
  actions,
  children,
}: {
  id?: string;
  icon: LucideIcon;
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section
      id={id}
      className="rounded-3xl border border-border bg-white p-6 shadow-[var(--shadow-card)] sm:p-8"
    >
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-accent text-primary">
            <Icon className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-bold tracking-tight text-foreground">{title}</h2>
            {description && (
              <p className="mt-1 text-sm text-muted-foreground">{description}</p>
            )}
          </div>
        </div>
        {actions}
      </div>
      {children}
    </section>
  );
}
