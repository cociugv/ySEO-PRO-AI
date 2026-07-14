/**
 * Competitor Tools — Competitive intelligence
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerCompetitorTools(server: McpServer): void {
  server.tool(
    "seo_competitor_compare",
    "Compare your page against a competitor. Returns advantages and gaps in content, performance, schema, multilingual coverage.",
    {
      your_url: z.string().url().describe("Your page URL"),
      competitor_url: z.string().url().describe("Competitor page URL"),
    },
    async ({ your_url, competitor_url }) =>
      engineToMcpContent("competitor_compare", { your_url, competitor_url })
  );

  server.tool(
    "seo_backlink_opportunities",
    "Find backlink opportunities: directories, guest post targets. Returns prioritized outreach plan.",
    {
      domain: z.string().describe("Your domain"),
      niche_keywords: z.array(z.string()).optional().default([]).describe("Niche keywords for discovery"),
    },
    async ({ domain, niche_keywords }) =>
      engineToMcpContent("backlink_opportunities", { domain, keywords: niche_keywords })
  );
}
