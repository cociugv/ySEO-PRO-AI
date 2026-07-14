"""
Base Agent — Foundation for all ySEO-PRO-AI crew agents.

Each agent:
- Has a defined role and capabilities
- Accesses specific modules
- Produces structured results
- Can be run independently or orchestrated
"""

from dataclasses import dataclass, field
from typing import Any
from ..core.pipeline import PipelineContext


@dataclass
class AgentResult:
    """Structured result from an agent execution."""
    agent_name: str
    success: bool
    summary: str = ""
    data: dict = field(default_factory=dict)
    issues_found: int = 0
    fixes_applied: int = 0
    recommendations: list = field(default_factory=list)
    elapsed_seconds: float = 0

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "success": self.success,
            "summary": self.summary,
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "recommendations": self.recommendations,
            "elapsed_seconds": self.elapsed_seconds,
            "data": self.data,
        }


class BaseAgent:
    """
    Base class for all crew agents.

    Subclass and implement `execute()` for specialized behavior.
    """

    name: str = "base"
    role: str = "Generic Agent"
    capabilities: list = []
    modules_used: list = []

    def __init__(self, config: dict = None):
        self.config = config or {}

    def execute(self, target_url: str, context: dict = None) -> AgentResult:
        """Execute agent's task. Override in subclasses."""
        raise NotImplementedError(f"{self.name} agent must implement execute()")

    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle a specific task type."""
        return task_type in self.capabilities

    def describe(self) -> dict:
        """Return agent metadata for routing decisions."""
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "modules": self.modules_used,
        }
