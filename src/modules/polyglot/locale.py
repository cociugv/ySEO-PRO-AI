"""
Locale Detector — Identifies page language and validates locale configuration.

Detects language from:
- HTML lang attribute
- Content-Language header
- Meta tags
- URL structure (/en/, /ro/, etc.)
- Content analysis (word frequency patterns)
"""

import re
from urllib.parse import urlparse
from ...core.pipeline import PipelineContext, Issue, Severity, Stage


class LocaleDetector:
    """Detects and validates page locale configuration."""

    # Common language indicators in URL paths
    LANG_PATH_PATTERNS = re.compile(
        r'^/(?:' +
        '|'.join([
            'en', 'ro', 'ru', 'de', 'es', 'fr', 'hi', 'id', 'it',
            'no', 'pt', 'tr', 'uk', 'ar', 'ja', 'ko', 'zh', 'nl',
            'pl', 'sv', 'da', 'fi', 'cs', 'hu', 'el', 'th', 'vi',
        ]) +
        r')(?:/|$)'
    )

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.expected_languages = self.config.get("languages", ["en"])
        self.default_language = self.config.get("default_language", "en")

    def register(self, pipeline) -> None:
        """Register into pipeline."""
        pipeline.register(Stage.DIAGNOSE, self.check_locale)

    def check_locale(self, ctx: PipelineContext) -> None:
        """Diagnose locale-related issues."""
        page = ctx.scan_data.get("page", {})
        lang_attr = page.get("lang", "")

        # Check HTML lang attribute
        if not lang_attr:
            ctx.issues.append(Issue(
                code="POLY-100",
                title="Missing HTML lang attribute",
                severity=Severity.HIGH,
                module="polyglot",
                url=ctx.target_url,
                description="<html> tag should declare the page language",
                fix_available=True,
            ))
        else:
            # Validate lang attribute format
            if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', lang_attr):
                ctx.issues.append(Issue(
                    code="POLY-101",
                    title=f"Invalid lang attribute format: '{lang_attr}'",
                    severity=Severity.MEDIUM,
                    module="polyglot",
                    url=ctx.target_url,
                    description="Use format like 'en', 'en-US', 'ro', 'de-AT'",
                    fix_available=True,
                ))

        # Check URL language consistency
        url_lang = self.detect_lang_from_url(ctx.target_url)
        if url_lang and lang_attr:
            base_lang = lang_attr.split("-")[0].lower()
            if url_lang != base_lang:
                ctx.issues.append(Issue(
                    code="POLY-110",
                    title="URL language mismatch with HTML lang",
                    severity=Severity.HIGH,
                    module="polyglot",
                    url=ctx.target_url,
                    description=f"URL suggests '{url_lang}' but HTML lang is '{lang_attr}'",
                    evidence={"url_lang": url_lang, "html_lang": lang_attr},
                ))

    def detect_lang_from_url(self, url: str) -> str:
        """Detect language from URL path structure."""
        path = urlparse(url).path
        match = self.LANG_PATH_PATTERNS.match(path)
        if match:
            return path.split("/")[1]
        return ""

    def detect_url_strategy(self, url: str) -> str:
        """
        Detect the internationalization URL strategy.

        Returns: 'subdirectory' | 'subdomain' | 'cctld' | 'parameter' | 'unknown'
        """
        parsed = urlparse(url)

        # Check for ccTLD (e.g., example.de, example.fr)
        tld = parsed.netloc.split(".")[-1]
        if len(tld) == 2 and tld not in ("io", "co", "me", "tv", "ai"):
            return "cctld"

        # Check for language subdomain (e.g., de.example.com, fr.example.com)
        parts = parsed.netloc.split(".")
        if len(parts) >= 3 and len(parts[0]) == 2:
            return "subdomain"

        # Check for subdirectory (e.g., example.com/de/)
        if self.LANG_PATH_PATTERNS.match(parsed.path):
            return "subdirectory"

        # Check for query parameter (e.g., ?lang=de)
        if "lang=" in (parsed.query or ""):
            return "parameter"

        return "unknown"

    def get_all_language_urls(self, base_url: str, strategy: str = "subdirectory") -> dict:
        """Generate URLs for all configured languages."""
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path

        urls = {}
        for lang in self.expected_languages:
            if lang == self.default_language:
                urls[lang] = base_url
            elif strategy == "subdirectory":
                # Remove existing lang prefix if present
                clean_path = re.sub(r'^/[a-z]{2}/', '/', path)
                urls[lang] = f"{domain}/{lang}{clean_path}"
            elif strategy == "subdomain":
                parts = parsed.netloc.split(".")
                if len(parts) >= 3 and len(parts[0]) == 2:
                    parts[0] = lang
                else:
                    parts.insert(0, lang)
                urls[lang] = f"{parsed.scheme}://{'.'.join(parts)}{path}"
            elif strategy == "parameter":
                sep = "&" if "?" in base_url else "?"
                urls[lang] = f"{base_url}{sep}lang={lang}"

        return urls
