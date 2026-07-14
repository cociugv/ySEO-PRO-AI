"""Tests for Remediation State Machine and File/Git Adapter."""

import os
import tempfile
import pytest
from src.core.remediation import (
    RemediationEngine, Remediation, RemediationState, RiskLevel,
    InvalidTransition, VALID_TRANSITIONS,
)
from src.adapters.file_adapter import FileAdapter, GitAdapter


class TestRemediationStateMachine:
    def test_propose_creates_remediation(self):
        engine = RemediationEngine()
        rem = engine.propose(
            finding_ids=["TECH-040"],
            target_url="https://x.com",
            after_content='<link rel="canonical" href="https://x.com">',
            description="Add canonical",
            category="canonical",
        )
        assert rem.state == RemediationState.PROPOSED
        assert rem.id != ""
        assert len(rem.finding_ids) == 1

    def test_full_lifecycle_happy_path(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: True)

        rem = engine.propose(
            finding_ids=["TECH-050"],
            target_url="https://x.com",
            after_content='<script type="application/ld+json">{}</script>',
            category="schema",
        )

        rem = engine.preview(rem.id)
        assert rem.state == RemediationState.PREVIEWED

        rem = engine.approve(rem.id, actor="user")
        assert rem.state == RemediationState.APPROVED
        assert rem.approved_at > 0

        rem = engine.apply(rem.id)
        assert rem.state == RemediationState.APPLIED

        rem = engine.verify(rem.id)
        assert rem.state == RemediationState.VERIFIED
        assert rem.verified_at > 0

    def test_apply_failure_path(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: False)  # Always fails

        rem = engine.propose(
            finding_ids=["X"], target_url="https://x.com",
            after_content="fix", category="meta",
        )
        engine.preview(rem.id)
        engine.approve(rem.id)
        rem = engine.apply(rem.id)

        assert rem.state == RemediationState.APPLY_FAILED
        assert rem.error != ""

    def test_verification_failure_with_rollback(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: True)
        engine.set_verifier(lambda r: False)  # Verification fails

        rem = engine.propose(
            finding_ids=["X"], target_url="https://x.com",
            before_content="old", after_content="new", category="meta",
        )
        engine.preview(rem.id)
        engine.approve(rem.id)
        engine.apply(rem.id)
        rem = engine.verify(rem.id)

        assert rem.state == RemediationState.ROLLBACK_AVAILABLE
        assert rem.rollback_available is True

        rem = engine.rollback(rem.id)
        assert rem.state == RemediationState.ROLLED_BACK

    def test_invalid_transition_raises(self):
        engine = RemediationEngine()
        rem = engine.propose(
            finding_ids=["X"], target_url="https://x.com",
            after_content="x", category="meta",
        )
        # Cannot go directly from PROPOSED to APPROVED
        with pytest.raises(InvalidTransition):
            engine.approve(rem.id)

    def test_no_adapter_means_apply_failed(self):
        engine = RemediationEngine()
        # No adapter set
        rem = engine.propose(
            finding_ids=["X"], target_url="https://x.com",
            after_content="x", category="meta",
        )
        engine.preview(rem.id)
        engine.approve(rem.id)
        rem = engine.apply(rem.id)
        assert rem.state == RemediationState.APPLY_FAILED

    def test_execute_full_low_risk(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: True)

        rem = engine.propose(
            finding_ids=["TECH-040"], target_url="https://x.com",
            after_content='<link rel="canonical">', category="canonical",
            risk=RiskLevel.LOW,
        )
        rem = engine.execute_full(rem.id, auto_approve=True)
        assert rem.state == RemediationState.VERIFIED

    def test_execute_full_high_risk_stops_at_preview(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: True)

        rem = engine.propose(
            finding_ids=["X"], target_url="https://x.com",
            after_content="redirect rule", category="redirect",
            risk=RiskLevel.HIGH,
        )
        rem = engine.execute_full(rem.id, auto_approve=False)
        assert rem.state == RemediationState.PREVIEWED

    def test_plan_summary(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: True)

        engine.propose(finding_ids=["A"], target_url="https://x.com", after_content="a", category="meta")
        rem2 = engine.propose(finding_ids=["B"], target_url="https://x.com", after_content="b", category="schema")
        engine.preview(rem2.id)

        summary = engine.get_plan_summary()
        assert summary["total"] == 2
        assert summary["pending_approval"] == 1

    def test_transitions_recorded(self):
        engine = RemediationEngine()
        engine.set_adapter(lambda r: True)

        rem = engine.propose(finding_ids=["X"], target_url="u", after_content="c", category="m")
        engine.preview(rem.id)
        engine.approve(rem.id)

        assert len(rem.transitions) == 2
        assert rem.transitions[0].from_state == RemediationState.PROPOSED
        assert rem.transitions[0].to_state == RemediationState.PREVIEWED


