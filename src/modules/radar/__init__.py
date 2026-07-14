"""
RADAR Module — Competitor Intelligence & Monitoring

Features:
- Track competitor SEO changes over time
- Compare technical SEO metrics side-by-side
- Monitor competitor content publishing frequency
- Detect new backlinks to competitors
- SERP position tracking
- Backlink opportunity finder (directories, guest post targets)
"""

from .tracker import CompetitorTracker
from .opportunities import BacklinkFinder

__all__ = ["CompetitorTracker", "BacklinkFinder"]
