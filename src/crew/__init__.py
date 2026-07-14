"""
ySEO-PRO-AI Crew — AI Agent Orchestration System

Unlike flat markdown agent files, Crew agents are class-based with:
- Defined capabilities and module access
- Task routing logic
- Parallel execution support
- Result aggregation

Agent Types:
- Orchestrator: Routes tasks to specialist agents
- Inspector Agent: Technical SEO analysis
- Doctor Agent: Auto-fix operations
- Polyglot Agent: Multilingual SEO
- Sentinel Agent: Drift monitoring
- Publisher Agent: Content publishing
- Strategist Agent: SEO planning + competitor intel
"""

from .orchestrator import CrewOrchestrator
from .base_agent import BaseAgent

__all__ = ["CrewOrchestrator", "BaseAgent"]
