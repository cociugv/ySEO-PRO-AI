"""
ARCHITECT Module — Programmatic SEO Page Generator

Creates templated pages at scale:
- City/location pages (e.g., "URL Shortener in Berlin")
- Comparison pages (e.g., "yLink vs Bitly")
- Feature pages (e.g., "QR Code Generator with Logo")
- Integration pages (e.g., "Zapier Integration for URL Shortener")
- Use case pages (e.g., "URL Shortener for Social Media Marketing")
"""

from .generator import ProgrammaticGenerator
from .templates import TemplateEngine

__all__ = ["ProgrammaticGenerator", "TemplateEngine"]
