import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Lock, Sparkles } from "lucide-react";
import { SiteNav } from "@/components/site-nav";
import { AIChatPanel } from "@/components/ai-chat-panel";
import { MULTI_PAGE_LOCKED_NOTE, PRICING_PLANS } from "@/lib/pricing";

export const Route = createFileRoute("/subscription")({
  head: () => ({
    meta: [
      { title: "Plans & Multi-Page Crawling — RankX" },
      {
        name: "description",
        content:
          "Single-page scans are free on RankX. Multi-page website crawling, sitemap analysis and full-site reports require a subscription.",
      },
      { property: "og:title", content: "Plans & Multi-Page Crawling — RankX" },
      {
        property: "og:description",
        content: "Compare RankX plans and unlock full-website crawling.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: SubscriptionPage,
});

function SubscriptionPage() {
  return (
    <div className="min-h-screen">
      <SiteNav />

      <main className="mx-auto max-w-7xl px-6 py-16 sm:py-24">
        <div className="mx-auto max-w-2xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs font-semibold text-primary">
            <Sparkles className="h-3.5 w-3.5" /> Plans
          </div>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
            Scan one page free. Crawl the whole site on Pro.
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">{MULTI_PAGE_LOCKED_NOTE}</p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {PRICING_PLANS.map((plan) => (
            <article
              key={plan.id}
              className={`flex flex-col rounded-3xl border bg-white p-6 shadow-[var(--shadow-card)] sm:p-8 ${
                plan.highlight ? "border-primary ring-2 ring-primary/15" : "border-border"
              }`}
            >
              {plan.highlight && (
                <span className="mb-4 w-fit rounded-full bg-accent px-3 py-1 text-xs font-semibold text-primary">
                  Most popular
                </span>
              )}
              <h2 className="text-lg font-bold tracking-tight text-foreground">{plan.name}</h2>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold tracking-tight text-foreground">
                  {plan.price}
                </span>
                {plan.period && (
                  <span className="text-sm font-medium text-muted-foreground">{plan.period}</span>
                )}
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{plan.tagline}</p>

              <ul className="mt-6 flex-1 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5 text-sm text-foreground">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                    {feature}
                  </li>
                ))}
              </ul>

              {plan.available ? (
                <Link
                  to="/"
                  className="mt-8 inline-flex items-center justify-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110"
                >
                  Start a free scan
                </Link>
              ) : (
                <button
                  type="button"
                  disabled
                  aria-disabled="true"
                  title="Coming soon"
                  className="mt-8 inline-flex cursor-not-allowed items-center justify-center gap-2 rounded-xl border border-border bg-secondary px-5 py-3 text-sm font-semibold text-muted-foreground"
                >
                  <Lock className="h-4 w-4" /> {plan.cta}
                </button>
              )}
            </article>
          ))}
        </div>

        <p className="mt-10 text-center text-sm text-muted-foreground">
          Multi-page crawling is not enabled in this deployment. Single-page scanning remains fully
          available and free.
        </p>
      </main>

      <AIChatPanel />
    </div>
  );
}
