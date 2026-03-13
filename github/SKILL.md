---
name: github
description: >
  Comprehensive GitHub repository optimization suite. Orchestrates 8 sub-skills
  and 6 scoring agents to audit, optimize, and professionalize GitHub repos.
  Covers README quality, legal compliance, metadata, SEO, community health,
  releases, and portfolio strategy. Data-first approach -- every recommendation
  cites its source. Does NOT handle GitHub Actions, CI/CD pipelines, git
  commands, or deployment. Use when user says "github", "optimize repo",
  "github setup", "optimize my github", "github help", "professionalize my
  repo", "make my repo look good", "repo optimization", or "github optimization".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - WebFetch
---

# GitHub -- Repository Optimization Suite

Comprehensive GitHub optimization across SEO, legal, community, and discoverability.
Orchestrates 8 specialized sub-skills and 6 subagents. Data-first: every recommendation
traces back to a data source.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/github audit` | Full repo health audit with 0-100 scoring |
| `/github audit <owner/repo>` | Audit a specific remote repo |
| `/github audit <username>` | Audit entire portfolio (empire-level) |
| `/github readme` | Generate or optimize README |
| `/github legal` | License, SECURITY.md, CITATION.cff, fork compliance |
| `/github meta` | Description, topics, settings, social preview |
| `/github seo` | Keyword research and content optimization strategy |
| `/github community` | Templates, CONTRIBUTING, CODE_OF_CONDUCT, devcontainer |
| `/github release` | CHANGELOG, badges, versioning, release strategy |
| `/github empire` | Multi-repo portfolio strategy, profile README |
| `/github dataforseo` | Live keyword/SERP data (requires DataForSEO account) |

## Prerequisites

Before any skill can operate, check these in order:

1. **Git installed?** Run `git --version`. If missing, guide user to install.
2. **GitHub CLI installed?** Run `gh --version`. If missing: `winget install GitHub.cli` (Windows) or `brew install gh` (macOS).
3. **Authenticated?** Run `gh auth status`. If not logged in, guide through `gh auth login`.
4. **In a git repo?** Run `git rev-parse --is-inside-work-tree`. If not, ask if they want to create one or point to an existing repo.

If a user has no GitHub account, direct them to https://github.com/signup and wait for them to complete signup before proceeding with `gh auth login`.

### API Credentials

Two recommended services power SEO research and banner generation. The install
script walks users through setting both up during installation. If they skipped
setup, Step 0 below will catch it and guide them before any skill runs.

**1. DataForSEO (MCP server -- NOT .env)**
DataForSEO provides live keyword and SERP data. It runs as an MCP server
(`dataforseo-mcp-server`) configured via `~/.claude/settings.json`.
The install script handles this automatically. When configured, tools like
`dataforseo_labs_google_keyword_suggestions` are available directly in conversation.
If the MCP server is not configured, SEO skills fall back to codebase analysis.

**2. KIE.ai (REST API -- uses .env)**
KIE.ai generates banner images for READMEs. It requires an API key in a `.env` file.

**Standard .env location:** Check these paths in order:
1. Current working directory: `./.env`
2. Skill root: `~/.claude/skills/github/.env`
3. User home: `~/.env`

**Loading credentials:** Before banner generation, load the .env:
```bash
for envfile in ./.env ~/.claude/skills/github/.env ~/.env; do
  if [ -f "$envfile" ]; then
    export $(grep -v '^#' "$envfile" | xargs) 2>/dev/null
    break
  fi
done
```

| Key | Required By | Purpose |
|-----|------------|---------|
| `KIE_API_KEY` | `/github readme` (banner generation) | KIE.ai image generation |
| DataForSEO credentials | SEO data pass, `/github seo`, `/github meta`, `/github readme`, `/github empire` | Configured via MCP server, not .env |

## Shared Data Cache

Skills persist their outputs to `.github-audit/` so other skills can reuse data
without re-gathering. The orchestrator writes `repo-context.json` after baseline
gathering. Each sub-skill reads cached data before gathering and writes its own
cache file after executing.

Reference: Read `~/.claude/skills/github/references/shared-data-cache.md` for
JSON schemas, dependency map, and freshness rules.

**Orchestrator responsibilities:** Cache writes are embedded directly in Step 2
and Step 3.5 below -- look for the **CACHE:** callouts in each step.

## Orchestration Logic

### Step 0: Setup Check (runs ONCE per session, before anything else)

Before routing to any sub-skill, check if the user has the recommended services
configured. This runs the FIRST time any `/github` command is used in a session.
After showing the setup status once, do not repeat it.

**Check 1 -- DataForSEO MCP:**
Use ToolSearch to look for `dataforseo_labs_google_keyword_suggestions`.

**Check 2 -- KIE.ai API Key:**
```bash
for envfile in ./.env ~/.claude/skills/github/.env ~/.env; do
  if [ -f "$envfile" ] && grep -q 'KIE_API_KEY=.' "$envfile" 2>/dev/null; then
    echo "KIE_CONFIGURED=true"; break
  fi
