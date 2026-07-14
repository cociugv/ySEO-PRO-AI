# ySEO-PRO-AI

**AI-powered SEO automation that audits, fixes, and grows your organic traffic.**
Built for multilingual SaaS by [Vadim Cociug](https://ylink.pro).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Kiro%20%7C%20Claude%20Code%20%7C%20Cursor-purple.svg)](#compatibility)

---

## What Makes ySEO-PRO-AI Different

| Feature | Typical SEO Tools | ySEO-PRO-AI |
|---------|-------------------|-------------|
| Audit | Report problems | **Audit + Auto-Fix** |
| Multilingual | Basic hreflang check | **14-language intelligence** |
| Content | Manual publishing | **Auto-publish + IndexNow ping** |
| Monitoring | Manual checks | **Continuous drift alerts** |
| AI Search | Not covered | **AI Readiness Score** |
| Programmatic | Not covered | **City/comparison page generator** |
| Competitors | Manual research | **Automated tracking** |

---

## Architecture

```
ySEO-PRO-AI/
├── src/
│   ├── core/                    # Engine + Pipeline + Parser + Fetcher
│   │   ├── pipeline.py          # 5-stage pipeline (Scan→Diagnose→Fix→Verify→Report)
│   │   ├── fetcher.py           # HTTP fetcher with cache + rate limiting
│   │   ├── parser.py            # HTML parser (stdlib only, no BS4)
│   │   └── config_loader.py     # YAML config with env var expansion
│   ├── modules/
│   │   ├── inspector/           # Technical SEO scanner (crawl, index, speed, security)
│   │   ├── doctor/              # Auto-fix engine (generates fixes, not just reports)
│   │   ├── sentinel/            # SEO drift monitoring & alerts
│   │   ├── polyglot/            # Multilingual SEO (hreflang audit + generation)
│   │   ├── architect/           # Programmatic page generator (city, vs, usecase)
│   │   ├── publisher/           # Blog auto-publish + IndexNow instant indexing
│   │   ├── radar/               # Competitor intelligence + backlink opportunities
│   │   └── citadel/             # Schema auto-injection + AI Search Readiness Score
│   ├── ops/                     # CLI operations
│   ├── crew/                    # AI agent definitions
│   ├── plugins/                 # Plugin system (auto-discovery)
│   └── templates/               # Report templates
├── config/                      # Configuration files
├── reports/                     # Generated reports (gitignored)
├── .yseo/                       # Runtime data (cache, snapshots)
└── .kiro/steering/              # Kiro CLI integration
```

---

## Quick Start

### Installation

```bash
git clone https://github.com/YOUR-USERNAME/ySEO-PRO-AI.git
cd ySEO-PRO-AI
cp config/.env.example .env
# Edit .env with your API keys
```

**Requirements:** Python 3.10+ (standard library only — no pip install needed for core features)

### Basic Usage

```bash
# Quick scan
python -m src.ops.cli scan https://ylink.pro

# Full audit with issue detection
python -m src.ops.cli audit https://ylink.pro

# Auto-fix detected issues (dry run)
python -m src.ops.cli fix https://ylink.pro --dry-run

# Auto-fix for real
python -m src.ops.cli fix https://ylink.pro

# AI Search Readiness Score
python -m src.ops.cli ai-score https://ylink.pro
```

---

## Modules

### INSPECTOR — Technical SEO Scanner
Crawls your site and detects 30+ technical SEO issues across categories:
- HTTP status, redirects, TTFB
- Title, meta description, H1 validation
- Canonical, viewport, robots
- HTTPS, security headers
- Structured data presence
- Content length (thin content detection)

### DOCTOR — Auto-Fix Engine
**Not just auditing — fixing.** For every fixable issue, Doctor generates:
- Missing meta tags (title, description)
- robots.txt content
- XML sitemaps
- Schema.org markup (JSON-LD)
- Canonical tags
- Hreflang tags for all configured languages

### POLYGLOT — Multilingual SEO Intelligence
Built for sites like yLink.pro with 14 languages:
- Hreflang audit (validates all tags)
- Missing language detection
- x-default validation
- Return tag verification (bidirectional)
- URL strategy detection (subdirectory/subdomain/ccTLD)
- Locale-content consistency

### SENTINEL — SEO Drift Monitoring
Takes snapshots and alerts on regressions:
- Title/description changes
- noindex additions (CRITICAL alert)
- Canonical changes
- Status code changes
- Content reduction (> 20% word drop)
- Response time degradation
- Hreflang/schema count changes

### ARCHITECT — Programmatic SEO Generator
Creates pages at scale:
- **City pages** — "URL Shortener in Berlin/Paris/Tokyo"
- **Comparison pages** — "yLink vs Bitly"
- **Use case pages** — "URL Shortener for Social Media"
- **Multilingual generation** — All pages in 14 languages

### PUBLISHER — Auto-Publish + IndexNow
- Publishes to blog API (yLink.pro, WordPress, custom)
- Pings IndexNow immediately after publish
- Supports batch URL submission (up to 10,000 URLs)
- Notifies all engines: Bing, Yandex, Seznam, Naver

### RADAR — Competitor Intelligence
- Scan competitor SEO profiles
- Side-by-side metric comparison
- Backlink opportunity finder (directories, guest posts)
- Weekly outreach plan generation

### CITADEL — Schema + AI Readiness
- Auto-detects page type (article, product, FAQ, service, software)
- Generates appropriate schema markup
- **AI Search Readiness Score** (0-100) measuring:
  - Citability
  - Entity presence
  - Answer clarity
  - Content structure
  - Authority signals
  - Freshness

---

## Pipeline Philosophy

Every operation flows through 5 stages:

```
SCAN → DIAGNOSE → FIX → VERIFY → REPORT
```

1. **SCAN** — Fetch pages, parse HTML, collect raw data
2. **DIAGNOSE** — Analyze data, identify issues with severity levels
3. **FIX** — Auto-remediate fixable issues (with backup + dry-run)
4. **VERIFY** — Confirm fixes were applied correctly
5. **REPORT** — Generate actionable output (HTML/JSON/Markdown)

Modules register handlers for one or more stages. The pipeline orchestrates execution.

---

## Compatibility

| Tool | Status | Integration |
|------|--------|-------------|
| **Kiro CLI** | Full | `.kiro/steering/` rules |
| **Claude Code** | Full | Agents + Skills pattern |
| **Cursor** | Full | Custom commands |
| **VS Code** | Partial | Terminal-based |
| **CLI** | Full | `python -m src.ops.cli` |

---

## Configuration

Edit `config/default.yaml` for global settings. Create `config/local.yaml` for overrides (gitignored).

Key settings:
- `targets.languages` — Your site's language list
- `modules.doctor.auto_fix` — Enable/disable auto-fixing
- `modules.doctor.dry_run` — Preview fixes without applying
- `integrations.indexnow.key` — Your IndexNow API key

Environment variables (`YSEO_*` prefix) override config file values.

---

## License

MIT License — Vadim Cociug / [yLink.pro](https://ylink.pro)

---

## Author

**Vadim Cociug**
- Website: [ylink.pro](https://ylink.pro)
- Project: ySEO-PRO-AI
- Focus: Multilingual SaaS SEO automation
