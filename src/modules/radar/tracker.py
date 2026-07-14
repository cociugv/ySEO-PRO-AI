"""
Competitor Tracker — Monitors competitor SEO state changes.

Captures competitor snapshots and compares against your site.
"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional
from ...core.fetcher import PageFetcher
from ...core.parser import parse_html


@dataclass
class CompetitorProfile:
    """SEO profile of a competitor."""
    domain: str
    last_checked: float = 0
    title: str = ""
    meta_description: str = ""
    h1: list = field(default_factory=list)
    word_count: int = 0
    schema_types: list = field(default_factory=list)
    hreflang_count: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    response_time_ms: float = 0
    technologies: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "last_checked": self.last_checked,
            "title": self.title,
            "meta_description": self.meta_description,
            "h1": self.h1,
            "word_count": self.word_count,
            "schema_types": self.schema_types,
            "hreflang_count": self.hreflang_count,
            "internal_links_count": self.internal_links_count,
            "external_links_count": self.external_links_count,
            "response_time_ms": self.response_time_ms,
        }


@dataclass
class ComparisonResult:
    """Side-by-side comparison between your site and a competitor."""
    your_domain: str
    competitor_domain: str
    metrics: dict = field(default_factory=dict)
    advantages: list = field(default_factory=list)
    disadvantages: list = field(default_factory=list)


class CompetitorTracker:
    """
    Tracks and compares competitor SEO metrics.

    Storage: .yseo/competitors/{domain}/latest.json
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.storage_dir = ".yseo/competitors"
        self.fetcher = PageFetcher(rate_limit_ms=2000)
        os.makedirs(self.storage_dir, exist_ok=True)

    def scan_competitor(self, url: str) -> CompetitorProfile:
        """Scan a competitor's homepage and build profile."""
        result = self.fetcher.fetch(url)
        profile = CompetitorProfile(
            domain=url,
            last_checked=time.time(),
            response_time_ms=result.elapsed_ms,
        )

        if result.ok and result.is_html:
            page_data = parse_html(result.body, url)
            profile.title = page_data.title
            profile.meta_description = page_data.meta_description
            profile.h1 = page_data.h1
            profile.word_count = page_data.word_count
            profile.hreflang_count = len(page_data.hreflang_tags)
            profile.internal_links_count = len(page_data.internal_links)
            profile.external_links_count = len(page_data.external_links)

            # Extract schema types
            for ld in page_data.json_ld:
                try:
                    schema = json.loads(ld)
                    schema_type = schema.get("@type", "")
                    if schema_type:
                        profile.schema_types.append(schema_type)
                except json.JSONDecodeError:
                    pass

        self._save_profile(profile)
        return profile

    def compare(self, your_url: str, competitor_url: str) -> ComparisonResult:
        """Compare your site against a competitor."""
        your_profile = self.scan_competitor(your_url)
        comp_profile = self.scan_competitor(competitor_url)

        result = ComparisonResult(
            your_domain=your_url,
            competitor_domain=competitor_url,
        )

        # Compare metrics
        metrics = {
            "word_count": (your_profile.word_count, comp_profile.word_count),
            "response_time_ms": (your_profile.response_time_ms, comp_profile.response_time_ms),
            "hreflang_count": (your_profile.hreflang_count, comp_profile.hreflang_count),
            "schema_types": (len(your_profile.schema_types), len(comp_profile.schema_types)),
            "internal_links": (your_profile.internal_links_count, comp_profile.internal_links_count),
        }
        result.metrics = metrics

        # Determine advantages / disadvantages
        if your_profile.word_count > comp_profile.word_count:
            result.advantages.append("More content (higher word count)")
        elif comp_profile.word_count > your_profile.word_count * 1.5:
            result.disadvantages.append("Competitor has significantly more content")

        if your_profile.response_time_ms < comp_profile.response_time_ms:
            result.advantages.append("Faster page load")
        elif your_profile.response_time_ms > comp_profile.response_time_ms * 1.5:
            result.disadvantages.append("Competitor is significantly faster")

        if your_profile.hreflang_count > comp_profile.hreflang_count:
            result.advantages.append("Better multilingual coverage")

        if len(your_profile.schema_types) > len(comp_profile.schema_types):
            result.advantages.append("More structured data markup")
        elif len(comp_profile.schema_types) > len(your_profile.schema_types):
            result.disadvantages.append("Competitor has more schema markup")

        return result

    def _save_profile(self, profile: CompetitorProfile) -> None:
        """Save competitor profile to disk."""
        from urllib.parse import urlparse
        domain = urlparse(profile.domain).netloc or profile.domain
        domain_dir = os.path.join(self.storage_dir, domain.replace(":", "_"))
        os.makedirs(domain_dir, exist_ok=True)

        filepath = os.path.join(domain_dir, "latest.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2)
