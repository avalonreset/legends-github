---
name: github-seo
description: >
  Keyword research and SEO content optimization strategy for GitHub repositories.
  Analyzes what Google indexes on GitHub, identifies target keywords for repo
  descriptions and README content, optimizes topics and tags for GitHub Explore
  and Google search, provides GEO optimization for AI citability by ChatGPT,
  Perplexity, and AI Overviews. For GitHub repo SEO only -- not website or blog
  SEO. Data-producing skill consumed by github-readme and github-meta. Use when
  user says "seo", "github seo", "keywords", "keyword research", "optimize for
  search", "discoverability", "ranking", "github ranking", "seo strategy",
  "ai citability", "geo", or "search optimization".
---

# GitHub SEO -- Keyword Research and Content Optimization

This is a **data-producing skill**. Its output is consumed by github-readme (for content
optimization) and github-meta (for description and topic selection). It can also run
standalone for SEO strategy analysis.

## The GitHub SEO Problem (Why This Isn't Normal SEO)

GitHub repos are NOT traditional websites. You cannot:
- Build backlinks to a README
- Optimize page speed (GitHub controls rendering)
- Add meta tags or schema markup (GitHub generates these)
- Control URL structure (github.com/{owner}/{repo} is fixed)

**What you CAN control:**
- README content (H1, headings, paragraphs, keywords) -- this IS the SEO page
- Repo description (350 chars, becomes OG description on social shares)
- Topics/tags (feed GitHub Explore and internal search)
- GitHub Pages site (if applicable -- full SEO control there)

**What DataForSEO does here:** It answers the question "what should I write in my
README, description, and topics so that people find this repo when they Google?"
It does NOT scan the repo as a domain. It discovers keyword opportunities.

## The Keyword Opportunity Framework

Not all keywords are worth targeting. A keyword is only valuable for GitHub if:

1. **People actually search for it** (volume > 0)
2. **GitHub repos can rank for it** (GitHub appears in SERP results)
3. **The competition is beatable** (difficulty is manageable)
4. **The intent matches** (informational = good for READMEs)

### Opportunity Categories

| Category | Volume | Difficulty | GitHub in SERP? | Action |
|----------|--------|------------|----------------|--------|
| **Sweet Spot** | 100-5,000/mo | Under 40 | Yes, repos in top 20 | TARGET THESE FIRST -- H1, description, first paragraph |
| **Worth It** | 1,000-10,000/mo | 40-60 | Yes, repos in top 20 | Target in H2 headings and body content |
| **Long Shot** | 10,000+/mo | 60+ | Sometimes | Use variations; may rank over time with stars |
| **Skip** | Any | Any | No GitHub repos rank | Don't waste effort -- Google doesn't serve repos for this |
| **Low Value** | Under 50/mo | Any | Any | Usually not enough traffic -- but see Niche Exception below |

**Niche Exception:** For ultra-niche repos where the ENTIRE addressable search space
is low volume (e.g., "knife design software" at 40/mo for a parametric knife CAD tool),
a <50/mo keyword may be the BEST keyword available. In these cases, promote the most
relevant low-volume keyword to Sweet Spot if:
1. It is a near-perfect semantic match for the project's core function
2. Competition is LOW (difficulty under 20 or no established players)
3. No higher-volume keywords exist that are equally specific
Mark it as "Sweet Spot (niche)" in the table. A perfectly targeted 40/mo keyword
beats a poorly targeted 390/mo keyword every time.

**The Sweet Spot is the entire play.** Medium traffic, low competition, GitHub repos
already ranking = a well-optimized README can break into page 1.

### Opportunity Score Formula

For each keyword candidate, calculate:

```
Opportunity Score = Volume × GitHub Viability × Intent Multiplier × Ease Factor
```

