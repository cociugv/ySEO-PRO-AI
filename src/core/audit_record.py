"""
Audit Record — Typed data model for SEO audit results.

Replaces the mutable dict (scan_data) with a structured dataclass.
Modules consume typed facts, not magic dict keys.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FetchFacts:
    """Facts about the HTTP fetch operation."""
    status_code: int = 0
    elapsed_ms: float = 0
    headers: dict = field(default_factory=dict)
    from_cache: bool = False
    error: str = ""

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400


@dataclass
class PageFacts:
    """Parsed page data — immutable facts extracted from HTML."""
    url: str = ""
    title: str = ""
    title_length: int = 0
    meta_description: str = ""
    description_length: int = 0
    canonical: str = ""
    lang: str = ""
    meta_robots: str = ""
    viewport: str = ""
    h1: list = field(default_factory=list)
    h2: list = field(default_factory=list)
    h3: list = field(default_factory=list)
    internal_links_count: int = 0
    external_links_count: int = 0
    images_count: int = 0
    images_without_alt: int = 0
    hreflang_tags: list = field(default_factory=list)
    json_ld_count: int = 0
    word_count: int = 0
    og_title: str = ""
    og_description: str = ""
    has_analytics: bool = False

    @classmethod
    def from_parser(cls, page_data) -> "PageFacts":
        """Build from parser's PageData object."""
        return cls(
            url=page_data.url,
            title=page_data.title,
            title_length=page_data.title_length,
            meta_description=page_data.meta_description,
            description_length=page_data.description_length,
            canonical=page_data.canonical,
            lang=page_data.lang,
            meta_robots=page_data.meta_robots,
            viewport=page_data.viewport,
            h1=page_data.h1,
            h2=page_data.h2,
            h3=page_data.h3,
            internal_links_count=len(page_data.internal_links),
            external_links_count=len(page_data.external_links),
            images_count=len(page_data.images),
            images_without_alt=sum(1 for img in page_data.images if not img.get("alt")),
            hreflang_tags=[{"lang": t["lang"], "url": t["url"]} for t in page_data.hreflang_tags],
            json_ld_count=len(page_data.json_ld),
            word_count=page_data.word_count,
            og_title=page_data.og_title,
            og_description=page_data.og_description,
            has_analytics=page_data.has_analytics,
        )

    def to_dict(self) -> dict:
        """Serialize for JSON output."""
        return {
            "url": self.url,
            "title": self.title,
            "title_length": self.title_length,
            "meta_description": self.meta_description,
            "description_length": self.description_length,
            "canonical": self.canonical,
            "lang": self.lang,
            "meta_robots": self.meta_robots,
            "viewport": self.viewport,
            "h1": self.h1,
            "h2": self.h2,
            "h3": self.h3,
            "internal_links_count": self.internal_links_count,
            "external_links_count": self.external_links_count,
            "images_count": self.images_count,
            "images_without_alt": self.images_without_alt,
            "hreflang_count": len(self.hreflang_tags),
            "hreflang_tags": self.hreflang_tags,
            "json_ld_count": self.json_ld_count,
            "word_count": self.word_count,
            "og_title": self.og_title,
            "has_analytics": self.has_analytics,
        }


@dataclass
class AIReadinessFacts:
    """Derived AI readiness scores."""
    overall_score: int = 0
    citability: int = 0
    entity_presence: int = 0
    answer_clarity: int = 0
    structure: int = 0
    authority: int = 0
    freshness: int = 0
    recommendations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "breakdown": {
                "citability": self.citability,
                "entity_presence": self.entity_presence,
                "answer_clarity": self.answer_clarity,
                "structure": self.structure,
                "authority": self.authority,
                "freshness": self.freshness,
            },
            "recommendations": self.recommendations,
        }


@dataclass
class AuditRecord:
    """
    Complete typed audit record.

    Owns all invariants and derived facts. Modules read from typed fields,
    not magic dict keys with implicit ordering constraints.
    """
    url: str
    fetch: FetchFacts = field(default_factory=FetchFacts)
    page: PageFacts = field(default_factory=PageFacts)
    ai_readiness: Optional[AIReadinessFacts] = None

    def to_dict(self) -> dict:
        result = {
            "url": self.url,
            "fetch": {
                "status_code": self.fetch.status_code,
                "elapsed_ms": self.fetch.elapsed_ms,
                "ok": self.fetch.ok,
            },
            "page": self.page.to_dict(),
        }
        if self.ai_readiness:
            result["ai_readiness"] = self.ai_readiness.to_dict()
        return result
