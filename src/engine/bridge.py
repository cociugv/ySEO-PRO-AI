"""
Engine Bridge — Connects MCP server to Python SEO operations.

Called as subprocess: python bridge.py <command> <args_json>
Routes to SEOOperations deep module — no pipeline internals leak here.
"""

import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.core.operations import SEOOperations


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: bridge.py <command> <args_json>"}))
        sys.exit(1)

    command = sys.argv[1]
    try:
        args = json.loads(sys.argv[2])
    except json.JSONDecodeError:
        args = {"url": sys.argv[2]}

    ops = SEOOperations(project_root=PROJECT_ROOT)

    # Route command → operation
    handlers = {
        "audit_page": lambda a: ops.audit(a["url"]),
        "check_indexability": lambda a: ops.audit(a["url"]),
        "fix_auto": lambda a: ops.fix(a["url"], dry_run=a.get("dry_run", True)),
        "generate_schema": lambda a: ops.generate_schema(a["url"], a.get("force_type", "auto")),
        "generate_hreflang": lambda a: ops.generate_hreflang(a["url"], a.get("languages", ["en"])),
        "ai_readiness": lambda a: ops.ai_readiness(a["url"]),
        "monitor_baseline": lambda a: ops.monitor_baseline(a["url"]),
        "monitor_compare": lambda a: ops.monitor_compare(a["url"]),
        "competitor_compare": lambda a: ops.competitor_compare(a["your_url"], a["competitor_url"]),
        "backlink_opportunities": lambda a: ops.backlink_opportunities(
            a["domain"], a.get("keywords", a.get("niche_keywords", []))
        ),
        "indexnow_ping": lambda a: ops.indexnow_ping(a.get("urls", []), a.get("key", "")),
    }

    handler = handlers.get(command)
    if not handler:
        print(json.dumps({
            "error": f"Unknown command: {command}",
            "available": list(handlers.keys()),
        }))
        sys.exit(1)

    try:
        result = handler(args)
        print(json.dumps(result.to_dict(), indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e), "command": command}))
        sys.exit(1)


if __name__ == "__main__":
    main()
