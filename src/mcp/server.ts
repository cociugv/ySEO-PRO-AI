/**
 * ySEO-PRO-AI — MCP Server
 *
 * A Model Context Protocol server providing 40+ SEO tools.
 * Compatible with: Claude Desktop, Claude Code, Cursor, Codex, Gemini, Windsurf.
 *
 * Architecture:
 * - Tools: Individual SEO operations (audit, fix, analyze, generate)
 * - Resources: SEO data sources (snapshots, configs, reports)
 *
 * @author Vadim Cociug <vadim@ylink.pro>
 * @license MIT
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Import tool handlers
import { registerAuditTools } from "./tools/audit.js";
import { registerFixTools } from "./tools/fix.js";
import { registerAnalyzeTools } from "./tools/analyze.js";
import { registerMonitorTools } from "./tools/monitor.js";
import { registerContentTools } from "./tools/content.js";
import { registerSchemaTools } from "./tools/schema.js";
import { registerMultilingualTools } from "./tools/multilingual.js";
import { registerPerformanceTools } from "./tools/performance.js";
import { registerCompetitorTools } from "./tools/competitor.js";
import { registerPublishTools } from "./tools/publish.js";

// Create server instance
const server = new McpServer({
  name: "yseo-pro-ai",
  version: "1.0.0",
});

// Register all tool groups
registerAuditTools(server);
registerFixTools(server);
registerAnalyzeTools(server);
registerMonitorTools(server);
registerContentTools(server);
registerSchemaTools(server);
registerMultilingualTools(server);
registerPerformanceTools(server);
registerCompetitorTools(server);
registerPublishTools(server);

// Start server with stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("ySEO-PRO-AI MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
