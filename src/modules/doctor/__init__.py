"""
DOCTOR Module — Auto-Fix Engine

Unlike audit-only tools, Doctor FIXES issues automatically:
- Generates missing meta tags
- Fixes broken canonical URLs
- Creates robots.txt
- Generates XML sitemaps
- Injects schema markup
- Fixes hreflang tags
- Optimizes title/description length

Each fix is:
1. Backed up before modification
2. Applied with dry-run option
3. Verified after application
"""

from .fixer import AutoFixer, FixArtifact, FixStatus

__all__ = ["AutoFixer", "FixArtifact", "FixStatus"]
