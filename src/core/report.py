"""
HTML Report Generator — Self-contained, professional SEO audit report.

Produces a single HTML file with embedded CSS (no external deps).
Can be opened in any browser, shared as attachment, or archived.
"""

import json
import time
from typing import Optional
from .pipeline import Severity


def generate_html_report(
    url: str,
    score: int,
    issues: list[dict],
    data: dict = None,
    title: str = "SEO Audit Report",
) -> str:
    """
    Generate a self-contained HTML report.

    Args:
        url: Audited URL
        score: Overall SEO score (0-100)
        issues: List of issue dicts
        data: Additional data (page info, AI readiness, etc.)
        title: Report title

    Returns:
        Complete HTML string
    """
    data = data or {}
    timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())

    # Categorize issues
    by_severity = {}
    for issue in issues:
        sev = issue.get("severity", "info")
        by_severity.setdefault(sev, []).append(issue)

    fixable_count = sum(1 for i in issues if i.get("fix_available"))
    fixed_count = sum(1 for i in issues if i.get("fix_applied"))

    # Score color
    if score >= 80:
        score_color = "#16a34a"
        score_label = "Good"
    elif score >= 60:
        score_color = "#ca8a04"
        score_label = "Needs Work"
    elif score >= 40:
        score_color = "#ea580c"
        score_label = "Poor"
    else:
        score_color = "#dc2626"
        score_label = "Critical"

    # Build issue rows
    issue_rows = ""
    for sev in ["critical", "high", "medium", "low", "info"]:
        items = by_severity.get(sev, [])
        for item in items:
            fix_badge = '<span class="badge fix">FIX</span>' if item.get("fix_available") else ""
            sev_class = sev
            issue_rows += f"""
            <tr class="issue-row {sev_class}">
                <td><span class="severity {sev_class}">{sev.upper()}</span></td>
                <td><code>{item.get('code','')}</code></td>
                <td>{item.get('title','')}{fix_badge}</td>
                <td class="desc">{item.get('description','')}</td>
            </tr>"""

    # Page data section
    page = data.get("page", {})
    page_info = ""
    if page:
        page_info = f"""
        <section class="card">
            <h2>Page Data</h2>
            <div class="grid">
                <div class="stat"><span class="label">Title</span><span class="value">{_esc(page.get('title',''))}</span></div>
                <div class="stat"><span class="label">H1</span><span class="value">{_esc(str(page.get('h1',[''])[0]) if page.get('h1') else '(missing)')}</span></div>
                <div class="stat"><span class="label">Words</span><span class="value">{page.get('word_count',0)}</span></div>
                <div class="stat"><span class="label">Internal Links</span><span class="value">{page.get('internal_links_count',0)}</span></div>
                <div class="stat"><span class="label">Schema</span><span class="value">{page.get('json_ld_count',0)}</span></div>
                <div class="stat"><span class="label">Hreflang</span><span class="value">{len(page.get('hreflang_tags',page.get('hreflang_count',0) if isinstance(page.get('hreflang_count'),int) else []))}</span></div>
            </div>
        </section>"""

    # AI readiness section
    ai = data.get("ai_readiness", {})
    ai_section = ""
    if ai and ai.get("overall_score"):
        bd = ai.get("breakdown", {})
        ai_section = f"""
        <section class="card">
            <h2>AI Search Readiness: {ai['overall_score']}/100</h2>
            <div class="grid">
                <div class="stat"><span class="label">Citability</span><span class="value">{bd.get('citability',0)}</span></div>
                <div class="stat"><span class="label">Entities</span><span class="value">{bd.get('entity_presence',0)}</span></div>
                <div class="stat"><span class="label">Answers</span><span class="value">{bd.get('answer_clarity',0)}</span></div>
                <div class="stat"><span class="label">Structure</span><span class="value">{bd.get('structure',0)}</span></div>
                <div class="stat"><span class="label">Authority</span><span class="value">{bd.get('authority',0)}</span></div>
                <div class="stat"><span class="label">Freshness</span><span class="value">{bd.get('freshness',0)}</span></div>
            </div>
        </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {_esc(url)}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#f8fafc; color:#1e293b; line-height:1.6; }}
.container {{ max-width:1100px; margin:0 auto; padding:24px 16px; }}
header {{ background:linear-gradient(135deg,#0f172a,#1e3a5f); color:white; padding:40px 24px; border-radius:12px; margin-bottom:24px; }}
header h1 {{ font-size:1.5rem; font-weight:600; }}
header .url {{ color:#94a3b8; font-size:0.9rem; margin-top:4px; word-break:break-all; }}
header .meta {{ display:flex; gap:24px; margin-top:16px; font-size:0.85rem; color:#cbd5e1; }}
.score-ring {{ display:inline-flex; align-items:center; gap:12px; margin-top:16px; }}
.score-ring .number {{ font-size:3rem; font-weight:700; color:{score_color}; }}
.score-ring .label {{ font-size:0.9rem; color:#94a3b8; }}
.summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:24px; }}
.summary .item {{ background:white; border-radius:8px; padding:16px; text-align:center; border:1px solid #e2e8f0; }}
.summary .item .num {{ font-size:1.8rem; font-weight:700; color:#0f172a; }}
.summary .item .lbl {{ font-size:0.8rem; color:#64748b; margin-top:4px; }}
.card {{ background:white; border-radius:8px; border:1px solid #e2e8f0; padding:20px; margin-bottom:16px; }}
.card h2 {{ font-size:1.1rem; margin-bottom:12px; color:#0f172a; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; }}
.stat .label {{ display:block; font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.05em; }}
.stat .value {{ font-size:0.95rem; font-weight:500; }}
table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
th {{ text-align:left; padding:8px 12px; background:#f1f5f9; border-bottom:2px solid #e2e8f0; font-weight:600; }}
td {{ padding:8px 12px; border-bottom:1px solid #f1f5f9; vertical-align:top; }}
td.desc {{ color:#64748b; max-width:300px; }}
.severity {{ display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:700; text-transform:uppercase; }}
.severity.critical {{ background:#fef2f2; color:#dc2626; }}
.severity.high {{ background:#fff7ed; color:#ea580c; }}
.severity.medium {{ background:#fefce8; color:#ca8a04; }}
.severity.low {{ background:#f0f9ff; color:#0284c7; }}
.severity.info {{ background:#f8fafc; color:#64748b; }}
.badge.fix {{ background:#ecfdf5; color:#059669; padding:1px 6px; border-radius:3px; font-size:0.65rem; margin-left:6px; }}
footer {{ text-align:center; padding:24px; color:#94a3b8; font-size:0.75rem; }}
code {{ background:#f1f5f9; padding:2px 5px; border-radius:3px; font-size:0.8rem; }}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>{title}</h1>
        <div class="url">{_esc(url)}</div>
        <div class="meta">
            <span>Generated: {timestamp}</span>
            <span>by ySEO-PRO-AI</span>
        </div>
        <div class="score-ring">
            <span class="number">{score}</span>
            <span class="label">/100 — {score_label}</span>
        </div>
    </header>

    <div class="summary">
        <div class="item"><div class="num">{len(issues)}</div><div class="lbl">Total Issues</div></div>
        <div class="item"><div class="num" style="color:#dc2626">{len(by_severity.get('critical',[]))}</div><div class="lbl">Critical</div></div>
        <div class="item"><div class="num" style="color:#ea580c">{len(by_severity.get('high',[]))}</div><div class="lbl">High</div></div>
        <div class="item"><div class="num" style="color:#ca8a04">{len(by_severity.get('medium',[]))}</div><div class="lbl">Medium</div></div>
        <div class="item"><div class="num" style="color:#059669">{fixable_count}</div><div class="lbl">Auto-Fixable</div></div>
    </div>

    {page_info}
    {ai_section}

    <section class="card">
        <h2>Issues ({len(issues)})</h2>
        <table>
            <thead><tr><th>Severity</th><th>Code</th><th>Issue</th><th>Details</th></tr></thead>
            <tbody>{issue_rows}</tbody>
        </table>
    </section>

    <footer>
        Generated by <strong>ySEO-PRO-AI</strong> — Open source SEO automation<br>
        <a href="https://github.com/cociugv/ySEO-PRO-AI">github.com/cociugv/ySEO-PRO-AI</a>
    </footer>
</div>
</body>
</html>"""

    return html


def save_report(html: str, output_path: str = "") -> str:
    """Save HTML report to file. Returns path."""
    import os
    if not output_path:
        os.makedirs("reports", exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        output_path = f"reports/audit-{ts}.html"

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
