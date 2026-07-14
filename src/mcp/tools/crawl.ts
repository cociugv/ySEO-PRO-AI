/**
 * Crawl Tools — Site crawling and performance
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { engineToMcpContent } from "../adapter.js";

export function registerCrawlTools(server: McpServer): void {
  server.tool(
    "seo_crawl_site",
    "Crawl a website discovering pages via sitemap and internal links. Returns crawl stats, page inventory, duplicates, and broken pages. Supports resume after interruption.",
    {
      url: z.string().url().describe("Homepage or sitemap URL"),
      max_pages: z.number().optional().default(50).describe("Max pages to crawl (1-500)"),
      max_depth: z.number().optional().default(3).describe("Max link depth (1-10)"),
    },
    async ({ url, max_pages, max_depth }) =>
      engineToMcpContent("crawl_site", { url, max_pages, max_depth })
  );

  server.tool(
    "seo_pagespeed",
    "Run Google PageSpeed Insights on a URL. Returns Lighthouse performance score, Core Web Vitals (LCP, INP, CLS), and optimization opportunities.",
    {
      url: z.string().url().describe("URL to test"),
      strategy: z.enum(["mobile", "desktop"]).optional().default("mobile").describe("Test strategy"),
    },
    async ({ url, strategy }) =>
      engineToMcpContent("pagespeed", { url, strategy })
  );

  server.tool(
    "seo_report_html",
    "Generate a self-contained HTML audit report for a URL. Beautiful, professional, shareable.",
    {
      url: z.string().url().describe("URL to audit and report on"),
    },
    async ({ url }) =>
      engineToMcpContent("report_html", { url })
  );
}
