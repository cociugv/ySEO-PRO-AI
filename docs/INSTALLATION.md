# Installation Guide

## Quick Install (30 seconds)

### For Claude Desktop / Claude Code

Add to your MCP configuration (`~/.claude/settings/mcp.json` or workspace `.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "yseo-pro-ai": {
      "command": "npx",
      "args": ["-y", "yseo-pro-ai"],
      "env": {}
    }
  }
}
```

### For Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "yseo-pro-ai": {
      "command": "npx",
      "args": ["-y", "yseo-pro-ai"]
    }
  }
}
```

### For Kiro CLI

The project includes `.kiro/steering/seo-automation.md` — just open the project folder in Kiro.

### From Source (Development)

```bash
git clone https://github.com/vadimc/ySEO-PRO-AI.git
cd ySEO-PRO-AI
npm install
python install.py
```

## Requirements

- **Node.js** >= 18 (for MCP server)
- **Python** >= 3.10 (for analysis engine — stdlib only, no pip install)
- **npm** (comes with Node.js)

## Configuration

1. Copy environment template:
   ```bash
   cp config/.env.example .env
   ```

2. Edit `.env` with your API keys (all optional):
   - `INDEXNOW_KEY` — For instant indexing notifications
   - `GSC_CREDENTIALS_JSON` — Google Search Console access
   - `PAGESPEED_API_KEY` — Google PageSpeed Insights
   - `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` — DataForSEO data

3. Edit `config/default.yaml` for default settings:
   - `targets.languages` — Your site's supported languages
   - `modules.*` — Enable/disable specific modules

## Verify Installation

After setup, ask Claude/Cursor:
```
Audit https://example.com for SEO issues
```

Or run CLI directly:
```bash
python -m src.ops.cli audit https://example.com
```

## Platform Compatibility

| Platform | Method | Status |
|----------|--------|--------|
| Claude Desktop | MCP server (stdio) | Full support |
| Claude Code | MCP server + Skills | Full support |
| Cursor | MCP server | Full support |
| Kiro CLI | Steering + MCP | Full support |
| Windsurf | MCP server | Full support |
| Codex CLI | Standalone Python | Full support |
| VS Code + Continue | MCP server | Full support |
| Gemini Code Assist | Python CLI | Full support |
| Any MCP client | stdio transport | Full support |
