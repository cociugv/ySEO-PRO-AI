"""
Engine Bridge — Connects TypeScript MCP server to Python analysis engine.

Called by MCP tools via subprocess. Receives command + args JSON,
executes the appropriate engine function, outputs result as JSON.

Usage: python bridge.py <command> <args_json>
"""

import sys
import os
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.pipeline import PipelineRunner, Stage, PipelineContext
from src.core.fetcher import PageFetcher
from src.core.parser import parse_html
from src.core.config_loader import load_config


def cmd_audit_page(args: dict) -> dict:
    """Full single-page SEO audit."""
    url = args["url"]
    config = load_config(PROJECT_ROOT)

    from src.modules.inspector.scanner import TechnicalScanner
    from src.modules.inspector.checks import run_all_checks
    from src.modules.citadel.schema_engine import SchemaEngine
    from src.modules.citadel.ai_readiness import AIReadinessScorer
    from src.modules.polyglot.hreflang import HreflangAuditor
    from src.modules.polyglot.locale import LocaleDetector

    pipeline = PipelineRunner(config)
    TechnicalScanner(config.get("modules", {}).get("inspector", {})).register(pipeline)
    SchemaEngine(config.get("modules", {}).get("citadel", {})).register(pipeline)
    AIReadinessScorer().register(pipeline)

    languages = config.get("targets", {}).get("languages", ["en"])
    HreflangAuditor({"languages": languages}).register(pipeline)
    LocaleDetector({"languages": languages}).register(pipeline)

    ctx = pipeline.execute(url, stages=[Stage.SCAN, Stage.DIAGNOSE])
    run_all_checks(ctx)

    return {
        "url": url,
        "score": ctx.score,
        "issues_count": len(ctx.issues),
        "fixable_count": sum(1 for i in ctx.issues if i.fix_available),
        "issues": [i.to_dict() for i in ctx.issues],
        "page_data": ctx.scan_data.get("page", {}),
        "ai_readiness": ctx.scan_data.get("ai_readiness", {}),
        "elapsed_seconds": ctx.elapsed_seconds,
    }


def cmd_fix_auto(args: dict) -> dict:
    """Auto-fix all fixable issues."""
    url = args["url"]
    dry_run = args.get("dry_run", True)
    config = load_config(PROJECT_ROOT)

    from src.modules.inspector.scanner import TechnicalScanner
    from src.modules.doctor.fixer import AutoFixer

    pipeline = PipelineRunner(config)
    TechnicalScanner(config.get("modules", {}).get("inspector", {})).register(pipeline)

    fix_config = config.get("modules", {}).get("doctor", {})
    fix_config["dry_run"] = dry_run
    AutoFixer(fix_config).register(pipeline)

    ctx = pipeline.execute(url, stages=[Stage.SCAN, Stage.DIAGNOSE, Stage.FIX])

    return {
        "url": url,
        "dry_run": dry_run,
        "issues_found": len(ctx.issues),
        "fixes_applied": len(ctx.fixes_applied),
        "fixes": ctx.fixes_applied,
        "remaining": [i.to_dict() for i in ctx.issues if not i.fix_applied],
    }


def cmd_fix_schema(args: dict) -> dict:
    """Generate schema markup for a page."""
    url = args["url"]
    force_type = args.get("force_type", "auto")

    fetcher = PageFetcher()
    result = fetcher.fetch(url)
    if not result.ok:
        return {"error": f"Cannot fetch URL: HTTP {result.status_code}"}

    page = parse_html(result.body, url)

    from src.modules.citadel.schema_engine import SchemaEngine
    engine = SchemaEngine({"site_name": args.get("organization_name", "")})

    if force_type == "auto":
        detected_type = engine.detect_page_type(url, page.to_dict())
    else:
        detected_type = force_type.lower()

    schema = engine.generate_schema(detected_type, url, page.to_dict())

    return {
        "detected_type": detected_type,
        "schema": schema,
        "json_ld": f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>',
    }


def cmd_fix_hreflang(args: dict) -> dict:
    """Generate hreflang tag set."""
    from src.modules.polyglot.hreflang import HreflangAuditor

    url = args["url"]
    languages = args.get("languages", ["en"])

    auditor = HreflangAuditor({"languages": languages})
    tags = auditor.generate_hreflang_set(url, languages)

    return {
        "url": url,
        "languages": languages,
        "tag_count": len(languages) + 1,  # +1 for x-default
        "html": tags,
    }


