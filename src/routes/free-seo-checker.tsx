import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import {
  ArrowRight, Sparkles, Search, Bot, ShieldCheck, Zap, Globe,
  Gauge, CheckCircle2, ChevronDown, FileText, Layers, Users,
} from "lucide-react";
import { SiteNav } from "@/components/site-nav";
import { AIChatPanel } from "@/components/ai-chat-panel";
import { validateWebsiteUrl } from "@/lib/url-validation";

export const Route = createFileRoute("/free-seo-checker")({
  head: () => ({
    meta: [
      { title: "Free SEO Checker | AI Website SEO Audit | BrandVizi" },
      {
        name: "description",
        content:
          "Use BrandVizi's free SEO checker to audit your website, find SEO issues, check your SEO score, and get actionable AI-powered recommendations.",
      },
      { property: "og:title", content: "Free SEO Checker | AI Website SEO Audit | BrandVizi" },
      {
        property: "og:description",
        content: "Audit your website with BrandVizi's free SEO checker. Find SEO issues, check your SEO score, and get AI-powered recommendations.",
      },
      { property: "og:url", content: "https://brandvizi.in/free-seo-checker" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "Free SEO Checker | AI Website SEO Audit | BrandVizi" },
      {
        name: "twitter:description",
        content: "Audit your website with BrandVizi's free SEO checker. Find SEO issues, check your SEO score, and get AI-powered recommendations.",
      },
      { name: "twitter:image", content: "/og-image.png" },
      {
        "script:ld+json": {
          "@context": "https://schema.org",
          "@graph": [
            {
              "@type": "Organization",
              name: "BrandVizi",
              url: "https://brandvizi.in/",
            },
            {
              "@type": "WebSite",
              name: "BrandVizi",
              url: "https://brandvizi.in/",
              description:
                "BrandVizi is a free AI-powered SEO and AEO website audit tool that audits your website, finds SEO issues, scores your site, and provides actionable recommendations.",
            },
            {
              "@type": "SoftwareApplication",
              name: "BrandVizi",
              url: "https://brandvizi.in/",
              applicationCategory: "BusinessApplication",
              operatingSystem: "Web",
              offers: {
                "@type": "Offer",
                price: "0",
              },
              description:
                "BrandVizi is a free AI-powered SEO and AEO website audit tool that audits your website, finds SEO issues, scores your site, and provides actionable recommendations.",
            },
          ],
        },
      },
    ],
    links: [
      { rel: "canonical", href: "https://brandvizi.in/free-seo-checker" },
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
                Free SEO Checker &amp; AI Website Audit
              </h1>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-6 max-w-xl text-lg text-muted-foreground">
                Use BrandVizi's free SEO checker to audit your website, find SEO issues, check your SEO score, and get actionable AI-powered recommendations.
              </p>
            </Reveal>
            <Reveal delay={240}>
              <form onSubmit={submit} className="mt-10 max-w-xl">
                <div className="overflow-hidden rounded-2xl border border-border bg-white shadow-[var(--shadow-card)] transition focus-within:border-primary/50 focus-within:ring-4 focus-within:ring-primary/10">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 p-2 sm:pl-4">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
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
                    </div>
                    <div className="flex gap-2 px-1 pb-1 sm:p-0">
                      <button
                        type="submit"
                        className="inline-flex flex-1 sm:flex-initial items-center justify-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] px-5 py-3.5 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:brightness-110 hover:-translate-y-0.5 active:scale-[.98]"
                      >
                        Analyze <ArrowRight className="h-4 w-4" />
                      </button>
                      <Link
                        to="/multi-page-audit"
                        className="inline-flex flex-1 sm:flex-initial items-center justify-center gap-2 rounded-xl border border-primary/25 bg-white px-5 py-3.5 text-sm font-semibold text-primary transition hover:bg-accent"
                      >
                        Multi-Page Audit
                      </Link>
                    </div>
                  </div>
                </div>
                {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
                <p className="mt-3 text-xs text-muted-foreground">Free scan · No signup required · Results in seconds</p>
              </form>
            </Reveal>
            <Reveal delay={320}>
              <div className="mt-10 flex flex-wrap items-center gap-x-8 gap-y-3 text-xs font-medium uppercase tracking-widest text-muted-foreground/80">
                <span>Free during early access</span>
                <span className="h-1 w-1 rounded-full bg-muted-foreground/30" />
                <span>No signup required</span>
                <span className="h-1 w-1 rounded-full bg-muted-foreground/30" />
                <span>AI-powered SEO & AEO analysis</span>
              </div>
            </Reveal>
          </div>

          {/* Hero visual */}
          <Reveal delay={200}>
            <div className="relative mx-auto aspect-square w-full max-w-lg overflow-hidden">
              <div className="absolute inset-6 rounded-[32px] border border-border bg-white p-6 shadow-[var(--shadow-glow)]">
                <div className="flex items-center gap-2 border-b border-border pb-4">
                  <span className="h-2.5 w-2.5 rounded-full bg-destructive/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--warning)]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[color:var(--success)]" />
                  <span className="ml-3 text-xs text-muted-foreground">acme.com — Overview</span>
                </div>
                <div className="mt-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs text-muted-foreground">SEO Score</div>
                      <div className="text-4xl font-extrabold tracking-tight text-foreground">92<span className="text-lg text-muted-foreground">/100</span></div>
                    </div>
                    <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[image:var(--gradient-primary)] text-white">
                      <Search className="h-6 w-6" />
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

              <div className="absolute -left-2 top-4 float-slow rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-card)]">
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-[color:var(--success)]/15 text-[color:var(--success)]">
                    <CheckCircle2 className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="text-xs text-muted-foreground">SEO audit</div>
                    <div className="text-sm font-bold text-foreground">Ready to run</div>
                  </div>
                </div>
              </div>

              <div className="absolute -right-4 bottom-16 float-slow rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-card)]" style={{ animationDelay: "1.2s" }}>
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent text-primary">
                    <Sparkles className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="text-xs text-muted-foreground">AI insights</div>
                    <div className="text-sm font-bold text-foreground">Plain-English fixes</div>
                  </div>
                </div>
              </div>

              <div className="absolute bottom-0 left-8 float-slow rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-card)]" style={{ animationDelay: "2.4s" }}>
                <div className="flex items-center gap-2">
                  <span className="grid h-8 w-8 place-items-center rounded-lg bg-[image:var(--gradient-primary)] text-white">
                    <FileText className="h-4 w-4" />
                  </span>
                  <div>
                    <div className="text-xs text-muted-foreground">Report</div>
                    <div className="text-sm font-bold text-foreground">Exportable</div>
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* WHAT IT CHECKS */}
      <section id="features" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="What it checks" title="A complete website SEO analysis" subtitle="BrandVizi scans your page for everything that affects search visibility and user experience." />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Search, title: "SEO score & grade", body: "Get a clear 0-100 score with a letter grade and a breakdown of every finding by severity." },
            { icon: ShieldCheck, title: "Metadata & structure", body: "Title, description, canonical, robots, language, charset, Open Graph and Twitter cards." },
            { icon: Gauge, title: "Performance signals", body: "Page weight, response size, and technical signals that impact crawlability and user experience." },
            { icon: Layers, title: "Media & content", body: "Image counts, missing alt text, and content structure that helps search engines understand your page." },
            { icon: Bot, title: "AI recommendations", body: "Every issue includes a plain-English reason and an actionable fix, not just a score." },
            { icon: FileText, title: "Downloadable report", body: "Export the full audit as a text report you can hand to a developer or client." },
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
          <SectionHeader eyebrow="How it works" title="From URL to action plan" subtitle="Five focused stages, one clear report." />
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

      {/* BENEFITS */}
      <section id="why" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="Why use it" title="Built for teams who ship" subtitle="Not another audit tool. A co-pilot that explains what to do next." />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: Zap, title: "faster audits", body: "Full reports in under a minute versus hours of manual work." },
            { icon: Bot, title: "AI that explains", body: "Every fix comes with the why, not just the what." },
            { icon: CheckCircle2, title: "actionable results", body: "Single-page and multi-page audits with prioritized actions." },
            { icon: Users, title: "simple for everyone", body: "Clear enough for founders, detailed enough for engineers." },
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

      {/* PRICING */}
      <section id="pricing" className="relative mx-auto max-w-7xl px-6 py-24">
        <Reveal>
          <SectionHeader
            eyebrow="Early Access"
            title="Everything is Free During Early Access"
            subtitle="Get access to all current BrandVizi features — no signup, no credit card, no paid plan."
          />
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-1 max-w-2xl mx-auto">
          <Reveal>
            <div className="relative flex h-full flex-col rounded-3xl border border-primary bg-white shadow-[var(--shadow-glow)] ring-2 ring-primary/15 p-8 transition hover:-translate-y-1">
              <div className="text-sm font-semibold text-primary">Early Access — Free</div>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-5xl font-extrabold tracking-tight">$0</span>
                <span className="text-sm text-muted-foreground">/free</span>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">All current BrandVizi features. No signup. No credit card. No paid plan.</p>
              <ul className="mt-6 flex-1 grid gap-3 sm:grid-cols-2 text-sm">
                {[
                  "Full SEO Audit",
                  "SEO Score & Issues",
                  "AI Recommendations",
                  "AI SEO Copilot",
                  "Multi-Page Audit",
                  "SEO Reports",
                  "All Current Features Included",
                ].map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" /> {feature}
                  </li>
                ))}
              </ul>
              <Link
                to="/"
                className="mt-8 w-full rounded-xl bg-[image:var(--gradient-primary)] px-4 py-3 text-center text-sm font-semibold text-white transition hover:brightness-110"
              >
                Start Free Audit
              </Link>
            </div>
          </Reveal>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="relative mx-auto max-w-3xl px-6 py-24">
        <Reveal>
          <SectionHeader eyebrow="FAQ" title="Frequently asked questions" subtitle="Everything you need to know before your first scan." />
        </Reveal>
        <div className="mt-12 space-y-3">
          {[
            { q: "How long does a scan take?", a: "A single-page website SEO analysis usually completes in a few seconds. Very slow sites can take up to two minutes before the request times out." },
            { q: "Do I need to install anything?", a: "No. BrandVizi is a free AI-powered SEO and AEO website audit tool that works with just a URL — no script, no DNS changes, no code." },
            { q: "Can BrandVizi crawl my whole website?", a: "Yes. Multi-page crawling and sitemap analysis are available now during early access. You can run a full SEO audit across multiple pages — no subscription required." },
            { q: "What is AEO?", a: "AEO stands for Answer Engine Optimization. BrandVizi helps you understand and improve your website for both traditional search engines and AI-powered answer engines, so you can improve your content for the way people search today." },
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
            <div className="flex items-center">
              <img
                src="/brandvizi-logo.png"
                alt="BrandVizi — AI SEO AEO Intelligence"
                className="h-8 w-auto object-contain sm:h-9"
              />
            </div>
            <p className="mt-4 max-w-xs text-sm text-muted-foreground">
              AI-powered SEO intelligence for modern teams.
            </p>
          </div>
          {[
            { title: "Product", links: [{ label: "Home", href: "/" }, { label: "Free SEO Checker", href: "/free-seo-checker" }, { label: "Multi-Page Audit", href: "/multi-page-audit" }, { label: "Subscription", href: "/subscription" }] },
          ].map((col) => (
            <div key={col.title}>
              <div className="text-sm font-semibold text-foreground">{col.title}</div>
              <ul className="mt-4 space-y-3">
                {col.links.map((l) => (
                  <li key={l.label}><Link to={l.href} className="text-sm text-muted-foreground transition hover:text-foreground">{l.label}</Link></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t border-border">
          <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-6 text-xs text-muted-foreground sm:flex-row">
            <div>© {new Date().getFullYear()} BrandVizi. All rights reserved.</div>
          </div>
        </div>
      </footer>
      <AIChatPanel />
    </div>
  );
}