Where:
- **Volume**: monthly search volume (raw number)
- **GitHub Viability**: 1.0 if github.com appears in top 10, 0.5 if in top 20, 0.0 if absent
- **Intent Multiplier**: 1.0 for informational, 0.7 for commercial, 0.3 for navigational, 0.1 for transactional
  - **Exception for free/open-source tools:** If the project IS the "product" people
    are searching to download/use, transactional intent aligns with repo discovery.
    Use 0.7 instead of 0.1 for transactional keywords that match the repo's core
    function (e.g., "knife design software" for a knife CAD tool, "python linter"
    for a linting library). The user searching transactionally WOULD land on GitHub.
- **Ease Factor**: (100 - difficulty) / 100

**Example:**
- "python web framework" → 5,400 × 1.0 × 1.0 × 0.28 = 1,512
- "lightweight python microframework" → 390 × 1.0 × 1.0 × 0.72 = 281
- "flask vs django" → 2,900 × 1.0 × 0.7 × 0.45 = 914
- "buy python hosting" → 1,200 × 0.0 × 0.1 × 0.80 = 0 (no GitHub repos rank, transactional)

Sort by score. The top keywords go into H1, description, and first paragraph.

## DataForSEO MCP Integration

### Which Tools Matter (and Which Don't)

Out of 79 DataForSEO MCP tools, only 10 are relevant for GitHub repo optimization.
The rest are for traditional website SEO (backlinks, on-page, tech stack, etc.).

**Primary tools (use every run):**

| Tool | What It Tells Us | Notes |
|------|-----------------|-------|
| `dataforseo_labs_google_keyword_suggestions` | Keyword ideas + volume + difficulty + intent | One call per seed. Returns everything inline. |
| `serp_organic_live_advanced` | What ranks for a query right now | **MOST IMPORTANT** -- verify GitHub repos can rank. Also returns AI Overview data. |

**Secondary tools (only when inline data is missing):**

| Tool | What It Tells Us | When to Use |
|------|-----------------|-------------|
| `kw_data_google_ads_search_volume` | Exact monthly search volume | Only if suggestions data is missing volume |
| `dataforseo_labs_bulk_keyword_difficulty` | Competition score 0-100 | Only if suggestions data is missing difficulty |
| `dataforseo_labs_search_intent` | Informational/commercial/etc. | Only if suggestions data is missing intent |
| `content_analysis_phrase_trends` | Is this topic trending? | Optional -- validate growing vs dying niche |
| `kw_data_google_trends_explore` | Google Trends data | Optional -- trend confirmation |

**Optional advanced tools (NOT used by default -- only when user requests deep analysis):**

| Tool | What It Tells Us | When to Use |
|------|-----------------|-------------|
| `dataforseo_labs_google_ranked_keywords` | What keywords a URL ranks for | Spy on competing repos to find keyword gaps |
| `ai_optimization_chat_gpt_scraper` | What ChatGPT recommends | Check if ChatGPT mentions this project or competitors |
| `ai_opt_llm_ment_search` | LLM mentions across platforms | Cross-platform AI visibility (ChatGPT, Perplexity, etc.) |

**DO NOT USE these tools (not relevant for GitHub):**
- Backlink tools (`backlinks_*`) -- you can't build links to a README
- On-page tools (`on_page_*`) -- GitHub controls page rendering
- Technology detection (`domain_analytics_technologies_*`) -- irrelevant
- WHOIS (`domain_analytics_whois_*`) -- irrelevant
- Business listings (`business_data_*`) -- irrelevant
- YouTube tools -- rarely relevant for repo optimization

### Cost Per Analysis

| Call | Cost | Notes |
|------|------|-------|
| Keyword suggestions (2 seeds) | ~0.06-0.10 | 2 calls, includes difficulty + intent inline |
| SERP check (1 query) | ~0.05-0.08 | Best opportunity candidate |
| **Total per repo** | **~0.10-0.15** | |

Warn user before portfolio-wide analysis (multiply by repo count).
Most users are on the free tier (includes credit balance) -- keep costs low.

