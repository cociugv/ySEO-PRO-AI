/**
 * Fix Tools — Auto-remediation for SEO issues
 *
 * What makes ySEO-PRO-AI unique: not just audit, but AUTO-FIX.
 *
 * Tools:
 * - seo_fix_auto: Auto-fix all fixable issues on a page
 * - seo_fix_meta: Generate/fix meta tags
 * - seo_fix_schema: Generate appropriate schema markup
 * - seo_fix_robots: Generate robots.txt
 * - seo_fix_sitemap: Generate XML sitemap
 * - seo_fix_hreflang: Generate hreflang tags
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerFixTools(server: McpServer): void {
  server.tool(
    "seo_fix_auto",
    "Automatically fix all detectable SEO issues on a page. Scans the page, identifies fixable problems, and generates corrected HTML/meta tags. Supports dry-run mode to preview changes without applying.",
    {
      url: z.string().url().describe("URL to fix"),
      dry_run: z.boolean().optional().default(true).describe("Preview fixes without applying (default: true)"),
      categories: z.array(z.string()).optional().describe("Limit to specific fix categories"),
    },
    async ({ url, dry_run, categories }) => {
      const result = await runEngine("fix_auto", { url, dry_run, categories });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_fix_meta",
    "Generate or optimize meta tags (title, description, Open Graph, Twitter Card) for a URL. Analyzes existing content and generates SEO-optimized tags.",
    {
      url: z.string().url().describe("URL to generate meta for"),
      target_keywords: z.array(z.string()).optional().describe("Target keywords to include"),
      brand_name: z.string().optional().describe("Brand name to append to title"),
    },
    async ({ url, target_keywords, brand_name }) => {
      const result = await runEngine("fix_meta", { url, target_keywords, brand_name });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_fix_schema",
    "Auto-detect page type and generate appropriate Schema.org JSON-LD markup. Supports: Article, Product, FAQ, Service, SoftwareApplication, Organization, WebSite, BreadcrumbList, HowTo, LocalBusiness.",
    {
      url: z.string().url().describe("URL to generate schema for"),
      force_type: z.enum([
        "auto", "Article", "Product", "FAQ", "Service",
        "SoftwareApplication", "Organization", "WebSite",
        "BreadcrumbList", "HowTo", "LocalBusiness"
      ]).optional().default("auto").describe("Force a specific schema type (default: auto-detect)"),
      organization_name: z.string().optional().describe("Organization name for publisher info"),
    },
    async ({ url, force_type, organization_name }) => {
      const result = await runEngine("fix_schema", { url, force_type, organization_name });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_fix_robots",
    "Generate an optimized robots.txt file for a domain. Analyzes site structure to determine appropriate allow/disallow rules and includes sitemap reference.",
    {
      domain: z.string().describe("Domain to generate robots.txt for (e.g., example.com)"),
      sitemap_url: z.string().optional().describe("Custom sitemap URL"),
      block_paths: z.array(z.string()).optional().describe("Additional paths to block"),
    },
    async ({ domain, sitemap_url, block_paths }) => {
      const result = await runEngine("fix_robots", { domain, sitemap_url, block_paths });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_fix_sitemap",
    "Generate an XML sitemap by crawling a website. Discovers pages via internal links and produces a valid sitemap with lastmod, changefreq, and priority.",
    {
      url: z.string().url().describe("Homepage URL to crawl"),
      max_pages: z.number().optional().default(200).describe("Max pages to include"),
      include_images: z.boolean().optional().default(false).describe("Include image sitemap entries"),
    },
    async ({ url, max_pages, include_images }) => {
      const result = await runEngine("fix_sitemap", { url, max_pages, include_images });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_fix_hreflang",
    "Generate complete hreflang tag set for multilingual pages. Validates language codes, creates bidirectional references, and includes x-default.",
    {
      url: z.string().url().describe("Base URL (default language version)"),
      languages: z.array(z.string()).describe("Language codes to generate (e.g., ['en', 'de', 'fr', 'ro'])"),
      url_pattern: z.enum(["subdirectory", "subdomain", "parameter"]).optional().default("subdirectory")
        .describe("URL pattern for alternate versions"),
    },
    async ({ url, languages, url_pattern }) => {
      const result = await runEngine("fix_hreflang", { url, languages, url_pattern });
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
    const proc = spawn("python", [enginePath, command, JSON.stringify(args)], {
      cwd: path.resolve(__dirname, "../../.."),
    });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d: Buffer) => { stdout += d.toString(); });
    proc.stderr.on("data", (d: Buffer) => { stderr += d.toString(); });
    proc.on("close", (code: number) => {
      resolve(code === 0 ? stdout : `Error: ${stderr || stdout}`);
    });
    proc.on("error", (e: Error) => resolve(`Engine error: ${e.message}`));
    setTimeout(() => { proc.kill(); resolve("Timeout"); }, 120000);
  });
}
