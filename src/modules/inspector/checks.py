"""
Additional diagnostic checks for the Inspector module.

Provides standalone check functions that can be used independently
or composed into the pipeline.
"""

import re
from urllib.parse import urlparse
from ...core.pipeline import Issue, Severity


def check_robots_txt(robots_content: str, url: str) -> list[Issue]:
    """Analyze robots.txt for SEO issues."""
    issues = []

    if not robots_content:
        issues.append(Issue(
            code="ROBOT-001",
            title="Missing robots.txt",
            severity=Severity.HIGH,
            module="inspector",
            url=url,
            description="No robots.txt found at domain root",
            fix_available=True,
        ))
        return issues

    lines = robots_content.strip().split("\n")

    # Check for sitemap declaration
    has_sitemap = any("sitemap:" in line.lower() for line in lines)
    if not has_sitemap:
        issues.append(Issue(
            code="ROBOT-010",
            title="No sitemap declared in robots.txt",
            severity=Severity.MEDIUM,
            module="inspector",
            url=url,
            description="robots.txt should reference XML sitemap",
            fix_available=True,
        ))

    # Check for overly restrictive rules
    for line in lines:
        clean = line.strip().lower()
        if clean == "disallow: /":
            issues.append(Issue(
                code="ROBOT-020",
                title="robots.txt blocks entire site",
                severity=Severity.CRITICAL,
                module="inspector",
                url=url,
                description="'Disallow: /' blocks all crawlers from the entire site",
            ))

    return issues


def check_sitemap_xml(sitemap_content: str, url: str) -> list[Issue]:
    """Analyze XML sitemap for issues."""
    issues = []

    if not sitemap_content:
        issues.append(Issue(
            code="SMAP-001",
            title="Missing XML sitemap",
            severity=Severity.HIGH,
            module="inspector",
            url=url,
            fix_available=True,
        ))
        return issues

    # Check for proper XML declaration
    if not sitemap_content.strip().startswith("<?xml"):
        issues.append(Issue(
            code="SMAP-010",
            title="Sitemap missing XML declaration",
            severity=Severity.LOW,
            module="inspector",
            url=url,
        ))

    # Count URLs in sitemap
    url_count = sitemap_content.count("<loc>")
    if url_count == 0:
        issues.append(Issue(
            code="SMAP-020",
            title="Sitemap contains no URLs",
            severity=Severity.HIGH,
            module="inspector",
            url=url,
        ))
    elif url_count > 50000:
        issues.append(Issue(
            code="SMAP-021",
            title="Sitemap exceeds 50,000 URL limit",
            severity=Severity.HIGH,
            module="inspector",
            url=url,
            description=f"Contains {url_count} URLs. Split into sitemap index.",
            fix_available=True,
        ))

    # Check for lastmod dates
    has_lastmod = "<lastmod>" in sitemap_content
    if not has_lastmod:
        issues.append(Issue(
            code="SMAP-030",
            title="Sitemap missing lastmod dates",
            severity=Severity.LOW,
            module="inspector",
            url=url,
            description="Adding lastmod helps search engines prioritize crawling",
        ))

    return issues


def check_security_headers(headers: dict, url: str) -> list[Issue]:
    """Check for important security headers."""
    issues = []
    lower_headers = {k.lower(): v for k, v in headers.items()}

    security_checks = [
        ("x-content-type-options", "SEC-010", "Missing X-Content-Type-Options header", Severity.LOW),
        ("x-frame-options", "SEC-011", "Missing X-Frame-Options header", Severity.LOW),
        ("content-security-policy", "SEC-012", "Missing Content-Security-Policy header", Severity.LOW),
    ]

    for header, code, title, severity in security_checks:
        if header not in lower_headers:
            issues.append(Issue(
                code=code,
                title=title,
                severity=severity,
                module="inspector",
                url=url,
                fix_available=True,
            ))

    return issues


def check_redirect_chain(redirects: list, url: str) -> list[Issue]:
    """Check for redirect chain issues."""
    issues = []

    if len(redirects) > 2:
        issues.append(Issue(
            code="REDIR-001",
            title="Long redirect chain",
            severity=Severity.MEDIUM,
            module="inspector",
            url=url,
            description=f"Page has {len(redirects)} redirects before final destination",
            evidence={"chain": redirects},
        ))

    return issues


def check_url_structure(url: str) -> list[Issue]:
    """Analyze URL structure for SEO best practices."""
    issues = []
    parsed = urlparse(url)
    path = parsed.path

    # Check for uppercase
    if path != path.lower():
        issues.append(Issue(
            code="URL-010",
            title="URL contains uppercase characters",
            severity=Severity.LOW,
            module="inspector",
            url=url,
            description="URLs should be lowercase for consistency",
            fix_available=True,
        ))

    # Check for underscores
    if "_" in path:
        issues.append(Issue(
            code="URL-011",
            title="URL uses underscores instead of hyphens",
            severity=Severity.LOW,
            module="inspector",
            url=url,
            description="Use hyphens (-) as word separators, not underscores (_)",
        ))

    # Check path depth
    segments = [s for s in path.split("/") if s]
    if len(segments) > 4:
        issues.append(Issue(
            code="URL-020",
            title="Deep URL structure (> 4 levels)",
            severity=Severity.LOW,
            module="inspector",
            url=url,
            description=f"URL has {len(segments)} path segments. Flatter is better.",
        ))

    # Check for query parameters in URL
    if parsed.query:
        issues.append(Issue(
            code="URL-030",
            title="URL has query parameters",
            severity=Severity.INFO,
            module="inspector",
            url=url,
            description="Consider using clean URLs without query strings for SEO pages",
        ))

    return issues


def run_all_checks(ctx) -> None:
    """Run all standalone checks and add issues to context."""
    # URL structure
    ctx.issues.extend(check_url_structure(ctx.target_url))

    # Security headers from scan data
    headers = ctx.scan_data.get("fetch_result", {}).get("headers", {})
    if headers:
        ctx.issues.extend(check_security_headers(headers, ctx.target_url))
