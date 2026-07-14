"""
Crew Orchestrator — Routes tasks to specialist agents and aggregates results.

The orchestrator:
1. Analyzes the incoming request
2. Determines which agents to activate
3. Executes them (parallel when possible)
4. Aggregates results into a unified report
"""

import time
from dataclasses import dataclass, field
from typing import Optional
from .base_agent import BaseAgent, AgentResult
from .inspector_agent import InspectorAgent
from .doctor_agent import DoctorAgent
from .polyglot_agent import PolyglotAgent
from .sentinel_agent import SentinelAgent
from .publisher_agent import PublisherAgent
from .strategist_agent import StrategistAgent


@dataclass
class CrewReport:
    """Aggregated report from all executed agents."""
    target_url: str
    total_issues: int = 0
    total_fixes: int = 0
    overall_score: int = 0
    agent_results: list = field(default_factory=list)
    elapsed_seconds: float = 0

    def to_dict(self) -> dict:
        return {
            "target": self.target_url,
            "total_issues": self.total_issues,
            "total_fixes": self.total_fixes,
            "overall_score": self.overall_score,
            "agents_executed": len(self.agent_results),
            "elapsed_seconds": self.elapsed_seconds,
            "results": [r.to_dict() for r in self.agent_results],
        }

    @property
    def summary(self) -> str:
        return (
            f"SEO Score: {self.overall_score}/100 | "
            f"Issues: {self.total_issues} | "
            f"Fixed: {self.total_fixes} | "
            f"Agents: {len(self.agent_results)}"
        )


class CrewOrchestrator:
    """
    Routes SEO tasks to specialized agents.

    Usage:
        crew = CrewOrchestrator(config)
        report = crew.full_audit("https://ylink.pro")
        report = crew.quick_scan("https://ylink.pro")
        report = crew.monitor("https://ylink.pro")
    """

    # Task type → agent mapping
    TASK_ROUTING = {
        "audit": ["inspector", "polyglot", "citadel"],
        "fix": ["inspector", "doctor"],
        "monitor": ["sentinel"],
        "publish": ["publisher"],
        "compete": ["strategist"],
        "full": ["inspector", "polyglot", "citadel", "doctor", "sentinel", "strategist"],
    }

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._agents: dict[str, BaseAgent] = {}
        self._register_agents()

    def _register_agents(self) -> None:
        """Initialize all available agents."""
        self._agents = {
            "inspector": InspectorAgent(self.config),
            "doctor": DoctorAgent(self.config),
            "polyglot": PolyglotAgent(self.config),
            "sentinel": SentinelAgent(self.config),
            "publisher": PublisherAgent(self.config),
            "strategist": StrategistAgent(self.config),
        }

    def full_audit(self, url: str) -> CrewReport:
        """Run all audit agents on a URL."""
        return self._execute_task("audit", url)

    def full_pipeline(self, url: str) -> CrewReport:
        """Run complete pipeline: audit + fix + monitor."""
        return self._execute_task("full", url)

    def quick_scan(self, url: str) -> CrewReport:
        """Quick scan — inspector only."""
        return self._execute_task("audit", url, agents=["inspector"])

    def auto_fix(self, url: str) -> CrewReport:
        """Run auto-fix pipeline."""
        return self._execute_task("fix", url)

    def monitor(self, url: str) -> CrewReport:
        """Run drift monitoring."""
        return self._execute_task("monitor", url)

    def compete(self, url: str, competitor_url: str) -> CrewReport:
        """Run competitor analysis."""
        return self._execute_task("compete", url, context={"competitor": competitor_url})

    def _execute_task(
        self,
        task_type: str,
        url: str,
        agents: list = None,
        context: dict = None,
    ) -> CrewReport:
        """Execute a task by routing to appropriate agents."""
        start = time.time()
        report = CrewReport(target_url=url)

        # Determine agents to use
        agent_names = agents or self.TASK_ROUTING.get(task_type, ["inspector"])

        # Execute each agent
        for name in agent_names:
            agent = self._agents.get(name)
            if not agent:
                continue

            try:
                result = agent.execute(url, context)
                report.agent_results.append(result)
                report.total_issues += result.issues_found
                report.total_fixes += result.fixes_applied
            except Exception as e:
                report.agent_results.append(AgentResult(
                    agent_name=name,
                    success=False,
                    summary=f"Agent error: {str(e)}",
                ))

        # Calculate overall score
        if report.total_issues == 0:
            report.overall_score = 100
        else:
            unfixed = report.total_issues - report.total_fixes
            report.overall_score = max(0, 100 - (unfixed * 5))

        report.elapsed_seconds = time.time() - start
        return report

    def list_agents(self) -> list[dict]:
        """List all available agents and their capabilities."""
        return [agent.describe() for agent in self._agents.values()]