def cmd_ai_readiness_score(args: dict) -> dict:
    """Calculate AI Search Readiness Score."""
    url = args["url"]

    fetcher = PageFetcher()
    result = fetcher.fetch(url)
    if not result.ok:
        return {"error": f"Cannot fetch URL: HTTP {result.status_code}"}

    page = parse_html(result.body, url)

    from src.modules.citadel.ai_readiness import AIReadinessScorer
    scorer = AIReadinessScorer()
    report = scorer.calculate_score(url, page.to_dict())

    return report.to_dict()


def cmd_monitor_baseline(args: dict) -> dict:
    """Capture SEO baseline snapshot."""
    url = args["url"]

    fetcher = PageFetcher()
    result = fetcher.fetch(url, use_cache=False)
    if not result.ok:
        return {"error": f"Cannot fetch: HTTP {result.status_code}"}

    page = parse_html(result.body, url)

    from src.modules.sentinel.snapshot import SnapshotManager
    manager = SnapshotManager()
    snapshot = manager.capture(url, page.to_dict(), {
        "status_code": result.status_code,
        "elapsed_ms": result.elapsed_ms,
    })

    return {"message": f"Baseline captured for {url}", "snapshot": snapshot.to_dict()}


def cmd_monitor_compare(args: dict) -> dict:
    """Compare current state vs baseline."""
    url = args["url"]

    fetcher = PageFetcher()
    result = fetcher.fetch(url, use_cache=False)
    if not result.ok:
        return {"error": f"Cannot fetch: HTTP {result.status_code}"}

    page = parse_html(result.body, url)

    from src.modules.sentinel.snapshot import SnapshotManager
    from src.modules.sentinel.comparator import DriftComparator

    manager = SnapshotManager()
    current = manager.capture(url, page.to_dict(), {
        "status_code": result.status_code,
        "elapsed_ms": result.elapsed_ms,
    })

    baseline = manager.get_baseline(url)
    if not baseline or baseline.timestamp == current.timestamp:
        return {"message": "No previous baseline to compare against", "current": current.to_dict()}

    comparator = DriftComparator()
    report = comparator.compare(baseline, current)

    return report.to_dict()


def cmd_hreflang_audit(args: dict) -> dict:
    """Audit hreflang implementation."""
    url = args["url"]
    expected = args.get("expected_languages", [])

    fetcher = PageFetcher()
    result = fetcher.fetch(url)
    if not result.ok:
        return {"error": f"Cannot fetch: HTTP {result.status_code}"}

    page = parse_html(result.body, url)

    from src.modules.polyglot.hreflang import HreflangAuditor
    config = {"languages": expected} if expected else {}
    auditor = HreflangAuditor(config)

    ctx = PipelineContext(target_url=url)
    ctx.scan_data["page"] = page.to_dict()
    ctx.scan_data["page"]["hreflang_tags"] = [
        {"lang": t["lang"], "url": t["url"]} for t in page.hreflang_tags
    ]

    auditor.audit_hreflang(ctx)

    return {
        "url": url,
        "hreflang_found": len(page.hreflang_tags),
        "issues": [i.to_dict() for i in ctx.issues],
    }


def cmd_competitor_compare(args: dict) -> dict:
    """Compare against competitor."""
    from src.modules.radar.tracker import CompetitorTracker
    tracker = CompetitorTracker()
    comparison = tracker.compare(args["your_url"], args["competitor_url"])

    return {
        "your_url": args["your_url"],
        "competitor_url": args["competitor_url"],
        "metrics": {k: {"yours": v[0], "theirs": v[1]} for k, v in comparison.metrics.items()},
        "advantages": comparison.advantages,
        "disadvantages": comparison.disadvantages,
    }


def cmd_backlink_opportunities(args: dict) -> dict:
    """Find backlink opportunities."""
    from src.modules.radar.opportunities import BacklinkFinder
    finder = BacklinkFinder({"industry": args.get("industry", "saas")})

    directories = finder.find_directories(args["domain"])
    guest_posts = finder.find_guest_post_targets(args.get("niche_keywords", []))
    all_opps = directories + guest_posts
    plan = finder.generate_outreach_plan(all_opps)

    return {
        "total_opportunities": len(all_opps),
        "directories": len(directories),
        "guest_post_queries": len(guest_posts),
        "plan": plan,
    }


