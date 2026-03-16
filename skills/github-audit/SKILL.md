---
name: github-audit
description: >
  Comprehensive GitHub repository health audit with 0-100 scoring across 6
  categories: README quality, metadata and discovery, legal compliance,
  community health, release and maintenance, SEO and discoverability. Audits
  GitHub repos only -- not websites or web applications. Supports single repo
  audit, remote repo audit, and portfolio-level audit across all public repos.
  Spawns 6 parallel agents for scoring. Produces prioritized action items. Use
  when user says "audit", "github audit", "repo audit", "audit my repo",
  "repo score", "health check", "github score", "rate my repo", "repo health",
  "audit my github", "portfolio audit", or "score".
---

# GitHub Audit -- Repository Health Scoring

Primary data-gathering skill. Produces the richest dataset that other skills consume.

## Modes

- `/github audit` -- Audit the repo in the current directory
- `/github audit <owner/repo>` -- Audit a specific remote repo
- `/github audit <username>` -- Audit entire portfolio (all public repos)

## Process (GARE Pattern)

### 1. Gather (Comprehensive Data Collection)

**Step 0 -- Check shared data cache:**
Before running a full audit, check `.github-audit/audit-data.json`.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for schemas.

- If `audit-data.json` exists and is from today: offer the user a choice --
  "Cached audit scores found from earlier today. Reuse them or re-run fresh?"
  If the user says reuse, skip to Step 3 (Recommend) with cached scores.
- If `repo-context.json` exists: use it for repo type, intent, language instead
  of re-querying `gh repo view`.
- If cache is stale or user says "re-run" / "refresh": proceed with full gather below.

This step collects ALL data before any analysis. Be thorough -- agents cannot
make their own API calls, so they depend entirely on the data you provide here.

**For local/specific repo, run ALL of these:**

```bash
# 1. Repo metadata (use repositoryTopics, not topics)
gh repo view {owner}/{repo} --json name,description,url,homepageUrl,repositoryTopics,visibility,defaultBranchRef,licenseInfo,stargazerCount,forkCount,watchers,primaryLanguage,createdAt,updatedAt,isArchived,isFork,parent,hasIssuesEnabled,hasWikiEnabled,hasDiscussionsEnabled,isSecurityPolicyEnabled,usesCustomOpenGraphImage

# 2. Recent activity
gh api repos/{owner}/{repo}/commits --jq '.[0].commit.committer.date' 2>/dev/null

# 3. Releases (with titles and dates)
gh release list --repo {owner}/{repo} --limit 5

# 4. README -- read the FULL content, not just check existence
gh api repos/{owner}/{repo}/readme --jq '.content' | base64 -d

# 5. Community files -- check EACH ONE individually
# Root-level files:
gh api repos/{owner}/{repo}/contents/CONTRIBUTING.md --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/CODE_OF_CONDUCT.md --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/SECURITY.md --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/CITATION.cff --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/CODEOWNERS --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/CHANGELOG.md --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/.gitattributes --jq '.name' 2>/dev/null
gh api repos/{owner}/{repo}/contents/SUPPORT.md --jq '.name' 2>/dev/null

# 6. .github directory contents (top level)
gh api repos/{owner}/{repo}/contents/.github --jq '.[].name' 2>/dev/null

# 7. Issue templates listing
gh api repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE --jq '.[].name' 2>/dev/null

# 8. PR template check
gh api repos/{owner}/{repo}/contents/.github/PULL_REQUEST_TEMPLATE.md --jq '.name' 2>/dev/null

# 9. Workflows listing (for CI detection)
gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name' 2>/dev/null

# 10. Devcontainer check
gh api repos/{owner}/{repo}/contents/.devcontainer/devcontainer.json --jq '.name' 2>/dev/null

# 11. Dependabot check
gh api repos/{owner}/{repo}/contents/.github/dependabot.yml --jq '.name' 2>/dev/null

# 12. Release config check
gh api repos/{owner}/{repo}/contents/.github/release.yml --jq '.name' 2>/dev/null

# 13. Funding check
gh api repos/{owner}/{repo}/contents/.github/FUNDING.yml --jq '.name' 2>/dev/null

# 14. SECURITY.md content (for legal agent quality assessment)
gh api repos/{owner}/{repo}/contents/SECURITY.md --jq '.content' 2>/dev/null | base64 -d 2>/dev/null

# 15. CITATION.cff content (for legal agent validation)
gh api repos/{owner}/{repo}/contents/CITATION.cff --jq '.content' 2>/dev/null | base64 -d 2>/dev/null

# 16. CHANGELOG.md first 50 lines (for releases agent)
gh api repos/{owner}/{repo}/contents/CHANGELOG.md --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | head -50

# 17. CONTRIBUTING.md content (for community agent quality assessment)
gh api repos/{owner}/{repo}/contents/CONTRIBUTING.md --jq '.content' 2>/dev/null | base64 -d 2>/dev/null

# 18. PR template content (for community agent quality assessment)
gh api repos/{owner}/{repo}/contents/.github/PULL_REQUEST_TEMPLATE.md --jq '.content' 2>/dev/null | base64 -d 2>/dev/null

# 19. LICENSE file content -- first 20 lines (for legal agent copyright verification)
gh api repos/{owner}/{repo}/contents/LICENSE --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | head -20
# Fallback: try LICENSE.md if LICENSE not found
gh api repos/{owner}/{repo}/contents/LICENSE.md --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | head -20

# 20. config.yml content from ISSUE_TEMPLATE (for community agent blank-issue check)
gh api repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE/config.yml --jq '.content' 2>/dev/null | base64 -d 2>/dev/null

# 21. Image files in assets/ and root (for image format optimization check)
gh api repos/{owner}/{repo}/contents/assets --jq '.[] | select(.name | test("\\.(png|jpg|jpeg|gif|webp|svg)$"; "i")) | "\(.name) \(.size)"' 2>/dev/null
```

