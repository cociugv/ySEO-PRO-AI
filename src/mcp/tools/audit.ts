/**
 * Audit Tools — Technical SEO scanning and diagnostics
 *
 * Tools:
 * - seo_audit_page: Full single-page SEO audit
 * - seo_audit_site: Multi-page site audit
 * - seo_check_indexability: Check if a page can be indexed
 * - seo_check_mobile: Mobile-friendliness check
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerAuditTools(server: McpServer): void {
  // Full page SEO audit
  server.tool(
    "seo_audit_page",
    "Run a comprehensive SEO audit on a single page. Checks title, meta, headings, links, images, schema, security headers, performance indicators, and more. Returns issues with severity levels and auto-fix suggestions.",
    {
      url: z.string().url().describe("The URL to audit"),
      depth: z.number().optional().default(1).describe("How many levels of internal links to follow (1-3)"),
      include_screenshots: z.boolean().optional().default(false).describe("Capture visual rendering"),
    },
    async ({ url, depth, include_screenshots }) => {
      // Delegate to Python engine
      const result = await runPythonEngine("audit_page", { url, depth, include_screenshots });
      return {
        content: [{ type: "text", text: result }],
      };
    }
  );

  // Full site audit
  server.tool(
    "seo_audit_site",
    "Crawl and audit an entire website. Discovers pages via sitemap and internal links, then runs technical SEO checks on each. Returns a prioritized list of issues across the whole site.",
    {
      url: z.string().url().describe("Homepage or sitemap URL to start crawling"),
      max_pages: z.number().optional().default(50).describe("Maximum pages to crawl (1-500)"),
      categories: z.array(z.enum([
        "technical", "content", "performance", "security",
        "multilingual", "schema", "images", "links"
      ])).optional().describe("Which audit categories to run (default: all)"),
    },
    async ({ url, max_pages, categories }) => {
      const result = await runPythonEngine("audit_site", { url, max_pages, categories });
      return {
        content: [{ type: "text", text: result }],
      };
    }
  );

  // Indexability check
  server.tool(
    "seo_check_indexability",
    "Check if a URL can be indexed by search engines. Analyzes robots.txt, meta robots, canonical, X-Robots-Tag header, and sitemap inclusion.",
    {
      url: z.string().url().describe("URL to check"),
    },
    async ({ url }) => {
      const result = await runPythonEngine("check_indexability", { url });
      return {
        content: [{ type: "text", text: result }],
      };
    }
  );

  // Mobile friendliness
  server.tool(
    "seo_check_mobile",
    "Analyze a page for mobile-friendliness issues. Checks viewport meta, responsive design indicators, tap target sizes, font sizes, and content width.",
    {
      url: z.string().url().describe("URL to check"),
    },
    async ({ url }) => {
      const result = await runPythonEngine("check_mobile", { url });
      return {
        content: [{ type: "text", text: result }],
      };
    }
  );
}

/**
 * Bridge to Python analysis engine
 */
async function runPythonEngine(command: string, args: Record<string, unknown>): Promise<string> {
  const { spawn } = await import("child_process");
  const path = await import("path");
  const { fileURLToPath } = await import("url");

  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const enginePath = path.resolve(__dirname, "../../engine/bridge.py");

  return new Promise((resolve, reject) => {
    const proc = spawn("python", [enginePath, command, JSON.stringify(args)], {
      cwd: path.resolve(__dirname, "../../.."),
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data: Buffer) => { stdout += data.toString(); });
    proc.stderr.on("data", (data: Buffer) => { stderr += data.toString(); });

    proc.on("close", (code: number) => {
      if (code === 0) {
        resolve(stdout || "Command completed successfully");
      } else {
        resolve(`Error (exit ${code}): ${stderr || stdout || "Unknown error"}`);
      }
    });

    proc.on("error", (err: Error) => {
      resolve(`Failed to run engine: ${err.message}`);
    });

    // Timeout after 120s
    setTimeout(() => {
      proc.kill();
      resolve("Operation timed out after 120 seconds");
    }, 120000);
  });
}