## Process (GARE Pattern)

### 1. Gather

**Step 0 -- Check shared data cache:**
Before gathering, check `.github-audit/` for cached data from other skills.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for schemas.

- `repo-context.json` (optional) -- if present, use repo type, intent, language, metadata
  instead of re-querying `gh repo view`. If missing, gather yourself in Step 1a.

**Step 1a -- Project context (always, free):**
- Read repo metadata: `gh repo view --json name,description,repositoryTopics,primaryLanguage,stargazerCount`
- Read existing README.md (extract current headings, keywords, structure)
- Scan codebase for project purpose (package.json description, setup.py long_description, etc.)
- Get user intent and repo type from orchestrator context

**Step 1b -- Seed keyword generation (always, free):**
Generate 2-3 seed keyword phrases. Each seed becomes a separate DataForSEO call,
so fewer seeds = lower cost.

Seed patterns (pick the 2-3 most relevant):
- `[language] [what it does]` -- e.g., "python web framework"
- `[specific capability]` -- e.g., "lightweight WSGI server"
- `[problem it solves]` -- e.g., "build REST APIs python"
- `[category] [type]` -- e.g., "python microframework"
- `[upstream project] [modifier]` -- e.g., "wezterm config" (for forks/distros)

Avoid seeds that are ambiguous across domains (e.g., "hacker terminal" could
mean gaming, novelty apps, or actual developer tools -- too noisy).

**Step 1c -- DataForSEO keyword discovery:**

First, check if the DataForSEO MCP server is available by searching for
`dataforseo_labs_google_keyword_suggestions` via ToolSearch.

**If DataForSEO is NOT available, STOP and show this message:**

```
DataForSEO is not configured. Without it, SEO analysis is limited to
codebase analysis and GitHub search -- no real keyword volume, difficulty
scores, or SERP position data.

Setting it up takes about 5 minutes:

1. Create a free account at https://dataforseo.com
   (free tier includes enough credits for hundreds of analyses)
2. Go to https://app.dataforseo.com/api-access for your login and password
3. Run the installer:
   macOS/Linux:  bash extensions/dataforseo/install.sh
   Windows:      powershell -File extensions\dataforseo\install.ps1

Want to set this up now, or continue with fallback analysis?
```

Wait for the user to respond. If they want to set it up, guide them. If they
say skip/continue/later, proceed to Step 1d (fallback analysis).

**If DataForSEO IS available, proceed:**

The keyword suggestions tool returns volume, difficulty, AND intent inline with
each result. This means you do NOT need separate volume/difficulty/intent calls
in most cases -- one call per seed gives you everything.

