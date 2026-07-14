"""
INSPECTOR Module — Technical SEO Scanner

Scans websites for technical SEO issues across categories:
- Crawlability (robots.txt, meta robots, canonical)
- Indexability (noindex, redirects, status codes)
- Performance (page speed, TTFB, resource sizes)
- Security (HTTPS, mixed content, headers)
- Mobile (viewport, responsive, tap targets)
- Structured Data (JSON-LD validation)
- Core Web Vitals indicators
"""

from .scanner import TechnicalScanner
from .checks import run_all_checks

__all__ = ["TechnicalScanner", "run_all_checks"]
