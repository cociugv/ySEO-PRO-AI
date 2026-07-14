"""
Polyglot Agent — Multilingual SEO specialist.

Capabilities:
- Hreflang audit and generation
- Language detection and validation
- Cross-locale consistency checks
- URL i18n strategy analysis
"""

import time
from .base_agent import BaseAgent, AgentResult
from ..core.pipeline import PipelineRunner, Stage
from ..core.fetcher import PageFetcher
from ..core.parser import parse_html
from ..modules.polyglot.hreflang import HreflangAuditor
from ..modules.polyglot.locale import LocaleDetector


class PolyglotAgent(BaseAgent):
    name = "polyglot"
    role = "Multilingual SEO Specialist"
    capabilities = ["hreflang", "multilingual", "locale", "i18n", "translation"]
    modules_used = ["polyglot"]

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Run multilingual SEO analysis."""
        start = time.time()

        languages = self.config.get("targets", {}).get("languages", ["en"])
        polyglot_config = {"languages": languages}

        pipeline = PipelineRunner(self.config)

        # Fetch page first (for scan data)
        fetcher = PageFetcher()
        result = fetcher.fetch(target_url)

        from ..core.pipeline import PipelineContext
        ctx = PipelineContext(target_url=target_url, config=self.config)

        if result.ok and result.is_html:
            page_data = parse_html(result.body, target_url)
            ctx.scan_data["page"] = page_data.to_dict()
            ctx.scan_data["page"]["hreflang_tags"] = [
                {"lang": t["lang"], "url": t["url"]} for t in page_data.hreflang_tags
            ]

        # Run hreflang audit
        auditor = HreflangAuditor(polyglot_config)
        auditor.audit_hreflang(ctx)

        # Run locale detection
        detector = LocaleDetector(polyglot_config)
        detector.check_locale(ctx)

        # Detect URL strategy
        strategy = detector.detect_url_strategy(target_url)

        elapsed = time.time() - start

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Multilingual audit: {len(ctx.issues)} issues for {len(languages)}-language site (strategy: {strategy})",
            data={
                "languages_configured": languages,
                "url_strategy": strategy,
                "hreflang_found": len(ctx.scan_data.get("page", {}).get("hreflang_tags", [])),
                "issues": [i.to_dict() for i in ctx.issues],
            },
            issues_found=len(ctx.issues),
            recommendations=[
                i.description for i in ctx.issues if i.description
            ][:5],
            elapsed_seconds=elapsed,
        )