```
1. KEYWORD EXPANSION (one call per seed -- run seeds in parallel)
   Call: dataforseo_labs_google_keyword_suggestions
   Params: { "keyword": "single seed phrase", "language_code": "en",
             "location_name": "United States", "limit": 30 }
   Note: the param is "keyword" (singular string), NOT "seed_keywords"
   Result: ~30 candidates per seed, each with:
     - keyword_info.search_volume (monthly volume)
     - keyword_properties.keyword_difficulty (0-100 score)
     - search_intent_info.main_intent (informational/commercial/etc.)
   Cost: ~0.05 per call

2. RELEVANCE FILTER -- Discard noise before scoring
   After collecting all candidates from all seeds, FILTER OUT:
   - Keywords about different products/domains (e.g., gaming results for
     a developer tool, Fallout "terminal hacker" for a terminal emulator)
   - Keywords with transactional intent (people buying, not reading READMEs)
   - Keywords where the project has zero semantic connection
   Keep only keywords that someone searching would plausibly want THIS project.

3. SERP VIABILITY CHECK -- THE MOST IMPORTANT CALL

   TARGETING LOGIC -- DO NOT just check the highest-volume keyword. Pick the
   keyword most likely to be a real opportunity for THIS repo:
   - Prefer keywords where the project has a genuine competitive angle
   - Prefer informational intent over navigational/commercial
   - Prefer niche-specific keywords over generic category keywords
   - If the repo is a fork/distro, check the upstream brand keyword FIRST
     (e.g., "wezterm terminal" before "terminal emulator for windows")
   - High volume + generic category = often dominated by product sites, not GitHub

   Call: serp_organic_live_advanced
   Params: { "keyword": "[best opportunity candidate]", "language_code": "en",
             "location_name": "United States", "device": "desktop", "depth": 20 }
   Result: the actual top 20 Google results
   Cost: ~0.10
   Check: scan results for "github.com" in the URLs
   - If github.com appears in top 10 → GitHub Viability = 1.0 (GOLD)
   - If github.com appears in 11-20 → GitHub Viability = 0.5 (possible)
   - If no github.com at all → GitHub Viability = 0.0 (SKIP this keyword)

   SERP PIVOT RULE (up to 2 checks):
   - If your first SERP check returns ZERO github.com results, do NOT stop.
     Spend one more SERP check on the top niche/brand keyword from a
     different keyword cluster. The goal is to find WHERE GitHub CAN rank,
     not just confirm where it can't.
   - If first check shows GitHub results → done (1 check used).
   - If first check shows no GitHub results → pivot to niche keyword (2 checks used).

   EXTRACT FROM EVERY SERP RESPONSE:
   a) GitHub viability (github.com URLs in results)
   b) AI Overview presence and content (free AI visibility intel)
   c) People Also Ask questions -- these are FAQ section goldmines for README
   d) "People also search for" terms -- free keyword ideas from Google itself
   e) Discussion/forum presence (Reddit, HN) -- signals community interest
```

**When inline data is missing:** If keyword_suggestions results are missing
difficulty or intent fields for some keywords, THEN make targeted follow-up calls:
- `dataforseo_labs_bulk_keyword_difficulty` for missing difficulty scores
- `dataforseo_labs_search_intent` for missing intent classifications
These are fallbacks, not standard steps.

### 2. Analyze

Reference: Read `~/.claude/skills/github/references/github-seo-guide.md` for
ranking factors and indexing rules.

**With DataForSEO data -- apply the Opportunity Framework:**

1. Calculate Opportunity Score for each keyword candidate
2. Sort by score descending
3. Categorize into Sweet Spot / Worth It / Long Shot / Skip
4. **CRITICAL: Only assign GitHub Viability scores based on actual SERP data.**
   - If you ran a SERP check for this keyword → use the real result
   - If you did NOT run a SERP check → mark as "Unverified" in the table
   - NEVER write "likely" or "probably" for GitHub Viability -- it's either
     verified by SERP data or it's unknown. Unverified keywords get scored
     with GitHub Viability = 0.5 (uncertain) and flagged as needing verification.
   - **SERP cluster rule:** Keywords that are minor variations of each other share
     one SERP (e.g., "terminal emulator for windows" / "windows terminal emulator"
     / "terminal emulator windows" are the same query cluster). If you verified ONE
     keyword in a cluster, apply that same GitHub Viability to all variants in that
     cluster and mark them "VERIFIED (cluster)" in the table. This prevents wasting
     SERP checks on near-duplicate queries and avoids misleading score differences
     between variants that would show identical Google results.
5. Select:
   - **Primary keyword**: highest-scoring Sweet Spot keyword (goes in H1, description, first paragraph)
   - **Secondary keywords**: next 3-5 Sweet Spot or Worth It keywords (go in H2 headings)
   - **Topic keywords**: all remaining viable keywords mapped to GitHub topic format
6. Check current README/description -- how many of these keywords are already present?
7. Assess AI citability -- is the project mentioned by LLMs? What competitors are mentioned instead?

**Process SERP intelligence beyond just GitHub viability:**

