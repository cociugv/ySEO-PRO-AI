# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Active |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Instead, please report them privately:

1. Email: vadim@ylink.pro
2. Subject: `[SECURITY] ySEO-PRO-AI: <brief description>`
3. Include: steps to reproduce, potential impact, suggested fix if available

You will receive an acknowledgment within 48 hours.

## Security Model

### What ySEO-PRO-AI does:

- **Audit** is read-only (HTTP GET requests to target URLs)
- **Fix/Remediation** generates content locally — never writes to remote targets without explicit adapter + approval
- All file writes are restricted to the workspace root
- Crawling respects robots.txt and configurable rate limits

### Network safety:

- Targets restricted to explicit URLs and same-site discovered links
- Blocks requests to: localhost, private networks (10.x, 192.168.x, 172.16-31.x), cloud metadata endpoints
- Validates redirects against the same policy
- No outbound data exfiltration — reports stay local

### Data handling:

- No telemetry or analytics collected
- No data sent to third-party servers (except when user explicitly configures API integrations)
- Secrets (API keys) loaded from environment variables or .env — never hardcoded
- Secrets never appear in reports, logs, or CLI output
- Crawl databases (.yseo/) are local and gitignored

### Remediation safety:

- Every mutation has a risk level (LOW/MEDIUM/HIGH/CRITICAL)
- HIGH and CRITICAL remediations require explicit user approval
- Backup created before every file modification
- Rollback available for all reversible changes
- Dry-run mode is the default

### Prompt injection protection:

- Content fetched from websites is treated as untrusted data
- Page content is never executed or evaluated
- If website content contains instructions (e.g., "ignore previous instructions"), it is treated as plain text evidence

## Dependencies

Core engine: **Python standard library only** — no third-party packages required.

Optional dependencies:
- `mcp` (Model Context Protocol SDK) — for MCP server mode only
- No dependencies with known critical vulnerabilities as of v0.1.0

## Responsible Disclosure Timeline

1. Report received → acknowledgment within 48h
2. Assessment and fix → within 7 days for critical, 30 days for others
3. Patch release → coordinated with reporter
4. Public disclosure → after patch is available
