"""
Rule Packs — Modular SEO check collections.

Each rule pack is independently versioned and testable.
Rules consume evidence (page facts) and produce findings (issues).
"""

import re
from urllib.parse import urlparse
from ...core.pipeline import Issue, Severity


# ─── Indexability Rules ────────────────────────────────────────────────────

def check_indexability(url: str, page: dict, headers: dict) -> list[Issue]:
    """Indexability matrix — can search engines index this page?"""
    issues = []
    meta_robots = page.get("meta_robots", "").lower()

    # noindex directive
    if "noindex" in meta_robots:
        issues.append(Issue(
            code="IDX-001", title="Page has noindex directive",
            severity=Severity.CRITICAL, module="inspector", url=url,
            description="This page is excluded from search engine indexes",
        ))

    # nofollow — links won't pass equity
    if "nofollow" in meta_robots:
        issues.append(Issue(
            code="IDX-002", title="Page has nofollow directive",
            severity=Severity.MEDIUM, module="inspector", url=url,
            description="Links on this page won't pass PageRank",
        ))

    # X-Robots-Tag header
    x_robots = headers.get("x-robots-tag", headers.get("X-Robots-Tag", "")).lower()
    if "noindex" in x_robots:
        issues.append(Issue(
            code="IDX-003", title="X-Robots-Tag header contains noindex",
            severity=Severity.CRITICAL, module="inspector", url=url,
        ))

    # Canonical points elsewhere
    canonical = page.get("canonical", "")
    if canonical and canonical != url and canonical != url + "/" and canonical != url.rstrip("/"):
        issues.append(Issue(
            code="IDX-010", title="Canonical points to different URL",
            severity=Severity.HIGH, module="inspector", url=url,
            description=f"Canonical: {canonical} (this page may not be indexed)",
            evidence={"canonical": canonical, "current": url},
        ))

    return issues


# ─── Link Graph Rules ──────────────────────────────────────────────────────

def check_link_graph(url: str, page: dict) -> list[Issue]:
    """Internal link structure analysis."""
    issues = []
    internal = page.get("internal_links_count", 0)
    external = page.get("external_links_count", 0)

    # Orphan page (no outgoing internal links)
    if internal == 0:
        issues.append(Issue(
            code="LINK-001", title="No internal links on page",
            severity=Severity.MEDIUM, module="inspector", url=url,
            description="Page has no outgoing internal links — poor for crawlability and equity flow",
            fix_available=True,
        ))

    # Too many outgoing links (dilution)
    total = internal + external
    if total > 200:
        issues.append(Issue(
            code="LINK-010", title=f"Too many links on page ({total})",
            severity=Severity.LOW, module="inspector", url=url,
            description="Excessive links may dilute link equity",
            evidence={"total_links": total, "internal": internal, "external": external},
        ))

    # High external ratio (link juice leaking)
    if internal > 0 and external > internal * 2:
        issues.append(Issue(
            code="LINK-020", title="External links outnumber internal links",
            severity=Severity.LOW, module="inspector", url=url,
            description=f"{external} external vs {internal} internal — consider adding more internal links",
        ))

    return issues


# ─── Sitemap Rules ─────────────────────────────────────────────────────────

