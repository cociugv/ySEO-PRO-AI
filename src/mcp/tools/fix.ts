/**
 * Fix Tools — Auto-remediation for SEO issues
 *
 * Each tool has a dedicated engine implementation.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerFixTools(server: McpServer): void {
  server.tool(
    "seo_fix_auto",
    "Auto-fix all detectable SEO issues on a page. Supports dry-run mode.",
    {
      url: z.string().url().describe("URL to fix"),
      dry_run: z.boolean().optional().default(true).describe("Preview fixes without applying"),
    },
    async ({ url, dry_run }) => engineToMcpContent("fix_auto", { url, dry_run })
  );

  server.tool(
    "seo_fix_schema",
    "Auto-detect page type and generate appropriate Schema.org JSON-LD markup.",
    {
      url: z.string().url().describe("URL to generate schema for"),
      force_type: z.string().optional().default("auto").describe("Force schema type or auto-detect"),
    },
    async ({ url, force_type }) => engineToMcpContent("generate_schema", { url, force_type })
  );

  server.tool(
    "seo_fix_hreflang",
    "Generate complete hreflang tag set for multilingual pages.",
    {
      url: z.string().url().describe("Base URL (default language version)"),
      languages: z.array(z.string()).describe("Language codes (e.g., ['en','de','fr'])"),
    },
    async ({ url, languages }) => engineToMcpContent("generate_hreflang", { url, languages })
  );
}
