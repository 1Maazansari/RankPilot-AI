import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import {
  ArrowRight, Sparkles, Search, Bot, BarChart3, ShieldCheck, Zap, Globe,
  Gauge, TrendingUp, CheckCircle2, Clock, ChevronDown, Rocket,
  FileText, Users, Layers, Twitter, Github, Linkedin, Mail,
} from "lucide-react";
import { SiteNav } from "@/components/site-nav";
import { AIChatPanel } from "@/components/ai-chat-panel";
import { AnimatedCounter } from "@/components/animated-counter";
import { validateWebsiteUrl } from "@/lib/url-validation";
import { PRICING_PLANS } from "@/lib/pricing";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "RankX - Instant AI SEO Audits for Any Web Page" },
      { name: "description", content: "Paste any URL. RankX returns an SEO score, every issue with a fix, metadata and media analysis, and AI recommendations." },
      { property: "og:title", content: "RankX - Instant AI SEO Audits" },
      { property: "og:description", content: "AI-powered SEO intelligence in under a minute. Scores, fixes, action plan." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Landing,
});

function Reveal({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); io.disconnect(); } },
      { threshold: 0.15 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div
      ref={ref}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(28px)",
        transition: `opacity 0.8s cubic-bezier(0.16,1,0.3,1) ${delay}ms, transform 0.8s cubic-bezier(0.16,1,0.3,1) ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

function Landing() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);

  function submit(e: FormEvent) {
    e.preventDefault();
    const result = validateWebsiteUrl(url);
    if (!result.ok) {
      setError(result.message);
      return;
    }
    setError(null);
    navigate({ to: "/analyze", search: { url: result.url } });
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background">
      {/* Parallax background shapes */}
      <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-32 top-20 h-96 w-96 rounded-full bg-[color:var(--brand-blue-light)] opacity-60 blur-3xl float-slow" />
        <div className="absolute right-[-8rem] top-[40rem] h-[28rem] w-[28rem] rounded-full bg-[color:var(--brand-blue-light)] opacity-50 blur-3xl float-slow" style={{ animationDelay: "1.5s" }} />
        <div className="absolute left-1/2 top-[80rem] h-96 w-96 -translate-x-1/2 rounded-full bg-[color:var(--brand-blue-light)] opacity-40 blur-3xl float-slow" style={{ animationDelay: "3s" }} />
      </div>

      <SiteNav />

      {/* HERO */}
      <section className="relative mx-auto max-w-7xl px-6 pb-24 pt-16 lg:pt-24">
        <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <Reveal>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-accent px-3 py-1.5 text-xs font-semibold text-primary">
                <Sparkles className="h-3.5 w-3.5" /> AI-powered SEO intelligence
              </div>
            </Reveal>
            <Reveal delay={80}>
              <h1 className="text-balance text-5xl font-extrabold leading-[1.05] tracking-tight text-foreground sm:text-6xl lg:text-7xl">
                Rank higher with an{" "}
                <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">AI co-pilot</span>{" "}
                for your website
              </h1>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-6 max-w-xl text-lg text-muted-foreground">
                Paste any URL. RankX scans the page, runs a full SEO rule engine, and returns AI recommendations you can act on in minutes.
              </p>
            </Reveal>
            <Reveal delay={240}>
              <form onSubmit={submit} className="mt-10 max-w-xl">
                <div className="flex items-center gap-2 rounded-2xl border border-border bg-white p-2 pl-4 shadow-[var(--shadow-card)] transition focus-within:border-primary/50 focus-within:ring-4 focus-within:ring-primary/10">
                  <Globe className="h-5 w-5 shrink-0 text-muted-foreground" />
                  <input
                    id="url-input"
                    type="text"
                    inputMode="url"
                    autoComplete="off"
                    spellCheck={false}
                    placeholder="yourwebsite.com"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="min-w-0 flex-1 bg-transparent py-3 text-base text-foreground outline-none placeholder:text-muted-foreground/70"
                  />
                  <button
                    type="submit"
                    className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110 hover:-translate-y-0.5 active:scale-[.98]"
                  >
                    Analyze <ArrowRight className="h-4 w-4" />
                  </button>
                  <Link
                    to="/multi-page-audit"
                    className="inline-flex shrink-0 items-center gap-2 rounded-xl border border-primary/25 bg-white px-5 py-3 text-sm font-semibold text-primary transition hover:bg-accent"
                  >
                    Multi-Page Audit
                  </Link>
                </div>
                {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
                <p className="mt-3 text-xs text-muted-foreground">Free scan ‚· No signup required ‚· Results in 60s</p>
              </form>
            </Reveal>
            <Reveal delay={320}>
              <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-3 text-xs font-medium uppercase tracking-widest text-muted-foreground/80">
                <span>Trusted by 12k+ teams</span>
                <span className="h-1 w-1 rounded-full bg-muted-foreground/30" />
                <span>SOC2 grade</span>
                <span className="h-1 w-1 rounded-full bg-muted-foreground/30" />
                <span>GPT-4 powered</span>
              </div>
            </Reveal>
          </div>

          {/* Hero visual: floating SEO score cards */}
          <Reveal delay={200}>
            <HeroVisual />
          </Reveal>
        </div>
      </section>

      {/* STATS */}
      <section className="relative mx-auto max-w-7xl px-6 pb-8">
        <Reveal>
          <div className="grid gap-4 rounded-3xl border border-border bg-white p-8 shadow-[var(--shadow-card)] sm:grid-cols-2 lg:grid-cols-4">
            {[
              { value: 12400, suffix: "+", label: "Websites analyzed" },
              { value: 3.2, suffix: "x", label: "Avg. traffic lift", decimals: 1 },
              { value: 60, suffix: "s", label: "Median scan time" },
              { value: 99.9, suffix: "%", label: "Uptime SLA", decimals: 1 },
            ].map((s) => (
              <div key={s.label} className="text-center sm:text-left">
                <div className="bg-[image:var(--gradient-primary)] bg-clip-text text-4xl font-extrabold tracking-tight text-transparent sm:text-5xl">
                  <AnimatedCounter to={s.value} suffix={s.suffix} decimals={s.decimals ?? 0} />
                </div>
                <div className="mt-2 text-sm font-medium text-muted-foreground">{s.label}</div>
              </div>
            ))}
          </div>
        </Reveal>
      </section>

      {/* FEATURES */}
      <section id="features" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="Features" title="Everything you need to outrank the competition" subtitle="A complete AI SEO workflow, from scan to shipped fix." />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Search, title: "Deep site scanning", body: "Crawl every page for meta, structure, schema, links, and Core Web Vitals in seconds." },
            { icon: Bot, title: "AI recommendations", body: "Every issue includes a plain-English reason and an actionable fix, not just a score." },
            { icon: BarChart3, title: "Priority action plan", body: "Ranked by impact and effort so your team knows exactly what to ship first." },
            { icon: ShieldCheck, title: "Website health", body: "Track performance, accessibility, best practices, and SEO across every deploy." },
            { icon: Zap, title: "Instant reports", body: "Beautifully formatted exports ready to share with clients and stakeholders." },
            { icon: Layers, title: "Modern stack ready", body: "Optimized for React, Next.js, TanStack, Astro, Shopify, Webflow, and more." },
          ].map(({ icon: Icon, title, body }, i) => (
            <Reveal key={title} delay={i * 60}>
              <div className="group h-full rounded-3xl border border-border bg-white p-7 shadow-[var(--shadow-card)] transition hover:-translate-y-1 hover:border-primary/40 hover:shadow-[var(--shadow-glow)]">
                <div className="mb-5 grid h-12 w-12 place-items-center rounded-2xl bg-accent text-primary transition group-hover:scale-110">
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold text-foreground">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="How it works" title="From URL to action plan in 60 seconds" subtitle="Five focused stages, one clear report." />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-5">
          {[
            { step: "01", label: "Validate URL", icon: ShieldCheck },
            { step: "02", label: "Scan Website", icon: Globe },
            { step: "03", label: "SEO Analysis", icon: Search },
            { step: "04", label: "AI Processing", icon: Bot },
            { step: "05", label: "Report", icon: FileText },
          ].map(({ step, label, icon: Icon }, i) => (
            <Reveal key={step} delay={i * 80}>
              <div className="group h-full rounded-3xl border border-border bg-white p-6 shadow-[var(--shadow-card)] transition hover:-translate-y-1 hover:border-primary/40">
                <div className="mb-4 flex items-center justify-between">
                  <span className="text-xs font-mono font-semibold text-primary">{step}</span>
                  <Icon className="h-5 w-5 text-primary/70 transition group-hover:text-primary" />
                </div>
                <div className="text-base font-semibold text-foreground">{label}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* LIVE DASHBOARD PREVIEW */}
      <section id="preview" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="Live preview" title="A dashboard your whole team will actually use" subtitle="Clarity over clutter. Every metric with the context that makes it actionable." />
        </Reveal>
        <Reveal delay={120}>
          <div className="mt-14 rounded-[28px] border border-border bg-white p-4 shadow-[var(--shadow-card)] sm:p-6">
            <div className="rounded-2xl bg-secondary p-6 sm:p-8">
              <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-white shadow-sm"><Globe className="h-4 w-4 text-primary" /></span>
                  <span className="font-semibold text-foreground">acme.com</span>
                </div>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-[color:var(--success)]/10 px-3 py-1 text-xs font-semibold text-[color:var(--success)]">
                  <CheckCircle2 className="h-3.5 w-3.5" /> Analysis complete
                </span>
              </div>
              <div className="grid gap-4 sm:grid-cols-4">
                {[
                  { label: "SEO Score", value: 87, icon: Sparkles },
                  { label: "Website Health", value: 92, icon: ShieldCheck },
                  { label: "Performance", value: 78, icon: Gauge },
                  { label: "Scan Time", value: "42s", icon: Clock },
                ].map(({ label, value, icon: Icon }) => (
                  <div key={label} className="rounded-2xl border border-border bg-white p-5 shadow-sm">
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{label}</span>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="mt-3 text-3xl font-bold tracking-tight text-foreground">{value}</div>
                    {typeof value === "number" && (
                      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-secondary">
                        <div className="h-full rounded-full bg-[image:var(--gradient-primary)]" style={{ width: `${value}%` }} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* WHY CHOOSE */}
      <section id="why" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="Why RankX" title="Built for teams who ship" subtitle="Not another audit tool. A co-pilot that explains what to do next." />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Rocket, title: "faster audits", body: "Full reports in under a minute versus hours of manual work." },
            { icon: Bot, title: "AI that explains", body: "Every fix comes with the why, not just the what." },
            { icon: TrendingUp, title: "Measurable results", body: "Teams see — organic growth within a quarter." },
            { icon: Users, title: "Loved by devs & marketers", body: "Simple enough for founders, deep enough for engineers." },
          ].map(({ icon: Icon, title, body }, i) => (
            <Reveal key={title} delay={i * 60}>
              <div className="h-full rounded-3xl border border-border bg-white p-6 shadow-[var(--shadow-card)] transition hover:-translate-y-1 hover:border-primary/40">
                <div className="mb-4 grid h-11 w-11 place-items-center rounded-xl bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-base font-semibold">{title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* CAPABILITIES */}
      <section id="capabilities" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader
            eyebrow="What you get"
            title="Everything in one single-page scan"
            subtitle="Every number in your report comes straight from the scan Ã¢â‚¬â€ nothing is estimated or invented."
          />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {[
            { title: "SEO score & grade", body: "A 0-100 score with a letter grade and a severity breakdown of every finding." },
            { title: "Rule-engine issues", body: "Each issue lists its severity, category, plain-English explanation and a concrete fix." },
            { title: "Metadata & social", body: "Title, description, canonical, robots, language, charset, Open Graph and Twitter cards." },
            { title: "Media analysis", body: "Image counts, missing alt text and previews of the images your page shares." },
            { title: "AI recommendations", body: "Prioritised actions with the reason, the impact and the estimated effort." },
            { title: "Downloadable report", body: "Export the full audit as a text report you can hand to a developer or client." },
          ].map((item, i) => (
            <Reveal key={item.title} delay={i * 60}>
              <div className="h-full rounded-3xl border border-border bg-white p-7 shadow-[var(--shadow-card)]">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-accent text-primary">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
                <h3 className="mt-5 text-base font-semibold text-foreground">{item.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{item.body}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* PRICING teaser */}
      <section id="pricing" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader
            eyebrow="Pricing"
            title="Single-page scans are free"
            subtitle="Multi-page website crawling requires a subscription."
          />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {PRICING_PLANS.map((plan, i) => (
            <Reveal key={plan.id} delay={i * 80}>
              <div
                className={`relative flex h-full flex-col rounded-3xl border p-8 transition hover:-translate-y-1 ${
                  plan.highlight
                    ? "border-primary bg-white shadow-[var(--shadow-glow)] ring-2 ring-primary/15"
                    : "border-border bg-white shadow-[var(--shadow-card)]"
                }`}
              >
                {plan.highlight && (
                  <span className="absolute right-6 top-6 rounded-full bg-accent px-3 py-1 text-xs font-semibold text-primary">
                    Most popular
                  </span>
                )}
                <div className="text-sm font-semibold text-primary">{plan.name}</div>
                <div className="mt-3 flex items-baseline gap-1">
                  <span className="text-5xl font-extrabold tracking-tight">{plan.price}</span>
                  {plan.period && <span className="text-sm text-muted-foreground">{plan.period}</span>}
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{plan.tagline}</p>
                <ul className="mt-6 flex-1 space-y-3 text-sm">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" /> {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  to="/subscription"
                  className={`mt-8 w-full rounded-xl px-4 py-3 text-center text-sm font-semibold transition ${
                    plan.highlight
                      ? "bg-[image:var(--gradient-primary)] text-white hover:brightness-110"
                      : "bg-foreground text-white hover:opacity-90"
                  }`}
                >
                  {plan.available ? "Scan a page free" : plan.cta}
                </Link>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="relative mx-auto max-w-3xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="FAQ" title="Frequently asked questions" subtitle="Everything you need to know before your first scan." />
        </Reveal>
        <div className="mt-12 space-y-3">
          {[
            { q: "How long does a scan take?", a: "A single-page scan usually completes in a few seconds. Very slow sites can take up to two minutes before the request times out." },
            { q: "Do I need to install anything?", a: "No. RankX works with just a URL Ã¢â‚¬â€ no script, no DNS changes, no code." },
            { q: "Can RankX crawl my whole website?", a: "Not on the free plan. Multi-page crawling and sitemap analysis are part of a paid subscription." },
            { q: "Can I export the report?", a: "Yes. Every report can be downloaded as a text file containing the score, all issues and every AI recommendation." },
            { q: "Where is my report stored?", a: "Your report is kept in your browser session only. Closing the tab clears it, and running a new scan replaces it." },
          ].map((f, i) => (
            <Reveal key={f.q} delay={i * 50}>
              <FAQItem q={f.q} a={f.a} />
            </Reveal>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section id="contact" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <div className="overflow-hidden rounded-[32px] bg-[image:var(--gradient-primary)] p-12 text-center shadow-[var(--shadow-glow)] sm:p-16">
            <h2 className="text-balance text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
              Ready to see your SEO score?
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-white/85">
              Run your first scan free. No credit card, no signup. Just paste a URL.
            </p>
            <button
              onClick={() => document.getElementById("url-input")?.scrollIntoView({ behavior: "smooth", block: "center" })}
              className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-semibold text-primary shadow-lg transition hover:-translate-y-0.5 hover:brightness-95"
            >
              Analyze my site <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </Reveal>
      </section>

      {/* FOOTER */}
      <footer className="relative border-t border-border bg-white">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 md:grid-cols-4">
          <div className="md:col-span-1">
            <div className="flex items-center gap-2.5">
              <div className="grid h-9 w-9 place-items-center rounded-xl bg-[image:var(--gradient-primary)]">
                <Zap className="h-5 w-5 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-lg font-bold tracking-tight">Rank<span className="text-primary">X</span></span>
            </div>
            <p className="mt-4 max-w-xs text-sm text-muted-foreground">
              AI-powered SEO intelligence for modern teams.
            </p>
            <div className="mt-6 flex gap-2">
              {[Twitter, Github, Linkedin, Mail].map((Icon, i) => (
                <a key={i} href="#" className="grid h-9 w-9 place-items-center rounded-lg border border-border text-muted-foreground transition hover:border-primary/40 hover:text-primary">
                  <Icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>
          {[
            { title: "Product", links: ["Features", "Pricing", "Dashboard", "Changelog"] },
            { title: "Resources", links: ["Docs", "Guides", "Blog", "API"] },
            { title: "Company", links: ["About", "Careers", "Contact", "Privacy"] },
          ].map((col) => (
            <div key={col.title}>
              <div className="text-sm font-semibold text-foreground">{col.title}</div>
              <ul className="mt-4 space-y-3">
                {col.links.map((l) => (
                  <li key={l}><a href="#" className="text-sm text-muted-foreground transition hover:text-foreground">{l}</a></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t border-border">
          <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-6 text-xs text-muted-foreground sm:flex-row">
            <div>Ã‚© {new Date().getFullYear()} RankX. All rights reserved.</div>
            <div className="flex gap-6">
              <a href="#" className="transition hover:text-foreground">Privacy</a>
              <a href="#" className="transition hover:text-foreground">Terms</a>
              <a href="#" className="transition hover:text-foreground">Status</a>
            </div>
          </div>
        </div>
      </footer>
      <AIChatPanel />
    </div>
  );
}

function SectionHeader({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-accent px-3 py-1 text-xs font-semibold text-primary">
        {eyebrow}
      </div>
      <h2 className="text-balance text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl md:text-5xl">
        {title}
      </h2>
      <p className="mx-auto mt-4 max-w-xl text-base text-muted-foreground">{subtitle}</p>
    </div>
  );
}

function FAQItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`overflow-hidden rounded-2xl border transition ${open ? "border-primary/40 bg-accent/50" : "border-border bg-white"}`}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
      >
        <span className="text-base font-semibold text-foreground">{q}</span>
        <ChevronDown className={`h-5 w-5 shrink-0 text-primary transition ${open ? "rotate-180" : ""}`} />
      </button>
      <div className={`grid transition-all duration-300 ${open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}>
        <div className="overflow-hidden">
          <p className="px-6 pb-5 text-sm leading-relaxed text-muted-foreground">{a}</p>
        </div>
      </div>
    </div>
  );
}

