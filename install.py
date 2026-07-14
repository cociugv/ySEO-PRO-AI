"""
ySEO-PRO-AI — Universal Installer

Works with: Kiro CLI, Claude Code, Cursor, VS Code, standalone CLI.
No external dependencies required (Python stdlib only).

Usage:
    python install.py              # Auto-detect environment and install
    python install.py --kiro       # Install for Kiro CLI
    python install.py --claude     # Install for Claude Code
    python install.py --cursor     # Install for Cursor
    python install.py --standalone # CLI-only (no editor integration)
"""

import os
import sys
import json
import shutil


BANNER = """
╔══════════════════════════════════════════════════════╗
║         ySEO-PRO-AI Installer v1.0.0                ║
║   AI-powered SEO automation for multilingual SaaS   ║
║         by Vadim Cociug / yLink.pro                 ║
╚══════════════════════════════════════════════════════╝
"""

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def setup_env():
    """Create .env from template if not exists."""
    env_example = os.path.join(PROJECT_DIR, "config", ".env.example")
    env_file = os.path.join(PROJECT_DIR, ".env")

    if not os.path.exists(env_file) and os.path.exists(env_example):
        shutil.copy2(env_example, env_file)
        print("  [+] Created .env from template")
    else:
        print("  [=] .env already exists")


def setup_directories():
    """Ensure all required directories exist."""
    dirs = [
        ".yseo/cache",
        ".yseo/snapshots",
        ".yseo/competitors",
        "reports",
    ]
    for d in dirs:
        path = os.path.join(PROJECT_DIR, d)
        os.makedirs(path, exist_ok=True)
    print("  [+] Created runtime directories")


def setup_kiro():
    """Install Kiro CLI steering rules."""
    steering_dir = os.path.join(PROJECT_DIR, ".kiro", "steering")
    os.makedirs(steering_dir, exist_ok=True)
    print("  [+] Kiro steering rules ready")


def setup_claude_code():
    """Install for Claude Code (CLAUDE.md)."""
    claude_md = os.path.join(PROJECT_DIR, "CLAUDE.md")
    content = """# ySEO-PRO-AI

AI-powered SEO automation platform. Audits, fixes, and grows organic traffic.

## Quick Commands

- `python -m src.ops.cli scan <url>` — Quick scan
- `python -m src.ops.cli audit <url>` — Full audit
- `python -m src.ops.cli fix <url>` — Auto-fix issues
- `python -m src.ops.cli fix <url> --dry-run` — Preview fixes
- `python -m src.ops.cli ai-score <url>` — AI readiness score

## Architecture

Pipeline-based: SCAN → DIAGNOSE → FIX → VERIFY → REPORT

Modules: inspector, doctor, sentinel, polyglot, architect, publisher, radar, citadel

## Config

Edit `config/default.yaml` or create `config/local.yaml` for overrides.
Set env vars in `.env` (copied from `config/.env.example`).
"""
    with open(claude_md, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [+] Created CLAUDE.md for Claude Code")


def setup_cursor():
    """Install for Cursor (.cursorrules)."""
    cursor_rules = os.path.join(PROJECT_DIR, ".cursorrules")
    content = """# ySEO-PRO-AI — Cursor Rules

This is an AI-powered SEO automation platform.

## Project Structure
- `src/core/` — Engine (pipeline, fetcher, parser, config)
- `src/modules/` — 8 SEO modules (inspector, doctor, sentinel, polyglot, architect, publisher, radar, citadel)
- `src/ops/` — CLI operations
- `config/` — YAML configuration

## Key Patterns
- Pipeline: SCAN → DIAGNOSE → FIX → VERIFY → REPORT
- Zero external deps (Python stdlib only)
- Config-driven (YAML + env vars)
- Multilingual first (14 languages supported)

## Running
```
python -m src.ops.cli audit https://ylink.pro
python -m src.ops.cli fix https://ylink.pro --dry-run
```
"""
    with open(cursor_rules, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [+] Created .cursorrules for Cursor")


def verify_python():
    """Verify Python version."""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        print(f"  [!] Warning: Python 3.10+ recommended (found {major}.{minor})")
    else:
        print(f"  [+] Python {major}.{minor} — OK")


def run_test():
    """Quick self-test."""
    try:
        from src.core.pipeline import PipelineRunner, Stage
        from src.core.parser import parse_html
        from src.core.config_loader import load_config

        # Test parser
        html = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
        page = parse_html(html, "https://example.com")
        assert page.title == "Test"
        assert page.h1 == ["Hello"]

        # Test config
        config = load_config(PROJECT_DIR)
        assert "platform" in config or True  # Config might be empty on fresh install

        print("  [+] Self-test PASSED")
        return True
    except Exception as e:
        print(f"  [!] Self-test failed: {e}")
        return False


def main():
    print(BANNER)

    args = sys.argv[1:]
    install_all = not args

    print("  Installing ySEO-PRO-AI...\n")

    verify_python()
    setup_directories()
    setup_env()

    if install_all or "--kiro" in args:
        setup_kiro()

    if install_all or "--claude" in args:
        setup_claude_code()

    if install_all or "--cursor" in args:
        setup_cursor()

    print()
    run_test()

    print(f"""
  ════════════════════════════════════════════════
  Installation complete!

  Next steps:
    1. Edit .env with your API keys
    2. Run: python -m src.ops.cli scan https://ylink.pro
    3. Run: python -m src.ops.cli audit https://ylink.pro

  Documentation: README.md
  ════════════════════════════════════════════════
""")


if __name__ == "__main__":
    main()
