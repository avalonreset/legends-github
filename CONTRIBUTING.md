# Contributing to legends-github

Thank you for being part of the community. This guide covers how to report issues, request features, and contribute improvements to `legends-github`.

## Reporting Bugs

Found something broken? Open a [Bug Report](https://github.com/avalonreset/legends-github/issues/new?template=bug_report.yml) with:

- Which workflow triggered the issue (`audit`, `seo`, `meta`, `readme`, `discover`, `release`, etc.)
- What you expected to happen vs. what actually happened
- Your operating system (Windows, macOS, Linux) and Python version
- Your coding agent host (if running through `cto-legends`)

The more detail you provide, the faster we can fix it.

## Requesting Features

Have an idea for a new workflow, a missing check in the audit, or a better discoverability pass? Open a [Feature Request](https://github.com/avalonreset/legends-github/issues/new?template=feature_request.yml). Include the problem you are trying to solve, not just the solution you imagine. Understanding the "why" helps us design the right fix.

## Asking Questions

For general questions, troubleshooting, and discussion, use [GitHub Discussions](https://github.com/avalonreset/legends-github/discussions). Keep Issues for confirmed bugs and feature requests.

Common questions to check first:

- **DataForSEO not working?** Run `python github/scripts/setup_dataforseo.py --check` and verify `requirements-dataforseo.txt` is installed alongside your `legends-dataforseo` credentials.
- **Router not discovering `legends-github`?** Run `cto-legends status` or ask your agent to read `AGENTS.md` directly.
- **Artwork missing?** Supply an existing local asset or use your host's image tool; a banner is optional.

## Contributing Code

If you want to submit a fix or improvement:

1. Create a branch from `main` with a descriptive name (`fix/audit-score-calculation`, `feature/new-workflow`)
2. Make your changes. Keep commits focused on one thing.
3. Run `python -m unittest discover -s tests -v` and test your changes against a real repository
4. Open a Pull Request with a clear description of what changed and why

All pull requests are reviewed by the project maintainer before merging.

## Code Style

- The vendored router skill (`skills/cto-legends/SKILL.md`) is byte-exact from the router repo; never edit it in place, re-pin from the canonical source instead
- Reference and recipe files use Markdown with consistent heading hierarchy
- Keep executable behavior in `github/scripts/` with `legends_github.py` as the public launcher
- Never commit credentials, API keys, or `.env` files

## Code of Conduct

All community members are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and professional.

## Security

If you discover a security vulnerability, **do not open a public issue.** Follow the process in [SECURITY.md](SECURITY.md).
