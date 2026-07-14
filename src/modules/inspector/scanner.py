"""
Technical SEO Scanner — Crawls pages and runs diagnostic checks.

Part of the INSPECTOR module.
Plugs into Pipeline stages: SCAN + DIAGNOSE
"""

from ...core.pipeline import PipelineContext, Issue, Severity, Stage
from ...core.fetcher import PageFetcher, FetchResult
from ...core.parser import parse_html, PageData


class TechnicalScanner:
    """
    Scans a target URL and diagnoses technical SEO issues.

    Registers into pipeline SCAN and DIAGNOSE stages.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.fetcher = PageFetcher(
            rate_limit_ms=self.config.get("rate_limit_ms", 1000),
            timeout_seconds=self.config.get("timeout_seconds", 30),
        )

    def register(self, pipeline) -> None:
        """Register this module into the pipeline."""
        pipeline.register(Stage.SCAN, self.scan)
        pipeline.register(Stage.DIAGNOSE, self.diagnose)

    def scan(self, ctx: PipelineContext) -> None:
        """SCAN stage: Fetch page and parse HTML."""
        result = self.fetcher.fetch(ctx.target_url)
        ctx.scan_data["fetch_result"] = {
            "status_code": result.status_code,
            "elapsed_ms": result.elapsed_ms,
            "headers": result.headers,
            "from_cache": result.from_cache,
            "error": result.error,
        }

        if result.ok and result.is_html:
            page_data = parse_html(result.body, ctx.target_url)
            ctx.scan_data["page"] = page_data.to_dict()
            ctx.scan_data["raw_html_length"] = len(result.body)
        else:
            ctx.scan_data["page"] = {}

    def diagnose(self, ctx: PipelineContext) -> None:
        """DIAGNOSE stage: Analyze scan data for issues."""
        fetch = ctx.scan_data.get("fetch_result", {})
        page = ctx.scan_data.get("page", {})

        # Check HTTP status
        status = fetch.get("status_code", 0)
        if status == 0:
            ctx.issues.append(Issue(
                code="TECH-001",
                title="Page unreachable",
                severity=Severity.CRITICAL,
                module="inspector",
                url=ctx.target_url,
                description=f"Failed to fetch page: {fetch.get('error', 'Unknown error')}",
            ))
            return

        if status >= 500:
            ctx.issues.append(Issue(
                code="TECH-002",
                title="Server error (5xx)",
                severity=Severity.CRITICAL,
                module="inspector",
                url=ctx.target_url,
                description=f"Server returned HTTP {status}",
            ))

        if status == 404:
            ctx.issues.append(Issue(
                code="TECH-003",
                title="Page not found (404)",
                severity=Severity.HIGH,
                module="inspector",
                url=ctx.target_url,
            ))

        # Response time
        elapsed = fetch.get("elapsed_ms", 0)
        if elapsed > 3000:
            ctx.issues.append(Issue(
                code="TECH-010",
                title="Slow server response (TTFB > 3s)",
                severity=Severity.HIGH,
                module="inspector",
                url=ctx.target_url,
                description=f"Time to first byte: {elapsed:.0f}ms",
                evidence={"ttfb_ms": elapsed},
            ))
        elif elapsed > 1500:
            ctx.issues.append(Issue(
                code="TECH-011",
                title="Moderate server response (TTFB > 1.5s)",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                description=f"Time to first byte: {elapsed:.0f}ms",
                evidence={"ttfb_ms": elapsed},
            ))

        if not page:
            return

        # Title checks
        title = page.get("title", "")
        title_len = page.get("title_length", 0)
        if not title:
            ctx.issues.append(Issue(
                code="TECH-020",
                title="Missing page title",
                severity=Severity.CRITICAL,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))
        elif title_len < 30:
            ctx.issues.append(Issue(
                code="TECH-021",
                title="Title too short (< 30 chars)",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                description=f"Title is {title_len} chars: '{title}'",
                fix_available=True,
            ))
        elif title_len > 60:
            ctx.issues.append(Issue(
                code="TECH-022",
                title="Title too long (> 60 chars)",
                severity=Severity.LOW,
                module="inspector",
                url=ctx.target_url,
                description=f"Title is {title_len} chars, may be truncated in SERP",
                fix_available=True,
            ))

        # Meta description checks
        desc = page.get("meta_description", "")
        desc_len = page.get("description_length", 0)
        if not desc:
            ctx.issues.append(Issue(
                code="TECH-025",
                title="Missing meta description",
                severity=Severity.HIGH,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))
        elif desc_len < 70:
            ctx.issues.append(Issue(
                code="TECH-026",
                title="Meta description too short (< 70 chars)",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))
        elif desc_len > 160:
            ctx.issues.append(Issue(
                code="TECH-027",
                title="Meta description too long (> 160 chars)",
                severity=Severity.LOW,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))

        # H1 checks
        h1_list = page.get("h1", [])
        if not h1_list:
            ctx.issues.append(Issue(
                code="TECH-030",
                title="Missing H1 heading",
                severity=Severity.HIGH,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))
        elif len(h1_list) > 1:
            ctx.issues.append(Issue(
                code="TECH-031",
                title="Multiple H1 headings",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                description=f"Found {len(h1_list)} H1 tags",
                evidence={"h1_tags": h1_list},
            ))

        # Canonical check
        canonical = page.get("canonical", "")
        if not canonical:
            ctx.issues.append(Issue(
                code="TECH-040",
                title="Missing canonical tag",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))

        # Viewport check
        viewport = page.get("viewport", "")
        if not viewport:
            ctx.issues.append(Issue(
                code="TECH-045",
                title="Missing viewport meta tag",
                severity=Severity.HIGH,
                module="inspector",
                url=ctx.target_url,
                description="Page may not be mobile-friendly",
                fix_available=True,
            ))

        # Image alt text check
        images_count = page.get("images_count", 0)
        # We'd need to check individual images for alt text
        # This is a simplified check based on scan data

        # Structured data check
        json_ld_count = page.get("json_ld_count", 0)
        if json_ld_count == 0:
            ctx.issues.append(Issue(
                code="TECH-050",
                title="No structured data (JSON-LD) found",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                description="Adding schema markup improves rich snippet eligibility",
                fix_available=True,
            ))

        # HTTPS check
        headers = fetch.get("headers", {})
        if ctx.target_url.startswith("http://"):
            ctx.issues.append(Issue(
                code="TECH-060",
                title="Page served over HTTP (not HTTPS)",
                severity=Severity.CRITICAL,
                module="inspector",
                url=ctx.target_url,
                description="All pages should be served over HTTPS",
                fix_available=True,
            ))

        # Security headers
        if "strict-transport-security" not in {k.lower() for k in headers.keys()}:
            ctx.issues.append(Issue(
                code="TECH-061",
                title="Missing HSTS header",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                fix_available=True,
            ))

        # Word count
        word_count = page.get("word_count", 0)
        if word_count < 300:
            ctx.issues.append(Issue(
                code="TECH-070",
                title="Thin content (< 300 words)",
                severity=Severity.MEDIUM,
                module="inspector",
                url=ctx.target_url,
                description=f"Page has only {word_count} words",
                evidence={"word_count": word_count},
            ))
