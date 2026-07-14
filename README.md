# ySEO-PRO-AI

**The open-source SEO automation platform that doesn't just audit — it fixes.**

40+ MCP tools for technical SEO, content optimization, multilingual intelligence, drift monitoring, AI search readiness, and programmatic page generation. Works with Claude, Cursor, Codex, Gemini, Windsurf, and any MCP client.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-1.0-blue.svg)](https://modelcontextprotocol.io)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

---

## Why ySEO-PRO-AI?

| | Traditional SEO Tools | Audit-Only MCP Servers | **ySEO-PRO-AI** |
|--|----------------------|------------------------|-----------------|
| Audit | Reports in dashboard | Lists issues | Finds issues |
| Fix | Manual work | Manual work | **Auto-fixes** |
| AI Search | Not covered | Basic | **AI Readiness Score** |
| Multilingual | Basic hreflang check | Not covered | **14-language intelligence** |
| Monitoring | Separate tool | Not covered | **Built-in drift alerts** |
| Programmatic | Not covered | Not covered | **City/vs/usecase generator** |
| Indexing | Manual submission | Not covered | **IndexNow auto-ping** |
| Cost | $100-500/month | Free (limited) | **Free + extensible** |

---

## Quick Start

### Install as MCP Server (Claude / Cursor / Windsurf)

```json
{
  "mcpServers": {
    "yseo-pro-ai": {
      "command": "npx",
      "args": ["-y", "yseo-pro-ai"]
    }
  }
}
```

### Install from Source

```bash
git clone https://github.com/cociugv/ySEO-PRO-AI.git
cd ySEO-PRO-AI
npm install
```

Then ask your AI assistant: *"Audit https://example.com for SEO issues and fix them"*

---

## 40+ SEO Tools

### Audit & Fix
- `seo_audit_page` — Full page audit (30+ checks)
- `seo_audit_site` — Crawl and audit entire site
- `seo_fix_auto` — **Auto-fix all fixable issues**
- `seo_fix_meta` — Generate optimized meta tags
- `seo_fix_schema` — Auto-inject schema markup
- `seo_fix_robots` — Generate robots.txt
- `seo_fix_sitemap` — Generate XML sitemap
- `seo_fix_hreflang` — Generate hreflang tags

### AI & Content
- `seo_score_ai_readiness` — AI Search Readiness (0-100)
- `seo_content_brief` — SEO content briefs
- `seo_content_optimize` — Optimize existing content
- `seo_programmatic_pages` — Generate pages at scale

### Monitoring & Intelligence
- `seo_monitor_baseline` — Capture SEO snapshot
- `seo_monitor_compare` — Detect regressions
- `seo_competitor_compare` — Compare vs competitors
- `seo_backlink_opportunities` — Find link targets

### Publishing & Indexing
- `seo_indexnow_ping` — Instant index notification
- `seo_publish_post` — Auto-publish + ping
- `seo_sitemap_submit` — Submit to search engines

[See all 40+ tools →](docs/TOOLS.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Clients                           │
│  Claude Desktop · Cursor · Codex · Gemini · Windsurf    │
└────────────────────────┬────────────────────────────────┘
                         │ stdio (MCP Protocol)
┌────────────────────────▼────────────────────────────────┐
│              TypeScript MCP Server                       │
│         40+ tools · Zod validation · Resources          │
└────────────────────────┬────────────────────────────────┘
                         │ subprocess bridge
┌────────────────────────▼────────────────────────────────┐
│              Python Analysis Engine                      │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Inspector │ │ Doctor   │ │Polyglot  │ │Sentinel  │  │
│  │(audit)   │ │(auto-fix)│ │(i18n)    │ │(drift)   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Architect │ │Publisher │ │ Radar    │ │Citadel   │  │
│  │(pages)   │ │(publish) │ │(compete) │ │(schema)  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  Pipeline: SCAN → DIAGNOSE → FIX → VERIFY → REPORT     │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Fix, don't just audit** — Every diagnosed issue has an auto-fix path
2. **MCP-native** — First-class MCP server, works with any compatible client
3. **Zero-config start** — Works out of the box, configure only what you need
4. **Multilingual by default** — Built for international sites (14+ languages)
5. **AI-search aware** — Optimizes for Google AI Overviews, ChatGPT, Perplexity
6. **Plugin-extensible** — Add custom tools, integrations, and data sources
7. **Privacy-first** — Runs locally, no data sent to third parties

---

## Platform Compatibility

| Platform | Integration | Setup |
|----------|-------------|-------|
| **Claude Desktop** | MCP server (stdio) | Add to mcp.json |
| **Claude Code** | MCP + Skills + Agents | Plugin auto-discovery |
| **Cursor** | MCP server | Add to .cursor/mcp.json |
| **Kiro CLI** | Steering rules + MCP | Open project in Kiro |
| **Windsurf** | MCP server | Add to configuration |
| **Codex CLI** | Python CLI | `python -m src.ops.cli` |
| **Gemini Code Assist** | Python CLI | Direct execution |
| **n8n / Zapier** | HTTP bridge | Via MCP HTTP transport |
| **Any MCP client** | stdio transport | Standard MCP protocol |

---

## CLI Usage

```bash
# Quick page scan
python -m src.ops.cli scan https://example.com

# Full audit with all modules
python -m src.ops.cli audit https://example.com

# Auto-fix (preview)
python -m src.ops.cli fix https://example.com --dry-run

# Auto-fix (apply)
python -m src.ops.cli fix https://example.com

# AI Search Readiness Score
python -m src.ops.cli ai-score https://example.com
```

---

## Configuration

Edit `config/default.yaml`:

```yaml
targets:
  primary_domain: "example.com"
  languages: [en, de, fr, es, ro]

modules:
  doctor:
    auto_fix: true
    dry_run: false
  sentinel:
    snapshot_interval_hours: 24
  publisher:
    indexnow_key: "your-key"
```

Environment variables (`.env`):
```
INDEXNOW_KEY=your-key
PAGESPEED_API_KEY=optional
GSC_CREDENTIALS_JSON=optional
```

---

## Modules

| Module | Purpose | Key Feature |
|--------|---------|-------------|
| **Inspector** | Technical SEO scanner | 30+ diagnostic checks |
| **Doctor** | Auto-fix engine | Generates fixes, not just reports |
| **Polyglot** | Multilingual SEO | Hreflang audit + generation |
| **Sentinel** | Drift monitoring | Snapshot comparison + alerts |
| **Architect** | Programmatic SEO | City/comparison/usecase pages |
| **Publisher** | Content publishing | Blog API + IndexNow ping |
| **Radar** | Competitor intel | Compare + backlink opportunities |
| **Citadel** | Schema + AI readiness | Auto-inject + scoring |

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas:
- New MCP tools
- Additional fix prescriptions
- Integration plugins (Ahrefs, Semrush, etc.)
- Translations for multilingual content templates
- Documentation improvements

---

## License

MIT License — [Vadim Cociug](https://github.com/cociugv)

---

## Links

- [Documentation](docs/)
- [Installation Guide](docs/INSTALLATION.md)
- [Tools Reference](docs/TOOLS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Plugin Development](docs/PLUGINS.md)
