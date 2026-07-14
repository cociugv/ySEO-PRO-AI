"""
POLYGLOT Module — Multilingual SEO Intelligence

Specialized for multilingual SaaS sites (like yLink.pro with 14 languages).
Features:
- Hreflang audit (validates all alternate tags)
- Hreflang generation for missing languages
- Locale detection and validation
- Cross-language content consistency checks
- URL structure analysis (subdirectory vs subdomain vs ccTLD)
- x-default validation
- Return tag verification (bidirectional hreflang)
"""

from .hreflang import HreflangAuditor
from .locale import LocaleDetector

__all__ = ["HreflangAuditor", "LocaleDetector"]