8. **People Also Ask (PAA) questions** → Include in report as "FAQ Opportunities."
   These are questions Google KNOWS people ask about this topic. Each one is a
   potential README section heading or FAQ entry. Extract the exact question text.
9. **People Also Search terms** → Include as "Google-suggested related keywords."
   These are free keyword ideas straight from Google's own data.
10. **Discussion/forum presence** → Note which forums (Reddit, HN, etc.) appear.
    If Reddit ranks for the keyword, it means community discussion drives traffic --
    the repo should be mentioned/linked in those communities.
11. **AI Overview content** → Note what the AI Overview says and which projects
    it mentions. This directly informs GEO recommendations.

**Without DataForSEO data (degraded mode -- strongly discourage):**

DataForSEO IS the skill. Without it, you have no volume data, no difficulty scores,
no SERP verification, no AI visibility checks. You're guessing. Tell the user:
"This analysis is severely limited without DataForSEO. Run the install script
(extensions/dataforseo/install.ps1) for real data."

Fallback (best-effort only):
1. Codebase analysis for project purpose
2. `gh search repos "[keyword]" --sort stars --limit 10` for competitor topics
3. Patterns from github-seo-guide.md reference file
4. Prioritize specificity > breadth since you can't measure volume

Mark every recommendation as "UNVERIFIED -- no DataForSEO data" in the report.

### 3. Recommend

Produce a structured keyword strategy report. This is the data that downstream
skills (readme, meta) consume.

**With DataForSEO data:**

```
## Keyword Strategy Report

### Data Sources
- DataForSEO MCP (live data, [date])
- Codebase analysis
- GitHub competitor search

### Keyword Opportunities (sorted by Opportunity Score)

| Keyword | Volume/mo | Difficulty | Intent | GitHub in SERP? | Score | Category |
|---------|----------|------------|--------|----------------|-------|----------|
| [term] | 2,400 | 32 | Info | **Yes (#4)** VERIFIED | 1,632 | Sweet Spot |
| [term] | 1,800 | 45 | Info | **Yes (#8)** VERIFIED | 990 | Worth It |
| [term] | 590 | 18 | Info | Unverified (0.5) | 242 | Needs SERP check |
| [term] | 8,100 | 72 | Comm | **No** VERIFIED | 0 | Skip |
| [term] | 3,200 | 55 | Info | Unverified (0.5) | 880 | Needs SERP check |

NOTE: "VERIFIED" = we ran a SERP check and know the answer. "Unverified" = we
used 0.5 as a placeholder. Never write "likely" or "probably" -- it's data or
it's unknown.

### Primary Keyword: "[term]"
- Volume: X/mo | Difficulty: Y | Category: Sweet Spot
- Currently in README H1: [yes/no]
- Currently in description: [yes/no]
- Placement: H1 tagline, first paragraph, repo description

### Secondary Keywords (for H2 headings):
1. "[term]" -- X/mo, difficulty Y → H2: "Installation"→ "[term] Installation"
2. "[term]" -- X/mo, difficulty Y → H2: "Features"
3. "[term]" -- X/mo, difficulty Y → H2: "Usage"

### Recommended Topics (for GitHub):
[list of 10-20 topics derived from keyword data, formatted as lowercase-hyphenated]

### Recommended Description:
"[keyword-optimized description under 350 chars with primary keyword in first 10 words]"

### AI Visibility Status:
- ChatGPT mentions project: [yes/no, context]
- Competitors ChatGPT mentions instead: [list]
- LLM mention count: [number across platforms]
- Recommendation: [what to add to README for better AI citability]

### Competitor Keywords:
- [competitor repo]: ranks for [keywords] -- we should target [overlapping terms]

### FAQ Opportunities (from People Also Ask):
Google confirms these questions are asked about this topic. Each is a potential
README section or FAQ entry:
1. "[exact PAA question]" → Recommend: add to README as H2/H3 or FAQ
2. "[exact PAA question]" → Recommend: address in description or first paragraph
[List ALL PAA questions extracted from SERP responses]

### Google-Suggested Related Keywords (from People Also Search):
Free keyword ideas direct from Google's own data:
- [term 1], [term 2], [term 3], ...
[These supplement DataForSEO suggestions -- may reveal keywords we missed]

### Community Signals (from SERP forums/discussions):
- Reddit threads ranking: [URLs and subreddits]
- Hacker News discussions: [URLs]
- Other forums: [URLs]
- Recommendation: [whether to engage these communities for visibility]
```

