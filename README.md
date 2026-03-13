<p align="center">
  <img src="assets/banner.jpg" alt="Claude GitHub - Claude Code skills for GitHub repository optimization" width="100%">
</p>

# Claude GitHub - Claude Code Skills for Repository Optimization

[![Version](https://img.shields.io/github/v/release/avalonreset-pro/claude-github)](https://github.com/avalonreset-pro/claude-github/releases)
[![License: Proprietary](https://img.shields.io/badge/license-proprietary-red)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-blue)]()
[![Built for Claude Code](https://img.shields.io/badge/built%20for-Claude%20Code-blueviolet)](https://claude.com/claude-code)

Most GitHub repos are invisible. No keywords in the description, no structured README, missing license files, zero community health signals. Search engines skip them. Developers scroll past them. Stars stay at zero.

Claude GitHub is a suite of Claude Code skills that audits, scores, and optimizes any GitHub repository across 8 dimensions. One command gives you a 0-100 health score with prioritized fixes. Follow-up commands generate the files, rewrite the README, select the right license, and configure your metadata, all using live keyword data from DataForSEO so every recommendation is specific and measurable.

> Built with the [Agent Skills](https://github.com/anthropics/claude-code) open standard for Claude Code.
> SEO methodology adapted from [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo).

## Table of Contents

- [What You Get](#what-you-get)
- [How the Audit Works](#how-the-audit-works)
- [Installation](#installation)
- [How Claude Code Skills Communicate](#how-claude-code-skills-communicate)
- [Architecture](#architecture)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Contributing and Security](#contributing-and-security)
- [Disclaimer](#disclaimer)
- [License](#license)

## What You Get

| Command | What It Does |
|---------|-------------|
| `/github audit` | Score any repo 0-100 across 6 categories with prioritized fixes |
| `/github readme` | Generate or rewrite your README with SEO-optimized headings and banner images |
| `/github legal` | Select a license, generate SECURITY.md, CITATION.cff, handle fork compliance |
| `/github meta` | Optimize description, topics, feature toggles, and social preview |
| `/github seo` | Run keyword research with real search volume and difficulty data |
| `/github community` | Generate issue templates, CONTRIBUTING.md, CODE_OF_CONDUCT.md, devcontainer |
| `/github release` | Plan release strategy, CHANGELOG, badges, and versioning |
| `/github empire` | Portfolio strategy across all your repos, profile README, cross-linking |

Every recommendation cites its source: DataForSEO keyword volume, GitHub API metadata, codebase analysis, or reference guides. Nothing is guesswork.

### Example: Audit Output

```
Overall Score: 60/100

| Category               | Score | Weight | Weighted |
|------------------------|-------|--------|----------|
| README Quality         | 63    | 25%    | 15.8     |
| Metadata & Discovery   | 70    | 20%    | 14.0     |
| Legal Compliance       | 60    | 15%    | 9.0      |
| Community Health       | 52    | 15%    | 7.8      |
| Release & Maintenance  | 48    | 15%    | 7.2      |
| SEO & Discoverability  | 64    | 10%    | 6.4      |

Top 3 Actions (by impact):
1. [Critical] Add badges to README (version, license, CI status)
2. [High] Create CONTRIBUTING.md with contribution guidelines
3. [High] Set up GitHub Releases with semantic versioning
```

Run `/github audit`, then follow the action items with the matching sub-command. The audit caches its findings so downstream skills like `/github readme` and `/github meta` pick up where it left off.

## How the Audit Works

Run `/github audit` and 6 specialized agents score your repo in parallel:

| Category | Weight | What It Checks |
|----------|--------|----------------|
| README Quality | 25% | Structure, headings, badges, table of contents, code examples |
| Metadata and Discovery | 20% | Description keywords, topics, homepage URL, feature toggles |
| Legal Compliance | 15% | License file, SECURITY.md, CITATION.cff, fork obligations |
| Community Health | 15% | Issue templates, CONTRIBUTING, CODE_OF_CONDUCT, devcontainer |
| Release and Maintenance | 15% | Releases, CHANGELOG, CI badges, dependabot, recency |
| SEO and Discoverability | 10% | Keyword placement, GitHub Explore signals, AI citability |

Each agent uses a detailed rubric with specific point values per checkpoint, not subjective impressions. The final score is a weighted sum. Agents run simultaneously in a single message, so a full audit completes in under 60 seconds.

### Portfolio Mode

Audit an entire GitHub profile at once:

```
/github audit avalonreset
```

This quick-scans all public repos, selects the top candidates for deep analysis, spawns up to 6 agents per repo, and produces a cross-portfolio report with shared patterns and priorities.

## Installation

**Prerequisites:** [Claude Code](https://claude.com/claude-code) and [GitHub CLI](https://cli.github.com/) (`gh`), both installed and authenticated.

**macOS / Linux:**
```bash
git clone https://github.com/avalonreset-pro/claude-github.git
cd claude-github
bash install.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/avalonreset-pro/claude-github.git
cd claude-github
.\install.ps1
```

The installer copies all skills, agents, and reference files to `~/.claude/skills/github/`, then walks you through setting up two optional services:

- **[DataForSEO](https://dataforseo.com)** powers live keyword research, SERP rankings, and AI visibility tracking. The installer configures the MCP server with your credentials automatically. Without it, skills fall back to codebase-only analysis (marked "unverified").
- **[KIE.ai](https://kie.ai/api-key)** generates AI banner images for READMEs. The installer saves your API key to `.env`. Without it, README generation skips the banner step.

Restart Claude Code after installing. Skills register on startup.

## How Claude Code Skills Communicate

Every skill follows the **GARE pattern**: Gather, Analyze, Recommend, Execute.

1. **Gather** data from the GitHub API, codebase scan, and DataForSEO
2. **Analyze** the current state against the ideal for your repo type and intent
3. **Recommend** specific changes with data sources cited
4. **Execute** only after you approve, with a confirmation gate before any live changes

Skills share data through a `.github-audit/` cache directory. When you run `/github audit` first, it writes `audit-data.json` and `seo-data.json` that downstream skills consume automatically. This means `/github readme` knows your keyword targets, `/github meta` knows your gaps, and `/github legal` knows your fork status without re-gathering anything.

| Cache File | Written By | Consumed By |
|------------|-----------|-------------|
| `repo-context.json` | Orchestrator | All skills |
| `seo-data.json` | Orchestrator or `/github seo` | `/github readme`, `/github meta` |
| `audit-data.json` | `/github audit` | All downstream skills |
| `legal-data.json` | `/github legal` | `/github readme` (badge selection) |

## Architecture

```
claude-github/
├── github/                    # Orchestrator skill
│   ├── SKILL.md               # Routing, intent capture, SEO data pass
│   └── references/            # 9 reference guides (loaded on-demand)
├── skills/                    # 8 sub-skills
│   ├── github-audit/          # 0-100 health scoring with 6 parallel agents
│   ├── github-readme/         # README generation, SEO optimization, banner images
│   ├── github-legal/          # License selection, SECURITY.md, fork compliance
│   ├── github-meta/           # Description, topics, settings, social preview
│   ├── github-seo/            # Keyword research and content strategy
│   ├── github-community/      # Community health files and templates
│   ├── github-release/        # Release strategy, CHANGELOG, versioning
│   └── github-empire/         # Portfolio strategy, profile README, cross-linking
├── agents/                    # 6 scoring agents (parallel audit)
├── extensions/
│   └── dataforseo/            # DataForSEO MCP server setup
├── install.sh                 # macOS/Linux installer
└── install.ps1                # Windows installer
```

1 orchestrator, 8 sub-skills, 6 scoring agents, 9 reference files. The orchestrator detects your repo type (library, CLI tool, API, application, framework, documentation, or skill/plugin) and adjusts recommendations for each.

## Frequently Asked Questions

### What are Claude Code skills?

Claude Code skills are markdown instruction files that extend Claude Code with specialized capabilities. They follow the [Agent Skills](https://github.com/anthropics/claude-code) open standard, which means any SKILL.md file placed in `~/.claude/skills/` is automatically loaded when Claude Code starts. Skills can define triggers, reference files, and sub-agents.

### How do I add skills to Claude Code?

Run the installer (`bash install.sh` or `.\install.ps1`). It copies all skill files to `~/.claude/skills/github/` and configures the DataForSEO MCP server. After installation, restart Claude Code and the skills are available immediately. Type `/github` to see available commands.

### Do I need DataForSEO to use this?

No. Every skill works without DataForSEO by falling back to codebase analysis, GitHub API data, and built-in reference guides. However, keyword recommendations will be marked "unverified" without live search data. DataForSEO adds real volume numbers, difficulty scores, and SERP verification for about 15-30 cents per repo analysis.

## Contributing and Security

This is a private project distributed to authorized community members. If you find a bug or have a feature request, open an issue in this repository.

For security vulnerabilities, **do not open a public issue.** Email benjamin@avalonreset.com directly. See [SECURITY.md](SECURITY.md) for the full disclosure policy and response timelines.

## Disclaimer

This tool provides automated recommendations for GitHub repository optimization, including license selection and compliance guidance. **It is not legal, financial, or professional advice.** All recommendations are generated by AI-driven analysis and should be reviewed with your own due diligence before applying. For complex licensing or compliance situations, consult a qualified attorney. The authors assume no liability for decisions made based on this tool's output. See [LICENSE](LICENSE) for full terms.

## License

[Proprietary](LICENSE). Licensed to authorized community members only. See LICENSE for full terms.
