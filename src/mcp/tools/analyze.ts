/**
 * Analyze Tools — Deep SEO analysis and scoring
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerAnalyzeTools(server: McpServer): void {
  server.tool(
    "seo_score_ai_readiness",
    "Calculate AI Search Readiness Score (0-100). Measures citability, entity presence, answer clarity, structure, authority, freshness.",
    {
      url: z.string().url().describe("URL to score"),
    },
    async ({ url }) => engineToMcpContent("ai_readiness", { url })
  );
}
