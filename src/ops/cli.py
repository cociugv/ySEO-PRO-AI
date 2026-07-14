"""
ySEO-PRO-AI CLI — Command-line interface for running SEO operations.

Usage:
    python -m src.ops.cli scan https://ylink.pro
    python -m src.ops.cli audit https://ylink.pro
    python -m src.ops.cli fix https://ylink.pro --dry-run
    python -m src.ops.cli drift baseline https://ylink.pro
    python -m src.ops.cli drift compare https://ylink.pro
    python -m src.ops.cli publish --title "My Post" --content post.md
    python -m src.ops.cli indexnow https://ylink.pro/blog/my-post
    python -m src.ops.cli competitor https://bit.ly
    python -m src.ops.cli ai-score https://ylink.pro
    python -m src.ops.cli generate city --data cities.json
"""

import sys
import os
import json
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.pipeline import PipelineRunner, Stage, PipelineContext
from src.core.config_loader import load_config
from src.core.fetcher import PageFetcher
from src.core.parser import parse_html


def cmd_scan(url: str, config: dict) -> None:
    """Quick scan — fetch + parse only."""
    print(f"\n{'='*60}")
    print(f"  ySEO-PRO-AI — Quick Scan")
    print(f"  Target: {url}")
    print(f"{'='*60}\n")

    fetcher = PageFetcher()
    result = fetcher.fetch(url)

    if not result.ok:
        print(f"  ERROR: Could not fetch URL (HTTP {result.status_code})")
        print(f"  {result.error}")
        return

    page = parse_html(result.body, url)

    print(f"  Status:          {result.status_code}")
    print(f"  Response Time:   {result.elapsed_ms:.0f}ms")
    print(f"  Title:           {page.title}")
    print(f"  Description:     {page.meta_description[:80]}...")
    print(f"  H1:              {page.h1[0] if page.h1 else '(missing)'}")
    print(f"  Word Count:      {page.word_count}")
    print(f"  Internal Links:  {len(page.internal_links)}")
    print(f"  External Links:  {len(page.external_links)}")
    print(f"  Images:          {len(page.images)}")
    print(f"  Hreflang Tags:   {len(page.hreflang_tags)}")
    print(f"  Schema (JSON-LD): {len(page.json_ld)}")
    print(f"  Canonical:       {page.canonical or '(missing)'}")
    print(f"  Language:        {page.lang or '(not set)'}")
    print(f"\n{'='*60}")


def cmd_audit(url: str, config: dict) -> None:
    """Full audit — scan + diagnose + fix + verify + report."""
    print(f"\n{'='*60}")
    print(f"  ySEO-PRO-AI — Full SEO Audit")
    print(f"  Target: {url}")
    print(f"{'='*60}\n")

    from src.modules.inspector.scanner import TechnicalScanner
    from src.modules.citadel.ai_readiness import AIReadinessScorer
    from src.modules.citadel.schema_engine import SchemaEngine

    pipeline = PipelineRunner(config)

    # Register modules
    scanner = TechnicalScanner(config.get("modules", {}).get("inspector", {}))
    scanner.register(pipeline)

    schema_engine = SchemaEngine(config.get("modules", {}).get("citadel", {}))
    schema_engine.register(pipeline)

    ai_scorer = AIReadinessScorer()
    ai_scorer.register(pipeline)

    # Run pipeline (SCAN + DIAGNOSE only for audit)
    ctx = pipeline.execute(url, stages=[Stage.SCAN, Stage.DIAGNOSE])

    # Print results
    print(f"  Issues Found: {len(ctx.issues)}")
    print(f"  SEO Score:    {ctx.score}/100")
    print(f"  Time Elapsed: {ctx.elapsed_seconds:.1f}s")
    print()

    # Group issues by severity
    from src.core.pipeline import Severity
    for sev in Severity:
        issues_at_level = [i for i in ctx.issues if i.severity == sev]
        if issues_at_level:
            print(f"  [{sev.value.upper()}] ({len(issues_at_level)} issues)")
            for issue in issues_at_level:
                fix_marker = " [AUTO-FIX]" if issue.fix_available else ""
                print(f"    • {issue.code}: {issue.title}{fix_marker}")
                if issue.description:
                    print(f"      {issue.description}")
            print()

    # AI Readiness
    ai_data = ctx.scan_data.get("ai_readiness")
    if ai_data:
        print(f"  AI Search Readiness: {ai_data['overall_score']}/100")
        breakdown = ai_data.get("breakdown", {})
        for key, val in breakdown.items():
            print(f"    {key}: {val}/100")
        print()

    print(f"{'='*60}")
    print(f"  Fixable issues: {sum(1 for i in ctx.issues if i.fix_available)}")
    print(f"  Run 'yseo fix {url}' to auto-fix")
    print(f"{'='*60}\n")


