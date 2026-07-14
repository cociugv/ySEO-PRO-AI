# ySEO-PRO-AI

**The open-source SEO automation platform that doesn't just audit — it fixes.**

11 real MCP tools for technical SEO, auto-fixing, multilingual intelligence, drift monitoring, AI search readiness, and competitive analysis. Works with Claude, Cursor, Codex, Gemini, Windsurf, and any MCP client.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-1.0-blue.svg)](https://modelcontextprotocol.io)
[![Tests](https://img.shields.io/badge/Tests-113%20passed-green.svg)](#testing)
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

## MCP Tools (11 real implementations)

### Audit
- `seo_audit_page` — Full page audit (30+ checks, all modules)
- `seo_check_indexability` — Robots, meta robots, canonical, X-Robots-Tag

### Auto-Fix
- `seo_fix_auto` — Fix all fixable issues (with dry-run support)
- `seo_fix_schema` — Auto-detect page type + generate JSON-LD
- `seo_fix_hreflang` — Generate complete hreflang tag set

### Analysis
- `seo_score_ai_readiness` — AI Search Readiness Score (0-100)

### Monitoring
- `seo_monitor_baseline` — Capture SEO state snapshot
- `seo_monitor_compare` — Detect drift vs baseline

### Competitor Intelligence
- `seo_competitor_compare` — Side-by-side comparison
- `seo_backlink_opportunities` — Find link building targets

### Publishing
- `seo_indexnow_ping` — Notify search engines instantly (batch support)

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
│         11 tools · Zod validation · Deep adapter         │
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

## Testing

```bash
# Run full test suite (113 tests)
python -m pytest tests/ -v

# Run only benchmark fixtures
python -m pytest tests/test_benchmark.py -v

# Run specific module tests
python -m pytest tests/test_remediation.py -v
```

Test coverage:
- **Parser**: 21 tests (extraction, broken HTML, serialization)
- **Pipeline**: 13 tests (stages, execution, scoring, hooks)
- **Doctor**: 9 tests (fix status honesty, generation, artifacts)
- **Modules**: 22 tests (hreflang, drift, architect, radar, citadel)
- **Operations**: 8 tests (deep module, typed records)
- **Remediation**: 18 tests (state machine, file adapter, integration)
- **Benchmark**: 22 tests (precision/recall against HTML fixtures)

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
