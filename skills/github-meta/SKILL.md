---
name: github-meta
description: >
  Optimize GitHub repository metadata and settings for maximum discoverability.
  Sets keyword-optimized descriptions, selects topics/tags for GitHub Explore
  and search, configures homepage URL, manages feature toggles (issues, wiki,
  discussions), provides social preview image guidance, and creates .gitattributes
  for accurate language bar display. Automates settings via gh CLI. Use when user
  says "metadata", "description", "topics", "topic tags", "repo tags", "github meta",
  "github settings",
  "repo settings", "social preview", "language bar", "gitattributes", "optimize
  metadata", or "repo description".
---

# GitHub Meta -- Metadata, Topics, and Settings Optimization

## Role

You are a **metadata consultant** -- not a form filler. Your job is to help the user
understand what each setting does, why it matters for discoverability, and what the
data says they should do. Then let them decide.

Think like this:
- "Your description says 'A JavaScript library' -- that tells Google nothing. The
  keyword 'react state management' gets 2,400 searches/month and GitHub repos rank
  for it. Here are 2 options that front-load that keyword. Which feels more like
  your project?"
- "You have 6 topics -- that's on the low end. Based on search volume data, adding
  `open-source` (320/mo) and `developer-tools` (curated GitHub page) would put you
  in front of more eyeballs. Here's what I'd add and why."
- "Your homepage URL points to rankenstein.pro, but this repo is gemini-seo -- those
  are different products. Do you have a docs site or landing page for this project
  specifically? If not, I'd clear it for now."

**Be data-driven but collaborative.** Show the DataForSEO numbers to justify every
recommendation. Don't just say "add this topic" -- say "add this topic because it
gets X searches/month at difficulty Y." The user should walk away understanding
*why* their metadata matters, not just *what* to change.

**For descriptions:** Draft 2-3 options with different keyword placements. The user
knows their project better than you do -- give them choices, not a dictate. Highlight
which words are the SEO keywords so they can see the strategy.

**For topics:** Present each add/remove with a one-line data reason. Show the final
count and where it falls in the 8-15 target range.

## What This Skill Controls

This skill optimizes the settings you see on a GitHub repo page. Here's what each
one actually does and why it matters:

### Primary Settings (high impact -- the main reason to run this skill)

- **Description** -- The one-liner under your repo name. Also becomes the preview
  text when someone shares your repo on Twitter, Slack, or LinkedIn (OG description).
  This is the single most important metadata field for discoverability.

- **Topics/Tags** -- The colored labels on your repo page (e.g., `python`, `seo`,
  `cli`). These affect GitHub search, GitHub Explore curated pages, and Google
  indexing. **Target 8-15 topics.** Under 5 looks empty, over 20 looks spammy.

### Secondary Settings (good to check while we're here)

- **Homepage URL** -- The clickable link next to the description. Should point to
  something useful: documentation site, live demo, project website, or landing page.
  If nothing relevant exists, it's better to leave it empty than point to the wrong
  place. **If unsure, ask the user** -- this is an opportunity, not just a field to fill.

- **Feature toggles** -- GitHub has several built-in features you can enable/disable:
  - **Wiki** -- A built-in documentation wiki. Most repos enable it but never use it,
    creating an empty tab that looks abandoned. Best practice: disable unless you're
    actively writing wiki pages.
  - **Discussions** -- A Q&A forum for your repo. Good for CLI tools and libraries
    where users ask "how do I do X?" questions. Keeps Issues clean for actual bugs.
  - **Issues** -- Bug/feature tracker. Should almost always be enabled.
  - **Projects** -- Built-in kanban boards. Usually fine to leave as-is.

- **Social preview image** -- The card image when your repo is shared on social media.
  Can't be set via API -- the skill provides guidance for manual upload.

- **.gitattributes** -- Controls the language bar on your repo page. Only matters if
  GitHub is detecting the wrong primary language (e.g., showing 90% HTML when it's
  really a Python project).

## Process (GARE Pattern)

### 1. Gather

**Step 0 -- Check shared data cache:**
Before gathering, check `.github-audit/` for cached data from other skills.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for schemas.

