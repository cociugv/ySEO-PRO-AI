"""
Rule Suppression — Allow users to silence specific findings.

Suppression config lives in .yseo/suppress.yaml (or config/suppress.yaml).

Format:
    suppress:
      - rule: TECH-027
        reason: "Meta description is intentionally long for this page"
        urls: ["https://ylink.pro"]  # optional, empty = all URLs

      - rule: TECH-061
        reason: "HSTS managed at load balancer level"

      - rule: IMG-001
        urls: ["https://ylink.pro/landing"]
        reason: "Decorative images intentionally without alt"
"""

import os
from typing import Optional
from .config_loader import load_yaml_simple
from .pipeline import Issue


def load_suppressions(project_root: str = ".") -> list[dict]:
    """Load suppression rules from config."""
    paths = [
        os.path.join(project_root, ".yseo", "suppress.yaml"),
        os.path.join(project_root, "config", "suppress.yaml"),
    ]

    for path in paths:
        if os.path.exists(path):
            data = load_yaml_simple(path)
            return data.get("suppress", [])

    return []


def is_suppressed(issue: Issue, suppressions: list[dict]) -> bool:
    """Check if an issue should be suppressed based on rules."""
    for rule in suppressions:
        if rule.get("rule") != issue.code:
            continue

        # Check URL filter
        urls = rule.get("urls", [])
        if urls and isinstance(urls, list):
            if issue.url and issue.url not in urls:
                continue

        # Match found — suppress
        return True

    return False


def apply_suppressions(issues: list[Issue], project_root: str = ".") -> tuple[list[Issue], list[Issue]]:
    """
    Apply suppressions and return (active_issues, suppressed_issues).

    Suppressed issues are not deleted — they're separated for transparency.
    """
    suppressions = load_suppressions(project_root)
    if not suppressions:
        return issues, []

    active = []
    suppressed = []

    for issue in issues:
        if is_suppressed(issue, suppressions):
            suppressed.append(issue)
        else:
            active.append(issue)

    return active, suppressed
