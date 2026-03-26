# Contributing to Claude GitHub

Thank you for being part of the community. This guide covers how to report issues, request features, and contribute improvements to the skill suite.

## Reporting Bugs

Found something broken? Open a [Bug Report](https://github.com/avalonreset/claude-github/issues/new?template=bug_report.yml) with:

- Which skill triggered the issue (`/github audit`, `/github readme`, etc.)
- What you expected to happen vs. what actually happened
- Your operating system (Windows, macOS, Linux)
- Your Claude Code version (`claude --version`)

The more detail you provide, the faster we can fix it.

## Requesting Features

Have an idea for a new skill, a missing check in the audit, or a better workflow? Open a [Feature Request](https://github.com/avalonreset/claude-github/issues/new?template=feature_request.yml). Include the problem you are trying to solve, not just the solution you imagine. Understanding the "why" helps us design the right fix.

## Asking Questions

For general questions, troubleshooting, and discussion, use [GitHub Discussions](https://github.com/avalonreset/claude-github/discussions). Keep Issues for confirmed bugs and feature requests.

Common questions to check first:

- **DataForSEO not working?** Verify your MCP config in `~/.claude/settings.json`. The installer sets this up, but credentials expire or get misconfigured.
- **Skills not showing up?** Restart Claude Code after installation. Skills register on startup.
- **Banner generation failing?** Check that `KIE_API_KEY` is set in `~/.claude/skills/github/.env`.

## Contributing Code

If you want to submit a fix or improvement:

1. Create a branch from `main` with a descriptive name (`fix/audit-score-calculation`, `feature/new-agent`)
2. Make your changes. Keep commits focused on one thing.
3. Test your changes by running the relevant skill against a real repo
4. Open a Pull Request with a clear description of what changed and why

All pull requests are reviewed by the project maintainer before merging.

## Code Style

- Skill files (SKILL.md) follow the [Agent Skills](https://github.com/anthropics/claude-code) open standard
- Reference files use Markdown with consistent heading hierarchy
- Shell scripts (`install.sh`) target Bash 4+
- PowerShell scripts (`install.ps1`) target PowerShell 5.1+
- Never commit credentials, API keys, or `.env` files

## Code of Conduct

All community members are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and professional.

## Security

If you discover a security vulnerability, **do not open a public issue.** Follow the process in [SECURITY.md](SECURITY.md).
