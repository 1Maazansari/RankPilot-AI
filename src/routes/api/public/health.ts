import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api/public/health")({
  server: {
    handlers: {
      GET: async () =>
        Response.json(
          {
            status: "ok",
            service: "rankpilot-ai",
            ai: process.env["LOVABLE_API_KEY"] ? "configured" : "unavailable",
            time: new Date().toISOString(),
          },
          { headers: { "cache-control": "no-store" } },
        ),
    },
  },
});