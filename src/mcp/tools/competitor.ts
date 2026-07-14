/**
 * Competitor Tools — Competitive intelligence and opportunity discovery
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerCompetitorTools(server: McpServer): void {
  server.tool(
    "seo_competitor_compare",
    "Compare your page/site against a competitor. Analyzes: content depth, technical setup, schema markup, performance, multilingual coverage. Returns advantages and gaps.",
    {
      your_url: z.string().url().describe("Your page URL"),
      competitor_url: z.string().url().describe("Competitor page URL"),
    },
    async ({ your_url, competitor_url }) => {
      const result = await runEngine("competitor_compare", { your_url, competitor_url });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_backlink_opportunities",
    "Find backlink opportunities: directories to submit to, guest post targets, resource pages, broken link building targets. Returns prioritized list with outreach plan.",
    {
      domain: z.string().describe("Your domain"),
      niche_keywords: z.array(z.string()).describe("Your niche keywords for guest post discovery"),
      industry: z.string().optional().describe("Your industry (saas, ecommerce, etc.)"),
    },
    async ({ domain, niche_keywords, industry }) => {
      const result = await runEngine("backlink_opportunities", { domain, niche_keywords, industry });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_serp_analyze",
    "Analyze SERP landscape for a keyword. Checks what types of results appear (featured snippets, PAA, images, videos) and what content patterns top-ranking pages use.",
    {
      keyword: z.string().describe("Keyword to analyze SERP for"),
      country: z.string().optional().default("us").describe("Country code for localized results"),
    },
    async ({ keyword, country }) => {
      const result = await runEngine("serp_analyze", { keyword, country });
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
    const proc = spawn("python", [enginePath, command, JSON.stringify(args)], { cwd: path.resolve(__dirname, "../../..") });
    let out = "";
    proc.stdout.on("data", (d: Buffer) => { out += d.toString(); });
    proc.stderr.on("data", (d: Buffer) => { out += d.toString(); });
    proc.on("close", () => resolve(out || "No output"));
    proc.on("error", (e: Error) => resolve(`Error: ${e.message}`));
    setTimeout(() => { proc.kill(); resolve("Timeout"); }, 120000);
  });
}
