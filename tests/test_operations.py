"""Tests for SEOOperations deep module — single entry point for all adapters."""

import pytest
from src.core.operations import SEOOperations, OperationResult
from src.core.audit_record import AuditRecord, FetchFacts, PageFacts, AIReadinessFacts


class TestOperationResult:
    def test_to_dict_structure(self):
        r = OperationResult(success=True, url="https://x.com", operation="audit", score=85)
        d = r.to_dict()
        assert d["success"] is True
        assert d["score"] == 85
        assert d["operation"] == "audit"
        assert d["issues_count"] == 0
        assert d["fixes_applied"] == 0

    def test_issues_count_reflects_list(self):
        r = OperationResult(
            success=True, url="https://x.com", operation="audit",
            issues=[{"code": "A"}, {"code": "B", "fix_available": True}],
        )
        d = r.to_dict()
        assert d["issues_count"] == 2
        assert d["fixable_count"] == 1


class TestAuditRecord:
    def test_fetch_facts_ok(self):
        f = FetchFacts(status_code=200, elapsed_ms=150)
        assert f.ok is True
        f2 = FetchFacts(status_code=404)
        assert f2.ok is False
        f3 = FetchFacts(status_code=0)
        assert f3.ok is False

    def test_page_facts_from_parser(self):
        from src.core.parser import parse_html
        html = "<html lang='de'><head><title>Hallo</title></head><body><h1>Welt</h1></body></html>"
        page = parse_html(html, "https://x.de")
        facts = PageFacts.from_parser(page)
        assert facts.title == "Hallo"
        assert facts.lang == "de"
        assert facts.h1 == ["Welt"]

    def test_audit_record_to_dict(self):
        record = AuditRecord(
            url="https://test.com",
            fetch=FetchFacts(status_code=200, elapsed_ms=100),
            page=PageFacts(title="Test", word_count=500),
        )
        d = record.to_dict()
        assert d["url"] == "https://test.com"
        assert d["fetch"]["ok"] is True
        assert d["page"]["title"] == "Test"

    def test_ai_readiness_facts(self):
        ai = AIReadinessFacts(overall_score=72, citability=80, entity_presence=65)
        d = ai.to_dict()
        assert d["overall_score"] == 72
        assert d["breakdown"]["citability"] == 80


class TestSEOOperationsInit:
    def test_initializes_with_config(self, project_root, sample_config):
        ops = SEOOperations(config=sample_config, project_root=project_root)
        assert ops is not None
        assert ops.config["platform"]["name"] == "ySEO-PRO-AI"

    def test_initializes_from_disk(self, project_root):
        ops = SEOOperations(project_root=project_root)
        assert ops is not None
