# MCP Tools Reference

ySEO-PRO-AI exposes 40+ SEO tools via Model Context Protocol.

## Audit Tools

| Tool | Description |
|------|-------------|
| `seo_audit_page` | Full single-page SEO audit (30+ checks) |
| `seo_audit_site` | Multi-page site audit via crawling |
| `seo_check_indexability` | Check robots.txt, meta robots, canonical |
| `seo_check_mobile` | Mobile-friendliness analysis |

## Fix Tools (Auto-Remediation)

| Tool | Description |
|------|-------------|
| `seo_fix_auto` | Auto-fix all fixable issues (with dry-run) |
| `seo_fix_meta` | Generate/optimize meta tags |
| `seo_fix_schema` | Auto-generate Schema.org JSON-LD |
| `seo_fix_robots` | Generate optimized robots.txt |
| `seo_fix_sitemap` | Generate XML sitemap from crawl |
| `seo_fix_hreflang` | Generate complete hreflang tag set |

## Analysis Tools

| Tool | Description |
|------|-------------|
| `seo_score_ai_readiness` | AI Search Readiness Score (0-100) |
| `seo_analyze_content` | Content quality + E-E-A-T signals |
| `seo_analyze_keywords` | Keyword placement analysis |
| `seo_analyze_links` | Internal/external link profile |
| `seo_analyze_images` | Image SEO (alt, size, format, lazy) |

## Monitoring Tools

| Tool | Description |
|------|-------------|
| `seo_monitor_baseline` | Capture SEO state snapshot |
| `seo_monitor_compare` | Detect drift vs baseline |
| `seo_monitor_history` | View change history |
| `seo_monitor_alerts` | Get regression alerts |

## Content Tools

| Tool | Description |
|------|-------------|
| `seo_content_brief` | Generate SEO content brief |
| `seo_content_optimize` | Optimize existing content |
| `seo_content_gaps` | Find content gap opportunities |
| `seo_programmatic_pages` | Generate pages at scale (city, vs, usecase) |

## Schema Tools

| Tool | Description |
|------|-------------|
| `seo_schema_validate` | Validate existing JSON-LD |
| `seo_schema_generate` | Auto-generate appropriate schema |
| `seo_schema_faq` | Generate FAQPage schema |

## Multilingual Tools

| Tool | Description |
|------|-------------|
| `seo_hreflang_audit` | Audit hreflang implementation |
| `seo_hreflang_generate` | Generate hreflang tags |
| `seo_locale_detect` | Detect page language |

## Performance Tools

| Tool | Description |
|------|-------------|
| `seo_performance_check` | Page speed analysis |
| `seo_pagespeed` | Google PageSpeed Insights |
| `seo_resource_audit` | Resource optimization audit |

## Competitor Tools

| Tool | Description |
|------|-------------|
| `seo_competitor_compare` | Side-by-side comparison |
| `seo_backlink_opportunities` | Find link building targets |
| `seo_serp_analyze` | SERP landscape analysis |

## Publishing Tools

| Tool | Description |
|------|-------------|
| `seo_indexnow_ping` | Notify search engines instantly |
| `seo_publish_post` | Auto-publish + index |
| `seo_sitemap_submit` | Submit sitemap to engines |

---

## Usage Examples

### Claude Desktop
```
"Audit https://example.com and fix all issues"
"Generate schema markup for my pricing page"
"Compare my SEO with https://competitor.com"
"What's my AI readiness score for https://mysite.com?"
```

### CLI
```bash
python -m src.ops.cli audit https://example.com
python -m src.ops.cli fix https://example.com --dry-run
python -m src.ops.cli ai-score https://example.com
```
