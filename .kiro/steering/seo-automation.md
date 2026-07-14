# ySEO-PRO-AI — Kiro Steering Rules

## Project Context

This is **ySEO-PRO-AI**, an AI-powered SEO automation platform built for multilingual SaaS sites.
Author: Vadim Cociug / yLink.pro

## Architecture

- **Pipeline-based**: Every operation flows through SCAN → DIAGNOSE → FIX → VERIFY → REPORT
- **Modular**: 8 independent modules (inspector, doctor, sentinel, polyglot, architect, publisher, radar, citadel)
- **Zero external deps**: Core uses only Python stdlib (no pip install needed)
- **Config-driven**: YAML config with env var expansion

## Commands

When the user asks for SEO operations, use the CLI:

| Task | Command |
|------|---------|
| Quick scan | `python -m src.ops.cli scan <url>` |
| Full audit | `python -m src.ops.cli audit <url>` |
| Auto-fix | `python -m src.ops.cli fix <url>` |
| Dry-run fix | `python -m src.ops.cli fix <url> --dry-run` |
| AI readiness | `python -m src.ops.cli ai-score <url>` |

## Module Usage

- **Inspector**: Technical SEO checks (title, meta, H1, canonical, speed, security)
- **Doctor**: Auto-generates fixes (meta tags, robots.txt, sitemap, schema)
- **Polyglot**: Multilingual hreflang audit and generation (14 languages)
- **Sentinel**: Drift monitoring (snapshots + comparison + alerts)
- **Architect**: Programmatic page generation (city, comparison, usecase pages)
- **Publisher**: Blog API publishing + IndexNow instant indexing
- **Radar**: Competitor tracking + backlink opportunities
- **Citadel**: Schema auto-injection + AI Search Readiness Score

## Key Principles

1. **Fix, don't just audit** — Every diagnosed issue should have an auto-fix path
2. **Multilingual first** — yLink.pro has 14 languages, always consider hreflang
3. **Pipeline is king** — All operations go through the 5-stage pipeline
4. **No external deps** — Core modules use only Python standard library
5. **Config over code** — Behavior is controlled via YAML config, not hardcoded
