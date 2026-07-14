/**
 * Monitor Tools — SEO drift detection and alerting
 *
 * Tools:
 * - seo_monitor_baseline: Capture SEO baseline snapshot
 * - seo_monitor_compare: Compare current state vs baseline
 * - seo_monitor_history: View drift history over time
 * - seo_monitor_alerts: Get active regression alerts
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerMonitorTools(server: McpServer): void {
  server.tool(
    "seo_monitor_baseline",
    "Capture an SEO baseline snapshot for a URL. Stores: title, meta, canonical, H1, status code, response time, hreflang count, schema count, word count. Use this before making changes to detect regressions later.",
    {
      url: z.string().url().describe("URL to snapshot"),
    },
    async ({ url }) => {
      const result = await runEngine("monitor_baseline", { url });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_monitor_compare",
    "Compare current SEO state against stored baseline. Detects: title changes, noindex additions, canonical shifts, content reduction, response time degradation, hreflang removal, and more. Returns severity-rated changes.",
    {
      url: z.string().url().describe("URL to compare"),
    },
    async ({ url }) => {
      const result = await runEngine("monitor_compare", { url });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_monitor_history",
    "View drift history for a URL over time. Shows all captured snapshots and detected changes chronologically.",
    {
      url: z.string().url().describe("URL to check history for"),
      limit: z.number().optional().default(30).describe("Max snapshots to return"),
    },
    async ({ url, limit }) => {
      const result = await runEngine("monitor_history", { url, limit });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_monitor_alerts",
    "Get active SEO regression alerts across all monitored URLs. Shows critical/high severity changes that need immediate attention.",
    {
      severity: z.enum(["all", "critical", "high", "medium"]).optional().default("high")
        .describe("Minimum severity to show"),
    },
    async ({ severity }) => {
      const result = await runEngine("monitor_alerts", { severity });
      return { content: [{ type: "text", text: result }] };
    }
  );
}

async function runEngine(command: string, args: Record<string, unknown>): Promise<string> {
  const { spawn } = await import("child_process");
  const path = await import("path");
  const { fileURLToPath } = await import("url");
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const enginePath = path.resolve(__dirname, "../../engine/bridge.py");
  return new Promise((resolve) => {
    const proc = spawn("python", [enginePath, command, JSON.stringify(args)], {
      cwd: path.resolve(__dirname, "../../.."),
    });
    let out = "";
    proc.stdout.on("data", (d: Buffer) => { out += d.toString(); });
    proc.stderr.on("data", (d: Buffer) => { out += d.toString(); });
    proc.on("close", () => resolve(out || "No output"));
    proc.on("error", (e: Error) => resolve(`Error: ${e.message}`));
    setTimeout(() => { proc.kill(); resolve("Timeout"); }, 120000);
  });
}