def check_sitemap(sitemap_content: str, url: str) -> list[Issue]:
    """XML sitemap validation rules."""
    issues = []

    if not sitemap_content:
        issues.append(Issue(
            code="SMAP-001", title="No XML sitemap found",
            severity=Severity.HIGH, module="inspector", url=url,
            description="sitemap.xml not found or empty",
            fix_available=True,
        ))
        return issues

    # XML declaration
    if not sitemap_content.strip().startswith("<?xml"):
        issues.append(Issue(
            code="SMAP-010", title="Sitemap missing XML declaration",
            severity=Severity.LOW, module="inspector", url=url,
        ))

    # URL count
    url_count = sitemap_content.count("<loc>")
    if url_count == 0:
        issues.append(Issue(
            code="SMAP-020", title="Sitemap contains no URLs",
            severity=Severity.HIGH, module="inspector", url=url,
        ))
    elif url_count > 50000:
        issues.append(Issue(
            code="SMAP-021", title=f"Sitemap exceeds 50,000 URLs ({url_count})",
            severity=Severity.HIGH, module="inspector", url=url,
            description="Split into sitemap index with multiple sitemaps",
            fix_available=True,
        ))

    # File size (uncompressed max 50MB per Google)
    if len(sitemap_content) > 50_000_000:
        issues.append(Issue(
            code="SMAP-022", title="Sitemap exceeds 50MB size limit",
            severity=Severity.HIGH, module="inspector", url=url,
        ))

    # lastmod presence
    if "<lastmod>" not in sitemap_content:
        issues.append(Issue(
            code="SMAP-030", title="Sitemap missing lastmod dates",
            severity=Severity.LOW, module="inspector", url=url,
            description="Adding lastmod helps search engines prioritize crawling",
        ))

    # HTTP URLs in HTTPS sitemap
    if "https://" in url and "http://" in sitemap_content and "<loc>http://" in sitemap_content:
        issues.append(Issue(
            code="SMAP-040", title="Sitemap contains HTTP URLs on HTTPS site",
            severity=Severity.MEDIUM, module="inspector", url=url,
            description="All sitemap URLs should use HTTPS",
            fix_available=True,
        ))

    return issues


# ─── Image SEO Rules ───────────────────────────────────────────────────────

def check_images(page: dict, url: str) -> list[Issue]:
    """Image SEO analysis."""
    issues = []
    images = page.get("images", [])

    if not images:
        return issues

    # Missing alt text
    missing_alt = [img for img in images if not img.get("alt")]
    if missing_alt:
        issues.append(Issue(
            code="IMG-001", title=f"{len(missing_alt)} image(s) missing alt text",
            severity=Severity.MEDIUM, module="inspector", url=url,
            description="Alt text is critical for accessibility and image SEO",
            evidence={"images_without_alt": [img.get("src", "") for img in missing_alt[:5]]},
            fix_available=True,
        ))

    # Empty alt (decorative) — check if it's actually content image
    empty_alt = [img for img in images if img.get("alt") == "" and img.get("src")]
    # We already caught these above

    # Missing dimensions (causes CLS)
    no_dimensions = [img for img in images if not img.get("width") or not img.get("height")]
    if no_dimensions:
        issues.append(Issue(
            code="IMG-010", title=f"{len(no_dimensions)} image(s) missing width/height",
            severity=Severity.LOW, module="inspector", url=url,
            description="Missing dimensions cause Cumulative Layout Shift (CLS)",
            evidence={"count": len(no_dimensions)},
        ))

    # No lazy loading on below-fold images (heuristic: skip first 2)
    if len(images) > 2:
        below_fold = images[2:]
        no_lazy = [img for img in below_fold if img.get("loading") != "lazy"]
        if no_lazy:
            issues.append(Issue(
                code="IMG-020", title=f"{len(no_lazy)} below-fold image(s) not lazy-loaded",
                severity=Severity.LOW, module="inspector", url=url,
                description="Use loading='lazy' for images below the fold",
            ))

    return issues


# ─── URL Hygiene Rules ─────────────────────────────────────────────────────

def check_url_hygiene(url: str) -> list[Issue]:
    """URL structure best practices."""
    issues = []
    parsed = urlparse(url)
    path = parsed.path

    if path != path.lower():
        issues.append(Issue(
            code="URL-001", title="URL contains uppercase characters",
            severity=Severity.LOW, module="inspector", url=url,
            description="Use lowercase URLs for consistency",
            fix_available=True,
        ))

    if "_" in path:
        issues.append(Issue(
            code="URL-002", title="URL uses underscores instead of hyphens",
            severity=Severity.LOW, module="inspector", url=url,
        ))

    segments = [s for s in path.split("/") if s]
    if len(segments) > 5:
        issues.append(Issue(
            code="URL-003", title=f"Deep URL structure ({len(segments)} levels)",
            severity=Severity.LOW, module="inspector", url=url,
            description="Flatter URL structures are preferred for SEO",
        ))

    if len(url) > 200:
        issues.append(Issue(
            code="URL-004", title=f"URL too long ({len(url)} chars)",
            severity=Severity.LOW, module="inspector", url=url,
        ))

    return issues
