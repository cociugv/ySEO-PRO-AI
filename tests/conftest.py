"""
Shared pytest fixtures for ySEO-PRO-AI test suite.
"""

import os
import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def project_root():
    """Path to project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def sample_html_minimal():
    """Minimal valid HTML page."""
    return """<!DOCTYPE html>
<html lang="en">
<head><title>Test Page</title></head>
<body><h1>Hello</h1><p>Content here.</p></body>
</html>"""


@pytest.fixture
def sample_html_full():
    """Full HTML page with all SEO elements."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Best URL Shortener 2026 | yLink.pro</title>
    <meta name="description" content="Free URL shortener with QR codes, analytics, and custom domains. Try yLink.pro today.">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://ylink.pro/">
    <link rel="alternate" hreflang="en" href="https://ylink.pro/">
    <link rel="alternate" hreflang="ro" href="https://ylink.pro/ro/">
    <link rel="alternate" hreflang="de" href="https://ylink.pro/de/">
    <link rel="alternate" hreflang="x-default" href="https://ylink.pro/">
    <meta property="og:title" content="Best URL Shortener">
    <meta property="og:description" content="Shorten links for free">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"yLink.pro","url":"https://ylink.pro"}</script>
</head>
<body>
    <h1>Best Free URL Shortener</h1>
    <h2>Features</h2>
    <p>Shorten links, generate QR codes, create bio pages, and track every click with real-time analytics.</p>
    <h2>Why Choose yLink.pro?</h2>
    <p>Because we offer unlimited links, custom domains, and detailed analytics completely free.</p>
    <a href="/pricing">Pricing</a>
    <a href="/features">Features</a>
    <a href="https://google.com" rel="nofollow">Google</a>
    <img src="/logo.png" alt="yLink Logo" width="200" height="50">
    <img src="/hero.jpg" alt="" width="800" height="400">
</body>
</html>"""


@pytest.fixture
def sample_html_broken():
    """HTML page with multiple SEO issues."""
    return """<html>
<head></head>
<body>
<p>Short content.</p>
<img src="/no-alt.jpg">
</body>
</html>"""


@pytest.fixture
def sample_config():
    """Standard test configuration."""
    return {
        "platform": {"name": "ySEO-PRO-AI", "version": "1.0.0"},
        "targets": {
            "primary_domain": "example.com",
            "languages": ["en", "ro", "de", "fr"],
            "default_language": "en",
        },
        "modules": {
            "inspector": {"timeout_seconds": 10},
            "doctor": {"dry_run": True, "backup_before_fix": True},
            "sentinel": {"snapshot_interval_hours": 24},
        },
        "integrations": {"indexnow": {"key": "test-key-123"}},
    }
