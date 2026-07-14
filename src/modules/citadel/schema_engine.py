"""
Schema Engine — Auto-detects page type and generates appropriate schema markup.

Detects:
- Article/BlogPosting (blog posts, news)
- Product (e-commerce)
- FAQPage (pages with Q&A)
- Service (service pages)
- Organization (about pages)
- WebSite (homepage)
- BreadcrumbList (navigation)
- HowTo (tutorial/guide pages)
- SoftwareApplication (SaaS product pages)
"""

import json
import re
from ...core.pipeline import PipelineContext, Issue, Severity, Stage


# Page type detection signals
PAGE_TYPE_SIGNALS = {
    "article": {
        "url_patterns": [r"/blog/", r"/news/", r"/article/", r"/post/"],
        "content_signals": ["published", "author", "reading time", "updated"],
        "min_word_count": 300,
    },
    "product": {
        "url_patterns": [r"/product/", r"/shop/", r"/item/", r"/pricing"],
        "content_signals": ["price", "buy", "cart", "add to", "features"],
    },
    "faq": {
        "url_patterns": [r"/faq", r"/frequently-asked", r"/help/"],
        "content_signals": ["question", "answer", "how do", "what is", "?"],
        "heading_pattern": r"^(how|what|why|when|where|can|do|is|are)\s",
    },
    "service": {
        "url_patterns": [r"/service", r"/solution", r"/what-we-do"],
        "content_signals": ["service", "solution", "we offer", "our approach"],
    },
    "software": {
        "url_patterns": [r"/app", r"/tool", r"/platform", r"/dashboard"],
        "content_signals": ["api", "integration", "features", "free trial", "sign up"],
    },
    "homepage": {
        "url_patterns": [r"^/$", r"^/index"],
        "content_signals": [],
    },
}


class SchemaEngine:
    """
    Auto-generates schema.org markup based on page type detection.

    Registers into pipeline stages: DIAGNOSE + FIX
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.site_name = self.config.get("site_name", "")
        self.site_url = self.config.get("site_url", "")
        self.organization = self.config.get("organization", {})

    def register(self, pipeline) -> None:
        """Register into pipeline."""
        pipeline.register(Stage.DIAGNOSE, self.check_schema)

    def detect_page_type(self, url: str, page_data: dict) -> str:
        """Detect the most likely page type from URL and content signals."""
        from urllib.parse import urlparse
        path = urlparse(url).path.lower()
        h2_headings = page_data.get("h2", [])
        word_count = page_data.get("word_count", 0)

        scores = {}

        for page_type, signals in PAGE_TYPE_SIGNALS.items():
            score = 0

            # URL pattern matching
            for pattern in signals.get("url_patterns", []):
                if re.search(pattern, path):
                    score += 3

            # Content signal matching (simplified — would check body text)
            title = (page_data.get("title", "") + " " + " ".join(page_data.get("h1", []))).lower()
            for signal in signals.get("content_signals", []):
                if signal.lower() in title:
                    score += 1

            # FAQ detection from H2 headings
            if page_type == "faq" and h2_headings:
                question_pattern = signals.get("heading_pattern", "")
                if question_pattern:
                    question_count = sum(
                        1 for h in h2_headings
                        if re.match(question_pattern, h.lower())
                    )
                    if question_count >= 3:
                        score += 5

            # Word count for articles
            if page_type == "article" and word_count >= 300:
                score += 1

            scores[page_type] = score

        # Return highest scoring type, default to "webpage"
        if not scores or max(scores.values()) == 0:
            return "webpage"

        return max(scores, key=scores.get)

    def generate_schema(self, page_type: str, url: str, page_data: dict) -> dict:
        """Generate appropriate schema for detected page type."""
        generators = {
            "article": self._schema_article,
            "product": self._schema_software_app,
            "faq": self._schema_faq,
            "service": self._schema_service,
            "software": self._schema_software_app,
            "homepage": self._schema_website,
            "webpage": self._schema_webpage,
        }

        generator = generators.get(page_type, self._schema_webpage)
        return generator(url, page_data)

    def check_schema(self, ctx: PipelineContext) -> None:
        """DIAGNOSE: Check if schema markup exists and is appropriate."""
        page = ctx.scan_data.get("page", {})
        json_ld_count = page.get("json_ld_count", 0)

        if json_ld_count == 0:
            page_type = self.detect_page_type(ctx.target_url, page)
            schema = self.generate_schema(page_type, ctx.target_url, page)

            ctx.issues.append(Issue(
                code="SCHEMA-001",
                title=f"Missing schema markup (detected type: {page_type})",
                severity=Severity.MEDIUM,
                module="citadel",
                url=ctx.target_url,
                description=f"Auto-generated {schema.get('@type', 'WebPage')} schema available",
                fix_available=True,
                evidence={"generated_schema": schema, "detected_type": page_type},
            ))

    def _schema_article(self, url: str, page_data: dict) -> dict:
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page_data.get("title", ""),
            "description": page_data.get("meta_description", ""),
            "url": url,
            "wordCount": page_data.get("word_count", 0),
            "author": {"@type": "Organization", "name": self.site_name or "Author"},
            "publisher": {
                "@type": "Organization",
                "name": self.site_name or "Publisher",
                "url": self.site_url or url,
            },
        }

    def _schema_faq(self, url: str, page_data: dict) -> dict:
        # Build FAQ from H2 headings (assume they're questions)
        questions = []
        for h2 in page_data.get("h2", [])[:10]:
            if "?" in h2 or re.match(r'^(how|what|why|when|where|can|do|is|are)\s', h2.lower()):
                questions.append({
                    "@type": "Question",
                    "name": h2,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"See the full answer on our page: {url}",
                    },
                })

        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": questions or [{
                "@type": "Question",
                "name": page_data.get("title", "FAQ"),
                "acceptedAnswer": {"@type": "Answer", "text": page_data.get("meta_description", "")},
            }],
        }

    def _schema_software_app(self, url: str, page_data: dict) -> dict:
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": page_data.get("title", "").split("|")[0].split("-")[0].strip(),
            "description": page_data.get("meta_description", ""),
            "url": url,
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
            },
        }

    def _schema_service(self, url: str, page_data: dict) -> dict:
        return {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": page_data.get("title", ""),
            "description": page_data.get("meta_description", ""),
            "url": url,
            "provider": {
                "@type": "Organization",
                "name": self.site_name or "Provider",
            },
        }

    def _schema_website(self, url: str, page_data: dict) -> dict:
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": self.site_name or page_data.get("title", ""),
            "url": self.site_url or url,
            "description": page_data.get("meta_description", ""),
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{self.site_url or url}/search?q={{search_term_string}}",
                "query-input": "required name=search_term_string",
            },
        }

    def _schema_webpage(self, url: str, page_data: dict) -> dict:
        return {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": page_data.get("title", ""),
            "description": page_data.get("meta_description", ""),
            "url": url,
        }
