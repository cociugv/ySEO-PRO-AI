"""
ySEO-PRO-AI CLI — Thin adapter over SEOOperations deep module.

Usage:
    python -m src.ops.cli scan <url>
    python -m src.ops.cli audit <url>
    python -m src.ops.cli fix <url> [--dry-run]
    python -m src.ops.cli ai-score <url>
    python -m src.ops.cli monitor baseline <url>
    python -m src.ops.cli monitor compare <url>
"""

import sys
import os
import json

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.operations import SEOOperations, OperationResult
from src.core.pipeline import Severity


def print_result(result: OperationResult) -> None:
    """Format and print an operation result."""
    print(f"\n{'='*60}")
    print(f"  ySEO-PRO-AI — {result.operation.upper()}")
    print(f"  Target: {result.url}")
    print(f"  Score:  {result.score}/100")
    print(f"  Time:   {result.elapsed_seconds:.1f}s")
    print(f"{'='*60}\n")

    if result.errors:
        for err in result.errors:
            e = err if isinstance(err, str) else err.get("error", str(err))
            print(f"  ERROR: {e}")
        return

    if result.issues:
        # Group by severity
        by_sev = {}
        for issue in result.issues:
            sev = issue.get("severity", "info")
            by_sev.setdefault(sev, []).append(issue)

        for sev in ["critical", "high", "medium", "low", "info"]:
            items = by_sev.get(sev, [])
            if items:
                print(f"  [{sev.upper()}] ({len(items)})")
                for item in items:
                    fix = " [FIX]" if item.get("fix_available") else ""
                    applied = " ✓" if item.get("fix_applied") else ""
                    print(f"    • {item.get('code','')}: {item.get('title','')}{fix}{applied}")
                print()

    if result.fixes:
        print(f"  Fixes ({len(result.fixes)}):")
        for fix in result.fixes:
            status = fix.get("status", "")
            print(f"    {status}: {fix.get('action','')} — {fix.get('description','')}")
        print()

    # Extra data display
    ai = result.data.get("ai_readiness")
    if ai and ai.get("overall_score"):
        print(f"  AI Readiness: {ai['overall_score']}/100")
        bd = ai.get("breakdown", {})
        for k, v in bd.items():
            print(f"    {k}: {v}/100")
        print()

    page = result.data.get("page", {})
    if page and result.operation == "scan":
        print(f"  Title:         {page.get('title','')}")
        print(f"  Description:   {str(page.get('meta_description',''))[:80]}")
        print(f"  H1:            {page.get('h1',['(none)'])[0] if page.get('h1') else '(none)'}")
        print(f"  Words:         {page.get('word_count',0)}")
        print(f"  Links:         {page.get('internal_links_count',0)} int / {page.get('external_links_count',0)} ext")
        print(f"  Hreflang:      {page.get('hreflang_count', len(page.get('hreflang_tags',[])))}")
        print(f"  Schema:        {page.get('json_ld_count',0)}")
        print()


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    ops = SEOOperations(project_root=PROJECT_ROOT)
    command = args[0].lower()

    if command == "scan" and len(args) > 1:
        print_result(ops.scan(args[1]))
    elif command == "audit" and len(args) > 1:
        print_result(ops.audit(args[1]))
    elif command == "fix" and len(args) > 1:
        dry_run = "--dry-run" in args
        print_result(ops.fix(args[1], dry_run=dry_run))
    elif command == "ai-score" and len(args) > 1:
        print_result(ops.ai_readiness(args[1]))
    elif command == "monitor" and len(args) > 2:
        sub = args[1].lower()
        url = args[2]
        if sub == "baseline":
            print_result(ops.monitor_baseline(url))
        elif sub == "compare":
            print_result(ops.monitor_compare(url))
    else:
        print(f"  Unknown: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
