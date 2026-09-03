import { useEffect, useRef, useState } from "react";
import { Bot, Send, X, Sparkles, MessageSquare, AlertTriangle } from "lucide-react";
import { useServerFn } from "@tanstack/react-start";
import { askCopilot } from "@/lib/analyze.functions";

type Msg = { role: "user" | "assistant"; content: string; error?: boolean };

const QUICK_PROMPTS = [
  "Explain my biggest issue",
  "Improve my title tag",
  "Generate a meta description",
  "What should I fix first?",
];

export function AIChatPanel({ context = "" }: { context?: string }) {
  const [open, setOpen] = useState(false);
  const ask = useServerFn(askCopilot);
  const [pending, setPending] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      content:
        "Hi — I'm the BrandVizi AI copilot. Ask me anything about your SEO report, or pick a prompt below.",
    },
  ]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, open, pending]);

  useEffect(() => {
    if (open && !pending) inputRef.current?.focus();
  }, [open, pending]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || pending) return;
    setMessages((m) => [...m, { role: "user", content: trimmed }]);
    setInput("");
    setPending(true);
    try {
      const res = await ask({ data: { question: trimmed, context } });
      setMessages((m) =>
        res.ok
          ? [...m, { role: "assistant", content: res.reply }]
          : [...m, { role: "assistant", content: res.message, error: true }],
      );
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Network error reaching the copilot. Please try again.", error: true },
      ]);
    } finally {
      setPending(false);
    }
  }

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-50 inline-flex items-center gap-2 rounded-full bg-[image:var(--gradient-primary)] px-5 py-3.5 text-sm font-semibold text-white shadow-[var(--shadow-glow)] transition hover:-translate-y-0.5 active:scale-[.98]"
          aria-label="Open AI assistant"
        >
          <MessageSquare className="h-4 w-4" />
          Ask AI
        </button>
      )}

      {open && (
        <div className="fixed bottom-6 right-6 z-50 flex h-[560px] w-[calc(100vw-3rem)] max-w-sm flex-col overflow-hidden rounded-3xl border border-border bg-white shadow-[0_24px_60px_-20px_oklch(0.5_0.05_260_/_0.3)]">
          <div className="flex items-center justify-between border-b border-border bg-[image:var(--gradient-primary)] px-5 py-4 text-white">
            <div className="flex items-center gap-2.5">
              <div className="grid h-8 w-8 place-items-center rounded-lg bg-white/20 backdrop-blur">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <div className="text-sm font-semibold">BrandVizi Copilot</div>
                <div className="text-[11px] text-white/80">Online · AI powered</div>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="grid h-8 w-8 place-items-center rounded-lg text-white/80 transition hover:bg-white/15"
              aria-label="Close chat"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto bg-secondary/40 p-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : m.error
                        ? "border border-destructive/30 bg-destructive/5 text-destructive"
                        : "border border-border bg-white text-foreground"
                  }`}
                >
                  {m.error && <AlertTriangle className="mr-1.5 inline h-3.5 w-3.5 align-[-2px]" />}
                  <span className="whitespace-pre-wrap">{m.content}</span>
                </div>
              </div>
            ))}
            {pending && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1.5 rounded-2xl border border-border bg-white px-4 py-3">
                  {[0, 150, 300].map((d) => (
                    <span
                      key={d}
                      className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary/60"
                      style={{ animationDelay: `${d}ms` }}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-border bg-white p-3">
            <div className="mb-2 flex flex-wrap gap-1.5">
              {QUICK_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => void send(p)}
                  disabled={pending}
                  className="inline-flex items-center gap-1 rounded-full border border-border bg-secondary px-2.5 py-1 text-[11px] font-medium text-foreground transition hover:border-primary/40 hover:bg-accent hover:text-primary disabled:opacity-50"
                >
                  <Sparkles className="h-3 w-3" /> {p}
                </button>
              ))}
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void send(input);
              }}
              className="flex items-center gap-2 rounded-xl border border-border bg-secondary px-3 py-2 focus-within:border-primary/50 focus-within:ring-4 focus-within:ring-primary/10"
            >
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your report…"
                className="min-w-0 flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground/70"
              />
              <button
                type="submit"
                disabled={pending}
                className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[image:var(--gradient-primary)] text-white transition hover:brightness-110 disabled:opacity-50"
                aria-label="Send"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}