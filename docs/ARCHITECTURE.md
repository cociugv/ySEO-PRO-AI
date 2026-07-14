# Architecture

## Overview

ySEO-PRO-AI uses a dual-layer architecture:

1. **TypeScript MCP Server** — Handles protocol communication, tool registration, input validation (Zod schemas), and client compatibility
2. **Python Analysis Engine** — Performs the actual SEO analysis, crawling, parsing, and fix generation

This separation provides:
- **MCP standard compliance** — TypeScript SDK is the reference implementation
- **Analysis power** — Python excels at HTML parsing, data analysis, and text processing
- **Zero external Python deps** — Engine uses only stdlib (no pip install required)
- **Easy contribution** — Add tools in TS, add analysis in Python

## Data Flow

```
User Query → MCP Client → MCP Server (TS) → Bridge → Python Engine → Result
                                                          ↓
                                              Pipeline (5 stages)
                                                          ↓
                                              Module handlers
```

## Pipeline Architecture

Every SEO operation flows through 5 stages:

```
SCAN → DIAGNOSE → FIX → VERIFY → REPORT
```

- **SCAN**: Fetch URL, parse HTML, extract SEO data
- **DIAGNOSE**: Run checks, identify issues with severity (critical/high/medium/low/info)
- **FIX**: Auto-remediate fixable issues (with dry-run support)
- **VERIFY**: Confirm fixes were applied correctly
- **REPORT**: Generate structured output

Modules register handlers for stages they participate in. The pipeline orchestrates execution order.

## Module System

8 independent modules, each responsible for a domain:

| Module | Stages | Domain |
|--------|--------|--------|
| Inspector | SCAN, DIAGNOSE | Technical SEO (30+ checks) |
| Doctor | FIX | Auto-remediation |
| Polyglot | DIAGNOSE | Multilingual/hreflang |
| Sentinel | SCAN, DIAGNOSE | Drift monitoring |
| Architect | — | Programmatic page generation |
| Publisher | — | Content publishing + indexing |
| Radar | — | Competitor intelligence |
| Citadel | DIAGNOSE | Schema + AI readiness |

## File Structure

```
ySEO-PRO-AI/
├── src/
│   ├── mcp/                    # TypeScript MCP server
│   │   ├── server.ts           # Main server entry point
│   │   ├── tools/              # Tool definitions (10 files, 40+ tools)
│   │   └── resources/          # MCP resources
│   ├── engine/                 # Python ↔ TypeScript bridge
│   │   └── bridge.py           # Command router
│   ├── core/                   # Python core engine
│   │   ├── pipeline.py         # 5-stage pipeline
│   │   ├── fetcher.py          # HTTP with cache + rate limit
│   │   ├── parser.py           # HTML parser (stdlib)
│   │   └── config_loader.py    # YAML config
│   ├── modules/                # 8 analysis modules
│   │   ├── inspector/          # Technical SEO
│   │   ├── doctor/             # Auto-fix
│   │   ├── polyglot/           # Multilingual
│   │   ├── sentinel/           # Drift monitoring
│   │   ├── architect/          # Programmatic SEO
│   │   ├── publisher/          # Publishing + IndexNow
│   │   ├── radar/              # Competitor intel
│   │   └── citadel/            # Schema + AI readiness
│   ├── crew/                   # Agent orchestration
│   ├── ops/                    # CLI operations
│   └── plugins/                # Plugin system
├── config/                     # Configuration
├── docs/                       # Documentation
├── .claude-plugin/             # Claude Code plugin manifest
├── .kiro/steering/             # Kiro integration
├── mcp.json                    # MCP configuration
├── package.json                # Node.js package
└── tsconfig.json               # TypeScript config
```
