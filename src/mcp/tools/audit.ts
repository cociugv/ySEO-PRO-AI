/**
 * Audit Tools — Technical SEO scanning and diagnostics
 *
 * Each tool has a dedicated engine implementation.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerAuditTools(server: McpServer): void {
  server.tool(
    "seo_audit_page",
    "Run a comprehensive SEO audit on a single page. Returns issues with severity levels and auto-fix suggestions.",
    {
      url: z.string().url().describe("The URL to audit"),
    },
    async ({ url }) => engineToMcpContent("audit_page", { url })
  );

  server.tool(
    "seo_check_indexability",
    "Check if a URL can be indexed by search engines. Analyzes robots.txt, meta robots, canonical, X-Robots-Tag header.",
    {
      url: z.string().url().describe("URL to check"),
    },
    async ({ url }) => engineToMcpContent("check_indexability", { url })
  );
}