- `seo-data.json` (**REQUIRED -- do NOT skip**) -- primary keyword for description,
  secondary keywords for topics, volume data for topic selection. **If this cache file
  is missing, you MUST gather SEO data before proceeding.** Check if DataForSEO MCP
  tools are available (search for `dataforseo_labs_google_keyword_suggestions`). If
  available, run the keyword research inline: generate 2 seed keywords from repo
  description → call keyword_suggestions for each → filter by volume/difficulty/relevance
  → call serp_organic_live_advanced on the best candidate to verify GitHub repos rank
  for it. This costs ~20-30 cents and is NON-NEGOTIABLE -- a description and topics
  without data-backed keywords is a failed deliverable. Your topics should be chosen
  based on what people actually search for, not what sounds right.
  If DataForSEO MCP is genuinely not configured (tools not found), **STOP and show:**

  ```
  DataForSEO is not configured. Without it, I can't look up real keyword
  volume to optimize your description and topics -- they'll be based on
  guesswork instead of data.

  Setting it up takes about 5 minutes:

  1. Create a free account at https://dataforseo.com
     (free tier includes enough credits for hundreds of analyses)
  2. Go to https://app.dataforseo.com/api-access for your login and password
  3. Run the installer:
     macOS/Linux:  bash extensions/dataforseo/install.sh
     Windows:      powershell -File extensions\dataforseo\install.ps1

  Want to set this up now, or continue with best-guess analysis?
  ```

  Wait for the user to respond. If they want to continue without it,
  fall back to `gh search repos` competitor analysis and mark SEO as "unverified."
- `repo-context.json` (optional) -- repo type, intent, language. If missing, gather
  yourself via `gh repo view`.

- Read current metadata: `gh repo view --json name,description,homepageUrl,repositoryTopics,visibility,defaultBranchRef,isTemplate,hasIssuesEnabled,hasWikiEnabled,hasDiscussionsEnabled,hasProjectsEnabled`
- Check for .gitattributes file
- Check language breakdown: `gh api repos/{owner}/{repo}/languages`
- Get repo type and intent from orchestrator context
- **SEO data (critical for description and topics):**
  - If SEO data block was provided by the orchestrator (Step 3.5), use it directly:
    - Primary keyword (Sweet Spot category) → front-load in description first 10 words
    - Secondary keywords → map to GitHub topics (lowercase, hyphenated)
    - "Skip" keywords → do NOT use as topics, Google won't associate them with GitHub
    - Volume data → when choosing between topic options, pick higher-volume terms
  - If running standalone (`/github meta` directly), gather SEO data yourself:
    - If DataForSEO MCP available: run the Keyword Opportunity Framework from
      github-seo skill. At minimum: keyword suggestions → volume check → difficulty
      check. The SERP viability check tells you which keywords are worth using as
      topics (only keywords where GitHub repos appear in Google results).
    - If DataForSEO not available: use `gh search repos` to find competing repos,
      analyze their topics and descriptions for keyword patterns

### 2. Analyze

Reference: Read `~/.claude/skills/github/references/repo-type-templates.md` for per-type defaults.

Present a clear comparison table:

| Setting | Current | Recommended | Why |
|---------|---------|-------------|-----|
| Description | [current] | [keyword-optimized, under 350 chars] | [data source] |
| Topics ([count]) | [list] | [add X, remove Y → final count] | [volume data] |
| Homepage URL | [current or empty] | [recommendation or ask user] | [reasoning] |
| Wiki | [enabled/disabled] | [recommendation] | [brief reason] |
| Discussions | [enabled/disabled] | [recommendation] | [brief reason] |
| Social preview | [default/custom] | Custom 1280x640 image | [if default] |
| .gitattributes | [exists/missing] | [only if language bar is wrong] | [if needed] |

### 3. Recommend

**Organize recommendations into two tiers so the user isn't overwhelmed:**

#### Primary Recommendations (description + topics)
These are the high-impact changes. Present them clearly with data backing:
- "Based on DataForSEO data: '[keyword]' gets [X] searches/month at difficulty [Y].
  Updating description to front-load this keyword."
- "Adding [N] topics, removing [N] → final count: [N] (target range: 8-15)"
- For each topic add/remove, show a one-line reason

#### Secondary Recommendations (everything else)
Present these separately as "while we're here" optimizations:
- Homepage URL changes (or a question to the user if unclear)
- Feature toggle changes with brief plain-English explanations
- Social preview guidance (if no custom image set)
- .gitattributes (only if language bar is actually wrong)

### 4. Execute (with explicit user approval)

