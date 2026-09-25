# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Credential Handling

Local workflows need no provider API key. Live GitHub reads and mutations use your existing GitHub CLI authentication. Optional research services use credentials managed by your chosen host or integration; never place secrets in reports, prompts, Git commits, or generated examples.

The toolkit does not call a paid image-generation service. Use an existing local asset or your host's image tool separately when artwork is requested.

Keep `.env`, `.env.local`, and other credential files out of version control. Offline mode disables the toolkit's external requests. Isolate cache/report output with `--artifacts-dir` when reviewing another repository.

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

- Launcher or script behavior (`legends_github.py`, `github/scripts/`) that modifies system configuration
- Credential handling in recipe files or reference documents
- MCP server configuration that could expose credentials
- Any workflow behavior that could leak sensitive data to external services

The following are out of scope:

- Vulnerabilities in third-party services (including optional research providers)
- Issues in the hosting agent itself (report to its provider)
- GitHub CLI (`gh`) vulnerabilities (report to [GitHub](https://github.com/cli/cli/security))
