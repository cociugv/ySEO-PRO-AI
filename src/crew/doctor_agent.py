"""
Doctor Agent — Auto-fix specialist.

Capabilities:
- Applies fixes for all fixable issues
- Generates missing meta tags, robots.txt, sitemaps
- Injects schema markup
- Supports dry-run mode
"""

import time
from .base_agent import BaseAgent, AgentResult
from ..core.pipeline import PipelineRunner, Stage
from ..modules.inspector.scanner import TechnicalScanner
from ..modules.doctor.fixer import AutoFixer


class DoctorAgent(BaseAgent):
    name = "doctor"
    role = "SEO Auto-Fix Specialist"
    capabilities = ["fix", "generate", "repair", "optimize"]
    modules_used = ["inspector", "doctor"]

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Run auto-fix pipeline."""
        start = time.time()
        context = context or {}

        pipeline = PipelineRunner(self.config)

        # Need inspector first to find issues
        scanner = TechnicalScanner(self.config.get("modules", {}).get("inspector", {}))
        scanner.register(pipeline)

        # Then doctor to fix them
        fix_config = self.config.get("modules", {}).get("doctor", {})
        fix_config["dry_run"] = context.get("dry_run", False)
        fixer = AutoFixer(fix_config)
        fixer.register(pipeline)

        # Run scan + diagnose + fix
        ctx = pipeline.execute(target_url, stages=[Stage.SCAN, Stage.DIAGNOSE, Stage.FIX])

        elapsed = time.time() - start

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Fixed {len(ctx.fixes_applied)}/{len([i for i in ctx.issues if i.fix_available])} fixable issues",
            data={
                "fixes": ctx.fixes_applied,
                "remaining_issues": [i.to_dict() for i in ctx.issues if not i.fix_applied],
            },
            issues_found=len(ctx.issues),
            fixes_applied=len(ctx.fixes_applied),
            recommendations=[
                f"Manual fix needed: {i.title}"
                for i in ctx.issues
                if not i.fix_available
            ][:5],
            elapsed_seconds=elapsed,
        )
