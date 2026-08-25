import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";
import type { AnalyzeResult } from "./report-types";

const AnalyzeInput = z.object({ url: z.string().min(3).max(2048) });
const ChatInput = z.object({
  question: z.string().min(1).max(2000),
  context: z.string().max(8000).optional(),
});

export const analyzeSite = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => AnalyzeInput.parse(input))
  .handler(async ({ data }): Promise<AnalyzeResult> => {
    // 1. Primary path — the project's FastAPI backend: POST /scan
    const { scanViaBackend } = await import("./backend.server");
    const result = await scanViaBackend(data.url);
    if (result.ok || result.code !== "offline") {
      return result as AnalyzeResult;
    }

    // 2. Backend not reachable from this environment — run the in-app crawler
    //    so the product still returns a real (never mocked) audit.
    const { analyzeWebsite } = await import("./analyze.server");
    const local = await analyzeWebsite(data.url);
    if (local.ok) {
      local.report.aiNotice =
        local.report.aiNotice ??
        "The RankX API (POST /scan) is not reachable from this environment — this report was produced by the built-in crawler. Set RANKX_API_URL to your running backend to use it.";
    }
    return local;
  });

export const getBackendHealth = createServerFn({ method: "GET" }).handler(async () => {
  const { backendHealth } = await import("./backend.server");
  return backendHealth();
});

export const askCopilot = createServerFn({ method: "POST" })
  .inputValidator((input: unknown) => ChatInput.parse(input))
  .handler(async ({ data }) => {
    const { copilotReply } = await import("./analyze.server");
    return copilotReply(data.question, data.context ?? "");
  });