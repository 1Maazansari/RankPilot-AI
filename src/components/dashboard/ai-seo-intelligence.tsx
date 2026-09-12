import { useState } from "react";
import { Bot, Brain, Cpu, ChevronDown, CheckCircle, AlertCircle, Copy, Loader2, FileCode, Sparkles } from "lucide-react";
import type { AgentAnalysis, ValidationResult, AgentFinding, CodeSuggestion } from "@/types/scan";
import { DashboardSection } from "./section";
import { EmptyState } from "./empty-state";
import { SEVERITY_BADGE, SEVERITY_LABEL, SEVERITY_ORDER } from "./severity";

const AGENT_TABS = [
  { key: "technical", label: "Technical SEO", icon: Cpu, description: "Crawlability, indexability, HTML structure, metadata, and technical foundations" },
  { key: "content", label: "Content Intelligence", icon: Brain, description: "Page purpose, topic clarity, semantic meaning, readability, and search intent alignment" },
  { key: "aeo_geo", label: "AEO/GEO", icon: Sparkles, description: "Answer Engine Optimization, Generative Engine Optimization, and machine understanding" },
] as const;

type AgentTabKey = (typeof AGENT_TABS)[number]["key"];

interface AgentTabConfig {
  key: AgentTabKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

function SeverityBadge({ severity }: { severity: string }) {
  const normalized = severity.toLowerCase() as keyof typeof SEVERITY_BADGE;
  const badgeClass = SEVERITY_BADGE[normalized] || SEVERITY_BADGE.medium;
  const label = SEVERITY_LABEL[normalized] || severity.charAt(0).toUpperCase() + severity.slice(1);
  return <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${badgeClass}`}>{label}</span>;
}

function CodeBlock({ suggestion }: { suggestion: CodeSuggestion }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(suggestion.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API failed silently
    }
  };

  const language = suggestion.language.toLowerCase();

  return (
    <div className="rounded-xl border border-border bg-secondary/50 overflow-hidden">
      <div className="flex items-center justify-between border-b border-border bg-secondary/80 px-4 py-2">
        <span className="text-xs font-medium text-muted-foreground uppercase">{language || "code"}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-white px-3 py-1.5 text-xs font-medium text-foreground transition hover:bg-secondary"
          aria-label={copied ? "Copied" : "Copy code"}
        >
          <Copy className="h-3.5 w-3.5" />
          {copied ? "Copied" : "Copy Code"}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm"><code className={`language-${language}`}>{suggestion.code}</code></pre>
      {(suggestion.file_hint || suggestion.location_hint || suggestion.explanation) && (
        <div className="border-t border-border bg-white px-4 py-3 text-sm text-muted-foreground">
          {suggestion.explanation && <p className="font-medium">{suggestion.explanation}</p>}
          {suggestion.file_hint && <p className="mt-1"><span className="font-medium">File: </span>{suggestion.file_hint}</p>}
          {suggestion.location_hint && <p className="mt-1"><span className="font-medium">Location: </span>{suggestion.location_hint}</p>}
        </div>
      )}
    </div>
  );
}

function FindingCard({ finding }: { finding: AgentFinding }) {
  const [open, setOpen] = useState(false);

  return (
    <article className="overflow-hidden rounded-2xl border border-border bg-white shadow-sm transition hover:border-primary/30">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-start justify-between gap-4 p-5 text-left"
      >
        <div className="min-w-0">
          <h3 className="text-base font-semibold text-foreground">{finding.title}</h3>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <SeverityBadge severity={finding.severity} />
            {finding.category && (
              <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium capitalize text-muted-foreground ring-1 ring-border">
                {finding.category}
              </span>
            )}
          </div>
        </div>
        <ChevronDown className={`mt-1 h-5 w-5 shrink-0 text-primary transition ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="space-y-4 border-t border-border px-5 pb-5 pt-4">
          {finding.explanation && (
            <div>
              <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <AlertCircle className="h-3.5 w-3.5" /> Why this matters
              </div>
              <p className="text-sm leading-relaxed text-foreground/90">{finding.explanation}</p>
            </div>
          )}
          {finding.recommendation && (
            <div>
              <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <CheckCircle className="h-3.5 w-3.5" /> Recommended action
              </div>
              <p className="rounded-xl border border-border bg-secondary/50 p-4 text-sm leading-relaxed text-foreground">{finding.recommendation}</p>
            </div>
          )}
          {finding.implementation_steps && finding.implementation_steps.length > 0 && (
            <div>
              <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <FileCode className="h-3.5 w-3.5" /> Implementation
              </div>
              <ol className="space-y-2 pl-5 list-decimal text-sm text-foreground/90">
                {finding.implementation_steps.map((step, index) => (
                  <li key={index} className="leading-relaxed">{step}</li>
                ))}
              </ol>
            </div>
          )}
          {finding.code_suggestion && (
            <div>
              <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <FileCode className="h-3.5 w-3.5" /> Code suggestion
              </div>
              {typeof finding.code_suggestion === "string" ? (
                <pre className="rounded-xl border border-border bg-secondary/50 p-4 text-sm overflow-x-auto">
                  <code>{finding.code_suggestion}</code>
                </pre>
              ) : (
                <CodeBlock suggestion={finding.code_suggestion} />
              )}
            </div>
          )}
        </div>
      )}
    </article>
  );
}

