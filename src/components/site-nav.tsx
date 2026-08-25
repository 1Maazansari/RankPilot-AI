import { Link } from "@tanstack/react-router";
import { Zap, Menu, X } from "lucide-react";
import { useState } from "react";
import { BackendStatus } from "@/components/backend-status";

const NAV_ITEMS = [
  { label: "Home", href: "/", type: "route" as const },
  { label: "Features", href: "#features", type: "hash" as const },
  { label: "Dashboard", href: "/dashboard", type: "route" as const },
  { label: "Pricing", href: "/subscription", type: "route" as const },
  { label: "FAQ", href: "#faq", type: "hash" as const },
];

export function SiteNav() {
  const [open, setOpen] = useState(false);

  const focusInput = () => {
    document.getElementById("url-input")?.focus();
    document.getElementById("url-input")?.scrollIntoView({ behavior: "smooth", block: "center" });
    setOpen(false);
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-white/75 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-[image:var(--gradient-primary)] shadow-[var(--shadow-glow)]">
            <Zap className="h-5 w-5 text-white" strokeWidth={2.5} />
          </div>
          <span className="text-lg font-bold tracking-tight text-foreground">
            Rank<span className="text-primary">X</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {NAV_ITEMS.map((item) =>
            item.type === "route" ? (
              <Link
                key={item.label}
                to={item.href}
                className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition hover:bg-secondary hover:text-foreground"
              >
                {item.label}
              </Link>
            ) : (
              <a
                key={item.label}
                href={item.href}
                className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition hover:bg-secondary hover:text-foreground"
              >
                {item.label}
              </a>
            ),
          )}
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          <BackendStatus />
          <button
            onClick={focusInput}
            className="rounded-xl bg-[image:var(--gradient-primary)] px-4 py-2.5 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110 active:scale-[.98]"
          >
            Get Started
          </button>
        </div>

        <button
          onClick={() => setOpen((v) => !v)}
          className="rounded-lg p-2 text-foreground lg:hidden"
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border bg-white lg:hidden">
          <nav className="mx-auto flex max-w-7xl flex-col gap-1 px-6 py-4">
            {NAV_ITEMS.map((item) =>
              item.type === "route" ? (
                <Link
                  key={item.label}
                  to={item.href}
                    onClick={() => setOpen(false)}
                  className="rounded-lg px-3 py-2.5 text-sm font-medium text-foreground hover:bg-secondary"
                >
                  {item.label}
                </Link>
              ) : (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-3 py-2.5 text-sm font-medium text-foreground hover:bg-secondary"
                >
                  {item.label}
                </a>
              ),
            )}
            <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
              <BackendStatus className="w-fit" />
              <button
                onClick={focusInput}
                className="rounded-lg bg-[image:var(--gradient-primary)] px-4 py-2 text-sm font-semibold text-white"
              >
                Get Started
              </button>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}