**Optimization:** You can run many of these checks in parallel using multiple
Bash tool calls in a single message. Group them logically:
- Group A: metadata + commits + releases + README (the big 4)
- Group B: all community file existence checks (batch into 2-3 commands)
- Group C: .github directory + templates + workflows
- Group D: file contents (SECURITY.md, CITATION.cff, CHANGELOG.md, CONTRIBUTING.md, PR template, LICENSE, config.yml)

**For portfolio audit:**
```bash
# Use repositoryTopics (not topics) -- topics field does not exist
gh repo list {username} --visibility public --limit 500 \
  --json name,description,repositoryTopics,stargazerCount,forkCount,primaryLanguage,updatedAt,licenseInfo,isArchived,isFork,homepageUrl,url,hasIssuesEnabled,hasDiscussionsEnabled,isSecurityPolicyEnabled,pushedAt,latestRelease
```

**Important:** Save ALL gathered data -- you will pass it to agents in Step 2.

### 2. Analyze (Spawn 6 Parallel Scoring Agents)

**You MUST use the Agent tool to spawn all 6 agents in parallel.** Do NOT score
categories yourself inline -- the agents have detailed point-by-point rubrics and
load reference files for deep domain analysis.

Launch all 6 agents in a **single message** (6 parallel Agent tool calls).
Each agent has its own rubric, scoring criteria, and reference file -- you just
need to pass the gathered data.

| subagent_type | Category | Weight |
|---------------|----------|--------|
| `github-readme` | README Quality | 25% |
| `github-meta` | Metadata & Discovery | 20% |
| `github-legal` | Legal Compliance | 15% |
| `github-community` | Community Health | 15% |
| `github-release` | Release & Maintenance | 15% |
| `github-seo` | SEO & Discoverability | 10% |

**Agent invocation -- use this exact pattern for EACH of the 6 agents:**

```
Agent tool call:
  subagent_type: "github-readme"   <- use the agent name from the table above
  description: "Score {repo} README"
  prompt: <the data payload below>
```

**Data payload template (same for all 6 agents):**

