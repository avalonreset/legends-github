# DataForSEO Setup Guide

## What is DataForSEO?

DataForSEO provides live SEO data via API: keyword research, SERP analysis, AI visibility tracking, and more. The Claude GitHub extension uses it to provide real data for optimization decisions instead of guessing.

## Getting API Credentials

1. Sign up at https://app.dataforseo.com/
2. Go to API Dashboard > API Credentials
3. Note your **API Login** (email) and **API Password**

## Installation

### macOS / Linux
```bash
./extensions/dataforseo/install.sh
```

### Windows
```powershell
.\extensions\dataforseo\install.ps1
```

The installer will:
1. Prompt for your API credentials
2. Install the github-dataforseo skill and agent
3. Configure the MCP server in `~/.claude/settings.json`

## Verifying Installation

After installation, test with:
```
/github dataforseo keywords "your project topic"
```

If you see keyword suggestions with search volumes, the extension is working.

## API Costs

DataForSEO charges per API call. Typical costs for GitHub optimization:
- Keyword suggestions: ~$0.05 per call
- Search volume: ~$0.05 per batch
- SERP analysis: ~$0.10 per query
- AI scrape: ~$0.15 per query

A typical repo optimization session uses $0.50-$2.00 in API credits.

## Uninstalling

Remove the skill, agent, and MCP config:
```bash
rm -rf ~/.claude/skills/github-dataforseo
rm ~/.claude/agents/github-dataforseo.md
# Manually remove "dataforseo" from ~/.claude/settings.json mcpServers
```
