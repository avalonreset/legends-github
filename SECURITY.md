# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Credential Handling

This skill suite integrates with external services that require credentials:

- **DataForSEO**: Configured via Claude Code MCP server settings
  (`~/.claude/settings.json`). Credentials are managed by the MCP server
  and are never stored in project files.
- **KIE.ai**: API key stored in `~/.claude/skills/github/.env`.
  This file is local to your machine and must not be committed to version control.

**Important:** Never commit `.env` files, API keys, or credentials to any repository.
The `.gitignore` in this project excludes `.env` files by default.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report
it responsibly. **Do not open public issues for security vulnerabilities.**

**Email:** benjamin@rankenstein.pro

**What to include:**

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Response timeline:**

- Acknowledgment within 48 hours
- Assessment within 7 days
- Fix or mitigation plan within 30 days for confirmed vulnerabilities

## Scope

The following are in scope for security reports:

- Install scripts (`install.sh`, `install.ps1`) that modify system configuration
- Credential handling in skill files or reference documents
- MCP server configuration that could expose credentials
- Any skill behavior that could leak sensitive data to external services

The following are out of scope:

- Vulnerabilities in third-party services (DataForSEO, KIE.ai)
- Issues with Claude Code itself (report to [Anthropic](https://github.com/anthropics/claude-code/issues))
- GitHub CLI (`gh`) vulnerabilities (report to [GitHub](https://github.com/cli/cli/security))
