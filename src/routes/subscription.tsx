import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Rocket } from "lucide-react";
import { SiteNav } from "@/components/site-nav";
import { AIChatPanel } from "@/components/ai-chat-panel";
import { PRICING_PLANS } from "@/lib/pricing";

export const Route = createFileRoute("/subscription")({
  head: () => ({
    meta: [
      { title: "Early Access — BrandVizi" },
      {
        name: "description",
        content:
          "Everything is free during early access. Get all current BrandVizi features — no signup, no credit card, no paid plan.",
      },
      { property: "og:title", content: "Early Access — BrandVizi" },
      {
        property: "og:description",
        content: "All current BrandVizi features are free during early access.",
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
            <Rocket className="h-3.5 w-3.5" /> Early Access
          </div>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
            Everything is Free During Early Access 🚀
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Get access to all current BrandVizi features — no signup, no credit card, no paid plan.
          </p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-1 max-w-2xl mx-auto">
          {PRICING_PLANS.map((plan) => (
            <article
              key={plan.id}
              className={`flex flex-col rounded-3xl border bg-white p-8 shadow-[var(--shadow-glow)] ring-2 ring-primary/15 sm:p-10`}
            >
              <span className="mb-4 w-fit rounded-full bg-accent px-3 py-1 text-xs font-semibold text-primary">
                {plan.name}
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-5xl font-extrabold tracking-tight text-foreground">
                  {plan.price}
                </span>
                {plan.period && (
                  <span className="text-sm font-medium text-muted-foreground">{plan.period}</span>
                )}
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{plan.tagline}</p>

              <ul className="mt-8 flex-1 grid gap-3 sm:grid-cols-2">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5 text-sm text-foreground">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                    {feature}
                  </li>
                ))}
              </ul>

              <Link
                to="/"
                className="mt-8 inline-flex items-center justify-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110"
              >
                {plan.cta}
              </Link>
            </article>
          ))}
        </div>

        <p className="mt-10 text-center text-sm text-muted-foreground">
          No account required. No payment needed. Just paste a URL and start your free audit.
        </p>
      </main>

      <AIChatPanel />
    </div>
  );
}
