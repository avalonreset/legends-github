<!-- Updated: 2026-03-08 -->
# GitHub SEO Guide — Ranking Factors, Indexing Rules, and Keyword Strategy

## Overview

GitHub repos rank in Google search results. Optimizing for both Google and GitHub's
internal search/Explore increases organic discovery. This guide covers what Google
indexes, what it ignores, and how to maximize visibility.

## What Google Indexes on GitHub

| Content | Indexed? | SEO Priority |
|---------|----------|-------------|
| README.md content | Yes — PRIMARY target | Critical |
| Repo landing page (name + description) | Yes | Critical |
| GitHub Pages sites | Yes — fully indexed | High |
| Discussions | Yes (2-3 week delay) | Medium |
| Releases / release notes | Yes | Medium |
| Wiki pages | Only if 500+ stars AND editing restricted | Low |
| Source code files | No (blocked by robots.txt `/*/*/tree/`) | None |
| Issues | Mostly blocked | None |
| Forks page | Blocked (`/*/*/forks`) | None |
| Projects / Milestones | Blocked | None |
| Pulse / Insights | Blocked | None |

**Key insight:** README is your homepage. Treat it like a landing page.

## GitHub's robots.txt Key Rules

```
Disallow: /*/*/tree/       # Blocks source code browsing
Disallow: /*/*/pulse       # Blocks activity insights
Disallow: /*/*/issues/new  # Blocks issue creation
Disallow: /*/*/forks       # Blocks forks page
Disallow: /*/*/projects    # Blocks project boards
Disallow: /*/*/milestones  # Blocks milestones
```

## Google Ranking Factors for GitHub Repos

### On-Page Factors (you control these)
1. **Repository name** — Keywords in repo name (hyphenated) rank strongly
2. **Description** — 350-char limit, keyword-rich, appears in search snippets
3. **README content** — H1, first paragraph, heading hierarchy, keyword density
4. **Topics/tags** — Feed GitHub Explore and search filters (5-20 recommended)
5. **Homepage URL** — Links to docs site boost authority

### Social/Authority Signals (earned)
1. **Stars** — Primary popularity signal (83% of developers consider it most useful)
2. **Forks** — Indicates active development/contribution
3. **Watchers** — Engaged audience signal
4. **"Used by" count** — Strong social proof for published packages
5. **Recent activity** — Signals active maintenance

### Technical Factors
1. **Canonical URLs** — GitHub handles these automatically
2. **OG tags** — GitHub auto-generates from name + description + language
3. **Page speed** — GitHub's infrastructure handles this

## GitHub-Internal Discovery

### Topics / GitHub Explore
- Up to 20 topics per repo
- Always lowercase, hyphenated: `machine-learning` not `Machine Learning`
- Use both specific (`react-hooks`) and general (`javascript`) topics
- Curated topics appear at github.com/topics/{topic}
- Topics feed "Suggested repositories" on the homepage

### GitHub Search
- Searches repo name, description, README content, and topics
- Filter by language, stars, forks, license, and more
- Recently updated repos rank higher in relevance sorting

## Keyword Strategy for GitHub

### Step 1: Identify Seed Keywords
- What problem does the project solve?
- What technology does it use?
- What would someone Google to find this?
- Examples: "react state management", "python web scraper", "cli tool for X"

### Step 2: Expand with Variations
- Synonyms: "state management" / "state container" / "store"
- Long-tail: "best react state management library 2026"
- Problem-based: "how to manage react state without redux"
- Comparison: "zustand vs redux vs jotai"

### Step 3: Place Keywords
| Location | What to Put |
|----------|-------------|
| Repo name | Primary keyword (hyphenated) |
| Description | Primary + secondary keywords, natural sentence |
| Topics | Mix of specific and general terms (5-20) |
| README H1 | Project name + primary keyword |
| README first paragraph | Primary keyword in first sentence |
| README H2 headings | Secondary keywords where natural |
| README body | Natural density (1-3%), semantic variations |

### Step 4: Validate with Data (if DataForSEO MCP available)

Use the **Keyword Opportunity Framework** from the github-seo skill to validate
keyword choices with real data. The framework categorizes keywords as:

| Category | Criteria | Action |
|----------|----------|--------|
| **Sweet Spot** | Volume 100-5K, difficulty <40, GitHub in SERP | Target first — H1, description, first paragraph |
| **Worth It** | Volume 1K-10K, difficulty 40-60, GitHub in SERP | Target in H2 headings and body |
| **Long Shot** | Volume 10K+, difficulty 60+ | Use variations; may rank with stars |
| **Skip** | No GitHub repos in SERP | Don't target — Google won't serve repos |
| **Low Value** | Volume <50/mo | Not enough traffic to matter |

**Key MCP tool calls (in order):**
1. `dataforseo_labs_google_keyword_suggestions` — expand seed keywords (~50 candidates)
2. `kw_data_google_ads_search_volume` — validate monthly search volume
3. `dataforseo_labs_bulk_keyword_difficulty` — find low-competition opportunities
4. `serp_organic_live_advanced` — **MOST IMPORTANT**: check if github.com appears in results
5. `ai_optimization_chat_gpt_scraper` — check AI citation visibility

The SERP viability check (step 4) is critical: if no github.com URLs appear in
the top 20 results for a keyword, a GitHub repo cannot realistically rank for it.

See the github-seo skill for the full Opportunity Score formula and detailed workflow.

## GEO Optimization (AI Citability)

### Why This Matters
AI systems (ChatGPT, Perplexity, Google AI Overviews) increasingly recommend tools
and libraries. Brand mentions correlate 3x more with AI visibility than backlinks.

### How to Optimize
- **Clear, quotable descriptions** — "X is a Y that does Z" (extractable by AI)
- **Structured comparisons** — Tables comparing your tool to alternatives
- **Statistics and facts** — Specific numbers AI systems can cite
- **Answer-first formatting** — Lead with the answer, then explain
- **Schema markup** — SoftwareSourceCode JSON-LD in GitHub Pages

### Monitoring AI Visibility
If DataForSEO MCP server is available:
- `ai_optimization_chat_gpt_scraper` — Check if ChatGPT mentions your project
- `ai_opt_llm_ment_search` — Track LLM mentions across platforms (ChatGPT, Perplexity, Claude, Gemini)

## GitHub Pages as SEO Multiplier

GitHub Pages sites are fully indexed by Google. A documentation site dramatically
expands your SEO footprint beyond just the README.

**When to recommend Pages:**
- Project has more than basic usage docs
- User intent is Business/Brand or Open Source Community
- Competing projects have docs sites
- README is getting too long (500+ lines)

**SEO benefits:**
- Multiple indexed pages (each can rank for different keywords)
- Custom meta tags and schema markup
- Sitemap.xml for better crawling
- Full control over content structure
