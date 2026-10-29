<a name="banner"></a>
<a name="legends-github"></a>

# ![legends-github](assets/banner.webp)

[![release](https://img.shields.io/github/v/release/avalonreset/legends-github?label=release&sort=date&style=flat-square&labelColor=000000&color=ff0000)](https://github.com/avalonreset/legends-github/releases/latest)
[![checks](https://img.shields.io/github/actions/workflow/status/avalonreset/legends-github/ci.yml?branch=main&label=checks&style=flat-square&labelColor=000000)](https://github.com/avalonreset/legends-github/actions/workflows/ci.yml)
[![license](https://img.shields.io/github/license/avalonreset/legends-github?label=license&style=flat-square&labelColor=000000&color=666666)](LICENSE)

`legends-github` is an open source GitHub SEO, repository audit, and discoverability toolkit for AI coding agents and developers. It helps you audit repository health, research real Google and GitHub search demand via `legends-dataforseo`, optimize GitHub repository descriptions and up to 20 GitHub topics, improve README structure without clobbering custom layouts, verify 1280x640 social preview cards, and ship clean releases.

Use it through your coding agent via the [`cto-legends`](https://github.com/avalonreset/cto-legends) router or run its deterministic Python CLI commands directly. No model vendor lock-in, no MCP server setup, and no paid image API keys are required.

**Quick links:** [Releases](https://github.com/avalonreset/legends-github/releases) · [Agent entry point](AGENTS.md) · [Module recipe](docs/GITHUB-RECIPE.md) · [DataForSEO research guide](docs/SEO-RESEARCH.md) · [Discovery guide](docs/DISCOVERY.md) · [Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)

## Agent setup (via `cto-legends`)

Part of the [`cto-legends`](https://github.com/avalonreset/cto-legends) ecosystem. `cto-legends` is the single registered router skill; this repository vendors a pinned copy at [`skills/cto-legends/SKILL.md`](skills/cto-legends/SKILL.md).

Install with `cto-legends install legends-github`, then ask your agent to audit, SEO-optimize, or prepare a release for any local or remote GitHub repository:

```sh
cto-legends install legends-github
```

 Once installed, give your coding agent a natural prompt:

> *"Use legends-github to audit my repository, run live DataForSEO keyword research for our category, optimize our GitHub description and 20 repository topics, and upgrade our README for search discoverability."*

Do not register `legends-github` as a standalone skill; the router loads [`docs/GITHUB-RECIPE.md`](docs/GITHUB-RECIPE.md) on demand.

## Start with your repository

Download and extract the [v0.2.1 installable ZIP](https://github.com/avalonreset/legends-github/releases/tag/v0.2.1), or clone this toolkit beside the repository you want to improve. Python 3.11+ and Git are required; authenticated [GitHub CLI (`gh`)](https://cli.github.com/) enables live GitHub metadata reads and `--apply` updates.

```sh
git clone --branch v0.2.1 https://github.com/avalonreset/legends-github.git
cd legends-github
python -m pip install -r github/requirements.txt
python legends_github.py capabilities
python legends_github.py --offline --artifacts-dir ./review-output verify --path /path/to/your/repo
python legends_github.py --offline --artifacts-dir ./review-output audit --path /path/to/your/repo
```

On systems where Python is named `python3` or `py -3`, use that executable instead. Audit and planning commands write local reports and cache files outside the target repository when `--artifacts-dir` is supplied, and never edit the target's `.gitignore`. Omit `--offline` when you want live GitHub metadata and release checks.

## What you can do: GitHub SEO, README, topics & release workflows

| Workflow | Primary outcome |
| --- | --- |
| `audit` | Collect versioned repository findings (`FINDINGS.json`), distinguish missing from unavailable evidence, and prioritize fixes across README, metadata, legal, community, release, and SEO. |
| `research` | Estimate or execute bounded Google keyword overview and organic SERP research (up to 100 keywords and 10 SERPs per batch) through `legends-dataforseo`. |
| `seo` | Synthesize repository keyword candidates or import verified DataForSEO demand (`--keyword-data`, `--serp-data`) to rank secondary keywords by search volume and CPC, build up to 20 GitHub topics, and draft an SEO-forward GitHub repository description. |
| `meta` | Plan and optionally `--apply` GitHub repository description, up to 20 repository topics (automatically stripping low-value build filler), homepage URL validation, and feature toggles via `gh repo edit`. |
| `readme` | Preserve existing custom README layouts verbatim for targeted agent review, or scaffold a missing README with verified setup, usage, and FAQ requirements. |
| `discover` | Build an evidence-backed organic discovery plan: target audience, reproducible example brief, workload cost transparency, competitor comparison matrix, and 14-day GitHub traffic baseline protocol. |
| `social-preview` | Validate a 1280x640 social preview card, guide agent upload, and `--verify` the live Open Graph image served by GitHub GraphQL pixel-for-pixel. |
| `release` | Audit changelog formatting (`CHANGELOG.md`), semver tags, CI workflows, and prepare draft or published GitHub releases. |
| `community` | Plan or scaffold `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `CODEOWNERS`, issue forms, and pull request templates. |
| `legal` | Inventory `LICENSE`, `SECURITY.md`, `CITATION.cff`, and upstream attribution notices without inventing legal claims. |
| `empire` | Audit a multi-repository GitHub portfolio and align profile presentation across related projects. |
| `cache-status` | Inspect isolated per-repository evidence and cache artifacts saved by earlier workflow runs. |

Run `python legends_github.py <workflow> --help` for exact flags. Default commands are read-only planning passes; mutation flags (`--write`, `--write-files`, `--apply`, `--execute`, `--create-release`, `--publish`) run only when explicitly passed.

## Measured GitHub SEO & DataForSEO keyword research

Most "GitHub SEO" tools guess keywords from local filenames or stuff irrelevant tags into your repository. `legends-github` separates unverified local hypotheses from measured search evidence:

```sh
python -m pip install -r requirements-dataforseo.txt
python legends_github.py research --path /path/to/your/repo --keyword "github seo" --keyword "open source seo tools" --serp "github seo" --execute --confirm-cost-usd 0.05
python legends_github.py seo --path /path/to/your/repo --keyword-data ./review-output/research-.../demand.json --primary-keyword "github seo" --serp-data ./review-output/research-.../serp-1.json
python legends_github.py meta --path /path/to/your/repo --apply
```

When you import live DataForSEO keyword and SERP exports into `seo`:

- **Volume and CPC prioritization:** Secondary keywords are sorted by verified monthly search volume and commercial CPC (`cpc`, `competition_level`, `keyword_difficulty`).
- **20-slot GitHub topic synthesis:** `seo` and `meta` generate up to 20 clean, hyphenated GitHub repository topics from your verified keyword clusters while filtering out build-tool noise (`vite`, `webpack`, `eslint`, `prospecting`) and preventing router pins (`skills/cto-legends/SKILL.md`) from misclassifying applications or CLIs as skills.
- **SERP rank detection:** Organic SERP exports are scanned to check whether `github.com` repositories already rank in Google's top 10 for your target queries (`github_in_serp`, `github_serp_position`).
- **Explicit cost receipts:** Every `research` run writes a `receipt.json` with exact task costs (`reported_cost_usd`). See [`docs/SEO-RESEARCH.md`](docs/SEO-RESEARCH.md) and [`docs/GEOGRID-SEARCH-STRATEGY.md`](docs/GEOGRID-SEARCH-STRATEGY.md).

## Organic discovery & why repositories earn GitHub stars

Ranking in GitHub search, Google, and AI coding assistants requires more than metadata tags. Use `discover` to plan high-conversion repository improvements around real developer tasks:

```sh
python legends_github.py --offline --artifacts-dir ./review-output discover --path /path/to/your/repo --audience "intended developers" --category "problem category" --competitor "Alternative A" --competitor "Alternative B"
```

The discovery planner inspects bounded repository evidence and builds a structured plan covering:

1. **Reproducible first result:** Make one high-value example or zero-credit demo effortless to run.
2. **Workload cost transparency:** If a tool calls metered APIs, document exact unit prices, cached operations, and spend guards.
3. **Evidence-backed alternatives matrix:** Compare your repository against named commercial or open source alternatives using dated, verifiable dimensions instead of hype.
4. **14-day GitHub traffic & release measurement:** Capture `gh api` views, clones, referrers, popular paths, and release asset download deltas before and after each discovery change. See [`docs/DISCOVERY.md`](docs/DISCOVERY.md) and [`docs/GEOGRID-VALIDATION.md`](docs/GEOGRID-VALIDATION.md).

## GitHub social preview & optional banner artwork

A strong repository does not require a mascot, paid image API, or decorative bloat. Keep an existing banner if it helps, supply your own local artwork, or use [`github/scripts/render_banner.py`](github/scripts/render_banner.py) and [`github/scripts/render_social_preview.py`](github/scripts/render_social_preview.py) with a supplied font. See the [social preview SOP](github/references/social-preview-sop.md), [README style guide](github/references/legends-readme-style.md), and [artwork guide](github/references/banner-generation.md).

```sh
python legends_github.py social-preview --repo OWNER/REPO --image /absolute/path/social-preview.png --output ./review-output/prepared.json
# Agent uploads via Settings > Social preview > Edit > Upload photo
python legends_github.py social-preview --repo OWNER/REPO --image /absolute/path/social-preview.png --verify --output ./review-output/verified.json
```

Verification queries GitHub GraphQL and compares the served Open Graph image's dimensions (`1280x640`) and decoded pixels against your local file so a stale cache or default avatar never passes silently.

## Use your AI coding agent

The portable boundary is files, CLI flags, and structured JSON output. That makes `legends-github` work cleanly across Claude Code, OpenAI Codex, Google Gemini CLI, Antigravity, Cursor, Windsurf, and Grok without per-host installer scripts.

| Integration surface | How it works |
| --- | --- |
| `cto-legends` router | Install once via `cto-legends install legends-github`; the router loads `docs/GITHUB-RECIPE.md` when you ask for GitHub or repository SEO work. |
| Direct agent entry point | Point any file-and-shell agent at [`AGENTS.md`](AGENTS.md) and name your target repository path. |
| Standalone Python CLI | Run `python legends_github.py <workflow>` in local terminals or CI pipelines (`ubuntu`, `windows`, `macos`). |
| Optional DataForSEO research | Powered by [`legends-dataforseo`](https://github.com/avalonreset/legends-dataforseo) via `requirements-dataforseo.txt`; no MCP server configuration required. |

## How to use the findings

Every `audit` run produces both versioned evidence findings (`FINDINGS.json`) and a compatibility scorecard (`SUMMARY.json`, `GITHUB-AUDIT-REPORT.md`).

- **Evidence first:** Each finding records its source, collection timestamp, confidence, applicability (`observed`, `missing`, `unavailable`, `not_applicable`), and verification method. Offline or unauthenticated GitHub checks are marked `unavailable`, never falsely penalized as missing repository files.
- **Agent-first README awareness:** The README evaluator recognizes modern agent-first onboarding sections (`Agent setup`, `Start here`, `Talk to your agent`, `What you can do`, `Visual tour`, `Why switch`, `Data-cost economics`) as well as traditional `Installation` and `Usage` headings.
- **Prioritize real utility:** Fix broken setup instructions, missing licenses, inaccurate descriptions, and weak search positioning before adding decorative badges.

## Frequently asked questions

### How does `legends-github` improve GitHub SEO and repository discoverability?
It combines technical repository hygiene (clear H1/H2 hierarchy, descriptive opening definition, valid local links, 1280x640 Open Graph social preview) with live Google and GitHub keyword demand from `legends-dataforseo`. Your GitHub About description, 20 repository topics, and README headings are aligned with the exact terms developers search for.

### Will `legends-github readme` overwrite my custom README layout or video embeds?
No. When a repository already has a `README.md`, `readme_repo.py` preserves existing content, HTML embeds, badges, and section order verbatim (`preserve-existing` mode) and outputs diagnostic scoring so your agent can make surgical edits without clobbering your work.

### Do I need DataForSEO credits to run an audit or metadata check?
No. All 13 workflows run locally and offline for free (`--offline`). Live DataForSEO keyword and SERP collection (`research --execute`) is strictly opt-in, costs roughly `$0.014` to `$0.03` per batch, and enforces explicit cost ceilings (`--confirm-cost-usd`).

### Why does `legends-github` use `cto-legends` instead of `.claude` or `.codex` installer scripts?
Per-host shell installers clutter your home directory and break across agent updates. By routing through `cto-legends` and exposing a deterministic Python CLI (`legends_github.py`), the exact same workflows run identically across every AI coding agent and operating system.

## Project layout

- [`legends_github.py`](legends_github.py): portable CLI entry point and workflow capability registry.
- [`github/scripts/`](github/scripts): deterministic Python workflows (`audit_repo.py`, `audit_evidence.py`, `seo_repo.py`, `seo_research.py`, `research_dataforseo.py`, `meta_repo.py`, `readme_repo.py`, `discovery_repo.py`, `release_repo.py`, `community_repo.py`, `legal_repo.py`, `empire_repo.py`, `social_preview.py`).
- [`github/references/`](github/references): rubrics, evidence contracts, banner/social-preview SOPs, and SEO guides.
- [`skills/cto-legends/SKILL.md`](skills/cto-legends/SKILL.md): pinned copy of the `cto-legends` router skill.
- [`docs/GITHUB-RECIPE.md`](docs/GITHUB-RECIPE.md): router-loaded module recipe.
- [`tests/`](tests): unit and regression test suite (`114+` tests across Windows, macOS, and Linux).

## Provenance & contributing

Scaffolded with [skill-forge](https://github.com/AgriciDaniel/skill-forge), with SEO methodology adapted from [claude-seo](https://github.com/AgriciDaniel/claude-seo). Contributions and bug reports are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), and [SECURITY.md](SECURITY.md).

## Disclaimer

This tool provides automated recommendations for GitHub repository optimization, including license selection and compliance guidance. **It is not legal, financial, or professional advice.** All recommendations should be reviewed with your own due diligence before applying. For complex licensing or compliance situations, consult a qualified attorney. See [LICENSE](LICENSE) for full terms.

## License

Released under the [MIT License](LICENSE). Free and open source.
