"""Tests for pipeline engine — stages, execution, scoring."""

import pytest
from src.core.pipeline import PipelineRunner, PipelineContext, Stage, Issue, Severity


class TestPipelineExecution:
    def test_executes_scan_stage(self):
        runner = PipelineRunner({})
        called = []
        runner.register(Stage.SCAN, lambda ctx: called.append("scan"))
        ctx = runner.execute("https://x.com", stages=[Stage.SCAN])
        assert called == ["scan"]

    def test_executes_multiple_stages_in_order(self):
        runner = PipelineRunner({})
        order = []
        runner.register(Stage.SCAN, lambda ctx: order.append("scan"))
        runner.register(Stage.DIAGNOSE, lambda ctx: order.append("diagnose"))
        runner.register(Stage.FIX, lambda ctx: order.append("fix"))
        runner.register(Stage.VERIFY, lambda ctx: order.append("verify"))
        runner.register(Stage.REPORT, lambda ctx: order.append("report"))
        ctx = runner.execute("https://x.com")
        assert order == ["scan", "diagnose", "fix", "verify", "report"]

    def test_multiple_handlers_per_stage(self):
        runner = PipelineRunner({})
        calls = []
        runner.register(Stage.SCAN, lambda ctx: calls.append("a"))
        runner.register(Stage.SCAN, lambda ctx: calls.append("b"))
        runner.execute("https://x.com", stages=[Stage.SCAN])
        assert calls == ["a", "b"]

    def test_handler_error_captured(self):
        runner = PipelineRunner({})
        def failing(ctx):
            raise ValueError("boom")
        runner.register(Stage.SCAN, failing)
        ctx = runner.execute("https://x.com", stages=[Stage.SCAN])
        assert len(ctx.errors) == 1
        assert "boom" in ctx.errors[0]["error"]

    def test_context_carries_target_url(self):
        runner = PipelineRunner({})
        captured = []
        runner.register(Stage.SCAN, lambda ctx: captured.append(ctx.target_url))
        runner.execute("https://example.com", stages=[Stage.SCAN])
        assert captured == ["https://example.com"]

    def test_subset_stages(self):
        runner = PipelineRunner({})
        order = []
        runner.register(Stage.SCAN, lambda ctx: order.append("scan"))
        runner.register(Stage.DIAGNOSE, lambda ctx: order.append("diagnose"))
        runner.register(Stage.FIX, lambda ctx: order.append("fix"))
        runner.execute("https://x.com", stages=[Stage.SCAN, Stage.DIAGNOSE])
        assert order == ["scan", "diagnose"]


class TestScoring:
    def test_perfect_score_no_issues(self):
        ctx = PipelineContext(target_url="https://x.com")
        assert ctx.score == 100

    def test_critical_deducts_15(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.issues.append(Issue(code="X", title="X", severity=Severity.CRITICAL, module="t"))
        assert ctx.score == 85

    def test_high_deducts_8(self):
        ctx = PipelineContext(target_url="https://x.com")
        ctx.issues.append(Issue(code="X", title="X", severity=Severity.HIGH, module="t"))
        assert ctx.score == 92

    def test_fixed_issues_not_counted(self):
        ctx = PipelineContext(target_url="https://x.com")
        issue = Issue(code="X", title="X", severity=Severity.CRITICAL, module="t")
        issue.fix_applied = True
        ctx.issues.append(issue)
        assert ctx.score == 100

    def test_score_never_negative(self):
        ctx = PipelineContext(target_url="https://x.com")
        for i in range(20):
            ctx.issues.append(Issue(code=f"X{i}", title="X", severity=Severity.CRITICAL, module="t"))
        assert ctx.score == 0


class TestHooks:
    def test_before_stage_hook(self):
        runner = PipelineRunner({})
        events = []
        runner.hook("before_stage", lambda ctx, stage: events.append(f"before_{stage.value}"))
        runner.register(Stage.SCAN, lambda ctx: None)
        runner.execute("https://x.com", stages=[Stage.SCAN])
        assert "before_scan" in events

    def test_on_complete_hook(self):
        runner = PipelineRunner({})
        completed = []
        runner.hook("on_complete", lambda ctx: completed.append(True))
        runner.execute("https://x.com", stages=[Stage.SCAN])
        assert completed == [True]
