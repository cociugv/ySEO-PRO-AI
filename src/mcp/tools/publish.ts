/**
 * Publish Tools — IndexNow instant indexing
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerPublishTools(server: McpServer): void {
  server.tool(
    "seo_indexnow_ping",
    "Ping IndexNow to notify search engines of new/updated URLs. Supports batch (up to 10,000).",
    {
      urls: z.array(z.string().url()).describe("URLs to submit for indexing"),
      key: z.string().optional().describe("IndexNow API key (uses config if not provided)"),
    },
    async ({ urls, key }) => engineToMcpContent("indexnow_ping", { urls, key: key || "" })
  );
}
