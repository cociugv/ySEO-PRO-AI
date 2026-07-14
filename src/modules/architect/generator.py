"""
Programmatic SEO Generator — Creates pages at scale from templates + data.

Supports page types:
- city: Location-based pages
- versus: Comparison pages (us vs competitor)
- usecase: Use case specific pages
- integration: Integration/partner pages
- feature: Feature-focused pages
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PageSpec:
    """Specification for a single generated page."""
    page_type: str
    slug: str
    title: str
    h1: str
    meta_description: str
    content_blocks: list = field(default_factory=list)
    schema_type: str = ""
    hreflang_base: str = ""
    internal_links: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    language: str = "en"

    def to_dict(self) -> dict:
        return {
            "type": self.page_type,
            "slug": self.slug,
            "title": self.title,
            "h1": self.h1,
            "meta_description": self.meta_description,
            "content_blocks": self.content_blocks,
            "schema_type": self.schema_type,
            "language": self.language,
            "keywords": self.keywords,
        }


class ProgrammaticGenerator:
    """
    Generates programmatic SEO page specifications at scale.

    Feed it templates + data and it produces page specs ready for publishing.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.brand_name = self.config.get("brand_name", "yLink.pro")
        self.base_url = self.config.get("base_url", "https://ylink.pro")
        self.languages = self.config.get("languages", ["en"])

    def generate_city_pages(self, cities: list[dict], template: dict = None) -> list[PageSpec]:
        """
        Generate city/location pages.

        cities: [{"name": "Berlin", "country": "Germany", "population": "3.6M"}, ...]
        """
        pages = []
        tpl = template or self._default_city_template()

        for city in cities:
            city_name = city.get("name", "")
            country = city.get("country", "")
            slug = f"url-shortener-{self._slugify(city_name)}"

            spec = PageSpec(
                page_type="city",
                slug=slug,
                title=tpl["title"].format(city=city_name, brand=self.brand_name),
                h1=tpl["h1"].format(city=city_name, brand=self.brand_name),
                meta_description=tpl["meta_description"].format(
                    city=city_name, country=country, brand=self.brand_name
                ),
                schema_type="Service",
                keywords=[
                    f"url shortener {city_name}",
                    f"link shortener {city_name}",
                    f"short url {country}",
                ],
                content_blocks=[
                    {
                        "type": "intro",
                        "content": tpl["intro"].format(city=city_name, brand=self.brand_name),
                    },
                    {
                        "type": "features",
                        "content": tpl["features"].format(city=city_name, brand=self.brand_name),
                    },
                    {
                        "type": "cta",
                        "content": tpl["cta"].format(city=city_name, brand=self.brand_name),
                    },
                ],
            )
            pages.append(spec)

        return pages

    def generate_comparison_pages(self, competitors: list[dict]) -> list[PageSpec]:
        """
        Generate vs/comparison pages.

        competitors: [{"name": "Bitly", "weaknesses": ["limited free tier"]}, ...]
        """
        pages = []

        for comp in competitors:
            comp_name = comp.get("name", "")
            slug = f"{self._slugify(self.brand_name)}-vs-{self._slugify(comp_name)}"

            spec = PageSpec(
                page_type="versus",
                slug=slug,
                title=f"{self.brand_name} vs {comp_name}: Which URL Shortener is Better?",
                h1=f"{self.brand_name} vs {comp_name} — Full Comparison",
                meta_description=f"Compare {self.brand_name} and {comp_name} side by side. Features, pricing, and performance. Find the best URL shortener for your needs.",
                schema_type="WebPage",
                keywords=[
                    f"{self.brand_name} vs {comp_name}",
                    f"{comp_name} alternative",
                    f"best url shortener comparison",
                ],
                content_blocks=[
                    {"type": "comparison_table", "content": ""},
                    {"type": "feature_breakdown", "content": ""},
                    {"type": "verdict", "content": ""},
                ],
            )
            pages.append(spec)

        return pages

    def generate_usecase_pages(self, use_cases: list[dict]) -> list[PageSpec]:
        """
        Generate use case pages.

        use_cases: [{"title": "Social Media Marketing", "keywords": [...]}, ...]
        """
        pages = []

        for uc in use_cases:
            title = uc.get("title", "")
            slug = f"url-shortener-for-{self._slugify(title)}"

            spec = PageSpec(
                page_type="usecase",
                slug=slug,
                title=f"URL Shortener for {title} | {self.brand_name}",
                h1=f"Best URL Shortener for {title}",
                meta_description=f"Discover how {self.brand_name} helps with {title}. Track clicks, customize links, and boost engagement.",
                schema_type="WebPage",
                keywords=uc.get("keywords", [f"url shortener {title.lower()}"]),
                content_blocks=[
                    {"type": "problem", "content": ""},
                    {"type": "solution", "content": ""},
                    {"type": "features", "content": ""},
                    {"type": "testimonial", "content": ""},
                    {"type": "cta", "content": ""},
                ],
            )
            pages.append(spec)

        return pages

    def generate_multilingual(self, base_pages: list[PageSpec]) -> list[PageSpec]:
        """Generate multilingual versions of pages."""
        all_pages = []

        for page in base_pages:
            # Keep original (default language)
            all_pages.append(page)

            # Generate specs for other languages
            for lang in self.languages:
                if lang == "en":
                    continue
                translated_page = PageSpec(
                    page_type=page.page_type,
                    slug=f"{lang}/{page.slug}",
                    title=f"[{lang.upper()}] {page.title}",  # Placeholder — needs translation
                    h1=f"[{lang.upper()}] {page.h1}",
                    meta_description=f"[{lang.upper()}] {page.meta_description}",
                    content_blocks=page.content_blocks,
                    schema_type=page.schema_type,
                    language=lang,
                    keywords=[f"{kw} [{lang}]" for kw in page.keywords],
                    hreflang_base=page.slug,
                )
                all_pages.append(translated_page)

        return all_pages

    def _default_city_template(self) -> dict:
        return {
            "title": "URL Shortener in {city} | {brand}",
            "h1": "Best URL Shortener in {city}",
            "meta_description": "Looking for a URL shortener in {city}, {country}? {brand} offers free link shortening, QR codes, and analytics. Start now!",
            "intro": "{brand} is the preferred URL shortener for businesses in {city}. Shorten links, generate QR codes, and track every click.",
            "features": "Features available in {city}: Custom domains, branded links, QR codes, bio pages, and real-time analytics.",
            "cta": "Start shortening links in {city} with {brand} — free, fast, and reliable.",
        }

    @staticmethod
    def _slugify(text: str) -> str:
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:60].strip('-')
