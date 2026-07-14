/**
 * ySEO-PRO-AI — MCP Server
 *
 * Model Context Protocol server providing SEO tools with real implementations.
 * Compatible with: Claude Desktop, Claude Code, Cursor, Codex, Gemini, Windsurf.
 *
 * Tools are registered only when they have a dedicated backend implementation.
 * Interface = behavior — no false contracts.
 *
 * @author Vadim Cociug <vadim@ylink.pro>
 * @license MIT
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { registerAuditTools } from "./tools/audit.js";
import { registerFixTools } from "./tools/fix.js";
import { registerAnalyzeTools } from "./tools/analyze.js";
import { registerMonitorTools } from "./tools/monitor.js";
import { registerCompetitorTools } from "./tools/competitor.js";
import { registerPublishTools } from "./tools/publish.js";
import { registerContentTools } from "./tools/content.js";
import { registerCrawlTools } from "./tools/crawl.js";

const server = new McpServer({
  name: "yseo-pro-ai",
  version: "1.0.0",
});

// Only tools with real, dedicated implementations
registerAuditTools(server);       // seo_audit_page, seo_check_indexability
registerFixTools(server);         // seo_fix_auto, seo_fix_schema, seo_fix_hreflang
registerAnalyzeTools(server);     // seo_score_ai_readiness
registerMonitorTools(server);     // seo_monitor_baseline, seo_monitor_compare
registerCompetitorTools(server);  // seo_competitor_compare, seo_backlink_opportunities
registerPublishTools(server);     // seo_indexnow_ping
registerContentTools(server);     // seo_content_brief, seo_programmatic_pages
registerCrawlTools(server);       // seo_crawl_site, seo_pagespeed

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("ySEO-PRO-AI MCP server running (15 tools)");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