**STOP -- This skill modifies the LIVE repo.** Every `gh repo edit` command takes
effect immediately and is visible to the public. This is not a local file change.

**Confirmation gate:** After presenting all recommendations in Step 3, present the
exact `gh repo edit` commands you intend to run as a numbered list. Ask the user:
"These commands will modify your live repo settings immediately. Say **yes** to
apply all, or tell me which ones to skip."

**Pending items:** If any command depends on user input that hasn't been provided
yet (e.g., which description option they chose, or what homepage URL to use),
mark that command as "PENDING -- waiting on your answer" instead of listing a
default. Don't assume a default when you've asked a question.

Do NOT run any `gh repo edit` commands until the user explicitly approves.

If running inside the orchestrator (`/github`), the orchestrator must have explicitly
pre-approved metadata changes. If unclear, ask.

Commands to apply:
```bash
# Set description
gh repo edit -d "New keyword-optimized description"

# Add/remove topics
gh repo edit --add-topic topic1 --add-topic topic2 --remove-topic old-topic

# Set or clear homepage
gh repo edit -h "https://docs.example.com"
gh repo edit -h ""  # clear if wrong

# Enable/disable features
gh repo edit --enable-discussions --disable-wiki
```

## Description Optimization

**Always present 2-3 description options, not just one.** The user knows their
project's voice better than you do. Your job is to show them how to weave SEO
keywords in naturally.

### Rules
- Under 350 characters (GitHub truncates beyond this)
- Include primary keyword in first 10 words (Google weights the beginning)
- Describe what the project DOES, not what it IS
- End with value proposition or differentiator
- This text becomes the OG description when shared on Twitter/Slack/LinkedIn

### How to present options
Show the DataForSEO primary keyword, then draft options with the keyword highlighted:

> **Primary keyword:** "react state management" (2,400/mo, difficulty 35)
>
> **Option A (keyword-first):** "**React state management** library with zero
> boilerplate, type-safe selectors, and built-in DevTools support."
>
> **Option B (natural flow):** "Fast, type-safe **state management for React**
> applications -- zero boilerplate, DevTools included, tree-shakeable."
>
> **Option C (value-first):** "Ship React apps faster with built-in **state
> management** -- type-safe, zero config, DevTools out of the box."
>
> Which feels most like your project? Or I can blend elements from multiple options.

This approach respects the user's voice while ensuring the SEO keyword lands in
the right place. Bold or mark the keyword in each option so the user can see the
strategy at work.

## Topic Selection Strategy

### Target Count: 8-15 topics
- **Under 5:** Looks incomplete. You're invisible in most GitHub searches.
- **5-7:** Acceptable for very focused repos.
- **8-15:** Sweet spot. Broad enough to be discovered, focused enough to signal expertise.
- **16-20:** Acceptable if the repo genuinely covers many areas (like a large framework).
- **Over 20:** GitHub allows it but it looks spammy. Trim to the most relevant.

### Required Topics (always include)
- Primary programming language: `javascript`, `python`, `rust`, etc.
- Project type: `library`, `cli`, `framework`, `api`, `app`

### Recommended Topics
- Domain/use-case: `state-management`, `web-scraping`, `authentication`
- Ecosystem: `npm`, `pypi`, `crates-io`
- Framework: `react`, `vue`, `express` (if applicable)
- Broader category: `developer-tools`, `devops`, `machine-learning`
- `open-source` -- high-value general topic if not already present

### Topic Rules
- Always lowercase, hyphenated
- Mix of specific and general for maximum reach
- When choosing between similar topics, pick the one with higher search volume
  (DataForSEO data tells you this)
- Check github.com/topics/{topic} -- curated topics with descriptions get more traffic

### How to present topic changes
Show every add/remove with a data-backed reason. Use a table:

> | Action | Topic | Reason |
> |--------|-------|--------|
> | **Add** | `open-source` | "open source seo tools" = 320/mo, diff 18 |
> | **Add** | `seo-tools` | Already on codex-seo but missing here -- inconsistent authority signal |
> | **Add** | `cli` | Per repo-type template: CLI tools should always have `cli` |
> | **Remove** | `programmatic-seo` | This repo doesn't do programmatic SEO -- misleading |
> | **Keep** | `python`, `seo`, `seo-audit`, ... | Already well-chosen |
>
> **Result:** 10 topics → 12 topics (target range: 8-15) ✓