```
Score this GitHub repository. Use your rubric and load your reference file.
All data is provided below -- do NOT attempt to fetch anything yourself.

Repository: {owner}/{repo}
Description: {description}
Topics: {topics list}
Primary Language: {language}
License: {license key} -- recognized by GitHub: {yes/no}
Stars: {count} | Forks: {count}
Is Fork: {yes/no} | Parent: {parent if fork}
Homepage URL: {url or "not set"}
Has Issues: {yes/no} | Has Wiki: {yes/no} | Has Discussions: {yes/no}
Security Policy Enabled (GitHub flag): {yes/no}
Custom Social Preview: {yes/no}
Is Archived: {yes/no}
Created: {date} | Last Push: {date} | Last Commit: {date}

Releases:
{list of recent releases with version, title, date -- or "none"}

Community Files Found: {list of all files confirmed to exist}
Community Files Missing: {list of all files confirmed NOT to exist}

.github/ Contents: {list of items in .github/ directory}
Issue Templates: {list of files in .github/ISSUE_TEMPLATE/ or "none/directory not found"}
PR Template: {exists/not found}
CI Workflows: {list of .yml files in .github/workflows/ or "none/directory not found"}
Devcontainer: {exists/not found}
Dependabot: {configured/not found}
Release Config: {configured/not found}
Funding: {configured/not found}

SECURITY.md Content:
{full content or "FILE NOT FOUND" if the API returned 404}

CITATION.cff Content:
{full content or "FILE NOT FOUND" if the API returned 404}

CHANGELOG.md (first 50 lines):
{content or "FILE NOT FOUND" if the API returned 404}

CONTRIBUTING.md Content:
{full content or "FILE NOT FOUND" if the API returned 404}

PR Template Content:
{full content or "FILE NOT FOUND" if the API returned 404}

LICENSE (first 20 lines):
{first 20 lines of LICENSE or LICENSE.md, or "FILE NOT FOUND"}

Issue Template config.yml Content:
{full content or "FILE NOT FOUND" if the API returned 404}

README Content:
{FULL README text -- paste the entire decoded content, or "FILE NOT FOUND"}

Image Files (assets/):
{list of image files with name and size in bytes, or "no assets/ directory" or "no images found"}

--- DATA QUALITY NOTES ---
- "FILE NOT FOUND" means the API confirmed the file does not exist (404).
- Files in "Community Files Found" were confirmed via API to exist.
- Files in "Community Files Missing" were confirmed via API to NOT exist.
- Agents: treat "FILE NOT FOUND" as definitive absence. Score 0 for that file.
```

**Critical rules:**
- **NEVER summarize or abbreviate the README.** Paste the ENTIRE decoded content
  verbatim into every agent's payload. Agents cannot score what they cannot see.
  Even if the README is 500+ lines, pass it in full. Summarizing causes agents to
  score stub content and produces artificially low scores.
- Pass the FULL README content to every agent (especially readme, seo, meta)
- Use `subagent_type` -- do NOT use general-purpose agents
- All 6 agents in ONE message (parallel, not sequential)
- Each agent loads its own reference file and applies its own rubric
- Each agent returns: score (0-100), point breakdown table, findings, prioritized issues
- Agents do NOT have Bash access -- they CANNOT fetch data themselves

### 2b. Write to Shared Data Cache

After all 6 agents return, write results to `.github-audit/audit-data.json`.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for schema.

```bash
mkdir -p .github-audit
grep -qxF '.github-audit/' .gitignore 2>/dev/null || echo '.github-audit/' >> .gitignore
```

Write `audit-data.json` with: timestamp, overall_score, per-category scores,
action_items array, and file_existence map (boolean for each community/legal file).
This cache is consumed by github-empire and optionally by github-readme.

### 3. Recommend (Aggregate and Prioritize)

**IMPORTANT: Wait for ALL 6 agents to return before compiling the report.**
Do NOT estimate scores for agents that haven't returned yet. Do NOT compile a
partial report. If running agents in background, wait for every single one to
complete before proceeding to this step. NEVER use estimated scores.

**Overall Score:** Weighted average of all 6 category scores.

**Score Interpretation:**
| Range | Rating | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | Best-in-class GitHub presence |
| 75-89 | Good | Well-maintained, minor improvements possible |
| 50-74 | Needs Work | Significant gaps in presentation or compliance |
| 25-49 | Poor | Major issues affecting discoverability and trust |
| 0-24 | Critical | Repo appears abandoned or unprofessional |

**Priority ranking of action items:**
- **Critical** -- Legal risk or completely missing essentials (no license, no README)
- **High** -- Significant impact on discoverability (empty description, zero topics)
- **Medium** -- Optimization opportunity (README could be better structured)
- **Low** -- Nice to have (add more badges, tweak topic selection)

### 4. Execute (Standard Operating Procedure)

After presenting the audit report, generate a **numbered SOP** that tells the user
exactly which skills to run and in what order. This is not a menu -- it is a step-by-step
remediation plan. The order matters because later skills depend on earlier ones.

**Canonical skill order (always this sequence):**

