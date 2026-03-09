---
name: github-dataforseo
description: >
  Live Google and AI discoverability data for GitHub optimization via DataForSEO
  MCP server. Provides keyword research (volume, difficulty, ideas), SERP analysis,
  AI visibility tracking (ChatGPT mentions, LLM citations), competitor keyword
  analysis, and trend data. Measures Google web search — not GitHub internal search.
  Requires DataForSEO extension installed. Use when user says "dataforseo",
  "github dataforseo", "keyword volume", "serp analysis", "ai mentions",
  "ai visibility", "keyword research live data", "search volume", or "trend data".
---

# GitHub DataForSEO — Live Search & AI Visibility Data (Extension)

Live search data via the DataForSEO MCP server. Provides real keyword volume,
SERP analysis, and AI visibility tracking for GitHub optimization decisions.

**Important:** DataForSEO measures Google web search volume and AI mentions — NOT
GitHub's internal search or Explore algorithm. Use this data to optimize how your
repo ranks in Google results and whether AI systems cite it.

## Prerequisites

This skill requires the DataForSEO extension:
```bash
./extensions/dataforseo/install.sh
```

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/github dataforseo keywords <seed>` | Keyword ideas from seed terms |
| `/github dataforseo volume <keywords>` | Google search volume for terms |
| `/github dataforseo serp <query>` | What ranks for this query? |
| `/github dataforseo ai-scrape <query>` | Is the project mentioned by ChatGPT? |
| `/github dataforseo ai-mentions <keyword>` | LLM mention tracking across platforms |
| `/github dataforseo competitors <domain>` | What competing projects rank for |
| `/github dataforseo trends <keyword>` | Interest trend over time |

## Commands

### keywords

Generate keyword ideas from seed terms related to the project.

**MCP tools:** `dataforseo_labs_google_keyword_suggestions`, `dataforseo_labs_google_related_keywords`

**Use for:** Discovering keyword opportunities for repo description, topics, and README content.

**Example:** `/github dataforseo keywords "react state management"`

### volume

Get actual Google search volume for specific terms.

**MCP tools:** `kw_data_google_ads_search_volume`

**Use for:** Validating which keywords are worth targeting. Higher volume = more potential traffic.

**Example:** `/github dataforseo volume "zustand,jotai,recoil,redux toolkit"`

### serp

Analyze what currently ranks for a query. Check if GitHub repos appear in results.

**MCP tools:** `serp_organic_live_advanced`

**Default parameters:** location_code=2840 (US), language_code=en

**Use for:** Understanding if GitHub repos can rank for target queries, and what the competition looks like.

**Example:** `/github dataforseo serp "best react state management library"`

### ai-scrape

Check if ChatGPT mentions your project when asked about your domain.

**MCP tools:** `ai_optimization_chat_gpt_scraper`

**Use for:** Monitoring AI visibility. If ChatGPT recommends your project, that drives adoption.

**Example:** `/github dataforseo ai-scrape "what are the best react state management libraries"`

### ai-mentions

Track LLM mentions across multiple AI platforms.

**MCP tools:** `ai_opt_llm_ment_search`

**Use for:** Cross-platform AI visibility monitoring (ChatGPT, Perplexity, Claude, etc.)

**Example:** `/github dataforseo ai-mentions "zustand"`

### competitors

Analyze what keywords competing projects rank for in Google.

**MCP tools:** `dataforseo_labs_google_ranked_keywords`

**Use for:** Finding keyword opportunities by analyzing what competing repos rank for.

**Example:** `/github dataforseo competitors "github.com/pmndrs/zustand"`

### trends

Check if interest in a technology or keyword is growing or declining.

**MCP tools:** `kw_data_google_trends_explore`

**Use for:** Validating that the project's niche is growing, not shrinking.

**Example:** `/github dataforseo trends "zustand"`

## Cross-Skill Integration

This extension enhances other skills when available:

| Skill | How DataForSEO Helps |
|-------|---------------------|
| github-seo | Real keyword volume instead of guessing, SERP validation |
| github-meta | Data-backed topic selection, validated descriptions |
| github-readme | Keyword volume data for heading optimization |
| github-empire | Niche keyword landscape, competitor analysis |
| github-audit | SEO score can reference real ranking data |

## Cost Awareness

DataForSEO charges per API call. Be efficient:
- Batch keyword volume checks (multiple keywords per call)
- Don't repeat SERP checks for the same query in one session
- Warn user before expensive operations (bulk competitor analysis)
