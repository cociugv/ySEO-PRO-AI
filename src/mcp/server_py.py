"""
ySEO-PRO-AI — Pure Python MCP Server (no Node.js required)

Implements the Model Context Protocol over stdio using the official Python SDK.
15 SEO tools with real backend implementations.

Compatible with: Claude Desktop, Claude Code, Cursor, Windsurf, any MCP client.

Install: pip install yseo-pro-ai
Run: yseo-mcp (starts stdio server)

Usage in mcp.json:
{
  "mcpServers": {
    "yseo-pro-ai": {
      "command": "yseo-mcp"
    }
  }
}
"""

import sys
import os
import json

# Ensure project root importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

from src.core.operations import SEOOperations

# Initialize
app = Server("yseo-pro-ai")
ops = SEOOperations(project_root=PROJECT_ROOT)


# ─── Tool Definitions ──────────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="seo_audit_page",
        description="Run a comprehensive SEO audit on a URL. Returns score (0-100), issues by severity, fixable count, AI readiness score, and page data.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to audit"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_fix_auto",
        description="Auto-fix all fixable SEO issues. Generates meta tags, schema, canonical, viewport, hreflang. Supports dry-run preview.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fix"},
                "dry_run": {"type": "boolean", "description": "Preview without applying (default: true)", "default": True},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_fix_schema",
        description="Auto-detect page type and generate Schema.org JSON-LD markup (Article, FAQ, Product, Service, WebSite, etc.).",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to generate schema for"},
                "force_type": {"type": "string", "description": "Force schema type or 'auto'", "default": "auto"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_fix_hreflang",
        description="Generate complete hreflang tag set for multilingual pages with x-default and bidirectional references.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Base URL (default language)"},
                "languages": {"type": "array", "items": {"type": "string"}, "description": "Language codes (e.g., ['en','de','fr'])"},
            },
            "required": ["url", "languages"],
        },
    ),
    Tool(
        name="seo_score_ai_readiness",
        description="Calculate AI Search Readiness Score (0-100). Measures citability, entity presence, answer clarity, structure, authority, freshness.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to score"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_monitor_baseline",
        description="Capture SEO baseline snapshot (title, meta, canonical, H1, status, word count, hreflang, schema). Use before changes to detect regressions.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to snapshot"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_monitor_compare",
        description="Compare current SEO state against stored baseline. Detects: title changes, noindex additions, canonical shifts, content reduction, TTFB degradation.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to compare against baseline"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_competitor_compare",
        description="Compare your page against a competitor. Returns metrics, advantages, and gaps in content, speed, schema, multilingual coverage.",
        inputSchema={
            "type": "object",
            "properties": {
                "your_url": {"type": "string", "description": "Your page URL"},
                "competitor_url": {"type": "string", "description": "Competitor URL"},
            },
            "required": ["your_url", "competitor_url"],
        },
    ),
    Tool(
        name="seo_backlink_opportunities",
        description="Find backlink opportunities: directories, guest post targets. Returns prioritized weekly outreach plan.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Your domain"},
                "niche_keywords": {"type": "array", "items": {"type": "string"}, "description": "Keywords for guest post discovery"},
            },
            "required": ["domain"],
        },
    ),
    Tool(
        name="seo_indexnow_ping",
        description="Ping IndexNow to notify search engines (Bing, Yandex, Seznam, Naver) of new/updated URLs. Batch up to 10,000.",
        inputSchema={
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "URLs to submit"},
                "key": {"type": "string", "description": "IndexNow API key (optional, uses config)"},
            },
            "required": ["urls"],
        },
    ),
    Tool(
        name="seo_content_brief",
        description="Generate SEO content brief: target keywords, suggested outline (H2s), word count, schema recommendation, internal link suggestions.",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic or seed keyword"},
                "content_type": {"type": "string", "enum": ["blog", "landing", "product", "comparison", "guide", "faq"], "default": "blog"},
                "language": {"type": "string", "default": "en"},
            },
            "required": ["topic"],
        },
    ),
    Tool(
        name="seo_programmatic_pages",
        description="Generate programmatic SEO page specs at scale: city pages, comparison pages, use case pages. Returns titles, meta, H1, content blocks.",
        inputSchema={
            "type": "object",
            "properties": {
                "page_type": {"type": "string", "enum": ["city", "comparison", "usecase"]},
                "brand_name": {"type": "string"},
                "data": {"type": "array", "items": {"type": "object"}, "description": "Data for pages (e.g., [{name:'Berlin',country:'Germany'}])"},
            },
            "required": ["page_type", "brand_name", "data"],
        },
    ),
    Tool(
        name="seo_crawl_site",
        description="Crawl a website with persistent frontier. Discovers pages via sitemap + internal links. Returns page inventory, duplicates, broken pages. Resumes after interruption.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Homepage URL"},
                "max_pages": {"type": "integer", "default": 50, "description": "Max pages to crawl"},
                "max_depth": {"type": "integer", "default": 3, "description": "Max link depth"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_pagespeed",
        description="Run Google PageSpeed Insights. Returns Lighthouse score, Core Web Vitals (LCP, INP, CLS, FCP, TTFB), optimization opportunities.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to test"},
                "strategy": {"type": "string", "enum": ["mobile", "desktop"], "default": "mobile"},
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="seo_report_html",
        description="Generate self-contained HTML audit report. Professional design, shareable as single file. Includes score, issues, page data, AI readiness.",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to audit and report"},
            },
            "required": ["url"],
        },
    ),
]


# ─── Tool Handlers ─────────────────────────────────────────────────────────

def handle_tool(name: str, arguments: dict) -> str:
    """Route tool call to SEOOperations method."""
    handlers = {
        "seo_audit_page": lambda a: ops.audit(a["url"]),
        "seo_fix_auto": lambda a: ops.fix(a["url"], dry_run=a.get("dry_run", True)),
        "seo_fix_schema": lambda a: ops.generate_schema(a["url"], a.get("force_type", "auto")),
        "seo_fix_hreflang": lambda a: ops.generate_hreflang(a["url"], a.get("languages", ["en"])),
        "seo_score_ai_readiness": lambda a: ops.ai_readiness(a["url"]),
        "seo_monitor_baseline": lambda a: ops.monitor_baseline(a["url"]),
        "seo_monitor_compare": lambda a: ops.monitor_compare(a["url"]),
        "seo_competitor_compare": lambda a: ops.competitor_compare(a["your_url"], a["competitor_url"]),
        "seo_backlink_opportunities": lambda a: ops.backlink_opportunities(a["domain"], a.get("niche_keywords", [])),
        "seo_indexnow_ping": lambda a: ops.indexnow_ping(a.get("urls", []), a.get("key", "")),
        "seo_content_brief": lambda a: ops.content_brief(a["topic"], a.get("content_type", "blog"), a.get("language", "en")),
        "seo_programmatic_pages": lambda a: ops.programmatic_pages(a["page_type"], a["brand_name"], a.get("data", []), a.get("languages")),
        "seo_crawl_site": lambda a: ops.crawl_site(a["url"], a.get("max_pages", 50), a.get("max_depth", 3)),
        "seo_pagespeed": lambda a: ops.pagespeed(a["url"], a.get("strategy", "mobile")),
        "seo_report_html": lambda a: ops.report_html(a["url"]),
    }

    handler = handlers.get(name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = handler(arguments)
        return json.dumps(result.to_dict(), indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── MCP Protocol Handlers ─────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result_text = handle_tool(name, arguments)
    return [TextContent(type="text", text=result_text)]


# ─── Entry Point ───────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def run():
    """Entry point for `yseo-mcp` command."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run()
