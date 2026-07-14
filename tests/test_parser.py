"""Tests for HTML parser — SEO data extraction."""

import pytest
from src.core.parser import parse_html


class TestParserBasic:
    def test_extracts_title(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert page.title == "Best URL Shortener 2026 | yLink.pro"
        assert page.title_length == len(page.title)

    def test_extracts_meta_description(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert "Free URL shortener" in page.meta_description
        assert page.description_length > 50

    def test_extracts_h1(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert page.h1 == ["Best Free URL Shortener"]

    def test_extracts_h2(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert len(page.h2) == 2
        assert "Features" in page.h2

    def test_extracts_canonical(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert page.canonical == "https://ylink.pro/"

    def test_extracts_lang(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert page.lang == "en"

    def test_extracts_viewport(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert "width=device-width" in page.viewport

    def test_extracts_hreflang(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert len(page.hreflang_tags) == 4  # en, ro, de, x-default
        langs = [t["lang"] for t in page.hreflang_tags]
        assert "en" in langs
        assert "x-default" in langs

    def test_extracts_json_ld(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert len(page.json_ld) == 1
        assert "WebSite" in page.json_ld[0]

    def test_extracts_og(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert page.og_title == "Best URL Shortener"

    def test_counts_links(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert len(page.internal_links) >= 2
        assert len(page.external_links) >= 1

    def test_counts_images(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert len(page.images) == 2

    def test_word_count(self, sample_html_full):
        page = parse_html(sample_html_full, "https://ylink.pro")
        assert page.word_count > 20


class TestParserBroken:
    def test_missing_title(self, sample_html_broken):
        page = parse_html(sample_html_broken, "https://test.com")
        assert page.title == ""

    def test_missing_h1(self, sample_html_broken):
        page = parse_html(sample_html_broken, "https://test.com")
        assert page.h1 == []

    def test_missing_description(self, sample_html_broken):
        page = parse_html(sample_html_broken, "https://test.com")
        assert page.meta_description == ""

    def test_missing_canonical(self, sample_html_broken):
        page = parse_html(sample_html_broken, "https://test.com")
        assert page.canonical == ""

    def test_missing_lang(self, sample_html_broken):
        page = parse_html(sample_html_broken, "https://test.com")
        assert page.lang == ""

    def test_image_without_alt(self, sample_html_broken):
        page = parse_html(sample_html_broken, "https://test.com")
        assert len(page.images) == 1
        assert page.images[0]["alt"] == ""

    def test_empty_html(self):
        page = parse_html("", "https://x.com")
        assert page.title == ""
        assert page.word_count == 0


class TestParserSerialization:
    def test_to_dict(self, sample_html_minimal):
        page = parse_html(sample_html_minimal, "https://x.com")
        d = page.to_dict()
        assert isinstance(d, dict)
        assert "title" in d
        assert "word_count" in d
        assert d["title"] == "Test Page"
