"""
Pipeline Engine — Heart of ySEO-PRO-AI

The pipeline processes SEO tasks through 5 stages:
  1. SCAN    — Crawl and collect raw data
  2. DIAGNOSE — Analyze data, identify issues with severity
  3. FIX     — Auto-remediate fixable issues
  4. VERIFY  — Confirm fixes applied correctly
  5. REPORT  — Generate actionable output

Each module plugs into one or more stages.
"""

import time
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class Stage(Enum):
    SCAN = "scan"
    DIAGNOSE = "diagnose"
    FIX = "fix"
    VERIFY = "verify"
    REPORT = "report"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Issue:
    """A single SEO issue found during diagnosis."""
    code: str
    title: str
    severity: Severity
    module: str
    url: str = ""
    description: str = ""
    fix_available: bool = False
    fix_applied: bool = False
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "severity": self.severity.value,
            "module": self.module,
            "url": self.url,
            "description": self.description,
            "fix_available": self.fix_available,
            "fix_applied": self.fix_applied,
            "evidence": self.evidence,
        }


@dataclass
class PipelineContext:
    """Shared context flowing through pipeline stages."""
    target_url: str
    config: dict = field(default_factory=dict)
    scan_data: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    fixes_applied: list = field(default_factory=list)
    verification_results: dict = field(default_factory=dict)
    report_data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    started_at: float = field(default_factory=time.time)
    errors: list = field(default_factory=list)

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.started_at

    @property
    def score(self) -> int:
        """Calculate overall SEO score (0-100)."""
        if not self.issues:
            return 100
        deductions = {
            Severity.CRITICAL: 15,
            Severity.HIGH: 8,
            Severity.MEDIUM: 4,
            Severity.LOW: 2,
            Severity.INFO: 0,
        }
        total_deduction = sum(
            deductions.get(issue.severity, 0)
            for issue in self.issues
            if not issue.fix_applied
        )
        return max(0, 100 - total_deduction)


class PipelineRunner:
    """
    Orchestrates module execution through pipeline stages.

    Usage:
        runner = PipelineRunner(config)
        runner.register(Stage.SCAN, my_scanner_func)
        runner.register(Stage.DIAGNOSE, my_diagnoser_func)
        context = runner.execute("https://example.com")
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._handlers: dict[Stage, list[Callable]] = {s: [] for s in Stage}
        self._hooks: dict[str, list[Callable]] = {
            "before_stage": [],
            "after_stage": [],
            "on_error": [],
            "on_complete": [],
        }

    def register(self, stage: Stage, handler: Callable) -> None:
        """Register a handler function for a pipeline stage."""
        self._handlers[stage].append(handler)

    def hook(self, event: str, callback: Callable) -> None:
        """Register a lifecycle hook."""
        if event in self._hooks:
            self._hooks[event].append(callback)

    def execute(self, target_url: str, stages: list[Stage] = None) -> PipelineContext:
        """Run the full pipeline for a target URL."""
        ctx = PipelineContext(
            target_url=target_url,
            config=self.config,
        )

        active_stages = stages or list(Stage)

        for stage in active_stages:
            self._fire_hooks("before_stage", ctx, stage)
            handlers = self._handlers.get(stage, [])

            for handler in handlers:
                try:
                    handler(ctx)
                except Exception as exc:
                    ctx.errors.append({
                        "stage": stage.value,
                        "handler": handler.__name__,
                        "error": str(exc),
                    })
                    self._fire_hooks("on_error", ctx, stage, exc)

            self._fire_hooks("after_stage", ctx, stage)

        self._fire_hooks("on_complete", ctx)
        return ctx

    def _fire_hooks(self, event: str, *args) -> None:
        for callback in self._hooks.get(event, []):
            try:
                callback(*args)
            except Exception:
                pass