class TestFileAdapter:
    def test_apply_creates_file(self, tmp_path):
        adapter = FileAdapter(workspace_root=str(tmp_path))
        target = os.path.join(str(tmp_path), "test.html")

        rem = Remediation(
            target_path="test.html",
            after_content="<h1>New Content</h1>",
        )
        result = adapter.apply(rem)
        assert result is True
        assert os.path.exists(target)
        with open(target) as f:
            assert "<h1>New Content</h1>" in f.read()

    def test_apply_modifies_existing_file(self, tmp_path):
        target = os.path.join(str(tmp_path), "page.html")
        with open(target, "w") as f:
            f.write("<html><head></head><body>Old</body></html>")

        adapter = FileAdapter(workspace_root=str(tmp_path))
        rem = Remediation(
            target_path="page.html",
            after_content='<meta name="description" content="New">',
            target_scope="head",
        )
        result = adapter.apply(rem)
        assert result is True

        with open(target) as f:
            content = f.read()
        assert "description" in content
        assert "New" in content

    def test_verify_checks_content_present(self, tmp_path):
        target = os.path.join(str(tmp_path), "page.html")
        expected = '<link rel="canonical" href="https://x.com">'
        with open(target, "w") as f:
            f.write(f"<html><head>{expected}</head></html>")

        adapter = FileAdapter(workspace_root=str(tmp_path))
        rem = Remediation(target_path="page.html", after_content=expected)
        assert adapter.verify(rem) is True

    def test_verify_fails_if_content_missing(self, tmp_path):
        target = os.path.join(str(tmp_path), "page.html")
        with open(target, "w") as f:
            f.write("<html><head></head></html>")

        adapter = FileAdapter(workspace_root=str(tmp_path))
        rem = Remediation(target_path="page.html", after_content="NOT_PRESENT")
        assert adapter.verify(rem) is False

    def test_rollback_restores_original(self, tmp_path):
        target = os.path.join(str(tmp_path), "page.html")
        original = "<html><head><title>Original</title></head></html>"
        with open(target, "w") as f:
            f.write(original)

        adapter = FileAdapter(workspace_root=str(tmp_path))
        rem = Remediation(target_path="page.html", after_content="CHANGED", target_scope="append")
        adapter.apply(rem)

        # Now rollback
        assert adapter.rollback(rem) is True
        with open(target) as f:
            assert f.read() == original

    def test_rejects_path_outside_workspace(self, tmp_path):
        adapter = FileAdapter(workspace_root=str(tmp_path))
        rem = Remediation(target_path="/etc/passwd", after_content="hacked")
        result = adapter.apply(rem)
        assert result is False

    def test_preview_without_modifying(self, tmp_path):
        target = os.path.join(str(tmp_path), "page.html")
        with open(target, "w") as f:
            f.write("<html></html>")

        adapter = FileAdapter(workspace_root=str(tmp_path))
        rem = Remediation(target_path="page.html", after_content="NEW", target_scope="append")
        preview = adapter.preview(rem)

        assert preview["file_exists"] is True
        assert preview["diff_lines"] > 0
        # File should NOT be modified
        with open(target) as f:
            assert f.read() == "<html></html>"


class TestIntegration:
    """Integration: RemediationEngine + FileAdapter working together."""

    def test_full_flow_with_file_adapter(self, tmp_path):
        # Setup file
        target = os.path.join(str(tmp_path), "index.html")
        with open(target, "w") as f:
            f.write("<html><head></head><body></body></html>")

        # Setup engine + adapter
        adapter = FileAdapter(workspace_root=str(tmp_path))
        engine = RemediationEngine()
        engine.set_adapter(adapter.apply)
        engine.set_verifier(adapter.verify)

        # Propose + execute
        rem = engine.propose(
            finding_ids=["TECH-040"],
            target_url="https://x.com",
            target_path="index.html",
            target_scope="head",
            after_content='<link rel="canonical" href="https://x.com">',
            category="canonical",
            risk=RiskLevel.LOW,
        )
        rem = engine.execute_full(rem.id, auto_approve=True)

        # Should be verified
        assert rem.state == RemediationState.VERIFIED

        # File should contain the canonical tag
        with open(target) as f:
            content = f.read()
        assert 'canonical' in content
        assert 'https://x.com' in content
