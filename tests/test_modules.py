"""Tests for individual SEO modules — polyglot, sentinel, architect, radar, citadel."""

import pytest
import json
from src.modules.polyglot.hreflang import HreflangAuditor
from src.modules.polyglot.locale import LocaleDetector
from src.modules.sentinel.snapshot import SEOSnapshot, SnapshotManager
from src.modules.sentinel.comparator import DriftComparator, DriftReport
from src.modules.architect.generator import ProgrammaticGenerator
from src.modules.architect.templates import TemplateEngine
from src.modules.radar.opportunities import BacklinkFinder, LinkOpportunity
from src.modules.citadel.schema_engine import SchemaEngine
from src.modules.citadel.ai_readiness import AIReadinessScorer
from src.core.pipeline import PipelineContext, Severity


class TestHreflangAuditor:
    def test_detects_missing_hreflang_on_multilingual_site(self):
        auditor = HreflangAuditor({"languages": ["en", "de", "fr"]})
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"hreflang_tags": []}
        auditor.audit_hreflang(ctx)
        assert len(ctx.issues) >= 1
        assert ctx.issues[0].code == "POLY-001"

    def test_no_issue_for_single_language(self):
        auditor = HreflangAuditor({"languages": ["en"]})
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"hreflang_tags": []}
        auditor.audit_hreflang(ctx)
        assert len(ctx.issues) == 0

    def test_generates_hreflang_set(self):
        auditor = HreflangAuditor({"languages": ["en", "de"]})
        tags = auditor.generate_hreflang_set("https://x.com/page", ["en", "de"])
        assert 'hreflang="en"' in tags
        assert 'hreflang="de"' in tags
        assert 'hreflang="x-default"' in tags


class TestLocaleDetector:
    def test_detects_lang_from_url(self):
        detector = LocaleDetector({"languages": ["en", "de", "fr"]})
        assert detector.detect_lang_from_url("https://x.com/de/page") == "de"
        assert detector.detect_lang_from_url("https://x.com/page") == ""

    def test_detects_url_strategy_subdirectory(self):
        detector = LocaleDetector()
        assert detector.detect_url_strategy("https://x.com/de/page") == "subdirectory"

    def test_detects_url_strategy_unknown(self):
        detector = LocaleDetector()
        assert detector.detect_url_strategy("https://x.com/page") == "unknown"


class TestDriftComparator:
    def test_detects_title_change(self):
        baseline = SEOSnapshot(url="https://x.com", title="Old Title", timestamp=1000)
        current = SEOSnapshot(url="https://x.com", title="New Title", timestamp=2000)
        comp = DriftComparator()
        report = comp.compare(baseline, current)
        assert report.change_count >= 1
        titles = [c for c in report.changes if c.field == "title"]
        assert len(titles) == 1

    def test_detects_noindex_critical(self):
        baseline = SEOSnapshot(url="https://x.com", meta_robots="index,follow", timestamp=1000)
        current = SEOSnapshot(url="https://x.com", meta_robots="noindex", timestamp=2000)
        comp = DriftComparator()
        report = comp.compare(baseline, current)
        assert report.has_regressions is True
        robots_changes = [c for c in report.changes if c.field == "meta_robots"]
        assert robots_changes[0].severity == Severity.CRITICAL

    def test_no_changes_empty_report(self):
        s = SEOSnapshot(url="https://x.com", title="Same", timestamp=1000)
        s2 = SEOSnapshot(url="https://x.com", title="Same", timestamp=2000)
        comp = DriftComparator()
        report = comp.compare(s, s2)
        assert report.change_count == 0
        assert report.has_regressions is False