function AgentTabContent({ analysis, isLoading, error }: { analysis: AgentAnalysis | undefined; isLoading?: boolean; error?: string }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-4 text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Analyzing with AI agent…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-6">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive shrink-0" />
          <div>
            <p className="font-medium text-destructive">Analysis temporarily unavailable</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis || analysis.findings.length === 0) {
    const emptyMessages: Record<string, string> = {
      technical: "No technical issues requiring AI analysis were identified.",
      content: "No content intelligence findings were identified from the available evidence.",
      aeo_geo: "No AEO/GEO findings were identified from the available evidence.",
    };
    return (
      <EmptyState
        icon={Bot}
        title="No findings"
        description={emptyMessages[analysis?.agent_name || ""] || "No AI findings were identified from the available evidence."}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl bg-accent/50 p-4 text-sm text-muted-foreground">
        {analysis.summary}
      </div>
      {analysis.findings.map((finding, index) => (
        <FindingCard key={`${finding.title}-${index}`} finding={finding} />
      ))}
    </div>
  );
}

function ValidationDisplay({ validation }: { validation: ValidationResult }) {
  if (!validation) return null;

  const { valid, validated_findings, rejected_findings, warnings } = validation;

  return (
    <div className="space-y-4">
      <div className={`rounded-xl p-4 ${valid ? "bg-green-50 border border-green-200" : "bg-amber-50 border border-amber-200"}`}>
        <div className="flex items-center gap-3">
          {valid ? (
            <CheckCircle className="h-5 w-5 text-green-600 shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-amber-600 shrink-0" />
          )}
          <div>
            <p className="font-medium text-foreground">
              {valid ? "✓ AI Findings Validated" : "⚠ AI Findings Partially Validated"}
            </p>
            <p className="text-sm text-muted-foreground">
              AI-generated findings were checked against the deterministic SEO analysis.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-white p-4 text-center">
          <p className="text-2xl font-bold text-green-600">{validated_findings.length}</p>
          <p className="text-sm text-muted-foreground">Validated findings</p>
        </div>
        <div className="rounded-xl border border-border bg-white p-4 text-center">
          <p className="text-2xl font-bold text-amber-600">{rejected_findings.length}</p>
          <p className="text-sm text-muted-foreground">Rejected findings</p>
        </div>
        <div className="rounded-xl border border-border bg-white p-4 text-center">
          <p className="text-2xl font-bold text-blue-600">{warnings.length}</p>
          <p className="text-sm text-muted-foreground">Warnings</p>
        </div>
      </div>

      {rejected_findings.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-muted-foreground">Rejected findings (not supported by deterministic evidence)</h4>
          {rejected_findings.map((finding, index) => (
            <div key={`${finding.title}-rejected-${index}`} className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm">
              <p className="font-medium text-amber-800">{finding.title}</p>
              <p className="mt-1 text-amber-700">{finding.explanation}</p>
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-muted-foreground">Validation warnings</h4>
          {warnings.map((warning, index) => (
            <div key={index} className="rounded-xl border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800">
              {warning}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function AiSeoIntelligence({ agents }: { agents?: import("@/types/scan").FinalAgentResult }) {
  const [activeTab, setActiveTab] = useState<AgentTabKey>("technical");

  if (!agents) {
    return (
      <DashboardSection
        icon={Bot}
        title="AI SEO Intelligence"
        description="Specialized AI analysis for technical SEO, content quality, and answer-engine visibility."
      >
        <EmptyState
          icon={Bot}
          title="AI agent analysis not available"
          description="This scan was completed before the multi-agent AI system was added. Run a new scan to see AI-powered insights."
        />
      </DashboardSection>
    );
  }

  const analyses: Record<AgentTabKey, AgentAnalysis> = {
    technical: agents.technical,
    content: agents.content,
    aeo_geo: agents.aeo_geo,
  };

  const currentAnalysis = analyses[activeTab];

  return (
    <DashboardSection
      id="ai-seo-intelligence"
      icon={Bot}
      title="AI SEO Intelligence"
      description="Specialized AI analysis for technical SEO, content quality, and answer-engine visibility."
    >
      <div className="mb-6 border-b border-border">
        <nav className="flex gap-1 -mb-px" role="tablist" aria-label="AI Agent tabs">
          {AGENT_TABS.map((tab) => (
            <button
              key={tab.key}
              role="tab"
              aria-selected={activeTab === tab.key}
              aria-controls={`panel-${tab.key}`}
              id={`tab-${tab.key}`}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 rounded-t-xl px-4 py-3 text-sm font-medium transition ${
                activeTab === tab.key
                  ? "bg-white text-primary border-b-2 border-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div id={`panel-${activeTab}`} role="tabpanel" aria-labelledby={`tab-${activeTab}`}>
        <AgentTabContent analysis={currentAnalysis} />
      </div>

      <div className="mt-6 pt-6 border-t border-border">
        <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-foreground">
          <CheckCircle className="h-5 w-5 text-primary" />
          Validation
        </h3>
        <ValidationDisplay validation={agents.validation} />
      </div>
    </DashboardSection>
  );
}