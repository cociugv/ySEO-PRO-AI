"""
SENTINEL Module — SEO Drift Monitoring & Alerts

Monitors your site for SEO regressions over time:
- Takes snapshots of SEO state
- Compares current vs baseline
- Alerts on critical changes (title changed, noindex added, etc.)
- Tracks historical drift over time
- Configurable alert thresholds
"""

from .snapshot import SnapshotManager
from .comparator import DriftComparator

__all__ = ["SnapshotManager", "DriftComparator"]
