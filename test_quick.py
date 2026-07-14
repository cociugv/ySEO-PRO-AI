"""Quick verification test for ySEO-PRO-AI core modules."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.pipeline import PipelineRunner, Stage, Severity, Issue, PipelineContext
from src.core.parser import parse_html, PageData
from src.core.config_loader import load_config, load_yaml_simple

# Test 1: HTML Parser
print("TEST 1: HTML Parser")
html = """<html lang="en">
<head>
    <title>yLink.pro - URL Shortener</title>
    <meta name="description" content="Free URL shortener with QR codes and analytics">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="https://ylink.pro/">
    <link rel="alternate" hreflang="en" href="https://ylink.pro/">
    <link rel="alternate" hreflang="ro" href="https://ylink.pro/ro/">
    <link rel="alternate" hreflang="de" href="https://ylink.pro/de/">
    <script type="application/ld+json">{"@type": "WebSite", "name": "yLink.pro"}</script>
</head>
<body>
    <h1>Best Free URL Shortener</h1>
    <h2>Features</h2>
    <p>Shorten links, generate QR codes, create bio pages, and track every click.</p>
    <a href="/pricing">Pricing</a>
    <a href="https://google.com">Google</a>
    <img src="/logo.png" alt="yLink Logo">
</body>
</html>"""

page = parse_html(html, "https://ylink.pro")
assert page.title == "yLink.pro - URL Shortener", f"Title failed: {page.title}"
assert page.h1 == ["Best Free URL Shortener"], f"H1 failed: {page.h1}"
assert page.meta_description == "Free URL shortener with QR codes and analytics"
assert page.lang == "en"
assert page.canonical == "https://ylink.pro/"
assert len(page.hreflang_tags) == 3
assert page.viewport == "width=device-width, initial-scale=1.0"
assert len(page.json_ld) == 1
assert len(page.internal_links) >= 1
assert len(page.external_links) >= 1
assert len(page.images) == 1
print("  PASSED: All parser assertions OK")

# Test 2: Pipeline
print("\nTEST 2: Pipeline Engine")
runner = PipelineRunner({"test": True})

scan_called = [False]
diagnose_called = [False]

def mock_scan(ctx):
    ctx.scan_data["fetched"] = True
    scan_called[0] = True

def mock_diagnose(ctx):
    ctx.issues.append(Issue(
        code="TEST-001",
        title="Test issue",
        severity=Severity.MEDIUM,
        module="test",
    ))
    diagnose_called[0] = True

runner.register(Stage.SCAN, mock_scan)
runner.register(Stage.DIAGNOSE, mock_diagnose)

ctx = runner.execute("https://ylink.pro")
assert scan_called[0], "Scan not called"
assert diagnose_called[0], "Diagnose not called"
assert len(ctx.issues) == 1
assert ctx.issues[0].code == "TEST-001"
assert ctx.score < 100  # Should have deductions
print("  PASSED: Pipeline execution OK")

# Test 3: Config Loader
print("\nTEST 3: Config Loader")
config = load_config(os.path.dirname(os.path.abspath(__file__)))
assert "platform" in config, f"Config missing platform key. Keys: {list(config.keys())}"
assert config["platform"]["name"] == "ySEO-PRO-AI"
assert config["platform"]["version"] == "1.0.0"
print("  PASSED: Config loaded OK")

# Test 4: Issue scoring
print("\nTEST 4: Scoring System")
ctx2 = PipelineContext(target_url="https://test.com")
assert ctx2.score == 100  # No issues = perfect score

ctx2.issues.append(Issue(code="X", title="X", severity=Severity.CRITICAL, module="test"))
assert ctx2.score == 85  # -15 for critical

ctx2.issues.append(Issue(code="Y", title="Y", severity=Severity.HIGH, module="test"))
assert ctx2.score == 77  # -15 -8

# Fixed issues don't count
ctx2.issues[0].fix_applied = True
assert ctx2.score == 92  # Only -8 for unfixed high
print("  PASSED: Scoring logic OK")

print("\n" + "=" * 50)
print("  ALL TESTS PASSED — ySEO-PRO-AI Core is functional!")
print("=" * 50)
