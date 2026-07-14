/**
 * Multilingual Tools — International SEO intelligence
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function registerMultilingualTools(server: McpServer): void {
  server.tool(
    "seo_hreflang_audit",
    "Audit hreflang implementation on a page. Checks: tag validity, bidirectional references, x-default presence, language code correctness (ISO 639-1), and missing languages. Returns issues and a complete fix.",
    {
      url: z.string().url().describe("URL to audit hreflang tags"),
      expected_languages: z.array(z.string()).optional().describe("Languages your site supports"),
    },
    async ({ url, expected_languages }) => {
      const result = await runEngine("hreflang_audit", { url, expected_languages });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_hreflang_generate",
    "Generate complete hreflang tag set for a multilingual page. Creates properly formatted alternate tags with self-referencing and x-default.",
    {
      base_url: z.string().url().describe("Default language version URL"),
      languages: z.array(z.string()).describe("All language codes (e.g., ['en','de','fr','ro','ru'])"),
      url_pattern: z.enum(["subdirectory", "subdomain", "cctld"]).optional().default("subdirectory"),
    },
    async ({ base_url, languages, url_pattern }) => {
      const result = await runEngine("hreflang_generate", { base_url, languages, url_pattern });
      return { content: [{ type: "text", text: result }] };
    }
  );

  server.tool(
    "seo_locale_detect",
    "Detect page language and validate locale configuration. Checks HTML lang attribute, Content-Language header, URL structure, and content patterns.",
    {
      url: z.string().url().describe("URL to detect locale for"),
    },
    async ({ url }) => {
      const result = await runEngine("locale_detect", { url });
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