| Step | Skill | Why This Order |
|------|-------|---------------|
| 1 | `/github legal` | Foundation -- license, compliance, fork obligations must be correct before anything else |
| 2 | `/github community` | Infrastructure -- templates, CoC, devcontainer build on legal foundation |
| 3 | `/github release` | Versioning -- CHANGELOG, badges, releases need legal + community in place |
| 4 | `/github seo` | Research -- keyword data feeds into meta descriptions and README content |
| 5 | `/github meta` | Settings -- description, topics, features use SEO keyword data |
| 6 | `/github readme` | Capstone -- the README references everything above and uses SEO keywords |
| 7 | Re-run `/github audit` | Measure improvement and verify all fixes landed |

**SOP generation rules:**
- **Only include skills where the score is below 90.** If legal scored 95, skip it.
- **Show the current score** next to each skill so the user sees the priority.
- **Show a brief reason** why that skill needs to run (from the action items).
- **Always end with Step 7: re-audit.** Even if only one skill ran, measure the delta.
- **Number the steps sequentially** (1, 2, 3...) skipping skills that scored 90+.

**Output format for the SOP (append this AFTER the Action Items section):**

```
### Recommended Next Steps (run in order)

| Step | Command | Current Score | What It Fixes |
|------|---------|---------------|---------------|
| 1 | `/github legal` | 67/100 | Fork copyright, missing CITATION.cff |
| 2 | `/github community` | 52/100 | Missing CODE_OF_CONDUCT, no dependabot |
| 3 | `/github release` | 56/100 | Catch-up releases, missing badges |
| 4 | `/github seo` | 56/100 | Keyword research for description + README |
| 5 | `/github meta` | 67/100 | Topics, settings, social preview |
| 6 | `/github readme` | 52/100 | Full README optimization with SEO keywords |
| 7 | `/github audit` | -- | Re-audit to measure improvement |

Start with Step 1 when ready. Each skill will guide you through its changes
and hand off to the next step.
```

**After presenting the SOP, wait for the user.** Do not auto-run any skill.
The user decides when to start and which step to run. If they say "go" or
"start" or "let's do it", run Step 1.

## Scoring Rubrics (Per Category)

### README Quality (25%)

| Score | Criteria |
|-------|----------|
| 90-100 | H1 with keyword, badges, ToC, installation, usage with examples, proper hierarchy |
| 70-89 | Most sections present, decent structure, minor keyword gaps |
| 50-69 | Basic README exists but missing key sections or poorly structured |
| 25-49 | Minimal README (just project name or one paragraph) |
| 0-24 | No README or empty README |

### Metadata & Discovery (20%)

| Score | Criteria |
|-------|----------|
| 90-100 | Keyword-rich description, 10-20 topics, homepage URL set, custom social preview |
| 70-89 | Good description, 5-9 topics, homepage URL |
| 50-69 | Basic description, 1-4 topics |
| 25-49 | Description exists but generic, zero topics |
| 0-24 | No description, no topics |

### Legal Compliance (15%)

| Score | Criteria |
|-------|----------|
| 90-100 | Correct license, SECURITY.md, CITATION.cff, fork compliance (if fork) |
| 70-89 | License present and correct, one of SECURITY/CITATION |
| 50-69 | License present but may not match intent |
| 25-49 | License file exists but not recognized by GitHub |
| 0-24 | No license (legally "all rights reserved") |

### Community Health (15%)

| Score | Criteria |
|-------|----------|
| 90-100 | Full Community Standards green, YAML issue forms, PR template, devcontainer |
| 70-89 | Most community files present, at least basic templates |
| 50-69 | CONTRIBUTING and CoC present, basic issue template |
| 25-49 | Only one or two community files |
| 0-24 | No community files at all |

### Release & Maintenance (15%)

| Score | Criteria |
|-------|----------|
| 90-100 | Regular semver releases, CHANGELOG, CI badges, Dependabot, recent activity |
| 70-89 | Releases exist, basic changelog or auto-notes, CI present |
| 50-69 | Some releases, no changelog, CI status unclear |
| 25-49 | No releases, but recent commits |
| 0-24 | No releases, no recent activity (stale) |

### SEO & Discoverability (10%)

| Score | Criteria |
|-------|----------|
| 90-100 | Keywords in README H1, optimized description, Pages site, Discussions enabled |
| 70-89 | Good keyword presence, adequate description, some discovery features |
| 50-69 | Basic keyword presence, room for optimization |
| 25-49 | No keyword strategy, generic content |
| 0-24 | Actively harmful (misleading description, wrong topics) |

