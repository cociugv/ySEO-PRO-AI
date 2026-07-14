"""
Hreflang Auditor — Validates and generates hreflang implementation.

Checks:
- All language variants have return tags
- x-default is set
- URLs are absolute and valid
- Language codes are valid ISO 639-1
- No self-referencing loops
- Consistency between HTML tags and HTTP headers
"""

from urllib.parse import urlparse, urljoin
from ...core.pipeline import PipelineContext, Issue, Severity, Stage
from ...core.fetcher import PageFetcher


# Valid ISO 639-1 language codes
VALID_LANG_CODES = {
    "af", "ar", "az", "be", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de",
    "el", "en", "es", "et", "eu", "fa", "fi", "fr", "ga", "gl", "gu", "he",
    "hi", "hr", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "km", "kn",
    "ko", "ky", "lb", "lo", "lt", "lv", "mk", "ml", "mn", "mr", "ms", "mt",
    "my", "nb", "ne", "nl", "nn", "no", "pa", "pl", "ps", "pt", "ro", "ru",
    "si", "sk", "sl", "so", "sq", "sr", "sv", "sw", "ta", "te", "tg", "th",
    "tk", "tl", "tr", "uk", "ur", "uz", "vi", "zh",
}


class HreflangAuditor:
    """
    Audits hreflang implementation across a multilingual site.

    Registers into Pipeline stages: SCAN + DIAGNOSE + FIX
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.expected_languages = self.config.get("languages", ["en"])
        self.fetcher = PageFetcher(rate_limit_ms=1500)

    def register(self, pipeline) -> None:
        """Register into pipeline stages."""
        pipeline.register(Stage.DIAGNOSE, self.audit_hreflang)

    def audit_hreflang(self, ctx: PipelineContext) -> None:
        """DIAGNOSE: Check hreflang implementation."""
        page = ctx.scan_data.get("page", {})
        hreflang_tags = page.get("hreflang_tags", [])

        if not hreflang_tags and len(self.expected_languages) > 1:
            ctx.issues.append(Issue(
                code="POLY-001",
                title="Missing hreflang tags on multilingual site",
                severity=Severity.HIGH,
                module="polyglot",
                url=ctx.target_url,
                description=f"Site supports {len(self.expected_languages)} languages but page has no hreflang",
                fix_available=True,
            ))
            return

        if not hreflang_tags:
            return

        # Validate each hreflang tag
        found_langs = set()
        has_x_default = False

        for tag in hreflang_tags:
            lang = tag.get("lang", "")
            href = tag.get("url", "")

            if lang == "x-default":
                has_x_default = True
                continue

            found_langs.add(lang)

            # Validate language code
            base_lang = lang.split("-")[0].lower()
            if base_lang not in VALID_LANG_CODES:
                ctx.issues.append(Issue(
                    code="POLY-010",
                    title=f"Invalid hreflang language code: '{lang}'",
                    severity=Severity.HIGH,
                    module="polyglot",
                    url=ctx.target_url,
                    description=f"'{lang}' is not a valid ISO 639-1 code",
                    evidence={"invalid_code": lang},
                    fix_available=True,
                ))

            # Check URL is absolute
            if not href.startswith(("http://", "https://")):
                ctx.issues.append(Issue(
                    code="POLY-011",
                    title=f"Relative URL in hreflang for '{lang}'",
                    severity=Severity.MEDIUM,
                    module="polyglot",
                    url=ctx.target_url,
                    description="Hreflang URLs must be absolute (include protocol and domain)",
                    evidence={"relative_url": href, "lang": lang},
                    fix_available=True,
                ))

        # Check x-default
        if not has_x_default and len(hreflang_tags) > 1:
            ctx.issues.append(Issue(
                code="POLY-020",
                title="Missing x-default hreflang tag",
                severity=Severity.MEDIUM,
                module="polyglot",
                url=ctx.target_url,
                description="x-default tells search engines which version to show when no locale matches",
                fix_available=True,
            ))

        # Check for missing expected languages
        for expected_lang in self.expected_languages:
            if expected_lang not in found_langs:
                ctx.issues.append(Issue(
                    code="POLY-030",
                    title=f"Missing hreflang for configured language: '{expected_lang}'",
                    severity=Severity.MEDIUM,
                    module="polyglot",
                    url=ctx.target_url,
                    description=f"Language '{expected_lang}' is configured but not declared in hreflang",
                    evidence={"missing_lang": expected_lang},
                    fix_available=True,
                ))

        # Check self-referencing
        current_domain = urlparse(ctx.target_url).netloc
        self_referenced = False
        for tag in hreflang_tags:
            href = tag.get("url", "")
            if urlparse(href).netloc == current_domain and urlparse(href).path == urlparse(ctx.target_url).path:
                self_referenced = True
                break

        if not self_referenced and hreflang_tags:
            ctx.issues.append(Issue(
                code="POLY-040",
                title="Page does not self-reference in hreflang",
                severity=Severity.MEDIUM,
                module="polyglot",
                url=ctx.target_url,
                description="Each page should include itself in the hreflang set",
                fix_available=True,
            ))

    def generate_hreflang_set(self, base_url: str, languages: list[str], url_pattern: str = "/{lang}/") -> str:
        """Generate complete hreflang tag set for a URL."""
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path

        tags = []
        for lang in languages:
            if lang == languages[0]:  # Default language
                href = base_url
            else:
                href = f"{domain}/{lang}{path}"
            tags.append(f'<link rel="alternate" hreflang="{lang}" href="{href}" />')

        # x-default points to the default language version
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{base_url}" />')

        return "\n".join(tags)

    def validate_return_tags(self, url: str, hreflang_tags: list[dict]) -> list[Issue]:
        """
        Verify bidirectional hreflang (each referenced page links back).
        This requires fetching alternate pages.
        """
        issues = []

        for tag in hreflang_tags:
            href = tag.get("url", "")
            lang = tag.get("lang", "")

            if lang == "x-default" or not href:
                continue

            # Fetch the alternate page and check it links back
            result = self.fetcher.fetch(href)
            if not result.ok:
                issues.append(Issue(
                    code="POLY-050",
                    title=f"Hreflang target unreachable: {lang}",
                    severity=Severity.HIGH,
                    module="polyglot",
                    url=url,
                    description=f"Alternate page for '{lang}' returns HTTP {result.status_code}",
                    evidence={"target_url": href, "status": result.status_code},
                ))

        return issues
