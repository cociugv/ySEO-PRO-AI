/**
 * Monitor Tools — SEO drift detection and alerting
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerMonitorTools(server: McpServer): void {
  server.tool(
    "seo_monitor_baseline",
    "Capture an SEO baseline snapshot for a URL. Stores title, meta, canonical, H1, status, hreflang count, schema count, word count.",
    {
      url: z.string().url().describe("URL to snapshot"),
    },
    async ({ url }) => engineToMcpContent("monitor_baseline", { url })
  );

  server.tool(
    "seo_monitor_compare",
    "Compare current SEO state against stored baseline. Detects title changes, noindex additions, canonical shifts, content reduction.",
    {
      url: z.string().url().describe("URL to compare"),
    },
    async ({ url }) => engineToMcpContent("monitor_compare", { url })
  );
}
