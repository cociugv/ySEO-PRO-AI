"""
Inspector Agent — Technical SEO analysis specialist.

Capabilities:
- Full technical audit (30+ checks)
- Performance analysis
- Security header validation
- Mobile-friendliness assessment
- Structured data validation
"""

import time
from .base_agent import BaseAgent, AgentResult
from ..core.pipeline import PipelineRunner, Stage
from ..modules.inspector.scanner import TechnicalScanner
from ..modules.inspector.checks import run_all_checks


class InspectorAgent(BaseAgent):
    name = "inspector"
    role = "Technical SEO Analyst"
    capabilities = ["audit", "technical", "performance", "security", "mobile"]
    modules_used = ["inspector"]

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Run technical SEO analysis."""
        start = time.time()

        pipeline = PipelineRunner(self.config)
        scanner = TechnicalScanner(self.config.get("modules", {}).get("inspector", {}))
        scanner.register(pipeline)

        # Run scan + diagnose
        ctx = pipeline.execute(target_url, stages=[Stage.SCAN, Stage.DIAGNOSE])

        # Run additional standalone checks
        run_all_checks(ctx)

        elapsed = time.time() - start

        return AgentResult(
            agent_name=self.name,
            success=len(ctx.errors) == 0,
            summary=f"Found {len(ctx.issues)} technical issues. Score: {ctx.score}/100",
            data={
                "score": ctx.score,
                "page_data": ctx.scan_data.get("page", {}),
                "issues": [i.to_dict() for i in ctx.issues],
            },
            issues_found=len(ctx.issues),
            fixes_applied=0,
            recommendations=[
                i.description for i in ctx.issues
                if i.description and i.fix_available
            ][:5],
            elapsed_seconds=elapsed,
        )
