"""
HTML Parser — Extract SEO-relevant data from HTML pages.

Uses only Python stdlib (html.parser). No BeautifulSoup dependency.
Extracts: title, meta, headings, links, images, schema, hreflang, canonical, etc.
"""

import re
from html.parser import HTMLParser
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin


@dataclass
class PageData:
    """Structured SEO data extracted from an HTML page."""
    url: str = ""
    title: str = ""
    meta_description: str = ""
    meta_robots: str = ""
    canonical: str = ""
    lang: str = ""
    charset: str = ""

    # Headings
    h1: list = field(default_factory=list)
    h2: list = field(default_factory=list)
    h3: list = field(default_factory=list)

    # Links
    internal_links: list = field(default_factory=list)
    external_links: list = field(default_factory=list)
    hreflang_tags: list = field(default_factory=list)

    # Images
    images: list = field(default_factory=list)

    # Schema.org
    json_ld: list = field(default_factory=list)

    # Open Graph
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    og_type: str = ""

    # Technical
    viewport: str = ""
    structured_data_count: int = 0
    word_count: int = 0
    has_analytics: bool = False
    scripts: list = field(default_factory=list)
    stylesheets: list = field(default_factory=list)

    @property
    def title_length(self) -> int:
        return len(self.title)

    @property
    def description_length(self) -> int:
        return len(self.meta_description)

    @property
    def has_h1(self) -> bool:
        return len(self.h1) > 0

    @property
    def multiple_h1(self) -> bool:
        return len(self.h1) > 1

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "title_length": self.title_length,
            "meta_description": self.meta_description,
            "description_length": self.description_length,
            "canonical": self.canonical,
            "lang": self.lang,
            "h1": self.h1,
            "h2": self.h2,
            "h3": self.h3,
            "internal_links_count": len(self.internal_links),
            "external_links_count": len(self.external_links),
            "images_count": len(self.images),
            "hreflang_count": len(self.hreflang_tags),
            "json_ld_count": len(self.json_ld),
            "word_count": self.word_count,
            "og_title": self.og_title,
            "og_description": self.og_description,
            "viewport": self.viewport,
        }


class SEOHTMLParser(HTMLParser):
    """Custom HTML parser that extracts SEO-relevant data."""

    def __init__(self, base_url: str = ""):
        super().__init__()
        self.base_url = base_url
        self.data = PageData(url=base_url)

        # Parser state
        self._current_tag = ""
        self._current_attrs = {}
        self._in_title = False
        self._in_heading = ""
        self._in_script = False
        self._in_style = False
        self._script_type = ""
        self._buffer = ""
        self._body_text = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attr_dict = dict(attrs)
        self._current_tag = tag
        self._current_attrs = attr_dict

        if tag == "title":
            self._in_title = True
            self._buffer = ""

        elif tag in ("h1", "h2", "h3"):
            self._in_heading = tag
            self._buffer = ""

        elif tag == "meta":
            self._handle_meta(attr_dict)

        elif tag == "link":
            self._handle_link(attr_dict)

        elif tag == "a":
            self._handle_anchor(attr_dict)

        elif tag == "img":
            self._handle_image(attr_dict)

        elif tag == "script":
            self._in_script = True
            self._script_type = attr_dict.get("type", "")
            self._buffer = ""
            src = attr_dict.get("src", "")
            if src:
                self.data.scripts.append(src)
                if "analytics" in src or "gtag" in src or "gtm" in src:
                    self.data.has_analytics = True

        elif tag == "style":
            self._in_style = True

        elif tag == "html":
            self.data.lang = attr_dict.get("lang", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            self.data.title = self._buffer.strip()

        elif tag in ("h1", "h2", "h3") and self._in_heading == tag:
            text = self._buffer.strip()
            if text:
                getattr(self.data, tag).append(text)
            self._in_heading = ""

        elif tag == "script":
            if self._script_type == "application/ld+json" and self._buffer.strip():
                self.data.json_ld.append(self._buffer.strip())
                self.data.structured_data_count += 1
            self._in_script = False

        elif tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._buffer += data
        elif self._in_heading:
            self._buffer += data
        elif self._in_script:
            self._buffer += data
        elif not self._in_style:
            stripped = data.strip()
            if stripped:
                self._body_text.append(stripped)

    def _handle_meta(self, attrs: dict) -> None:
        name = attrs.get("name", "").lower()
        prop = attrs.get("property", "").lower()
        content = attrs.get("content", "")

        if name == "description":
            self.data.meta_description = content
        elif name == "robots":
            self.data.meta_robots = content
        elif name == "viewport":
            self.data.viewport = content
        elif prop == "og:title":
            self.data.og_title = content
        elif prop == "og:description":
            self.data.og_description = content
        elif prop == "og:image":
            self.data.og_image = content
        elif prop == "og:type":
            self.data.og_type = content

        charset = attrs.get("charset", "")
        if charset:
            self.data.charset = charset

    def _handle_link(self, attrs: dict) -> None:
        rel = attrs.get("rel", "").lower()
        href = attrs.get("href", "")

        if rel == "canonical" and href:
            self.data.canonical = self._resolve_url(href)
        elif rel == "alternate":
            hreflang = attrs.get("hreflang", "")
            if hreflang and href:
                self.data.hreflang_tags.append({
                    "lang": hreflang,
                    "url": self._resolve_url(href),
                })
        elif rel == "stylesheet" and href:
            self.data.stylesheets.append(href)

    def _handle_anchor(self, attrs: dict) -> None:
        href = attrs.get("href", "")
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            return

        resolved = self._resolve_url(href)
        if self._is_internal(resolved):
            self.data.internal_links.append(resolved)
        else:
            self.data.external_links.append(resolved)

    def _handle_image(self, attrs: dict) -> None:
        self.data.images.append({
            "src": attrs.get("src", ""),
            "alt": attrs.get("alt", ""),
            "width": attrs.get("width", ""),
            "height": attrs.get("height", ""),
            "loading": attrs.get("loading", ""),
        })

    def _resolve_url(self, href: str) -> str:
        if href.startswith(("http://", "https://", "//")):
            return href
        return urljoin(self.base_url, href)

    def _is_internal(self, url: str) -> bool:
        if not self.base_url:
            return True
        from urllib.parse import urlparse
        base_domain = urlparse(self.base_url).netloc
        link_domain = urlparse(url).netloc
        return link_domain == base_domain or link_domain == ""

    def finalize(self) -> PageData:
        """Call after feeding all HTML to compute derived fields."""
        full_text = " ".join(self._body_text)
        self.data.word_count = len(full_text.split())
        return self.data


def parse_html(html: str, url: str = "") -> PageData:
    """Parse HTML and extract SEO-relevant data."""
    parser = SEOHTMLParser(base_url=url)
    try:
        parser.feed(html)
    except Exception:
        pass
    return parser.finalize()
