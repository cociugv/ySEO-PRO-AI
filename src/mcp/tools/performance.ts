/**
 * Performance Tools — Core Web Vitals and speed analysis
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerPerformanceTools(server: McpServer): void {
  server.tool(
    "seo_performance_check",
    "Check page performance metrics: TTFB, total page size, number of requests, render-blocking resources, and estimated Core Web Vitals indicators.",
    {
      url: z.string().url().describe("URL to check"),
    },
    async ({ url }) => {
      const result = await runEngine("performance_check", { url });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_pagespeed",
    "Run Google PageSpeed Insights API for a URL. Returns Lighthouse scores, Core Web Vitals (LCP, FID/INP, CLS), and optimization opportunities.",
    {
      url: z.string().url().describe("URL to test"),
      strategy: z.enum(["mobile", "desktop"]).optional().default("mobile").describe("Test strategy"),
      api_key: z.string().optional().describe("Google API key (optional, uses free tier)"),
    },
    async ({ url, strategy, api_key }) => {
      const result = await runEngine("pagespeed", { url, strategy, api_key });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_resource_audit",
    "Audit page resources for SEO performance impact: unused CSS/JS, render-blocking scripts, uncompressed assets, missing cache headers, oversized images.",
    {
      url: z.string().url().describe("URL to audit resources"),
    },
    async ({ url }) => {
      const result = await runEngine("resource_audit", { url });
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
    const proc = spawn("python", [enginePath, command, JSON.stringify(args)], { cwd: path.resolve(__dirname, "../../..") });
    let out = "";
    proc.stdout.on("data", (d: Buffer) => { out += d.toString(); });
    proc.stderr.on("data", (d: Buffer) => { out += d.toString(); });
    proc.on("close", () => resolve(out || "No output"));
    proc.on("error", (e: Error) => resolve(`Error: ${e.message}`));
    setTimeout(() => { proc.kill(); resolve("Timeout"); }, 120000);
  });
}