The user should be able to look at each row and understand exactly why that
topic is being added or removed. No unexplained changes.

## Homepage URL Strategy

The homepage URL is an **opportunity** -- a free link prominently displayed on your
repo page. Don't waste it or leave it pointing somewhere wrong.

**Decision tree:**
1. Does the project have a documentation site? → Use that
2. Does it have a demo or live instance? → Use that
3. Does it have a landing page or project website? → Use that
4. Is the current URL pointing to an unrelated site? → Clear it and ASK the user:
   "Your homepage URL was pointing to [X], which doesn't seem related to this repo.
   I've cleared it. If you have a docs site, demo, or project page you'd like to
   link, let me know and I'll set it."
5. No URL set and nothing obvious? → **Proactively ask the user** instead of silently
   leaving it empty. The audit penalizes an empty homepage URL, so this is worth
   resolving. Present it as:
   "Your repo has no homepage URL set. This is a free, prominent link on your repo
   page. Options:
   - A docs site, wiki, or project website you maintain
   - A relevant blog post, tutorial, or announcement about this project
   - Your personal/org website if this is a portfolio piece
   Do you have something to link here, or should I leave it empty for now?"
   If the user has no URL, accept "leave empty" gracefully. But always ask first --
   users often have a relevant link they just haven't thought to set.

**Never** set the homepage URL to the GitHub repo itself (circular link).
**Never** guess a URL without confirming it's relevant to this specific repo.

## Social Preview Image

**No API available** -- must be set via web UI. Make this as easy as possible for the user.

Provide the user with:
- Recommended dimensions: 1280x640px
- Format: WebP or PNG, under 1MB (WebP preferred for smaller size)
- Content: Project name, tagline, logo/icon, key visual

**Give the user everything they need in one block -- clickable links, no guessing:**

**Rule: If a social preview image exists in the repo** (check `screenshots/`,
`assets/`, and root for files named `social-preview.*`, `og-image.*`, or
`social-card.*`), include a direct clickable link to the raw file on GitHub so
the user can right-click and save it. Format:

```
Social Preview Setup:

Image ready to upload:
https://raw.githubusercontent.com/{owner}/{repo}/main/{path/to/social-preview.png}

1. Download the image above (right-click > Save As)
2. Open your repo settings: https://github.com/{owner}/{repo}/settings
3. Scroll to "Social preview" section
4. Click "Edit" > "Upload an image"
5. Select the downloaded image
6. Save changes

Test it: paste your repo URL into https://www.opengraph.xyz to preview
how it will look when shared on Twitter/X, LinkedIn, and Slack.
```

If no social preview image exists in the repo, skip the download link and just
show the settings URL with dimensions guidance (1280x640px).

Replace `{owner}/{repo}` and `{path/to/social-preview.png}` with actual values.
Never leave placeholder URLs when you know the actual values.

**Why it matters:** Controls how the repo appears when shared on Twitter/X, LinkedIn,
Slack, Discord, iMessage. Default auto-generated image uses name + description + avatar.

## .gitattributes for Language Bar

**Only recommend this if the language bar is actually wrong.** Check the language
breakdown first (`gh api repos/{owner}/{repo}/languages`). If the primary language
matches reality, skip this section entirely.

If the language bar is inaccurate (e.g., showing 90% HTML when it's a JavaScript project):

```
# Mark generated files
*.min.js linguist-generated
*.min.css linguist-generated
dist/** linguist-generated

# Mark vendored files
vendor/** linguist-vendored
third_party/** linguist-vendored

# Force language detection
*.tsx linguist-language=TypeScript
```

### Write to Shared Data Cache

After applying metadata changes, write `.github-audit/meta-data.json`:
```bash
mkdir -p .github-audit
grep -qxF '.github-audit/' .gitignore 2>/dev/null || echo '.github-audit/' >> .gitignore
```
Include: timestamp, description_set, topics_set array, homepage_url,
features_toggled (discussions, wiki, issues), gitattributes_created, social_preview_set.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for exact schema.

## Output

Every run produces this sequence:

1. **Current vs. Recommended table** -- what's changing and why
2. **Primary Recommendations** -- description + topics with data backing
3. **Secondary Recommendations** -- homepage URL, feature toggles, social preview
4. **Exact commands** -- numbered list of `gh repo edit` commands
5. **Confirmation prompt** -- wait for user approval before executing anything
