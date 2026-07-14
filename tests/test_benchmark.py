"""
Benchmark Tests — Verify audit precision against known HTML fixtures.

Each fixture has expected_issues (must be found) and expected_no_issues (must not appear).
This ensures the audit rules don't regress or produce false positives.
"""

import pytest
from src.core.pipeline import PipelineRunner, PipelineContext, Stage
from src.core.parser import parse_html
from src.modules.inspector.scanner import TechnicalScanner
from tests.fixtures.benchmark import FIXTURES


class TestBenchmarkFixtures:
    """Run all benchmark fixtures and verify precision."""

    @pytest.fixture(autouse=True)
    def setup_scanner(self):
        self.scanner = TechnicalScanner({})

    @pytest.mark.parametrize("fixture", FIXTURES, ids=[f["name"] for f in FIXTURES])
    def test_expected_issues_found(self, fixture):
        """Every expected issue code must be present in findings."""
        page = parse_html(fixture["html"], fixture["url"])
        ctx = PipelineContext(target_url=fixture["url"])
        ctx.scan_data["page"] = page.to_dict()
        ctx.scan_data["fetch_result"] = {
            "status_code": 200, "elapsed_ms": 100, "headers": {}, "error": "",
        }

        # Run diagnose
        self.scanner.diagnose(ctx)

        found_codes = {issue.code for issue in ctx.issues}

        for expected in fixture["expected_issues"]:
            assert expected in found_codes, (
                f"[{fixture['name']}] Expected issue {expected} not found. "
                f"Got: {sorted(found_codes)}"
            )

    @pytest.mark.parametrize("fixture", FIXTURES, ids=[f["name"] for f in FIXTURES])
    def test_no_false_positives(self, fixture):
        """Codes in expected_no_issues must NOT appear."""
        page = parse_html(fixture["html"], fixture["url"])
        ctx = PipelineContext(target_url=fixture["url"])
        ctx.scan_data["page"] = page.to_dict()
        ctx.scan_data["fetch_result"] = {
            "status_code": 200, "elapsed_ms": 100, "headers": {}, "error": "",
        }

        self.scanner.diagnose(ctx)

        found_codes = {issue.code for issue in ctx.issues}

        for not_expected in fixture["expected_no_issues"]:
            assert not_expected not in found_codes, (
                f"[{fixture['name']}] False positive: {not_expected} should NOT be found. "
                f"Got: {sorted(found_codes)}"
            )
