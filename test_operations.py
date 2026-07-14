"""Test SEOOperations deep module and Doctor fix status honesty."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.operations import SEOOperations, OperationResult
from src.core.audit_record import AuditRecord, FetchFacts, PageFacts
from src.modules.doctor.fixer import AutoFixer, FixArtifact, FixStatus
from src.core.pipeline import PipelineRunner, PipelineContext, Stage, Issue, Severity

# Test 1: OperationResult structure
print("TEST 1: OperationResult structure")
r = OperationResult(success=True, url="https://x.com", operation="audit", score=85)
d = r.to_dict()
assert d["success"] is True
assert d["score"] == 85
assert d["operation"] == "audit"
assert d["issues_count"] == 0
print("  PASSED")

# Test 2: AuditRecord typed model
print("\nTEST 2: AuditRecord typed model")
record = AuditRecord(
    url="https://example.com",
    fetch=FetchFacts(status_code=200, elapsed_ms=150),
    page=PageFacts(
        url="https://example.com",
        title="Example",
        title_length=7,
        h1=["Hello"],
        word_count=500,
    ),
)
assert record.fetch.ok is True
assert record.page.title == "Example"
assert record.page.word_count == 500
d = record.to_dict()
assert d["fetch"]["ok"] is True
assert d["page"]["title"] == "Example"
print("  PASSED")

# Test 3: Doctor FixStatus honesty
print("\nTEST 3: Doctor FixStatus honesty")

# Dry run: fix_applied should NOT be True
pipeline = PipelineRunner({})
ctx = PipelineContext(target_url="https://test.com")
ctx.scan_data["page"] = {"title": "", "h1": [], "meta_description": "", "word_count": 100}
ctx.issues.append(Issue(
    code="TECH-020", title="Missing title",
    severity=Severity.CRITICAL, module="inspector",
    fix_available=True,
))

fixer = AutoFixer({"dry_run": True})
fixer.run_fixes(ctx)

# In dry-run: artifact generated but fix_applied stays False
assert ctx.issues[0].fix_applied is False, "Dry-run should NOT set fix_applied!"
assert len(ctx.fixes_applied) == 1
assert ctx.fixes_applied[0]["status"] == "dry_run"
print("  PASSED: dry_run does NOT claim fix was applied")

# Test 4: Doctor without target adapter — GENERATED only
print("\nTEST 4: Doctor without target — generated only")
ctx2 = PipelineContext(target_url="https://test.com")
ctx2.scan_data["page"] = {"title": "X", "h1": ["X"], "meta_description": "", "word_count": 100}
ctx2.issues.append(Issue(
    code="TECH-025", title="Missing meta",
    severity=Severity.HIGH, module="inspector",
    fix_available=True,
))

fixer2 = AutoFixer({"dry_run": False})  # NOT dry-run, but no target adapter
fixer2.run_fixes(ctx2)

assert ctx2.issues[0].fix_applied is False, "No adapter → should NOT claim applied!"
assert ctx2.fixes_applied[0]["status"] == "generated"
print("  PASSED: no adapter = generated status, not applied")

# Test 5: SEOOperations initializes without error
print("\nTEST 5: SEOOperations initialization")
ops = SEOOperations(project_root=os.path.dirname(os.path.abspath(__file__)))
assert ops is not None
print("  PASSED")

print("\n" + "=" * 50)
print("  ALL ARCHITECTURE TESTS PASSED!")
print("=" * 50)
