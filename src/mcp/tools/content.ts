/**
 * Content Tools — SEO content generation and optimization
 *
 * Tools:
 * - seo_content_brief: Generate SEO content brief
 * - seo_content_optimize: Optimize existing content for SEO
 * - seo_content_gaps: Find content gap opportunities
 * - seo_programmatic_pages: Generate programmatic page specs at scale
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerContentTools(server: McpServer): void {
  server.tool(
    "seo_content_brief",
    "Generate a comprehensive SEO content brief for a topic. Includes: target keywords, search intent, suggested outline (H1/H2/H3), word count target, internal linking suggestions, schema type, competitor references, and content angle.",
    {
      topic: z.string().describe("Topic or seed keyword for the brief"),
      target_audience: z.string().optional().describe("Who is the content for"),
      content_type: z.enum(["blog", "landing", "product", "comparison", "guide", "faq"]).optional()
        .default("blog").describe("Type of content to brief"),
      language: z.string().optional().default("en").describe("Content language"),
    },
    async ({ topic, target_audience, content_type, language }) => {
      const result = await runEngine("content_brief", { topic, target_audience, content_type, language });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_content_optimize",
    "Analyze and optimize existing content for SEO. Checks keyword placement, heading structure, internal links, readability, and suggests improvements. Can generate optimized meta tags and schema.",
    {
      url: z.string().url().describe("URL of content to optimize"),
      target_keywords: z.array(z.string()).describe("Target keywords to optimize for"),
      suggestions_only: z.boolean().optional().default(true).describe("Only suggest changes (don't rewrite)"),
    },
    async ({ url, target_keywords, suggestions_only }) => {
      const result = await runEngine("content_optimize", { url, target_keywords, suggestions_only });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_content_gaps",
    "Identify content gap opportunities by analyzing your site against competitors. Finds topics/keywords competitors rank for that you don't cover.",
    {
      your_domain: z.string().describe("Your domain"),
      competitor_domains: z.array(z.string()).describe("Competitor domains to compare against"),
      max_opportunities: z.number().optional().default(20).describe("Max opportunities to return"),
    },
    async ({ your_domain, competitor_domains, max_opportunities }) => {
      const result = await runEngine("content_gaps", { your_domain, competitor_domains, max_opportunities });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_programmatic_pages",
    "Generate programmatic SEO page specifications at scale. Creates templated pages for: city/location pages, comparison pages (vs competitors), use case pages, integration pages. Outputs page specs with title, meta, H1, content blocks, and schema.",
    {
      page_type: z.enum(["city", "comparison", "usecase", "integration", "feature"]).describe("Type of pages to generate"),
      brand_name: z.string().describe("Your brand name"),
      data: z.array(z.record(z.string())).describe("Data for each page (e.g., [{name:'Berlin',country:'Germany'}])"),
      languages: z.array(z.string()).optional().describe("Generate in multiple languages"),
      base_url: z.string().optional().describe("Base URL for the pages"),
    },
    async ({ page_type, brand_name, data, languages, base_url }) => {
      const result = await runEngine("programmatic_pages", { page_type, brand_name, data, languages, base_url });
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