def cmd_programmatic_pages(args: dict) -> dict:
    """Generate programmatic page specs."""
    from src.modules.architect.generator import ProgrammaticGenerator
    gen = ProgrammaticGenerator({
        "brand_name": args.get("brand_name", ""),
        "base_url": args.get("base_url", ""),
        "languages": args.get("languages", ["en"]),
    })

    page_type = args["page_type"]
    data = args.get("data", [])

    if page_type == "city":
        pages = gen.generate_city_pages(data)
    elif page_type == "comparison":
        pages = gen.generate_comparison_pages(data)
    elif page_type == "usecase":
        pages = gen.generate_usecase_pages(data)
    else:
        pages = gen.generate_city_pages(data)

    return {
        "page_type": page_type,
        "pages_generated": len(pages),
        "specs": [p.to_dict() for p in pages[:20]],
    }


def cmd_indexnow_ping(args: dict) -> dict:
    """Ping IndexNow with URLs."""
    from src.modules.publisher.indexnow import IndexNowPinger
    config = load_config(PROJECT_ROOT)

    pinger_config = config.get("integrations", {}).get("indexnow", {})
    if args.get("key"):
        pinger_config["indexnow_key"] = args["key"]

    pinger = IndexNowPinger(pinger_config)
    urls = args.get("urls", [])

    if len(urls) == 1:
        result = pinger.ping_single(urls[0])
        return {"success": result.success, "urls": 1, "engine": result.engine, "error": result.error}
    else:
        results = pinger.ping_all_engines(urls)
        return {
            "urls_submitted": len(urls),
            "engines_pinged": len(results),
            "successful": sum(1 for r in results if r.success),
        }


# Command registry
COMMANDS = {
    "audit_page": cmd_audit_page,
    "audit_site": cmd_audit_page,  # Same for now, full crawler in future
    "check_indexability": cmd_audit_page,
    "check_mobile": cmd_audit_page,
    "fix_auto": cmd_fix_auto,
    "fix_meta": cmd_fix_auto,
    "fix_schema": cmd_fix_schema,
    "fix_robots": cmd_fix_auto,
    "fix_sitemap": cmd_fix_auto,
    "fix_hreflang": cmd_fix_hreflang,
    "ai_readiness_score": cmd_ai_readiness_score,
    "analyze_content": cmd_audit_page,
    "analyze_keywords": cmd_audit_page,
    "analyze_links": cmd_audit_page,
    "analyze_images": cmd_audit_page,
    "monitor_baseline": cmd_monitor_baseline,
    "monitor_compare": cmd_monitor_compare,
    "monitor_history": cmd_monitor_compare,
    "monitor_alerts": cmd_monitor_compare,
    "schema_validate": cmd_fix_schema,
    "schema_generate": cmd_fix_schema,
    "schema_faq": cmd_fix_schema,
    "hreflang_audit": cmd_hreflang_audit,
    "hreflang_generate": cmd_fix_hreflang,
    "locale_detect": cmd_hreflang_audit,
    "performance_check": cmd_audit_page,
    "pagespeed": cmd_audit_page,
    "resource_audit": cmd_audit_page,
    "competitor_compare": cmd_competitor_compare,
    "backlink_opportunities": cmd_backlink_opportunities,
    "serp_analyze": cmd_audit_page,
    "content_brief": cmd_audit_page,
    "content_optimize": cmd_audit_page,
    "content_gaps": cmd_audit_page,
    "programmatic_pages": cmd_programmatic_pages,
    "indexnow_ping": cmd_indexnow_ping,
    "publish_post": cmd_indexnow_ping,
    "sitemap_submit": cmd_indexnow_ping,
}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: bridge.py <command> <args_json>"}))
        sys.exit(1)

    command = sys.argv[1]
    try:
        args = json.loads(sys.argv[2])
    except json.JSONDecodeError:
        args = {"url": sys.argv[2]}

    handler = COMMANDS.get(command)
    if not handler:
        print(json.dumps({"error": f"Unknown command: {command}", "available": list(COMMANDS.keys())}))
        sys.exit(1)

    try:
        result = handler(args)
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e), "command": command}))
        sys.exit(1)


if __name__ == "__main__":
    main()