function HeroVisual() {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-lg">
      {/* Main card */}
      <div className="absolute inset-6 rounded-[32px] border border-border bg-white p-6 shadow-[var(--shadow-glow)]">
        <div className="flex items-center gap-2 border-b border-border pb-4">
          <span className="h-2.5 w-2.5 rounded-full bg-destructive/70" />
          <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--warning)]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--success)]" />
          <span className="ml-3 text-xs text-muted-foreground">acme.com Ã¢â‚¬â€ Overview</span>
        </div>
        <div className="mt-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-muted-foreground">SEO Score</div>
              <div className="text-4xl font-extrabold tracking-tight text-foreground">92<span className="text-lg text-muted-foreground">/100</span></div>
            </div>
            <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[image:var(--gradient-primary)] text-white">
              <TrendingUp className="h-6 w-6" />
            </div>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-secondary">
            <div className="h-full w-[92%] rounded-full bg-[image:var(--gradient-primary)]" />
          </div>
          <div className="grid grid-cols-3 gap-2 pt-2">
            {[
              { l: "Perf", v: 88 },
              { l: "A11y", v: 95 },
              { l: "Best", v: 91 },
            ].map((m) => (
              <div key={m.l} className="rounded-xl border border-border bg-secondary/50 p-3 text-center">
                <div className="text-xs text-muted-foreground">{m.l}</div>
                <div className="text-lg font-bold text-foreground">{m.v}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Floating card 1 */}
      <div className="absolute -left-2 top-4 float-slow rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-card)]">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-[color:var(--success)]/15 text-[color:var(--success)]">
            <CheckCircle2 className="h-4 w-4" />
          </span>
          <div>
            <div className="text-xs text-muted-foreground">Core Web Vitals</div>
            <div className="text-sm font-bold text-foreground">All Passing</div>
          </div>
        </div>
      </div>

      {/* Floating card 2 */}
      <div className="absolute -right-4 bottom-16 float-slow rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-card)]" style={{ animationDelay: "1.2s" }}>
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent text-primary">
            <Sparkles className="h-4 w-4" />
          </span>
          <div>
            <div className="text-xs text-muted-foreground">AI Fixes</div>
            <div className="text-sm font-bold text-foreground">12 Suggested</div>
          </div>
        </div>
      </div>

      {/* Floating card 3 */}
      <div className="absolute bottom-0 left-8 float-slow rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-card)]" style={{ animationDelay: "2.4s" }}>
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-[image:var(--gradient-primary)] text-white">
            <Gauge className="h-4 w-4" />
          </span>
          <div>
            <div className="text-xs text-muted-foreground">LCP</div>
            <div className="text-sm font-bold text-foreground">1.4s</div>
          </div>
        </div>
      </div>
    </div>
  );
}