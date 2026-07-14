"""
Sentinel Agent — SEO drift monitoring specialist.

Capabilities:
- Capture SEO snapshots
- Compare current state vs baseline
- Detect regressions
- Alert on critical changes
"""

import time
from .base_agent import BaseAgent, AgentResult
from ..core.fetcher import PageFetcher
from ..core.parser import parse_html
from ..modules.sentinel.snapshot import SnapshotManager
from ..modules.sentinel.comparator import DriftComparator


class SentinelAgent(BaseAgent):
    name = "sentinel"
    role = "SEO Drift Monitor"
    capabilities = ["monitor", "drift", "snapshot", "baseline", "alert"]
    modules_used = ["sentinel"]

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Run drift monitoring — capture snapshot and compare to baseline."""
        start = time.time()
        context = context or {}
        action = context.get("action", "auto")  # auto | baseline | compare

        fetcher = PageFetcher()
        manager = SnapshotManager()
        comparator = DriftComparator()

        # Fetch current state
        result = fetcher.fetch(target_url, use_cache=False)
        if not result.ok:
            return AgentResult(
                agent_name=self.name,
                success=False,
                summary=f"Cannot monitor: page returned HTTP {result.status_code}",
                elapsed_seconds=time.time() - start,
            )

        page_data = parse_html(result.body, target_url).to_dict()
        fetch_data = {
            "status_code": result.status_code,
            "elapsed_ms": result.elapsed_ms,
        }

        # Capture snapshot
        snapshot = manager.capture(target_url, page_data, fetch_data)

        # Determine action
        if action == "baseline":
            return AgentResult(
                agent_name=self.name,
                success=True,
                summary=f"Baseline captured for {target_url}",
                data={"snapshot": snapshot.to_dict()},
                elapsed_seconds=time.time() - start,
            )

        # Compare to baseline
        baseline = manager.get_baseline(target_url)
        if not baseline or baseline.timestamp == snapshot.timestamp:
            return AgentResult(
                agent_name=self.name,
                success=True,
                summary="First snapshot captured (no baseline to compare yet)",
                data={"snapshot": snapshot.to_dict()},
                elapsed_seconds=time.time() - start,
            )

        # Run comparison
        drift_report = comparator.compare(baseline, snapshot)
        drift_issues = comparator.to_issues(drift_report)

        elapsed = time.time() - start

        has_regressions = drift_report.has_regressions
        status_msg = "REGRESSIONS DETECTED" if has_regressions else "No critical changes"

        return AgentResult(
            agent_name=self.name,
            success=True,
            summary=f"Drift: {drift_report.change_count} changes detected. {status_msg}",
            data={
                "drift_report": drift_report.to_dict(),
                "current_snapshot": snapshot.to_dict(),
            },
            issues_found=len(drift_issues),
            recommendations=[
                c.description for c in drift_report.changes
                if c.severity.value in ("critical", "high")
            ],
            elapsed_seconds=elapsed,
        )