**Without DataForSEO data (degraded mode):**

Same structure but prefix report with a prominent warning:
"⚠ DEGRADED MODE -- No DataForSEO data. All recommendations are unverified guesses.
Install DataForSEO for real keyword data: extensions/dataforseo/install.ps1"

Use qualitative assessments ("High relevance based on codebase analysis") but mark
every row in the keyword table as "Unverified" with Score = N/A.

### 4. Execute

**Write to shared data cache** after producing the keyword strategy report:
```bash
mkdir -p .github-audit
grep -qxF '.github-audit/' .gitignore 2>/dev/null || echo '.github-audit/' >> .gitignore
```
Write `.github-audit/seo-data.json` with: timestamp, mode (quick/full),
primary_keyword (keyword, volume, difficulty, category, intent),
secondary_keywords array, skip_keywords array, recommended_description,
recommended_topics, paa_questions, ai_visibility, serp_verified flag,
github_in_serp flag, github_serp_position.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for exact schema.

SEO skill primarily produces recommendations -- execution happens in other skills:
- github-readme applies keyword recommendations to README content
- github-meta applies topic and description recommendations to GitHub settings
- If running standalone, present the strategy report for the user to act on

## GEO Optimization Checklist

For AI citability (ChatGPT, Perplexity, Google AI Overviews):

- [ ] Clear "X is a Y that does Z" definition statement in README
- [ ] Structured comparisons (tables comparing to alternatives)
- [ ] Specific statistics and data points
- [ ] Answer-first formatting for key questions
- [ ] Well-structured heading hierarchy (H1 > H2 > H3)
- [ ] SoftwareSourceCode schema on GitHub Pages (if applicable)

## Output

Structured keyword strategy report that other skills can consume.
Every keyword recommendation cites its data source (DataForSEO volume, GitHub search,
codebase analysis, etc.). No keyword is ever recommended without justification.

### DataForSEO Cost Receipt

At the END of every report, include a cost receipt showing exactly what was spent.
Track each DataForSEO MCP call made during the analysis and calculate the total.

```
---
### DataForSEO Cost Receipt
| Call | Tool | Cost |
|------|------|------|
| Seed 1: "[seed phrase]" | keyword_suggestions | ~0.05 |
| Seed 2: "[seed phrase]" | keyword_suggestions | ~0.05 |
| SERP: "[checked keyword]" | serp_organic_live_advanced | ~0.10 |
| **Total DataForSEO cost** | | **~0.20** |
| Mode | Quick | |
---
```

Cost estimates per call type:
- `keyword_suggestions`: ~0.05 per call
- `serp_organic_live_advanced`: ~0.10 per call
- `ranked_keywords`: ~0.05 per call
- `ai_optimization_chat_gpt_scraper`: ~0.15 per call
- `ai_opt_llm_ment_search`: ~0.10 per call
- `bulk_keyword_difficulty`: ~0.02 per call
- `search_intent`: ~0.02 per call

Always show the receipt. Users deserve to know what they're spending.

### Next Step

After completing SEO keyword research, always end with this handoff:

```
SEO research complete. Keywords are cached in .github-audit/seo-data.json.
Next recommended step:
  /github meta -- optimize description, topics, and settings using your keyword data
```

If running as part of the audit SOP, reference the step number:
"Step 4 complete. Ready for Step 5: `/github meta`"
