"""
Drift Comparator — Detects SEO regressions between snapshots.

Compares current state against baseline and reports changes with severity.
"""

from dataclasses import dataclass, field
from typing import Optional
from .snapshot import SEOSnapshot
from ...core.pipeline import Issue, Severity


@dataclass
class DriftChange:
    """A single detected change between snapshots."""
    field: str
    old_value: str
    new_value: str
    severity: Severity
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "old": self.old_value,
            "new": self.new_value,
            "severity": self.severity.value,
            "description": self.description,
        }


@dataclass
class DriftReport:
    """Complete drift analysis between two snapshots."""
    url: str
    baseline_time: float
    current_time: float
    changes: list = field(default_factory=list)
    score_delta: int = 0

    @property
    def has_regressions(self) -> bool:
        return any(
            c.severity in (Severity.CRITICAL, Severity.HIGH)
            for c in self.changes
        )

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "baseline_time": self.baseline_time,
            "current_time": self.current_time,
            "change_count": self.change_count,
            "has_regressions": self.has_regressions,
            "changes": [c.to_dict() for c in self.changes],
        }


class DriftComparator:
    """Compares SEO snapshots and identifies regressions."""

    def compare(self, baseline: SEOSnapshot, current: SEOSnapshot) -> DriftReport:
        """Compare two snapshots and generate drift report."""
        report = DriftReport(
            url=current.url,
            baseline_time=baseline.timestamp,
            current_time=current.timestamp,
        )

        # Title change
        if baseline.title != current.title:
            severity = Severity.HIGH if not current.title else Severity.MEDIUM
            report.changes.append(DriftChange(
                field="title",
                old_value=baseline.title,
                new_value=current.title,
                severity=severity,
                description="Page title changed" if current.title else "Page title removed!",
            ))

        # Meta description change
        if baseline.meta_description != current.meta_description:
            severity = Severity.MEDIUM if current.meta_description else Severity.HIGH
            report.changes.append(DriftChange(
                field="meta_description",
                old_value=baseline.meta_description[:80],
                new_value=current.meta_description[:80],
                severity=severity,
                description="Meta description changed" if current.meta_description else "Meta description removed!",
            ))

        # Canonical change
        if baseline.canonical != current.canonical:
            report.changes.append(DriftChange(
                field="canonical",
                old_value=baseline.canonical,
                new_value=current.canonical,
                severity=Severity.HIGH,
                description="Canonical URL changed — may affect indexing",
            ))

        # H1 change
        if baseline.h1 != current.h1:
            report.changes.append(DriftChange(
                field="h1",
                old_value=str(baseline.h1),
                new_value=str(current.h1),
                severity=Severity.MEDIUM,
                description="H1 heading changed",
            ))

        # Robots directive change (CRITICAL if noindex added)
        if baseline.meta_robots != current.meta_robots:
            severity = Severity.CRITICAL if "noindex" in current.meta_robots.lower() else Severity.HIGH
            report.changes.append(DriftChange(
                field="meta_robots",
                old_value=baseline.meta_robots,
                new_value=current.meta_robots,
                severity=severity,
                description="NOINDEX ADDED — page will be deindexed!" if "noindex" in current.meta_robots.lower()
                           else "Robots directive changed",
            ))

        # Status code change
        if baseline.status_code != current.status_code:
            severity = Severity.CRITICAL if current.status_code >= 400 else Severity.HIGH
            report.changes.append(DriftChange(
                field="status_code",
                old_value=str(baseline.status_code),
                new_value=str(current.status_code),
                severity=severity,
                description=f"HTTP status changed from {baseline.status_code} to {current.status_code}",
            ))

        # Hreflang count change
        if baseline.hreflang_count != current.hreflang_count:
            severity = Severity.HIGH if current.hreflang_count < baseline.hreflang_count else Severity.INFO
            report.changes.append(DriftChange(
                field="hreflang_count",
                old_value=str(baseline.hreflang_count),
                new_value=str(current.hreflang_count),
                severity=severity,
                description=f"Hreflang tags changed: {baseline.hreflang_count} → {current.hreflang_count}",
            ))

        # Schema count change
        if baseline.schema_count != current.schema_count:
            severity = Severity.MEDIUM if current.schema_count < baseline.schema_count else Severity.INFO
            report.changes.append(DriftChange(
                field="schema_count",
                old_value=str(baseline.schema_count),
                new_value=str(current.schema_count),
                severity=severity,
                description=f"Schema markup count changed: {baseline.schema_count} → {current.schema_count}",
            ))

        # Word count significant change (> 20% drop)
        if baseline.word_count > 0:
            pct_change = (current.word_count - baseline.word_count) / baseline.word_count * 100
            if pct_change < -20:
                report.changes.append(DriftChange(
                    field="word_count",
                    old_value=str(baseline.word_count),
                    new_value=str(current.word_count),
                    severity=Severity.HIGH,
                    description=f"Content reduced by {abs(pct_change):.0f}% ({baseline.word_count} → {current.word_count} words)",
                ))

        # Response time degradation (> 2x slower)
        if baseline.response_time_ms > 0 and current.response_time_ms > baseline.response_time_ms * 2:
            report.changes.append(DriftChange(
                field="response_time_ms",
                old_value=f"{baseline.response_time_ms:.0f}ms",
                new_value=f"{current.response_time_ms:.0f}ms",
                severity=Severity.MEDIUM,
                description=f"Response time degraded: {baseline.response_time_ms:.0f}ms → {current.response_time_ms:.0f}ms",
            ))

        return report

    def to_issues(self, report: DriftReport) -> list[Issue]:
        """Convert drift report changes to pipeline Issues."""
        issues = []
        for change in report.changes:
            issues.append(Issue(
                code=f"DRIFT-{change.field.upper()[:8]}",
                title=change.description,
                severity=change.severity,
                module="sentinel",
                url=report.url,
                evidence={
                    "field": change.field,
                    "old": change.old_value,
                    "new": change.new_value,
                },
            ))
        return issues
