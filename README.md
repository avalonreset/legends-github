<a name="banner"></a>
<a name="legends-github"></a>

# ![legends-github](assets/banner.webp)

<<<<<<< HEAD
A GitHub companion for improving repositories: understand what exists, identify the changes that matter, and turn them into reviewable work.
=======
[![release](https://img.shields.io/github/v/release/avalonreset/legends-github?label=release&sort=date&style=flat-square&labelColor=000000&color=ff0000)](https://github.com/avalonreset/legends-github/releases/latest)
[![checks](https://img.shields.io/github/actions/workflow/status/avalonreset/legends-github/ci.yml?branch=main&label=checks&style=flat-square&labelColor=000000)](https://github.com/avalonreset/legends-github/actions/workflows/ci.yml)
[![license](https://img.shields.io/github/license/avalonreset/legends-github?label=license&style=flat-square&labelColor=000000&color=666666)](LICENSE)
>>>>>>> origin/main

Use it through your agent or run its Python commands directly. Skills are an optional instruction layer; the underlying workflows do not require a particular model vendor.

[Releases](https://github.com/avalonreset/legends-github/releases) · [Modernization plan](docs/MODERNIZATION.md) · [Agent entry point](AGENTS.md) · [MIT license](LICENSE)

## Start with your repository

Clone this toolkit beside the repository you want to improve. Python 3.10+ and Git are required; authenticated [GitHub CLI](https://cli.github.com/) enables live GitHub metadata and changes.

<<<<<<< HEAD
```sh
=======
## Table of Contents

- [What You Get](#what-you-get)
- [Skill Examples](#skill-examples)
- [How the Audit Works](#how-the-audit-works)
- [How to Add Skills](#how-to-add-skills)
- [Getting Started](#getting-started)
- [Standard Operating Procedure](#standard-operating-procedure)
- [How Skills Communicate](#how-skills-communicate)
- [Headless Runtime](#headless-runtime)
- [Architecture](#architecture)
- [Best Practices](#best-practices)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Contributing and Security](#contributing-and-security)
- [Community](#community)
- [Other Projects](#other-projects)
- [Disclaimer](#disclaimer)
- [License](#license)

## What You Get

| Command | What It Does |
|---------|-------------|
| `/github audit` / `github-audit` | Score any repo 0-100 across 6 categories with prioritized fixes |
| `/github legal` / `github-legal` | Select a license, generate SECURITY.md, CITATION.cff by default, handle fork compliance |
| `/github community` / `github-community` | Generate issue templates, CONTRIBUTING.md, CODE_OF_CONDUCT.md, .gitattributes, CI workflow, devcontainer |
| `/github release` / `github-release` | Plan release strategy, CHANGELOG, badges, versioning, and package distribution |
| `/github seo` / `github-seo` | Run keyword research with real search volume and difficulty data |
| `/github meta` / `github-meta` | Optimize description, topics, homepage URL, feature toggles, and social preview |
| `/github readme` / `github-readme` | Generate or rewrite your README with SEO-optimized headings and banner images |
| `/github empire` / `github-empire` | Portfolio strategy, profile README, AI avatar generation, profile completeness, cross-linking |

Every recommendation cites its source: DataForSEO keyword volume, GitHub API metadata, codebase analysis, or reference guides. Nothing is guesswork.

## Skill Examples

### Audit Output

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

### SEO Keyword Discovery

```
Primary Keyword: "github repository optimization" (example keyword opportunity)
GitHub ranks #2 for this query. Recommended for H1, description, first paragraph.

Secondary Keywords:
- "github repo audit"
- "github seo tools"
- "readme generator"

Topics recommended: github-optimization, repository-audit, developer-tools...
```

### Workflow

Run `/github audit` and it generates a numbered Standard Operating Procedure with your scores. Run each skill in order: legal, community, release, seo, meta, readme. Each skill hands off to the next. Re-audit at the end to measure your improvement.

## How the Audit Works

Run `/github audit` and 6 specialized reviewers score your repo in parallel:

| Category | Weight | What It Checks |
|----------|--------|----------------|
| README Quality | 25% | Structure, headings, badges, table of contents, code examples |
| Metadata and Discovery | 20% | Description keywords, topics, homepage URL, feature toggles |
| Legal Compliance | 15% | License file, SECURITY.md, CITATION.cff, fork obligations |
| Community Health | 15% | Issue templates, CONTRIBUTING, CODE_OF_CONDUCT, devcontainer |
| Release and Maintenance | 15% | Releases, CHANGELOG, CI badges, dependabot, recency |
| SEO and Discoverability | 10% | Keyword placement, GitHub Explore signals, AI citability |

Each reviewer uses a detailed rubric with specific point values per checkpoint, not subjective impressions. The final score is a weighted sum. Claude Code uses subagents, Codex uses multi-agent workers, and Gemini CLI can load the bundled skills through the extension manifest. All six reviewers launch before aggregation where the runtime supports parallel delegation, so a full audit completes quickly instead of walking categories one by one.

### Portfolio Mode

Audit an entire GitHub profile at once:

```
/github audit avalonreset
```

This quick-scans all public repos, selects the top candidates for deep analysis, spawns up to 6 agents per repo, and produces a cross-portfolio report with shared patterns and priorities.

## How to Add Skills

**Prerequisites:** one supported agent runtime and [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated.

### Claude Code Install

**macOS / Linux:**

```bash
>>>>>>> origin/main
git clone https://github.com/avalonreset/legends-github.git
cd legends-github
python -m pip install -r github/requirements.txt
python legends_github.py capabilities
python legends_github.py --offline --artifacts-dir ./review-output verify --path /path/to/your/repo
python legends_github.py --offline --artifacts-dir ./review-output audit --path /path/to/your/repo
```

On systems where Python is named `python3`, use that instead. Audit commands write local reports and cache files. With `--artifacts-dir`, these are isolated by target repository outside the target itself. They do not apply repository fixes or edit its `.gitignore`. Omit `--offline` when you want live GitHub evidence. Missing GitHub access limits live evidence; it must not be interpreted as proof that a feature is absent.

For agent-driven work, ask your agent to read this toolkit's `AGENTS.md`, then give it the target repository and your objective. The agent needs file access and a command runner. A chat-only service needs a tool bridge or an operator to execute commands.

## What you can do

| Workflow | Useful outcome |
| --- | --- |
| `audit` | Collect versioned findings, distinguish missing from unavailable evidence, and prioritize applicable fixes. |
| `discover` | Build an organic discovery plan: audience, comparison briefs, proof, distribution, and measurement. |
| `readme` | Preserve an existing README for targeted review, or scaffold a missing README with explicit draft requirements. |
| `meta` | Propose descriptions, topics, and repository settings. |
| `community` | Plan contributor documentation and issue workflows. |
| `release` | Plan changelog, versioning, and release preparation. |
| `legal` | Inventory licensing and attribution material for review. |
| `seo` | Produce repository-derived keyword hypotheses; enrich them with research when available. |
| `empire` | Review a portfolio and prepare a consistent presentation. |
| `cache-status` | Inspect evidence saved by earlier workflows. |

Run `python legends_github.py <workflow> --help` for its exact options. Default planning commands still write local artifacts. Flags such as `--write`, `--write-files`, `--apply`, `--generate-assets`, and `--publish` have additional effects; select them deliberately for the user's task.

## Use your agent

The portable interface is files plus commands and JSON output. That is the intended integration boundary for Grok, Codex, Claude, Gemini, Cursor, Meta Muse, and other agent environments. Naming a host here is not a claim that its native integration has been tested.

| Integration | Current state |
| --- | --- |
| Python command interface | Included; independent of agent-specific installation paths. |
| File-based instructions | Read `AGENTS.md` explicitly when the host does not discover it automatically. |
| Skills | Included under `github/`, `skills/`, and `extensions/`; specialized instructions share the portable evidence and execution contract. |
| Existing native adapters | Claude and Codex installers and a Gemini extension manifest are retained. Their presence is not an end-to-end compatibility certificate. |
| Other hosts | Use the command interface where file and shell tools exist. Native adapter verification is planned. |

No new provider API key is needed for the local audit. Keyword research and image generation are optional capabilities, not prerequisites for basic repository improvement. An existing agent subscription can provide the reasoning; the toolkit does not require its own LLM account.

## How to use the findings

Audits now lead with evidence-backed findings, repository profiles, coverage, and practical next actions. Each finding carries a source, confidence, applicability, and verification. Offline or failed collection is labeled unavailable rather than a missing repository feature.

The retained legacy audit score is a weighted checklist across six categories. It is useful for finding missing signals, but it is **not a validated measure of software quality, security, search ranking, or business value**.

Start with the repository's purpose and audience. Check whether users can install it, understand it, trust its claims, and complete the main workflow. Prioritize broken instructions and missing evidence ahead of decorative badges. Do not add a citation file, community policy, generated artwork, or a release ceremony merely to increase a score.

For each proposed change, record the evidence, expected benefit, effort, and how to verify it. Keep observed facts separate from hypotheses. Parallel reviewers are optional; a single agent can perform the same work sequentially.

## Organic discovery without guesswork

```sh
python legends_github.py --offline --artifacts-dir ./review-output discover --path /path/to/your/repo --audience "intended users" --category "problem this solves" --competitor "a relevant alternative"
```

The plan turns repository evidence into candidate comparison pages, useful examples, metadata, and distribution experiments. Competitor claims, demand, and prices remain unverified until researched. It does not invent keyword volume or publish messages. The same workflow applies to a package, CLI, service, skill, or documentation project. [Discovery guide](docs/DISCOVERY.md) · [GeoGrid validation](docs/GEOGRID-VALIDATION.md).

## Optional artwork

A strong repository does not require a mascot or banner. Keep an existing image if it helps, supply your own local asset, or use the image tool already available in your agent. The toolkit has no paid image-generation integration and asks for no image-provider key. Legacy image flags now reuse or convert local assets only. For a typography-first banner, use the [optional Legends recipe](github/references/legends-banner-style.md) with a supplied font. [Artwork guide](github/references/banner-generation.md).

## Existing skill installers

These are retained for existing users while the portable interface is modernized. Review installer behavior before running it; legacy installers can configure optional services.

| Adapter | macOS / Linux | Windows |
| --- | --- | --- |
| Claude | `bash install.sh` | `./install.ps1` |
| Codex | `bash install-codex.sh` | `./install-codex.ps1` |

Gemini integration is described by `gemini-extension.json` and `GEMINI.md`. For other hosts, start with the explicit `AGENTS.md` workflow instead of guessing an installation directory.

## Project layout

- `legends_github.py`: portable command entry point.
- `github/scripts/`: existing deterministic workflows and shared runtime.
- `github/references/`: rubrics, evidence guidance, and workflow references.
- `skills/`: specialized agent instructions.
- `agents/`: existing reviewer definitions.
- `extensions/`: optional service integrations.
- `docs/MODERNIZATION.md`: reconciliation findings, milestones, and acceptance criteria.

## Provenance

<<<<<<< HEAD
Scaffolded with [skill-forge](https://github.com/AgriciDaniel/skill-forge), with SEO methodology adapted from [claude-seo](https://github.com/AgriciDaniel/claude-seo). See the repository's license and attribution files. The house `legends-github-kit` is a separate wrapper around GitHub CLI, not this repository-improvement suite.
=======
The Claude and Codex installers can help set up:

- **[DataForSEO](https://dataforseo.com)** (strongly recommended) - powers live keyword research, SERP rankings, and AI visibility tracking. The installer configures the MCP server with your credentials automatically. Without it, SEO-dependent skills fall back to codebase-only analysis and all keyword recommendations are marked "unverified." A free account includes enough credits for hundreds of analyses. A single repo analysis costs about 15-30 cents.
- **[KIE.ai](https://kie.ai/api-key)** (strongly recommended) - generates AI banner images for READMEs and AI profile avatars for your GitHub profile. The installer saves your API key to `.env`. Without it, image generation is skipped entirely. Each image costs about 4 cents.

Both services are technically optional, but without them you lose the two most differentiated features of the suite: data-backed keyword optimization and professional AI-generated visuals. **Set them up during installation.** It takes 5 minutes and makes every other skill dramatically more useful.

Restart your agent runtime after installing. Skills and extensions register on startup.

## Getting Started

**Run these skills from inside the project you want to optimize.** This is the single most important thing to get right.

The skills read your actual source code, configuration files, git history, and GitHub remote to understand what your project is and how to improve it. If you run them from an empty folder or from the wrong directory, the agent has no real data to work with and recommendations will be generic at best.

```bash
# Right - run from inside your project
cd ~/projects/my-awesome-tool
claude
> /github audit

# Wrong - running from a random directory
cd ~/Desktop
claude
> /github audit   # Claude can't see your code, configs, or git remote
```

### Standard Operating Procedure

The audit generates a numbered remediation plan tailored to your repo's scores. Run each skill in order. Each one hands off to the next when it's done.

**Phase 1: Per-Repo Optimization** (repeat for each repo)

| Step | Command | What It Does |
|------|---------|-------------|
| 0 | `/github audit` | Diagnose: scores 6 categories, generates your SOP |
| 1 | `/github legal` | Foundation: license, compliance, fork obligations |
| 2 | `/github community` | Infrastructure: templates, CoC, devcontainer |
| 3 | `/github release` | Versioning: CHANGELOG, badges, catch-up releases |
| 4 | `/github seo` | Research: keyword data for description and README |
| 5 | `/github meta` | Settings: description, topics, features (uses SEO data) |
| 6 | `/github readme` | Capstone: README optimization (uses everything above) |
| 7 | `/github audit` | Measure: re-audit to verify improvement |

Skills scoring 90+ are skipped automatically. Each skill ends with a handoff telling you exactly what to run next. Each skill caches its findings in a `.github-audit/` directory so downstream skills build on previous results instead of starting from scratch.

**Phase 2: Portfolio Optimization** (run once, after all repos are done)

| Command | What It Does |
|---------|-------------|
| `/github empire` | Profile README, cross-linking, topic sync, branding, avatar |

Empire assumes each repo is already in good shape. Always finish Phase 1 on all your repos first.

### What the Skills Read From Your Project

| Source | Skills That Use It | Why |
|--------|-------------------|-----|
| Source code and file structure | README, Community, Release | Detects language, frameworks, project type |
| `package.json`, `Cargo.toml`, etc. | Legal, Community, Release | Identifies dependencies, license conflicts, build tools |
| Git history and remotes | All skills | Determines repo owner, branch strategy, release cadence |
| GitHub API (`gh repo view`) | All skills | Reads description, topics, settings, stars, forks |
| Existing community files | Legal, Community | Checks what already exists before generating |
| DataForSEO (if configured) | SEO, README, Meta | Live keyword volume, difficulty, SERP rankings |

## How Skills Communicate

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

## Headless Runtime

legends-github includes a deterministic runner for non-interactive audits and automation:

```bash
python3 github/scripts/run_headless.py verify --mode both --path /path/to/repo
python3 github/scripts/run_headless.py audit --path /path/to/repo
python3 github/scripts/run_headless.py seo --path /path/to/repo
python3 github/scripts/run_headless.py legal --path /path/to/repo --write-files
python3 github/scripts/run_headless.py community --path /path/to/repo --write-files
python3 github/scripts/run_headless.py meta --path /path/to/repo
python3 github/scripts/run_headless.py readme --path /path/to/repo --generate-assets
python3 github/scripts/run_headless.py release --path /path/to/repo
python3 github/scripts/run_headless.py empire --path /path/to/repo
```

The runner writes machine-readable cache files under `.github-audit/` plus reports under `.github-audit/output/`. Conversational skills still provide the richer subagent or multi-agent flow; headless mode is for repeatable local checks, API jobs, and automation.

## Architecture

```
legends-github/
├── github/                    # Orchestrator skill
│   ├── SKILL.md               # Routing, intent capture, SEO data pass
│   └── references/            # 9 reference guides (loaded on-demand)
│   ├── scripts/               # Deterministic Codex/headless runtime
│   └── requirements.txt       # Python deps for headless image/TOML support
├── skills/                    # 8 sub-skills
│   ├── github-audit/          # 0-100 health scoring with 6 parallel agents
│   ├── github-legal/          # License selection, SECURITY.md, fork compliance
│   ├── github-community/      # Community health files and templates
│   ├── github-release/        # Release strategy, CHANGELOG, versioning
│   ├── github-seo/            # Keyword research and content strategy
│   ├── github-meta/           # Description, topics, settings, social preview
│   ├── github-readme/         # README generation, SEO optimization, banner images
│   └── github-empire/         # Portfolio strategy, profile README, cross-linking
├── agents/                    # 6 scoring agents (parallel audit)
├── extensions/
│   └── dataforseo/            # DataForSEO MCP server setup
├── install.sh                 # Claude Code macOS/Linux installer
├── install.ps1                # Claude Code Windows installer
├── install-codex.sh           # Codex macOS/Linux installer
└── install-codex.ps1          # Codex Windows installer
```

1 orchestrator, 8 sub-skills, 6 scoring reviewers, 9 reference files, and 1 deterministic runtime. The orchestrator detects your repo type (library, CLI tool, API, application, framework, documentation, or skill/plugin) and adjusts recommendations for each.

## Best Practices

Getting the most out of the skill suite comes down to running from the right place, in the right order, with the right services configured.

**Always run from your project folder.** The skills analyze your actual codebase, git history, and GitHub remote. Running from an empty or unrelated directory gives the agent nothing real to work with. Open Claude Code, Codex, or Gemini CLI in the root of the repo you want to optimize.

**Set up DataForSEO and KIE.ai during installation.** Both are technically optional, but without DataForSEO every keyword recommendation is guesswork, and without KIE.ai you skip banner and avatar generation entirely. Five minutes of setup unlocks the most powerful features in the suite.

**Run audit first.** Always start with `/github audit`. It produces the baseline score and caches findings that every other skill reads. Without it, downstream skills gather data from scratch, which works but takes longer and misses cross-category insights.

**Follow the SOP.** After the audit, run skills in the order shown in the [Standard Operating Procedure](#standard-operating-procedure): legal, community, release, seo, meta, readme. Each skill hands off to the next and builds on the cache from previous steps.

**Review before executing.** Every skill pauses at a confirmation gate before making live changes (pushing releases, editing repo settings, creating files). Read the proposal, adjust if needed, then approve.

**Re-audit after changes.** Run `/github audit` again when you finish. The score delta shows exactly what improved and what still needs attention.

## Frequently Asked Questions

### What are Claude Code skills?

Claude Code skills are markdown instruction files that extend Claude Code with specialized capabilities. They follow the [Agent Skills](https://github.com/anthropics/claude-code) open standard, which means any SKILL.md file placed in `~/.claude/skills/` is automatically loaded when Claude Code starts. Skills can define triggers, reference files, and sub-agents.

### How do I add skills to Claude Code?

Run the installer (`bash install.sh` or `.\install.ps1`). It copies all skill files to `~/.claude/skills/github/` and configures the DataForSEO MCP server. After installation, restart Claude Code and the skills are available immediately. Type `/github` to see available commands.

### How do I add skills to Codex?

Run the Codex installer (`bash install-codex.sh` or `.\install-codex.ps1`). It copies the orchestrator to `~/.codex/skills/github/`, specialized skills to `~/.codex/skills/github-*`, and the headless runtime to `~/.codex/skills/github/scripts/`. Restart Codex, then use commands like `github-audit`, `github-readme`, and `github-meta`.

### How do I add skills to Gemini CLI?

Run `gemini extensions install https://github.com/avalonreset/legends-github`, then restart Gemini CLI. The extension manifest points Gemini CLI at the bundled `skills/` directory and `GEMINI.md` context file.

### How does the parallel audit work?

Skills are instruction files (`SKILL.md`) loaded by the active agent runtime. In this suite, the audit flow assigns 6 category reviewers, one per scoring category, then aggregates only after the reviewer results return.

### Do I need DataForSEO to use this?

No. Every skill works without DataForSEO by falling back to codebase analysis, GitHub API data, and built-in reference guides. However, keyword recommendations will be marked "unverified" without live search data. DataForSEO adds real volume numbers, difficulty scores, and SERP verification for about 15-30 cents per repo analysis.

### What makes legends-github different?

It combines live keyword research via DataForSEO, AI image generation via KIE.ai, and a structured audit across 6 categories into one workflow. Most repo helpers handle one task. legends-github handles eight, and they share data through a cache so each step builds on the last. The audit-to-readme pipeline takes a repo from zero community health signals to a fully optimized public project in under an hour.

## Contributing and Security

Contributions are welcome. If you find a bug or have a feature request, open an issue. Pull requests are encouraged - see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

For security vulnerabilities, **do not open a public issue.** Email benjamin@rankenstein.pro directly. See [SECURITY.md](SECURITY.md) for the full disclosure policy and response timelines.

## Community

Join [AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro/about?ref=59f96e9d9f2b4047b53627692d8c8f0c) for access to exclusive projects (referral link).

## Other Projects

**[gemini-seo](https://github.com/avalonreset/gemini-seo)** - 14 professional SEO workflows for Gemini CLI. Technical audits, schema markup, Core Web Vitals, E-E-A-T, and AI search readiness.

**[BenjaminTerm](https://github.com/avalonreset/BenjaminTerm)** - Hacker-styled WezTerm distribution for Windows. Smart clipboard, paste undo, 86 curated dark themes, borderless glass mode.

**[wan2gp-operator](https://github.com/avalonreset/wan2gp-operator)** - CLI operator for Wan2GP text-to-video. VRAM-aware compose, headless batch runs, and a music video pipeline.
>>>>>>> origin/main

## Disclaimer

This tool provides automated recommendations for GitHub repository optimization, including license selection and compliance guidance. **It is not legal, financial, or professional advice.** All recommendations are generated by AI-driven analysis and should be reviewed with your own due diligence before applying. For complex licensing or compliance situations, consult a qualified attorney. The authors assume no liability for decisions made based on this tool's output. See [LICENSE](LICENSE) for full terms.

## License

[MIT](LICENSE). Free and open source. See LICENSE for full terms.

### Measured search research

Use [DataForSEO research imports](docs/SEO-RESEARCH.md) to ground keyword decisions in actual evidence. See the [GeoGrid research pilot](docs/GEOGRID-SEARCH-STRATEGY.md) for demand, search intent, costs, and proposed changes. Local-only SEO runs remain explicitly labeled hypotheses.
