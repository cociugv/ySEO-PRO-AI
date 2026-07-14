/**
 * Schema Tools — Structured data generation and validation
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerSchemaTools(server: McpServer): void {
  server.tool(
    "seo_schema_validate",
    "Validate existing Schema.org JSON-LD on a page. Checks syntax, required fields, Google rich result eligibility, and common errors.",
    { url: z.string().url().describe("URL to validate schema on") },
    async ({ url }) => {
      const result = await runEngine("schema_validate", { url });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_schema_generate",
    "Generate Schema.org JSON-LD markup based on page type auto-detection. Supports: Article, FAQ, HowTo, Product, SoftwareApplication, Organization, WebSite, BreadcrumbList, LocalBusiness, Service, Event, Recipe, VideoObject.",
    {
      url: z.string().url().describe("URL to generate schema for"),
      type: z.string().optional().describe("Force schema type (default: auto-detect from content)"),
      include_breadcrumb: z.boolean().optional().default(true).describe("Also generate BreadcrumbList"),
    },
    async ({ url, type, include_breadcrumb }) => {
      const result = await runEngine("schema_generate", { url, type, include_breadcrumb });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_schema_faq",
    "Generate FAQPage schema from a list of questions and answers. Outputs valid JSON-LD ready to paste into HTML.",
    {
      questions: z.array(z.object({
        question: z.string(),
        answer: z.string(),
      })).describe("Array of Q&A pairs"),
      page_url: z.string().url().optional().describe("Page URL for mainEntity"),
    },
    async ({ questions, page_url }) => {
      const result = await runEngine("schema_faq", { questions, page_url });
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