done
```
(Check that the key is not just present but has a non-empty value after the `=`.)

**If BOTH are configured:** Show a one-liner and move on:
```
Services: DataForSEO [active] | KIE.ai [active] -- full power mode.
```

**If one or both are missing, STOP and show the setup guide:**
```
## Setup Check

This suite works best with two recommended services. Here's your status:

DataForSEO  [not configured]  -- powers live keyword research, SERP rankings, and AI visibility
KIE.ai      [not configured]  -- powers AI-generated banner images for READMEs

### How to set up DataForSEO (5 minutes)

1. Create a free account at https://dataforseo.com
   (free tier includes enough credits for hundreds of keyword analyses)
2. Go to https://app.dataforseo.com/api-access to find your login and password
3. From the claude-github directory you cloned during install, run:
   - macOS/Linux: bash extensions/dataforseo/install.sh
   - Windows: powershell -File extensions\dataforseo\install.ps1
   The installer will prompt for your credentials and configure the MCP server.

### How to set up KIE.ai (2 minutes)

1. Go to https://kie.ai/api-key and create a free account
2. Copy your API key
3. Paste it into ~/.claude/skills/github/.env:
   KIE_API_KEY=your_key_here

Want to set these up now, or continue without them?
(Skills still work without these services, but SEO recommendations will be
less precise and banner generation won't be available.)
```

Wait for the user to respond before proceeding. If they say continue/skip/later,
proceed normally. If they want to set things up, guide them through it.

### Step 1: Capture User Intent

On first interaction, ask conversationally what they want to accomplish. Map to one of:

| Intent | Optimization Priorities |
|--------|------------------------|
| **Open Source Community** | README (welcoming), community files (critical), topics (broad), SEO (discovery) |
| **Professional Portfolio** | README (impressive), badges (social proof), branding (consistent), pinned repos |
| **Business / Brand** | SEO (aggressive keywords), description (value prop), Pages, cross-linking |
| **Internal to Public** | Legal (thorough), SECURITY.md (critical), README (docs-heavy), CITATION.cff |
| **Academic / Research** | CITATION.cff (required), README (methodology), license (permissive), releases |
| **Hobby / Learning** | README (authentic), legal (simple MIT), community (lightweight), SEO (lower priority) |

If the user skips intent, fall back to repo-type defaults.

### Step 2: Gather Baseline Data

For any repo, collect:
- `gh repo view --json name,description,url,homepageUrl,repositoryTopics,visibility,defaultBranchRef,licenseInfo,stargazerCount,forkCount,watchers,primaryLanguage,createdAt,updatedAt`
- File existence: README.md, LICENSE, CONTRIBUTING.md, SECURITY.md, CITATION.cff, CODE_OF_CONDUCT.md, .github/ISSUE_TEMPLATE/, .github/PULL_REQUEST_TEMPLATE.md, .github/FUNDING.yml, .gitattributes, CHANGELOG.md
- Codebase scan for repo-type detection

**CACHE: After gathering, write `.github-audit/repo-context.json`** with all
baseline data. Create the directory and gitignore entry first:
```bash
mkdir -p .github-audit
grep -qxF '.github-audit/' .gitignore 2>/dev/null || echo '.github-audit/' >> .gitignore
```

### Step 3: Detect Repo Type

| Type | Signals |
|------|---------|
| Library/Package | package.json, setup.py, Cargo.toml, go.mod, pyproject.toml |
| CLI Tool | bin/, "usage:", commander, yargs, clap, argparse |
| Framework | middleware, routing, plugins, "getting started" |
| API/Service | /api, swagger, OpenAPI, endpoints |
| Application | docker-compose, Dockerfile, deployment configs |
| Skill/Plugin | SKILL.md, AGENTS.md, extension pattern |
| Documentation | mkdocs.yml, docusaurus.config.js, mostly .md files |

### Step 3.5: SEO Data Pass (DataForSEO Integration)

**This step runs automatically when the DataForSEO MCP server is available.**
It discovers keyword opportunities that all downstream skills consume. If the
MCP server is not configured, this step is skipped and skills use fallback methods.

**How to check availability:** Use ToolSearch to look for
`dataforseo_labs_google_keyword_suggestions`. If it exists, the MCP server is running.
Do NOT waste an API call just to test availability.

**When to run:** Before routing to ANY content-producing sub-skill (readme, meta,
seo, empire). Skip for legal, community, releases (they don't need keyword data).

**Important context:** GitHub repos are NOT traditional websites. We don't scan
a domain -- we discover what keywords people Google where a well-optimized GitHub
repo could rank, then place those keywords in the README, description, and topics.
See the github-seo skill for the full Keyword Opportunity Framework.

**Cost and auto-run behavior:**
- Each `keyword_suggestions` call costs ~3-5 cents
- Each `serp_organic_live_advanced` call costs ~5-8 cents
- Typical per-repo cost: 2 keyword calls + 1 SERP = ~10-15 cents

**For single repos and small portfolios (1-5 repos):** Just run it automatically.
The cost is under 75 cents -- not worth interrupting the flow to ask permission.
Show a brief note in the output: "Running DataForSEO keyword analysis (~10 cents)..."

**For large portfolios (6+ repos):** Show the cost estimate and ask before proceeding,
because 10+ repos can cost over a dollar:
```
DataForSEO SEO Pass: [N] repo(s) x ~15 cents = ~[estimated total]
Proceed? [y/n]
```
**Actually STOP and wait for a response. Do NOT continue working while waiting.**

**If DataForSEO is NOT configured:** Do not silently skip it. Encourage setup:
"DataForSEO is not configured. SEO data will use GitHub search fallback only.
For live keyword research, set it up in 5 minutes: https://dataforseo.com
Then run the install script in extensions/dataforseo/."

---

`keyword_suggestions` returns volume + difficulty + intent INLINE -- no separate
volume or difficulty calls needed.

```
1. Generate 2-3 seed phrases from: repo name + description + primary language

   SEED QUALITY RULES (critical -- bad seeds waste API calls):
   - Keep seeds SHORT: 2-3 words max. "seo audit tool" not "gemini cli seo audit tool"
   - Use CATEGORY-LEVEL terms, not project-specific jargon
   - Think: "what would a developer Google to find this kind of project?"
   - Good seeds: "python web framework", "open source seo tools", "terminal emulator"
   - Bad seeds: "gemini cli seo tools", "lightweight WSGI microframework server"

   SEED FALLBACK: If a seed returns zero results, it was too specific.
   Broaden it by removing words. "gemini cli seo" → "seo tools" → "open source seo tools".
   Budget: max 4 keyword_suggestions calls total. If all 4 return nothing usable,
   fall back to codebase + GitHub search analysis (no DataForSEO).

2. Call: dataforseo_labs_google_keyword_suggestions (once per seed)
   Params: { "keyword": "python web framework", "location_name": "United States", "language_code": "en", "limit": 30 }
   → Returns ~30 candidates each with volume, difficulty, and intent already included
   → Filter: drop anything under 50/mo volume, flag difficulty under 40 as Sweet Spot
   → NOTE: parameter is "keyword" (singular string), NOT "seed_keywords" (array)
   → NOTE: use "location_name": "United States", NOT "location_code": 2840

3. Call: serp_organic_live_advanced (on best Sweet Spot candidate)
   Params: { "keyword": "python web framework", "location_name": "United States", "language_code": "en", "device": "desktop", "depth": 20 }
   → THE CRITICAL CHECK: scan for "github.com" in results.
   → If github.com in top 10: keyword is GOLD (GitHub Viability = 1.0)
   → If github.com in 11-20: possible (0.5)
   → If no github.com at all: SKIP this keyword, try next candidate
```

**Store the results as SEO context.** Format:

```
## SEO Data (from DataForSEO)

### Keyword Opportunities (by Opportunity Score)
| Keyword | Volume/mo | Difficulty | GitHub in SERP? | Category |
|---------|----------|------------|----------------|----------|
| [term] | X | Y | Yes (#N) | Sweet Spot |
| [term] | X | Y | Yes (#N) | Worth It |

### Placements
- Primary keyword: [term] → H1, description, first paragraph
- Secondary keywords: [terms] → H2 headings
- Topic keywords: [terms] → GitHub topics

### AI Visibility
- ChatGPT mentions: [yes/no]
- Competitors mentioned instead: [list]

Data source: DataForSEO MCP (live, [date])
```

If DataForSEO is NOT available, note: `SEO Data: fallback mode (codebase + GitHub search analysis)`.
Skills will then use their own fallback methods (see github-seo skill).

**CACHE: After the SEO pass, write `.github-audit/seo-data.json`** with keyword
opportunities, placements, and AI visibility findings.

**Cost:** ~10-15 cents per repo (2 keyword calls + 1 SERP check). Warn user
before portfolio analysis (multiply by repo count).

### Step 4: Route to Sub-Skill

Pass intent + repo type + baseline data + SEO data (if available) to the
appropriate sub-skill.

**Default behavior for bare `/github <owner/repo>` (no sub-command):**
When the user provides a repo without specifying a sub-skill, run Steps 1-3.5
(intent, baseline, repo type, SEO data), then present a **Quick Health Summary**:

```
## Quick Health Summary: owner/repo

**Repo type:** [detected type] | **Intent:** [captured or assumed intent]
**Stars:** X | **License:** MIT | **Last release:** vX.X.X (date)

### Top 3 Recommended Actions (by impact)
1. [Highest impact action] → use `/github [sub-skill]`
2. [Second action] → use `/github [sub-skill]`
3. [Third action] → use `/github [sub-skill]`

### SEO Snapshot (if DataForSEO available)
Primary keyword opportunity: "[keyword]" (X/mo, difficulty Y, GitHub at #Z)

Run `/github audit` for a full 0-100 score, or pick an action above to start.
```

This gives the user immediate value and a clear next step, instead of just
showing a menu.

For commands explicitly matching a sub-skill (e.g., `/github readme`), route
directly to that sub-skill.

## The GARE Pattern

Every skill follows Gather, Analyze, Recommend, Execute:
1. **Gather** -- Collect data before making decisions
2. **Analyze** -- Compare current state vs. ideal for repo type + intent
3. **Recommend** -- Present data-backed recommendations with reasoning
4. **Execute** -- Apply changes with user approval

Every recommendation must cite its source:
- "Based on DataForSEO keyword volume..." (live data)
- "Based on analysis of your codebase..." (repo scan)
- "Based on your repo type (CLI tool)..." (detection)
- "Based on GitHub's indexing rules..." (reference file)
- "Based on audit findings..." (prior audit run)
- "Based on your stated intent..." (user intent)

## UX Principles (applies to ALL skills)

**Hold the user's hand through manual steps.** Many GitHub actions have no API
(profile photo upload, social preview, repo settings). When a skill requires manual
action, provide:

1. **Clickable file links** for generated files: `file:///[absolute-path]/assets/banner.webp`
2. **Direct URLs** to the exact settings page: `https://github.com/{owner}/{repo}/settings`
   -- always substitute the actual owner/repo, never leave placeholders when you know the values
3. **Step-by-step instructions** numbered and specific: "Go to X, click Y, upload Z"
4. **Verification links** when possible: "Test your social preview at https://www.opengraph.xyz"

The goal is zero guesswork for the user. If they need to upload a file, show them
exactly where the file is AND exactly where to upload it. If they need to change a
setting, link them to the exact page. Make the manual parts as close to automated
as possible.

**Image format pipeline:** All AI-generated images (banners, avatars) follow the
same flow: request PNG from KIE.ai (lossless source) then convert to WebP (quality
80) for delivery. WebP is ~30% smaller than JPEG at equivalent quality and GitHub
renders it natively. See `banner-generation.md` Image Format Pipeline for details.

## Reference Files

Load on-demand as needed -- do NOT load all at startup.

**Path resolution:** Reference files are installed at `~/.claude/skills/github/references/`.
When a sub-skill says `Read github/references/foo.md`, use the Read tool with the full path:
`~/.claude/skills/github/references/foo.md`

- `references/license-guide.md` -- License types, compatibility, fork obligations
- `references/readme-framework.md` -- README structure, SEO patterns, headings
- `references/github-seo-guide.md` -- GitHub ranking factors, Google indexing rules
- `references/community-files-guide.md` -- Standard files, best practices, priority by intent
- `references/community-templates.md` -- YAML issue forms, PR template, devcontainer, dependabot
- `references/banner-generation.md` -- KIE.ai Nano Banana 2 API, prompt engineering, defaults
- `references/releases-guide.md` -- Semver, changelog format, badge URLs
- `references/repo-type-templates.md` -- Per-type defaults for all repo types
- `references/shared-data-cache.md` -- Cross-skill data persistence schemas and rules

## Scoring Methodology

### GitHub Health Score (0-100)

| Category | Weight |
|----------|--------|
| README Quality | 25% |
| Metadata & Discovery | 20% |
| Legal Compliance | 15% |
| Community Health | 15% |
| Release & Maintenance | 15% |
| SEO & Discoverability | 10% |

### Priority Levels
- **Critical**: Blocks discoverability or creates legal risk (immediate fix)
- **High**: Significantly impacts professional appearance (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## Sub-Skills

1. **github-audit** -- Full repo health audit with 0-100 scoring
2. **github-readme** -- README generation and optimization
3. **github-legal** -- License, attribution, SECURITY.md, CITATION.cff
4. **github-meta** -- Description, topics, settings, social preview
5. **github-seo** -- Keyword research and content optimization
6. **github-community** -- Community health files and templates
7. **github-release** -- Release strategy, CHANGELOG, badges
8. **github-empire** -- Portfolio strategy, profile README, org profile

## Subagents

For parallel analysis during audits:
- `github-readme` -- README quality scoring
- `github-meta` -- Metadata and discovery scoring
- `github-legal` -- Legal compliance scoring
- `github-community` -- Community health scoring
- `github-release` -- Release and maintenance scoring
- `github-seo` -- SEO and discoverability scoring
