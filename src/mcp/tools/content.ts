/**
 * Content Tools — SEO content generation (real implementations)
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerContentTools(server: McpServer): void {
  server.tool(
    "seo_content_brief",
    "Generate an SEO content brief: target keywords, search intent, suggested outline, word count target, internal linking suggestions, schema type recommendation.",
    {
      topic: z.string().describe("Topic or seed keyword"),
      content_type: z.enum(["blog", "landing", "product", "comparison", "guide", "faq"]).optional()
        .default("blog").describe("Content type"),
      language: z.string().optional().default("en").describe("Content language"),
    },
    async ({ topic, content_type, language }) =>
      engineToMcpContent("content_brief", { topic, content_type, language })
  );

  server.tool(
    "seo_programmatic_pages",
    "Generate programmatic SEO page specifications at scale: city pages, comparison pages, use case pages. Returns titles, meta descriptions, H1s, content blocks, and schema types.",
    {
      page_type: z.enum(["city", "comparison", "usecase"]).describe("Type of pages"),
      brand_name: z.string().describe("Your brand name"),
      data: z.array(z.record(z.string())).describe("Data array (e.g., [{name:'Berlin',country:'Germany'}])"),
      languages: z.array(z.string()).optional().describe("Generate multilingual versions"),
    },
    async ({ page_type, brand_name, data, languages }) =>
      engineToMcpContent("programmatic_pages", { page_type, brand_name, data, languages })
  );
}
