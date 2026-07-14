"""
Operations — Deep execution module for ySEO-PRO-AI.

Single entry point for all SEO operations. Callers (CLI, MCP bridge, Crew agents)
choose WHAT to do, never HOW — stage ordering, module registration, and result
assembly are encapsulated here.

This is the "deep module" that hides pipeline internals from all adapters.
"""

import time
from dataclasses import dataclass, field
from typing import Optional

from .pipeline import PipelineRunner, PipelineContext, Stage, Issue, Severity
from .fetcher import PageFetcher
from .parser import parse_html
from .config_loader import load_config


@dataclass
class OperationResult:
    """Uniform result from any SEO operation."""
    success: bool
    url: str
    operation: str
    score: int = 0
    issues: list = field(default_factory=list)
    fixes: list = field(default_factory=list)
    data: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    elapsed_seconds: float = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "url": self.url,
            "operation": self.operation,
            "score": self.score,
            "issues_count": len(self.issues),
            "fixable_count": sum(1 for i in self.issues if i.get("fix_available")),
            "fixes_applied": len(self.fixes),
            "issues": self.issues,
            "fixes": self.fixes,
            "data": self.data,
            "errors": self.errors,
            "elapsed_seconds": self.elapsed_seconds,
        }


class SEOOperations:
    """
    Deep module that owns ALL execution logic.

    Adapters call one method → get one OperationResult.
    No knowledge of stages, module registration, or pipeline internals leaks out.
    """

    def __init__(self, config: dict = None, project_root: str = "."):
        self.config = config or load_config(project_root)
        self._project_root = project_root

    def scan(self, url: str) -> OperationResult:
        """Quick scan — fetch + parse, no diagnosis."""
        start = time.time()
        fetcher = PageFetcher()
        result = fetcher.fetch(url)

        if not result.ok:
            return OperationResult(
                success=False, url=url, operation="scan",
                errors=[f"HTTP {result.status_code}: {result.error}"],
                elapsed_seconds=time.time() - start,
            )

        page = parse_html(result.body, url)
        return OperationResult(
            success=True, url=url, operation="scan", score=100,
            data={
                "page": page.to_dict(),
                "fetch": {
                    "status_code": result.status_code,
                    "elapsed_ms": result.elapsed_ms,
                    "from_cache": result.from_cache,
                },
            },
            elapsed_seconds=time.time() - start,
        )

    def audit(self, url: str) -> OperationResult:
        """Full SEO audit — scan + diagnose all modules."""
        start = time.time()
        pipeline = self._build_pipeline(stages=[Stage.SCAN, Stage.DIAGNOSE])
        ctx = pipeline.execute(url, stages=[Stage.SCAN, Stage.DIAGNOSE])

        # Run additional standalone checks
        from ..modules.inspector.checks import run_all_checks
        run_all_checks(ctx)

        return OperationResult(
            success=len(ctx.errors) == 0,
            url=url, operation="audit", score=ctx.score,
            issues=[i.to_dict() for i in ctx.issues],
            data={
                "page": ctx.scan_data.get("page", {}),
                "ai_readiness": ctx.scan_data.get("ai_readiness", {}),
            },
            errors=ctx.errors,
            elapsed_seconds=time.time() - start,
        )

    def fix(self, url: str, dry_run: bool = True) -> OperationResult:
        """Audit + auto-fix — scan, diagnose, then fix fixable issues."""
        start = time.time()
        pipeline = self._build_pipeline(
            stages=[Stage.SCAN, Stage.DIAGNOSE, Stage.FIX],
            fix_dry_run=dry_run,
        )
        ctx = pipeline.execute(url, stages=[Stage.SCAN, Stage.DIAGNOSE, Stage.FIX])

        return OperationResult(
            success=True, url=url, operation="fix", score=ctx.score,
            issues=[i.to_dict() for i in ctx.issues],
            fixes=ctx.fixes_applied,
            data={"dry_run": dry_run},
            errors=ctx.errors,
            elapsed_seconds=time.time() - start,
        )

    def ai_readiness(self, url: str) -> OperationResult:
        """Calculate AI Search Readiness Score."""
        start = time.time()
        fetcher = PageFetcher()
        result = fetcher.fetch(url)

        if not result.ok:
            return OperationResult(
                success=False, url=url, operation="ai_readiness",
                errors=[f"HTTP {result.status_code}: {result.error}"],
                elapsed_seconds=time.time() - start,
            )

        page = parse_html(result.body, url)

        from ..modules.citadel.ai_readiness import AIReadinessScorer
        scorer = AIReadinessScorer()
        report = scorer.calculate_score(url, page.to_dict())

        return OperationResult(
            success=True, url=url, operation="ai_readiness",
            score=report.overall_score,
            data=report.to_dict(),
            elapsed_seconds=time.time() - start,
        )

    def monitor_baseline(self, url: str) -> OperationResult:
        """Capture SEO snapshot as baseline."""
        start = time.time()
        fetcher = PageFetcher()
        result = fetcher.fetch(url, use_cache=False)

        if not result.ok:
            return OperationResult(
                success=False, url=url, operation="monitor_baseline",
                errors=[f"HTTP {result.status_code}"],
                elapsed_seconds=time.time() - start,
            )

        page = parse_html(result.body, url)

        from ..modules.sentinel.snapshot import SnapshotManager
        manager = SnapshotManager()
        snapshot = manager.capture(url, page.to_dict(), {
            "status_code": result.status_code,
            "elapsed_ms": result.elapsed_ms,
        })

        return OperationResult(
            success=True, url=url, operation="monitor_baseline",
            data={"snapshot": snapshot.to_dict()},
            elapsed_seconds=time.time() - start,
        )

    def monitor_compare(self, url: str) -> OperationResult:
        """Compare current state vs baseline."""
        start = time.time()
        fetcher = PageFetcher()
        result = fetcher.fetch(url, use_cache=False)

        if not result.ok:
            return OperationResult(
                success=False, url=url, operation="monitor_compare",
                errors=[f"HTTP {result.status_code}"],
                elapsed_seconds=time.time() - start,
            )

        page = parse_html(result.body, url)

        from ..modules.sentinel.snapshot import SnapshotManager
        from ..modules.sentinel.comparator import DriftComparator

        manager = SnapshotManager()
        current = manager.capture(url, page.to_dict(), {
            "status_code": result.status_code,
            "elapsed_ms": result.elapsed_ms,
        })
        baseline = manager.get_baseline(url)

        if not baseline or baseline.timestamp == current.timestamp:
            return OperationResult(
                success=True, url=url, operation="monitor_compare",
                data={"message": "First snapshot — no baseline to compare", "snapshot": current.to_dict()},
                elapsed_seconds=time.time() - start,
            )

        comparator = DriftComparator()
        report = comparator.compare(baseline, current)

        return OperationResult(
            success=True, url=url, operation="monitor_compare",
            issues=[c.to_dict() for c in report.changes],
            data=report.to_dict(),
            elapsed_seconds=time.time() - start,
        )

    def generate_schema(self, url: str, force_type: str = "auto") -> OperationResult:
        """Generate schema.org markup for a page."""
        start = time.time()
        fetcher = PageFetcher()
        result = fetcher.fetch(url)

        if not result.ok:
            return OperationResult(
                success=False, url=url, operation="generate_schema",
                errors=[f"HTTP {result.status_code}"],
                elapsed_seconds=time.time() - start,
            )

        page = parse_html(result.body, url)

        from ..modules.citadel.schema_engine import SchemaEngine
        engine = SchemaEngine()
        detected = engine.detect_page_type(url, page.to_dict()) if force_type == "auto" else force_type
        schema = engine.generate_schema(detected, url, page.to_dict())

        import json
        return OperationResult(
            success=True, url=url, operation="generate_schema",
            data={
                "detected_type": detected,
                "schema": schema,
                "json_ld": f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>',
            },
            elapsed_seconds=time.time() - start,
        )

    def generate_hreflang(self, url: str, languages: list[str]) -> OperationResult:
        """Generate hreflang tag set."""
        start = time.time()
        from ..modules.polyglot.hreflang import HreflangAuditor
        auditor = HreflangAuditor({"languages": languages})
        tags = auditor.generate_hreflang_set(url, languages)

        return OperationResult(
            success=True, url=url, operation="generate_hreflang",
            data={"languages": languages, "html": tags, "tag_count": len(languages) + 1},
            elapsed_seconds=time.time() - start,
        )

    def competitor_compare(self, your_url: str, competitor_url: str) -> OperationResult:
        """Compare your site vs competitor."""
        start = time.time()
        from ..modules.radar.tracker import CompetitorTracker
        tracker = CompetitorTracker()
        comparison = tracker.compare(your_url, competitor_url)

        return OperationResult(
            success=True, url=your_url, operation="competitor_compare",
            data={
                "competitor": competitor_url,
                "metrics": {k: {"yours": v[0], "theirs": v[1]} for k, v in comparison.metrics.items()},
                "advantages": comparison.advantages,
                "disadvantages": comparison.disadvantages,
            },
            elapsed_seconds=time.time() - start,
        )

    def backlink_opportunities(self, domain: str, keywords: list[str] = None) -> OperationResult:
        """Find backlink opportunities."""
        start = time.time()
        from ..modules.radar.opportunities import BacklinkFinder
        finder = BacklinkFinder()
        directories = finder.find_directories(domain)
        guest_posts = finder.find_guest_post_targets(keywords or [])
        all_opps = directories + guest_posts
        plan = finder.generate_outreach_plan(all_opps)

        return OperationResult(
            success=True, url=domain, operation="backlink_opportunities",
            data={"total": len(all_opps), "directories": len(directories),
                  "guest_queries": len(guest_posts), "plan": plan},
            elapsed_seconds=time.time() - start,
        )

    def indexnow_ping(self, urls: list[str], key: str = "") -> OperationResult:
        """Ping IndexNow with URLs."""
        start = time.time()
        from ..modules.publisher.indexnow import IndexNowPinger
        pinger_config = self.config.get("integrations", {}).get("indexnow", {})
        if key:
            pinger_config["indexnow_key"] = key
        pinger = IndexNowPinger(pinger_config)

        if len(urls) == 1:
            r = pinger.ping_single(urls[0])
            return OperationResult(
                success=r.success, url=urls[0], operation="indexnow_ping",
                data={"engine": r.engine, "status_code": r.status_code},
                errors=[r.error] if r.error else [],
                elapsed_seconds=time.time() - start,
            )
        else:
            results = pinger.ping_all_engines(urls)
            return OperationResult(
                success=any(r.success for r in results),
                url=urls[0] if urls else "", operation="indexnow_ping",
                data={"urls_count": len(urls), "engines_ok": sum(1 for r in results if r.success)},
                elapsed_seconds=time.time() - start,
            )

    # ─── Private: pipeline construction ────────────────────────────────

    def _build_pipeline(self, stages: list[Stage], fix_dry_run: bool = True) -> PipelineRunner:
        """Internal: construct pipeline with appropriate modules for requested stages."""
        pipeline = PipelineRunner(self.config)

        # Always register scanner for SCAN/DIAGNOSE
        if Stage.SCAN in stages or Stage.DIAGNOSE in stages:
            from ..modules.inspector.scanner import TechnicalScanner
            TechnicalScanner(self.config.get("modules", {}).get("inspector", {})).register(pipeline)

            from ..modules.citadel.schema_engine import SchemaEngine
            SchemaEngine(self.config.get("modules", {}).get("citadel", {})).register(pipeline)

            from ..modules.citadel.ai_readiness import AIReadinessScorer
            AIReadinessScorer().register(pipeline)

            languages = self.config.get("targets", {}).get("languages", ["en"])
            from ..modules.polyglot.hreflang import HreflangAuditor
            from ..modules.polyglot.locale import LocaleDetector
            HreflangAuditor({"languages": languages}).register(pipeline)
            LocaleDetector({"languages": languages}).register(pipeline)

        # Register fixer only for FIX stage
        if Stage.FIX in stages:
            from ..modules.doctor.fixer import AutoFixer
            fix_config = self.config.get("modules", {}).get("doctor", {})
            fix_config["dry_run"] = fix_dry_run
            AutoFixer(fix_config).register(pipeline)

        return pipeline
