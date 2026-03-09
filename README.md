# Claude GitHub: Claude Code Skills for Repository Optimization

Most GitHub repos are invisible. No keywords in the description, no structured README, missing license files, zero community health signals. Search engines skip them. Developers scroll past them. Stars stay at zero.

Claude GitHub fixes that with one command. It audits, optimizes, and professionalizes any GitHub repository across 8 dimensions, using live keyword data to make every recommendation specific and measurable.

> Built with the [Agent Skills](https://github.com/anthropics/claude-code) open standard for Claude Code.
> SEO methodology adapted from [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo).

## What You Get

| Command | What It Does |
|---------|-------------|
| `/github audit` | Score any repo 0-100 across 6 categories with prioritized fixes |
| `/github readme` | Generate or rewrite your README with SEO-optimized headings and banner images |
| `/github legal` | Select a license, generate SECURITY.md, CITATION.cff, handle fork compliance |
| `/github meta` | Optimize description, topics, feature toggles, and social preview |
| `/github seo` | Run keyword research with real volume and difficulty data |
| `/github community` | Generate issue templates, CONTRIBUTING.md, CODE_OF_CONDUCT.md, devcontainer |
| `/github release` | Plan release strategy, CHANGELOG, badges, and versioning |
| `/github empire` | Portfolio strategy across all your repos, profile README, cross-linking |

Every recommendation cites its source: DataForSEO keyword volume, GitHub API metadata, codebase analysis, or reference guides. Nothing is guesswork.

## Installation

**Prerequisites:** [Claude Code](https://claude.com/claude-code) and [GitHub CLI](https://cli.github.com/) (`gh`), both installed and authenticated.

**macOS / Linux:**
```bash
git clone https://github.com/avalonreset/claude-github.git
cd claude-github
bash install.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/avalonreset/claude-github.git
cd claude-github
.\install.ps1
```

Restart Claude Code after installing. The skills register on startup.

### Recommended: DataForSEO Integration

Live keyword research, SERP rankings, and AI visibility tracking. This is what turns generic advice into data you can act on.

```bash
# macOS / Linux
bash extensions/dataforseo/install.sh

# Windows (PowerShell)
powershell -File extensions\dataforseo\install.ps1
```

Requires a [DataForSEO](https://dataforseo.com) account (free tier includes credits for hundreds of analyses). The install script configures the MCP server automatically.

Without DataForSEO, all skills still work but fall back to codebase analysis and GitHub search.

### Recommended: KIE.ai Banner Generation

AI-generated banner images for READMEs. Add your API key to `~/.claude/skills/github/.env`:

```
KIE_API_KEY=your_key_here
```

Get a key at [kie.ai/api-key](https://kie.ai/api-key).

## How the Audit Works

Run `/github audit` and 6 specialized agents score your repo in parallel:

| Category | Weight | What It Checks |
|----------|--------|----------------|
| README Quality | 25% | Structure, headings, badges, table of contents, examples |
| Metadata & Discovery | 20% | Description, topics, homepage URL, feature toggles |
| Legal Compliance | 15% | License, SECURITY.md, CITATION.cff, fork obligations |
| Community Health | 15% | Issue templates, CONTRIBUTING, CODE_OF_CONDUCT, devcontainer |
| Release & Maintenance | 15% | Releases, CHANGELOG, CI badges, dependabot, recency |
| SEO & Discoverability | 10% | Keyword placement, GitHub Explore signals, search indexing |

The final score is a weighted sum with a prioritized list of fixes sorted by impact.

### Example Audit Output

```
## Audit Results: avalonreset/gemini-seo

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

## How Skills Communicate

Every skill follows the **GARE pattern**: Gather, Analyze, Recommend, Execute.

1. **Gather** data via GitHub API, codebase scan, and DataForSEO
2. **Analyze** current state against the ideal for your repo type and intent
3. **Recommend** specific changes with sources cited
4. **Execute** changes only after you approve them

Skills share data through a `.github-audit/` cache directory, so running `/github audit` first gives downstream skills (like `/github readme` or `/github meta`) richer context to work with.

## Architecture

```
claude-github/
├── github/                    # Orchestrator skill
│   ├── SKILL.md               # Routing, intent capture, SEO data pass
│   └── references/            # 9 reference guides (loaded on-demand)
├── skills/                    # 8 sub-skills
│   ├── github-audit/          # 0-100 health scoring
│   ├── github-readme/         # README generation and optimization
│   ├── github-legal/          # License, security, citation
│   ├── github-meta/           # Description, topics, settings
│   ├── github-seo/            # Keyword research and content strategy
│   ├── github-community/      # Community health files and templates
│   ├── github-release/        # Release strategy and changelog
│   └── github-empire/         # Portfolio-level strategy
├── agents/                    # 6 scoring agents (parallel audit)
├── extensions/
│   └── dataforseo/            # DataForSEO MCP server setup
├── install.sh                 # macOS/Linux installer
└── install.ps1                # Windows installer
```

1 orchestrator, 8 sub-skills, 6 scoring agents, 9 reference files. The orchestrator detects your repo type (library, CLI tool, API, application, framework, documentation, or skill/plugin) and adjusts recommendations accordingly.

## License

[MIT](LICENSE)
