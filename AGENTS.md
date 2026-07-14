# ySEO-PRO-AI

AI-powered SEO automation that audits, fixes, and grows organic traffic.
Built for multilingual SaaS by Vadim Cociug / yLink.pro

## Quick Commands

| Command | Description |
|---------|-------------|
| `python -m src.ops.cli scan <url>` | Quick scan (fetch + parse) |
| `python -m src.ops.cli audit <url>` | Full SEO audit (30+ checks) |
| `python -m src.ops.cli fix <url>` | Auto-fix detected issues |
| `python -m src.ops.cli fix <url> --dry-run` | Preview fixes without applying |
| `python -m src.ops.cli ai-score <url>` | AI Search Readiness Score |

## Architecture

**Pipeline-based:** SCAN → DIAGNOSE → FIX → VERIFY → REPORT

**8 Modules:**
- `inspector` — Technical SEO scanner
- `doctor` — Auto-fix engine
- `sentinel` — Drift monitoring & alerts
- `polyglot` — Multilingual SEO (14 languages)
- `architect` — Programmatic page generator
- `publisher` — Blog API + IndexNow
- `radar` — Competitor intelligence
- `citadel` — Schema auto-injection + AI readiness

**6 Crew Agents:**
- `inspector` — Technical analysis
- `doctor` — Auto-fix
- `polyglot` — Multilingual
- `sentinel` — Drift monitor
- `publisher` — Publish + index
- `strategist` — Competitor + opportunities

## Key Files

```
src/core/pipeline.py      — Pipeline engine (5 stages)
src/core/fetcher.py       — HTTP with cache + rate limit
src/core/parser.py        — HTML parser (stdlib only)
src/core/config_loader.py — YAML config + env vars
src/ops/cli.py            — CLI entry point
src/crew/orchestrator.py  — Agent orchestration
config/default.yaml       — Default configuration
```

## Configuration

Edit `config/default.yaml` for settings. Key sections:
- `targets.languages` — Site languages (14 configured)
- `modules.*` — Enable/disable modules
- `integrations.*` — API keys and endpoints

## Principles

1. **Fix, don't just audit** — Every issue has an auto-fix path
2. **Multilingual first** — Always consider hreflang (14 languages)
3. **Pipeline is king** — All ops flow through 5 stages
4. **Zero external deps** — Core uses Python stdlib only
5. **Config over code** — YAML config drives behavior