## Portfolio Audit Mode

For `/github audit <username>`:

### Step 0: Filter Out Noise

After fetching the repo list, **immediately exclude** repos that aren't worth
auditing. These get listed in a "Skipped" section but consume zero tokens:

- **Archived repos** -- frozen, not actionable
- **Bare forks with zero commits ahead** -- just a mirror, nothing to optimize
- **Repos with no description AND no README AND last push > 2 years ago** -- dead repos

Report how many were filtered:
```
Found {N} public repos for {username}.
Filtered out {F} repos (archived, bare forks, abandoned).
{N-F} active repos to evaluate.
```

### Step 1: Quick Scan (all active repos, no agents)

Gather metadata for ALL active repos via `gh repo list`. For each repo, do a
lightweight inline score based on metadata alone (description, topics, license,
releases, last push date). This produces a rough ranking. Quick-scan is cheap --
it uses only the data from the single `gh repo list` call.

### Step 2: Select Deep Dives

Pick which repos get the full 6-agent treatment:

| Active Repos | Deep Dive Selection | Max Agents |
|-------------|-------------------|------------|
| 1-9 | ALL repos | 54 |
| 10-30 | Top 3 + worst 5 by quick-scan score | 48 |
| 31-100 | Top 3 + worst 7 | 60 |
| 100+ | Top 3 + worst 7 + highest-starred 2 (if not already selected) | 72 |

**Hard cap: Never deep-dive more than 12 repos** (= 72 agents max).

**Prioritize wisely for deep dives:**
- "Top" = highest quick-scan score (these are your showcase repos -- worth polishing)
- "Worst" = lowest quick-scan score AMONG repos that are still worth saving
  (skip repos with zero stars, zero forks, and last push > 1 year ago --
  they're probably experiments the user forgot about)
- "Highest-starred" = repos with the most community visibility (most to gain)

### Step 3: Confirmation

Before spawning any agents, show the plan:
```
Portfolio: {username} ({N-F} active repos, {F} skipped)

Deep-diving {M} repos (6 agents each = {M*6} total):
  - repo-a (stars: 42, quick score: 78) -- top repo
  - repo-b (stars: 15, quick score: 71) -- top repo
  - repo-c (stars: 8, quick score: 65) -- top repo
  - repo-d (stars: 0, quick score: 22) -- needs work
  - repo-e (stars: 1, quick score: 18) -- needs work
  ...

Remaining {N-F-M} repos get quick-scan estimated scores.
Proceed? [Y/n]
```

### Step 4: Deep Dive (WITH agents)

For each selected repo:
1. Gather full data (README content + all 16 file checks from Gather step)
2. Spawn all 6 agents in parallel (same as single-repo audit)
3. **Wait for ALL agents to complete before compiling any report**

### Portfolio Report Includes
- Per-repo scores (sorted by score, ascending)
- Skipped repos summary (with reason for each)
- Portfolio average score (active repos only)
- Consistency check (description style, topic overlap, badge usage)
- Topic coverage analysis (niche authority gaps)
- Top 3 repos to prioritize improving
- Cross-repo patterns (common issues)

## Output Format

```
## GitHub Audit Report: {repo-name}

### Overall Score: XX/100 ({rating})

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| README Quality | XX/100 | 25% | XX |
| Metadata & Discovery | XX/100 | 20% | XX |
| Legal Compliance | XX/100 | 15% | XX |
| Community Health | XX/100 | 15% | XX |
| Release & Maintenance | XX/100 | 15% | XX |
| SEO & Discoverability | XX/100 | 10% | XX |

### Action Items

#### Critical
- [item with specific fix]

#### High
- [item with specific fix]

#### Medium
- [item with specific fix]

#### Low
- [item with specific fix]

### Recommended Next Steps (run in order)

| Step | Command | Current Score | What It Fixes |
|------|---------|---------------|---------------|
| 1 | `/github legal` | XX/100 | [specific issues] |
| 2 | `/github community` | XX/100 | [specific issues] |
| 3 | `/github release` | XX/100 | [specific issues] |
| 4 | `/github seo` | XX/100 | [specific issues] |
| 5 | `/github meta` | XX/100 | [specific issues] |
| 6 | `/github readme` | XX/100 | [specific issues] |
| 7 | `/github audit` | -- | Re-audit to measure improvement |

Start with Step 1 when ready. Each skill will guide you through
its changes and hand off to the next step.
```
