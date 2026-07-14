"""
CITADEL Module — Schema Intelligence & AI Search Readiness

Features:
- Auto-detect page type (article, product, FAQ, service, etc.)
- Auto-inject appropriate schema.org markup
- AI Search Readiness Score (citability, entity presence, clear answers)
- Validate existing structured data
- Generate FAQ schema from content
- Generate Organization/WebSite schema
"""

from .schema_engine import SchemaEngine
from .ai_readiness import AIReadinessScorer

__all__ = ["SchemaEngine", "AIReadinessScorer"]
