/**
 * Analyze Tools — Deep SEO analysis and scoring
 *
 * Tools:
 * - seo_score_ai_readiness: AI Search Readiness Score (GEO/AEO)
 * - seo_analyze_content: Content quality and E-E-A-T analysis
 * - seo_analyze_keywords: Keyword density and placement analysis
 * - seo_analyze_links: Internal/external link profile analysis
 * - seo_analyze_images: Image SEO analysis (alt, size, format, lazy)
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerAnalyzeTools(server: McpServer): void {
  server.tool(
    "seo_score_ai_readiness",
    "Calculate AI Search Readiness Score (0-100). Measures how well a page performs in AI search engines (Google AI Overviews, ChatGPT, Perplexity). Evaluates: citability, entity presence, answer clarity, structure, authority signals, and freshness.",
    {
      url: z.string().url().describe("URL to score"),
    },
    async ({ url }) => {
      const result = await runEngine("ai_readiness_score", { url });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_analyze_content",
    "Analyze content quality and E-E-A-T signals. Checks: word count, readability, heading structure, expertise signals, freshness indicators, unique value, and thin content detection.",
    {
      url: z.string().url().describe("URL to analyze"),
      target_keyword: z.string().optional().describe("Primary target keyword for relevance scoring"),
    },
    async ({ url, target_keyword }) => {
      const result = await runEngine("analyze_content", { url, target_keyword });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_analyze_keywords",
    "Analyze keyword usage and placement on a page. Checks: title, H1, first paragraph, URL, meta description, heading distribution, and keyword density.",
    {
      url: z.string().url().describe("URL to analyze"),
      keywords: z.array(z.string()).describe("Keywords to check placement for"),
    },
    async ({ url, keywords }) => {
      const result = await runEngine("analyze_keywords", { url, keywords });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_analyze_links",
    "Analyze internal and external link profile of a page. Checks: link count, anchor text distribution, broken links, nofollow usage, link equity flow.",
    {
      url: z.string().url().describe("URL to analyze"),
      check_broken: z.boolean().optional().default(false).describe("Also check for broken links (slower)"),
    },
    async ({ url, check_broken }) => {
      const result = await runEngine("analyze_links", { url, check_broken });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_analyze_images",
    "Analyze image SEO on a page. Checks: alt text presence, file sizes, modern formats (WebP/AVIF), lazy loading, responsive images, and image sitemap eligibility.",
    {
      url: z.string().url().describe("URL to analyze"),
    },
    async ({ url }) => {
      const result = await runEngine("analyze_images", { url });
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