class TestProgrammaticGenerator:
    def test_generates_city_pages(self):
        gen = ProgrammaticGenerator({"brand_name": "TestBrand", "base_url": "https://x.com"})
        cities = [{"name": "Berlin", "country": "Germany"}, {"name": "Paris", "country": "France"}]
        pages = gen.generate_city_pages(cities)
        assert len(pages) == 2
        assert "Berlin" in pages[0].title
        assert pages[0].page_type == "city"

    def test_generates_comparison_pages(self):
        gen = ProgrammaticGenerator({"brand_name": "MyApp"})
        comps = [{"name": "Bitly"}, {"name": "TinyURL"}]
        pages = gen.generate_comparison_pages(comps)
        assert len(pages) == 2
        assert "Bitly" in pages[0].title
        assert pages[0].page_type == "versus"

    def test_generates_usecase_pages(self):
        gen = ProgrammaticGenerator({"brand_name": "MyApp"})
        usecases = [{"title": "Social Media Marketing"}]
        pages = gen.generate_usecase_pages(usecases)
        assert len(pages) == 1
        assert "Social Media" in pages[0].title


class TestTemplateEngine:
    def test_simple_variable(self):
        engine = TemplateEngine()
        assert engine.render("Hello {name}!", {"name": "World"}) == "Hello World!"

    def test_default_value(self):
        engine = TemplateEngine()
        assert engine.render("{missing|fallback}", {}) == "fallback"

    def test_missing_stays(self):
        engine = TemplateEngine()
        assert engine.render("{unknown}", {}) == "{unknown}"


class TestSchemaEngine:
    def test_detects_homepage(self):
        engine = SchemaEngine()
        page_type = engine.detect_page_type("https://x.com/", {"title": "Home", "h1": ["Welcome"]})
        assert page_type == "homepage"

    def test_detects_article(self):
        engine = SchemaEngine()
        page_type = engine.detect_page_type(
            "https://x.com/blog/my-post",
            {"title": "My Post", "h1": ["My Post"], "h2": [], "word_count": 1000}
        )
        assert page_type == "article"

    def test_generates_schema(self):
        engine = SchemaEngine()
        schema = engine.generate_schema("article", "https://x.com/blog/post", {
            "title": "Test Article", "meta_description": "Desc", "word_count": 500, "h1": ["Test"]
        })
        assert schema["@type"] == "Article"
        assert schema["@context"] == "https://schema.org"


class TestAIReadiness:
    def test_scores_good_page(self):
        scorer = AIReadinessScorer()
        report = scorer.calculate_score("https://x.com", {
            "title": "Complete Guide to URL Shorteners",
            "meta_description": "Everything you need to know about URL shorteners, QR codes, and link management.",
            "h1": ["Complete Guide to URL Shorteners"],
            "h2": ["What is a URL Shortener", "How They Work", "Best Practices", "Top Tools"],
            "h3": ["Custom Domains", "Analytics"],
            "word_count": 2000,
            "json_ld_count": 1,
            "internal_links_count": 10,
            "external_links_count": 5,
            "images_count": 4,
            "url": "https://x.com/guide",
            "og_title": "Complete Guide",
        })
        assert report.overall_score >= 60

    def test_scores_thin_page_low(self):
        scorer = AIReadinessScorer()
        report = scorer.calculate_score("https://x.com", {
            "title": "", "meta_description": "", "h1": [], "h2": [],
            "h3": [], "word_count": 50, "json_ld_count": 0,
            "internal_links_count": 0, "external_links_count": 0,
            "images_count": 0, "url": "https://x.com", "og_title": "",
        })
        assert report.overall_score < 40


class TestBacklinkFinder:
    def test_finds_directories(self):
        finder = BacklinkFinder({"industry": "saas"})
        opps = finder.find_directories("example.com")
        assert len(opps) > 0
        assert all(o.strategy == "directory" for o in opps)

    def test_generates_outreach_plan(self):
        finder = BacklinkFinder()
        opps = [
            LinkOpportunity(url="https://a.com", strategy="directory", priority="high"),
            LinkOpportunity(url="https://b.com", strategy="guest_post", priority="medium"),
        ]
        plan = finder.generate_outreach_plan(opps)
        assert plan["total_opportunities"] == 2
        assert "weekly_targets" in plan
