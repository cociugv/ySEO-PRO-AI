/**
 * Publish Tools — Content publishing and instant indexing
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerPublishTools(server: McpServer): void {
  server.tool(
    "seo_indexnow_ping",
    "Ping IndexNow to notify search engines of new or updated URLs. Supports batch submission (up to 10,000 URLs). Notifies Bing, Yandex, Seznam, and Naver simultaneously.",
    {
      urls: z.array(z.string().url()).describe("URLs to submit for indexing"),
      key: z.string().optional().describe("IndexNow API key (uses config if not provided)"),
    },
    async ({ urls, key }) => {
      const result = await runEngine("indexnow_ping", { urls, key });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_publish_post",
    "Publish a blog post via API and automatically ping IndexNow for instant indexing. Supports WordPress REST API and custom endpoints.",
    {
      title: z.string().describe("Post title"),
      content: z.string().describe("Post content (HTML or Markdown)"),
      slug: z.string().optional().describe("URL slug"),
      meta_description: z.string().optional().describe("Meta description"),
      language: z.string().optional().default("en").describe("Content language"),
      tags: z.array(z.string()).optional().describe("Post tags"),
      category: z.string().optional().describe("Post category"),
      api_url: z.string().optional().describe("Blog API endpoint URL"),
    },
    async ({ title, content, slug, meta_description, language, tags, category, api_url }) => {
      const result = await runEngine("publish_post", {
        title, content, slug, meta_description, language, tags, category, api_url
      });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_sitemap_submit",
    "Submit sitemap URL to Google and Bing for crawling. Also pings IndexNow with all URLs from the sitemap.",
    {
      sitemap_url: z.string().url().describe("Sitemap URL to submit"),
      engines: z.array(z.enum(["google", "bing", "yandex"])).optional().default(["google", "bing"])
        .describe("Search engines to notify"),
    },
    async ({ sitemap_url, engines }) => {
      const result = await runEngine("sitemap_submit", { sitemap_url, engines });
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
