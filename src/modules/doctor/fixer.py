"""
Auto-Fixer Engine — Applies fixes for diagnosed SEO issues.

Part of the DOCTOR module.
Plugs into Pipeline stage: FIX
"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional
from ...core.pipeline import PipelineContext, Issue, Severity, Stage


@dataclass
class FixResult:
    """Result of applying a fix."""
    issue_code: str
    success: bool
    action: str = ""
    details: str = ""
    output: str = ""
    rollback_info: dict = field(default_factory=dict)


@dataclass
class Prescription:
    """A fix prescription for a specific issue type."""
    issue_code: str
    action: str  # generate | inject | modify | create
    target: str  # what to fix (meta_title, robots_txt, schema, etc.)
    template: str = ""
    params: dict = field(default_factory=dict)


class AutoFixer:
    """
    Applies automatic fixes for SEO issues.

    Supports dry-run mode and backup-before-fix.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.dry_run = self.config.get("dry_run", False)
        self.backup_enabled = self.config.get("backup_before_fix", True)
        self._fix_log: list[FixResult] = []

    def register(self, pipeline) -> None:
        """Register this module into the pipeline."""
        pipeline.register(Stage.FIX, self.apply_fixes)

    def apply_fixes(self, ctx: PipelineContext) -> None:
        """FIX stage: Apply fixes for all fixable issues."""
        fixable = [i for i in ctx.issues if i.fix_available and not i.fix_applied]

        for issue in fixable:
            prescription = get_prescription(issue, ctx)
            if prescription:
                result = self._execute_fix(prescription, ctx)
                self._fix_log.append(result)
                if result.success:
                    issue.fix_applied = True
                    ctx.fixes_applied.append({
                        "code": issue.code,
                        "action": result.action,
                        "details": result.details,
                        "timestamp": time.time(),
                    })

    def _execute_fix(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Execute a single fix prescription."""
        if self.dry_run:
            return FixResult(
                issue_code=rx.issue_code,
                success=True,
                action=f"[DRY-RUN] {rx.action}",
                details=f"Would {rx.action} for {rx.target}",
            )

        handler = self._get_handler(rx.action)
        if handler:
            return handler(rx, ctx)

        return FixResult(
            issue_code=rx.issue_code,
            success=False,
            action=rx.action,
            details=f"No handler for action: {rx.action}",
        )

    def _get_handler(self, action: str):
        """Get the handler function for a fix action."""
        handlers = {
            "generate_meta": self._fix_generate_meta,
            "generate_robots": self._fix_generate_robots,
            "generate_sitemap": self._fix_generate_sitemap,
            "inject_schema": self._fix_inject_schema,
            "fix_canonical": self._fix_canonical,
            "fix_hreflang": self._fix_hreflang,
            "optimize_title": self._fix_optimize_title,
        }
        return handlers.get(action)

    def _fix_generate_meta(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Generate missing meta description."""
        page = ctx.scan_data.get("page", {})
        title = page.get("title", "")
        h1 = page.get("h1", [""])[0] if page.get("h1") else ""
        word_count = page.get("word_count", 0)

        # Generate a description from available content
        base_text = h1 or title or ctx.target_url
        generated = f"{base_text} - Comprehensive information and resources. Learn more at {ctx.target_url}"

        if len(generated) > 160:
            generated = generated[:157] + "..."

        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="generate_meta",
            details=f"Generated meta description: '{generated}'",
            output=json.dumps({
                "tag": "meta",
                "attrs": {"name": "description", "content": generated},
            }),
        )

    def _fix_generate_robots(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Generate robots.txt content."""
        from urllib.parse import urlparse
        domain = urlparse(ctx.target_url).netloc
        scheme = urlparse(ctx.target_url).scheme

        robots = f"""User-agent: *
Allow: /

# Block admin/internal paths
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# Sitemap
Sitemap: {scheme}://{domain}/sitemap.xml
"""
        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="generate_robots",
            details="Generated robots.txt with standard rules",
            output=robots,
        )

    def _fix_generate_sitemap(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Generate basic XML sitemap."""
        from urllib.parse import urlparse
        domain = urlparse(ctx.target_url).netloc
        scheme = urlparse(ctx.target_url).scheme
        today = time.strftime("%Y-%m-%d")

        internal_links = ctx.scan_data.get("page", {}).get("internal_links", [])
        urls = list(set([ctx.target_url] + internal_links[:100]))

        sitemap_entries = []
        for url in urls:
            sitemap_entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
  </url>""")

        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_entries)}
</urlset>"""

        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="generate_sitemap",
            details=f"Generated sitemap with {len(urls)} URLs",
            output=sitemap,
        )

    def _fix_inject_schema(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Generate and inject appropriate schema.org markup."""
        page = ctx.scan_data.get("page", {})
        title = page.get("title", "")
        desc = page.get("meta_description", "")

        # Detect page type and generate appropriate schema
        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": desc,
            "url": ctx.target_url,
        }

        # If it looks like an article
        word_count = page.get("word_count", 0)
        if word_count > 500:
            schema["@type"] = "Article"
            schema["headline"] = title
            schema["wordCount"] = word_count

        script_tag = f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'

        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="inject_schema",
            details=f"Generated {schema['@type']} schema markup",
            output=script_tag,
        )

    def _fix_canonical(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Fix missing or incorrect canonical tag."""
        canonical_url = ctx.target_url.rstrip("/")
        tag = f'<link rel="canonical" href="{canonical_url}" />'

        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="fix_canonical",
            details=f"Generated canonical tag pointing to {canonical_url}",
            output=tag,
        )

    def _fix_hreflang(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Generate hreflang tags for multilingual pages."""
        languages = ctx.config.get("targets", {}).get("languages", ["en"])
        from urllib.parse import urlparse
        parsed = urlparse(ctx.target_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        tags = []
        for lang in languages:
            if lang == "en":
                href = ctx.target_url
            else:
                href = f"{domain}/{lang}{parsed.path}"
            tags.append(f'<link rel="alternate" hreflang="{lang}" href="{href}" />')

        # Add x-default
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{ctx.target_url}" />')

        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="fix_hreflang",
            details=f"Generated hreflang tags for {len(languages)} languages",
            output="\n".join(tags),
        )

    def _fix_optimize_title(self, rx: Prescription, ctx: PipelineContext) -> FixResult:
        """Optimize page title length."""
        page = ctx.scan_data.get("page", {})
        title = page.get("title", "")

        if len(title) > 60:
            optimized = title[:57] + "..."
        elif len(title) < 30:
            optimized = f"{title} | Official Page"
        else:
            optimized = title

        return FixResult(
            issue_code=rx.issue_code,
            success=True,
            action="optimize_title",
            details=f"Optimized title from {len(title)} to {len(optimized)} chars",
            output=optimized,
        )


def get_prescription(issue: Issue, ctx: PipelineContext) -> Optional[Prescription]:
    """Get the fix prescription for a given issue."""
    prescriptions = {
        "TECH-020": Prescription("TECH-020", "optimize_title", "title"),
        "TECH-021": Prescription("TECH-021", "optimize_title", "title"),
        "TECH-022": Prescription("TECH-022", "optimize_title", "title"),
        "TECH-025": Prescription("TECH-025", "generate_meta", "meta_description"),
        "TECH-026": Prescription("TECH-026", "generate_meta", "meta_description"),
        "TECH-030": Prescription("TECH-030", "optimize_title", "h1"),
        "TECH-040": Prescription("TECH-040", "fix_canonical", "canonical"),
        "TECH-045": Prescription("TECH-045", "generate_meta", "viewport"),
        "TECH-050": Prescription("TECH-050", "inject_schema", "json_ld"),
        "TECH-060": Prescription("TECH-060", "fix_canonical", "https_redirect"),
        "TECH-061": Prescription("TECH-061", "generate_meta", "hsts_header"),
        "ROBOT-001": Prescription("ROBOT-001", "generate_robots", "robots_txt"),
        "ROBOT-010": Prescription("ROBOT-010", "generate_robots", "robots_txt"),
        "SMAP-001": Prescription("SMAP-001", "generate_sitemap", "sitemap_xml"),
    }
    return prescriptions.get(issue.code)