def cmd_fix(url: str, config: dict, dry_run: bool = False) -> None:
    """Auto-fix — run full pipeline including FIX stage."""
    print(f"\n{'='*60}")
    print(f"  ySEO-PRO-AI — Auto-Fix {'(DRY RUN)' if dry_run else ''}")
    print(f"  Target: {url}")
    print(f"{'='*60}\n")

    from src.modules.inspector.scanner import TechnicalScanner
    from src.modules.doctor.fixer import AutoFixer

    fix_config = config.get("modules", {}).get("doctor", {})
    fix_config["dry_run"] = dry_run

    pipeline = PipelineRunner(config)

    scanner = TechnicalScanner(config.get("modules", {}).get("inspector", {}))
    scanner.register(pipeline)

    fixer = AutoFixer(fix_config)
    fixer.register(pipeline)

    ctx = pipeline.execute(url, stages=[Stage.SCAN, Stage.DIAGNOSE, Stage.FIX])

    print(f"  Issues Found:    {len(ctx.issues)}")
    print(f"  Fixes Applied:   {len(ctx.fixes_applied)}")
    print()

    for fix in ctx.fixes_applied:
        print(f"    ✓ {fix['code']}: {fix['action']}")
        print(f"      {fix['details']}")
        print()

    remaining = [i for i in ctx.issues if not i.fix_applied]
    if remaining:
        print(f"  Remaining unfixed issues: {len(remaining)}")
        for issue in remaining:
            print(f"    • {issue.code}: {issue.title}")

    print(f"\n{'='*60}\n")


def cmd_ai_score(url: str, config: dict) -> None:
    """Calculate AI Search Readiness Score."""
    print(f"\n  ySEO-PRO-AI — AI Search Readiness Score")
    print(f"  Target: {url}\n")

    fetcher = PageFetcher()
    result = fetcher.fetch(url)

    if not result.ok:
        print(f"  ERROR: Could not fetch URL")
        return

    page = parse_html(result.body, url)

    from src.modules.citadel.ai_readiness import AIReadinessScorer
    scorer = AIReadinessScorer()
    report = scorer.calculate_score(url, page.to_dict())

    print(f"  Overall Score: {report.overall_score}/100\n")
    print(f"  Breakdown:")
    print(f"    Citability:       {report.citability_score}/100")
    print(f"    Entity Presence:  {report.entity_score}/100")
    print(f"    Answer Clarity:   {report.answer_clarity_score}/100")
    print(f"    Structure:        {report.structure_score}/100")
    print(f"    Authority:        {report.authority_score}/100")
    print(f"    Freshness:        {report.freshness_score}/100")

    if report.recommendations:
        print(f"\n  Recommendations:")
        for rec in report.recommendations:
            print(f"    • {rec['title']}")
    print()


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    config = load_config(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    command = args[0].lower()
    url = args[1] if len(args) > 1 else ""

    if command == "scan" and url:
        cmd_scan(url, config)
    elif command == "audit" and url:
        cmd_audit(url, config)
    elif command == "fix" and url:
        dry_run = "--dry-run" in args
        cmd_fix(url, config, dry_run=dry_run)
    elif command == "ai-score" and url:
        cmd_ai_score(url, config)
    else:
        print(f"  Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
