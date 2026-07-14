"""Tests for Doctor module — fix generation, status honesty, state machine."""

import pytest
from src.core.pipeline import PipelineContext, Issue, Severity, Stage
from src.modules.doctor.fixer import AutoFixer, FixArtifact, FixStatus


class TestFixStatusHonesty:
    """The core contract: fix_applied is ONLY true after real application."""

    def test_dry_run_never_claims_applied(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"title": "", "h1": [], "meta_description": "", "word_count": 50}
        ctx.issues.append(Issue(
            code="TECH-020", title="Missing title",
            severity=Severity.CRITICAL, module="inspector", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": True})
        fixer.run_fixes(ctx)

        assert ctx.issues[0].fix_applied is False
        assert ctx.fixes_applied[0]["status"] == "dry_run"

    def test_no_adapter_means_generated_only(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"title": "X", "h1": ["X"], "meta_description": "", "word_count": 50}
        ctx.issues.append(Issue(
            code="TECH-025", title="Missing meta",
            severity=Severity.HIGH, module="inspector", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": False})
        fixer.run_fixes(ctx)

        assert ctx.issues[0].fix_applied is False
        assert ctx.fixes_applied[0]["status"] == "generated"

    def test_with_adapter_marks_applied(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"title": "", "h1": [], "meta_description": "", "word_count": 50}
        ctx.issues.append(Issue(
            code="TECH-040", title="Missing canonical",
            severity=Severity.MEDIUM, module="inspector", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": False})
        fixer.set_target_adapter(lambda artifact: True)  # mock adapter
        fixer.run_fixes(ctx)

        assert ctx.issues[0].fix_applied is True
        assert ctx.fixes_applied[0]["status"] == "verified"


class TestFixGeneration:
    def test_generates_canonical(self):
        ctx = PipelineContext(target_url="https://example.com/page")
        ctx.scan_data["page"] = {"title": "T", "h1": ["H"], "meta_description": "D", "word_count": 100}
        ctx.issues.append(Issue(
            code="TECH-040", title="Missing canonical",
            severity=Severity.MEDIUM, module="inspector", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": True})
        fixer.run_fixes(ctx)

        artifact = ctx.fixes_applied[0]
        assert "canonical" in artifact["content"]
        assert "https://example.com/page" in artifact["content"]

    def test_generates_viewport(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"title": "T", "h1": ["H"], "meta_description": "D", "word_count": 100}
        ctx.issues.append(Issue(
            code="TECH-045", title="Missing viewport",
            severity=Severity.HIGH, module="inspector", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": True})
        fixer.run_fixes(ctx)

        assert "viewport" in ctx.fixes_applied[0]["content"]
        assert "width=device-width" in ctx.fixes_applied[0]["content"]

    def test_generates_schema(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {"title": "My Page", "h1": ["My Page"], "meta_description": "Desc", "word_count": 200}
        ctx.issues.append(Issue(
            code="TECH-050", title="No schema",
            severity=Severity.MEDIUM, module="inspector", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": True})
        fixer.run_fixes(ctx)

        content = ctx.fixes_applied[0]["content"]
        assert "application/ld+json" in content
        assert "schema.org" in content

    def test_unknown_code_returns_failed(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.scan_data["page"] = {}
        ctx.issues.append(Issue(
            code="UNKNOWN-999", title="Unknown",
            severity=Severity.LOW, module="test", fix_available=True,
        ))
        fixer = AutoFixer({"dry_run": False})
        fixer.run_fixes(ctx)

        assert ctx.fixes_applied[0]["status"] == "failed"


class TestFixArtifact:
    def test_was_applied_property(self):
        a = FixArtifact(issue_code="X", status=FixStatus.GENERATED)
        assert a.was_applied is False

        a.status = FixStatus.APPLIED
        assert a.was_applied is True

        a.status = FixStatus.VERIFIED
        assert a.was_applied is True

        a.status = FixStatus.SKIPPED_DRY_RUN
        assert a.was_applied is False

    def test_to_dict(self):
        a = FixArtifact(
            issue_code="TECH-040", status=FixStatus.GENERATED,
            action="gen_canonical", content="<link rel=canonical>",
        )
        d = a.to_dict()
        assert d["issue_code"] == "TECH-040"
        assert d["status"] == "generated"
        assert d["was_applied"] is False
