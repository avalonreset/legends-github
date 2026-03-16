---
name: github-readme
description: >
  Generate new or optimize existing GitHub README files with SEO optimization
  and professional banner image generation. Creates structured READMEs with
  keyword-optimized headings, badge rows, table of contents, installation
  instructions, usage examples, and proper heading hierarchy for search engine
  ranking. Generates 21:9 banner images via KIE.ai Nano Banana 2 as standard
  practice. Adapts tone and structure to repo type and user intent. Consumes
  keyword data from github-seo. Use when user says "readme", "github readme",
  "write readme", "optimize readme", "improve readme", "README.md", "generate
  readme", "rewrite readme", "readme template", "readme optimization", "banner",
  "repo banner", or "github banner".
---

# GitHub README -- Generation and Optimization

## Process (GARE Pattern)

### 1. Gather

**Step 0 -- Check shared data cache:**
Before gathering, check `.github-audit/` for cached data from other skills.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for schemas.

- `seo-data.json` (**REQUIRED -- do NOT skip**) -- primary keyword, secondary keywords, PAA
  questions, AI visibility. **If this cache file is missing, you MUST gather SEO data
  before proceeding.** Check if DataForSEO MCP tools are available (search for
  `dataforseo_labs_google_keyword_suggestions`). If available, run the keyword research
  inline: generate 2 seed keywords from repo description → call keyword_suggestions for
  each → filter by volume/difficulty/relevance → call serp_organic_live_advanced on the
  best candidate to verify GitHub repos can rank for it. This costs ~20-30 cents and is
  NON-NEGOTIABLE -- a README without data-backed keywords is a failed deliverable.
  If DataForSEO MCP is genuinely not configured (tools not found), THEN and ONLY THEN
  fall back to codebase-derived keywords and mark SEO as "unverified."
- `repo-context.json` (optional) -- repo type, intent, language, metadata. If missing,
  gather yourself via `gh repo view`.
- `legal-data.json` (optional) -- license type for badge selection. If missing, just
  check LICENSE file directly.
- `audit-data.json` (optional) -- README quality findings from prior audit. If present,
  use to prioritize which sections need the most improvement.

- **Codebase scan:** What does this project actually do?
  - Read package.json/setup.py/Cargo.toml for description, scripts, dependencies
  - Check for existing docs, examples, config files
  - Identify main entry point and key exports/commands
- **Existing README:** Read current README.md (if any)
  - Also check for README.rst (reStructuredText) -- some Python/Sphinx projects use it
  - If both exist, README.md takes priority (GitHub renders it on the landing page)
  - Assess structure, headings, content depth
  - Identify what's missing vs. ideal for this repo type
- **SEO data:** Use keyword opportunity data from the orchestrator's SEO data pass,
  or run github-seo inline if running standalone.
  - If SEO data block was provided (from Step 3.5 of orchestrator), use it directly:
    - Primary keyword (Sweet Spot category) → goes in H1 tagline and first paragraph
    - Secondary keywords (Worth It category) → go in H2 headings where natural
    - "Skip" keywords → do NOT target in H1/H2, but if a Skip keyword appears
      naturally in body text and is semantically relevant, that's fine -- just don't
      optimize headings or structure around it. The distinction is between "targeting"
      (building structure around a keyword) and "mentioning" (natural use in prose).
    - AI citation status → if not cited, add stronger "X is a Y that does Z" definition
  - If running standalone (`/github readme` directly), gather SEO data yourself:
    - If DataForSEO MCP available: run the Keyword Opportunity Framework from
      github-seo skill (seed generation → keyword expansion → volume → difficulty →
      SERP viability check). The SERP check is critical -- only target keywords where
      GitHub repos actually appear in Google results.
    - If DataForSEO not available: analyze codebase, check competitor repos via
      `gh search repos`, apply patterns from github-seo-guide.md
  - In all cases, produce: primary keyword, secondary keywords, recommended H1, H2 headings
  - Every keyword placed in the README must have a justification (volume data, competitor
    analysis, or codebase relevance)
- **Legal data:** Check LICENSE type for License section
- **Audit data:** If a prior `/github audit` ran, use its README quality findings
- **Intent + repo type:** From orchestrator context
- **Banner status:** Does the repo already have a banner image? Check for `assets/banner.webp`, `assets/banner.jpg`, `assets/banner.png`, or any image referenced at the top of README

### 2. Analyze

Reference: Read `~/.claude/skills/github/references/readme-framework.md` for structure patterns.
Reference: Read `~/.claude/skills/github/references/repo-type-templates.md` for per-type README structure.

**Docs-site detection:** If the Homepage URL points to a documentation site
(readthedocs, github.io, custom docs domain) or the README links to external
docs, apply adjusted expectations:
- Do NOT penalize for missing Installation/Configuration/API sections if docs
  cover them -- the README is a gateway, not the full docs
- DO still require: strong H1 + tagline, opening paragraph with keywords,
  badges, one code example, Contributing link, License mention
- Note in your analysis: "External docs detected at [URL] -- scoring adjusted"
- Completeness score should evaluate whether the README effectively directs
  users to the docs, not whether it duplicates them

Score the current README (if exists) using these objective rubrics. Each criterion
has specific checkpoints worth defined points. Score by counting what's present --
not by subjective impression.

#### Structure (20 points max)
| Checkpoint | Points |
|------------|--------|
| Exactly one H1 heading | 4 |
| H1 includes descriptive tagline (not just project name) | 4 |
| Proper heading hierarchy (no skipped levels) | 4 |
| At least 4 H2 sections | 4 |
| Table of Contents present (for READMEs with 4+ sections) | 4 |

#### Content Depth (20 points max)
| Checkpoint | Points |
|------------|--------|
| Installation/setup instructions with code block | 5 |
| At least one usage example with code block | 5 |
| Configuration, API reference, or detailed options/commands section (skip if repo type doesn't need config -- redistribute 4 pts to other Content checkpoints) | 4 |
| Architecture/how-it-works explanation | 3 |
| Troubleshooting, FAQ, or common issues | 3 |

#### SEO Optimization (20 points max)
| Checkpoint | Points |
|------------|--------|
| Primary keyword in H1 (verified via SEO data, not guessed) | 6 |
| Primary keyword in first paragraph | 4 |
| Secondary keywords in at least 2 H2 headings | 4 |
| All images have descriptive alt text with keywords | 3 |
| Descriptive link text (no "click here") | 3 |

#### Badges (10 points max)
| Checkpoint | Points |
|------------|--------|
| At least one badge present | 3 |
| License badge | 2 |
| Version/release badge | 2 |
| CI/build status or other quality signal badge | 3 |

#### Visual Appeal (10 points max)
| Checkpoint | Points |
|------------|--------|
| Banner image at top | 4 |
| Code blocks use syntax highlighting (language specified) | 2 |
| At least one table for structured data | 2 |
| Short paragraphs (no walls of text over 5 sentences) | 2 |

#### Completeness (10 points max)
| Checkpoint | Points |
|------------|--------|
| All required sections for repo type present | 4 |
| Contributing section or link to CONTRIBUTING.md | 2 |
| License section with link to LICENSE file | 2 |
| Links to external resources (docs, homepage, etc.) | 2 |

#### AI Citability (10 points max)
| Checkpoint | Points |
|------------|--------|
| Clear "X is a Y that does Z" definition in first 2 sentences | 4 |
| Structured comparison table (vs alternatives) | 2 |
| Answer-first formatting for key questions (FAQ or PAA-derived) | 2 |
| Specific quantifiable claims (stats, benchmarks, counts) | 2 |

### 3. Recommend

Present README plan before writing:

```
## README Optimization Plan

### Current Score: XX/100
[breakdown by criterion]

### Proposed Structure:
1. Banner image (generated via KIE.ai Nano Banana 2)
2. H1: [Project Name -- keyword-rich tagline]
3. Badges: [CI, version, license, downloads]
4. Opening paragraph: [with primary keyword]
5. Table of Contents
6. [Section list based on repo type]

### Banner Concept:
- Visual: [description of banner concept based on project domain]
- Aspect ratio: 21:9 (default) or [user preference]
- Resolution: 1K (default) or [user preference]

### Keyword Integration:
- H1: "[primary keyword]"
- First paragraph: "[primary keyword] naturally embedded"
- H2 headings: [list with secondary keywords]

### Data Sources Used:
- [list: codebase scan, SEO analysis, audit findings, etc.]
```

### 4. Execute (with user approval)

**PAUSE HERE.** After presenting the optimization plan (Step 3), ask the user:
"Ready to generate the optimized README? (This will also generate a banner image
if KIE_API_KEY is available.)"

Do NOT generate the README until the user confirms. The plan is the checkpoint --
the user may want to adjust the keyword strategy, change the tone, skip the banner,
or add/remove sections before you write anything.

If the user invoked the skill with a clear directive like "generate a readme" or
"optimize this readme", treat that as pre-approval and proceed without pausing.

Generate the full README.md or a rewritten version of the existing one.

**Write to shared data cache** after generating the README:
```bash
mkdir -p .github-audit
grep -qxF '.github-audit/' .gitignore 2>/dev/null || echo '.github-audit/' >> .gitignore
```
Write `.github-audit/readme-data.json` with: timestamp, score_before, score_after,
banner_generated, banner_path, keywords_integrated (primary_in_h1, primary_in_first_paragraph,
secondary_in_h2 list), sections list.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for exact schema.

## README Generation Rules

### Image Format Optimization (applies to ALL images)

Reference: Read `~/.claude/skills/github/references/banner-generation.md` -- see the
**Image Format Optimization** section for the full decision table.

**The pipeline: always generate as PNG (lossless source), then convert to the
optimal delivery format.** See `banner-generation.md` for the full Image Format
Pipeline section.

When generating or placing images in the README:
- **Banners** (AI-generated): request PNG from KIE.ai, convert to **WebP** (quality 80).
  WebP is ~30% smaller than JPEG and GitHub renders it natively.
- **Screenshots** (terminal, UI): keep as **PNG**. Lossless, sharp text, often smaller
  than lossy formats for flat-color content. Do NOT convert screenshots.
- **Logos/icons**: PNG or SVG. Clean edges need lossless compression.
- **Flag existing repo images** using the wrong format or that are oversized:
  - PNG banners/photos > 200KB: convert to WebP (saves 60-70%)
  - JPEG screenshots with blurry text: should be PNG
  - Any image > 1MB: flag for optimization

**Offer to convert, not just flag.** Use Pillow to convert, strip metadata, and show savings:
```python
from PIL import Image
import os
src = Image.open("assets/banner.png")
clean = Image.new(src.mode, src.size)  # strip all metadata
clean.putdata(list(src.getdata()))
clean.save("assets/banner.webp", "WEBP", quality=80, method=6)
old = os.path.getsize("assets/banner.png")
new = os.path.getsize("assets/banner.webp")
print(f"{old//1024}KB -> {new//1024}KB ({100-new*100//old}% smaller, metadata stripped)")
```

### Banner Image (Standard Practice -- Two-Step)

Every README should include a professional banner. Generate one as part of the standard
README creation/optimization workflow using the two-step process.

Reference: Read `~/.claude/skills/github/references/banner-generation.md` for full details
including prompt strategy, text compositing script, and positioning principles.

**Two-step flow:**
1. Craft a background prompt (visual metaphor, NO text in image, subject offset to one side)
2. Call KIE.ai API to generate background (21:9, 1K, **png** -- always request lossless source)
3. Poll for completion, download as `assets/banner-source.png`
4. Composite text overlay via Pillow (project name, tagline, optional features)
5. Convert to WebP (quality 80): `assets/banner.webp`, delete source PNG
6. Place at the very top of README, before H1:

```markdown
<p align="center">
  <img src="assets/banner.webp" alt="[Project Name] banner" width="100%">
</p>
```

**Prerequisite:** Load KIE_API_KEY from `.env` (standard practice):
```bash
if [ -z "$KIE_API_KEY" ]; then
  for envfile in ./.env ~/.claude/skills/github/.env ~/.env; do
    if [ -f "$envfile" ]; then
      export $(grep -v '^#' "$envfile" | xargs) 2>/dev/null
      break
    fi
  done
fi
[ -n "$KIE_API_KEY" ] && echo "KIE_API_KEY loaded" || echo "KIE_API_KEY NOT FOUND"
```
If key is not found after checking `.env`, **STOP and show this message:**

```
Banner generation requires a KIE.ai API key. It takes about 2 minutes to set up:

1. Go to https://kie.ai/api-key and create a free account
2. Copy your API key
3. Paste it into ~/.claude/skills/github/.env:
   KIE_API_KEY=your_key_here

Want to set this up now, or skip the banner and continue with the README?
```

Wait for the user to respond. If they want to set it up, help them. If they
say skip/continue/later, generate the rest of the README with a placeholder
comment: `<!-- TODO: Add banner image -->` at the top.

### H1 (Exactly One)
- Format: `# Project Name - Keyword-rich tagline`
- Include primary keyword naturally (do NOT cram multiple keywords into the title)
- Keep under 80 characters
- The tagline should communicate what the project does, not list keywords
- Bad: `# MyTool - Fast Python CLI Tool Framework Library for Developers`
- Good: `# MyTool - Build CLI Applications in Minutes`

### Opening Paragraph
- First sentence includes primary keyword
- Lead with the PROBLEM or NEED, then the solution. Not just "X is a Y that does Z"
  but "Z is hard/missing/broken. X solves this by..."
- Keep it to 2-3 sentences. This becomes the Google search snippet.
- The reader should finish this paragraph knowing: what problem exists, what this
  project does about it, and why they should keep reading.
- Bad: "MyTool is a Python framework for building CLI applications with plugins."
- Good: "Building CLI tools in Python means wrestling with argparse, plugin systems,
  and config management. MyTool handles all of it so you can focus on your commands."

### Badge Row
Place immediately after H1, before opening paragraph:
```markdown
[![CI](badge-url)](link) [![Version](badge-url)](link) [![License](badge-url)](link)
```

Select badges based on repo type (see `~/.claude/skills/github/references/releases-guide.md` for URLs).

### Heading Hierarchy
- H1: Project name (exactly one)
- H2: Major sections (Features, Installation, Usage, etc.)
- H3: Subsections within H2s
- NEVER skip levels (H1 → H3 without H2)

### Section Flow

Every README, regardless of repo type, should follow this rhetorical arc:

1. **Hook** (H1 + opening paragraph): What problem does this solve? Why should I care?
2. **Orient** (features/overview): What does it do? What are the key capabilities?
3. **Onboard** (installation + quick start): How do I get started right now?
4. **Deepen** (usage, API, config, architecture): How do I use it for real?
5. **Invite** (contributing, community, license): How do I get involved?

This is not a sales funnel. It is the natural order of questions a developer asks
when they land on a repo. Answer them in order and the README feels effortless to read.

### Section Order by Repo Type

These map the flow above to concrete H2 sections:

**Library/Package:** Features > Installation > Quick Start > Usage > API > Configuration > Contributing > License

**CLI Tool:** Installation > Quick Start > Commands > Configuration > Examples > Contributing > License

**Framework:** Why This Framework > Getting Started > Documentation > Architecture > Contributing > License

**Application:** About > Screenshots > Getting Started > Deployment > Contributing > License

**Skill/Plugin:** What It Does > Installation > Commands > Configuration > Examples > License

### Section Pruning

Not every project needs every section. A 50-line utility does not need an Architecture
diagram. A project with no competitors does not need a comparison table. Apply these rules:

- **Drop sections you cannot populate with real content.** A FAQ with invented questions
  or a Contributing section that just says "PRs welcome" adds noise, not value.
- **FAQ requires real questions.** Only add a FAQ section if you have PAA data from SERP
  results, actual GitHub issues asking common questions, or questions the user explicitly
  provided. Never fabricate FAQ entries.
- **Architecture is for complex projects.** If the project is a single file or a small
  library, skip it. If understanding the project requires knowing how components connect,
  include it.
- **Comparison tables require real alternatives.** Only include "vs" comparisons if you
  can name specific competing projects and make honest, factual comparisons.
- **When in doubt, leave it out.** A shorter README with strong sections beats a longer
  one padded with filler. Every section should earn its place.

### Content Rules
- Use code blocks for all code examples
- Use tables for structured data (commands, options, config)
- Use descriptive link text (never "click here")
- Keep paragraphs short (2-4 sentences)
- Include at least one code example in Quick Start
- NEVER use em dashes (--) in generated READMEs. Use commas, periods, or rewrite the sentence instead.

### Disclaimer Rules
- If the project includes features that provide legal, financial, medical, or security
  guidance (license selection, compliance checking, vulnerability scanning, etc.), the
  README MUST include a brief disclaimer noting that the tool's output is automated
  assistance, not professional advice. Place it in the relevant section or in a dedicated
  "Disclaimer" subsection near the bottom (before License).
- Keep it short: one sentence acknowledging the limitation plus a pointer to the skill's
  detailed disclaimers. Do not bury it or make it hard to find.

### Example Quality
- Examples should show what happens, not just what to type. Include expected output
  or describe the result after the code block ("This spawns 6 agents and returns a
  score breakdown within 30 seconds.")
- For tools with visual output, describe what the user will see.
- For tools with before/after effects, show both states if practical.
- One detailed example is worth more than five one-liners.

### SEO Rules
- Primary keyword in H1 and first paragraph
- Secondary keywords in H2 headings (where natural)
- Natural keyword density (1-3%)
- Semantic keyword variations throughout
- All images have descriptive alt text

### AI Citability Rules
- Include a clear definition statement: "X is a Y that does Z"
- Add structured comparisons (tables) if alternatives exist
- Include specific statistics where available
- Use answer-first formatting for key questions

### PAA-to-Content Integration (SERP Intelligence → README Sections)

When SEO data includes People Also Ask (PAA) questions from SERP responses,
**use them actively in the README** -- don't just report them. PAA questions are
Google-confirmed queries that real people ask about this topic.

**How to integrate PAA questions:**

1. **Direct FAQ section** -- If 3+ relevant PAA questions were found, add a
   `## Frequently Asked Questions` section near the bottom (before Contributing).
   Format each as an H3 with a concise answer-first response (2-3 sentences).
   This directly targets Google's PAA feature and AI Overview citations.

2. **Fold into existing sections** -- If a PAA question maps to an existing section
   (e.g., "How do I install X?" → Installation section), ensure that section
   explicitly answers the question in its opening sentence.

3. **H2 heading alignment** -- If a PAA question matches a natural H2 heading,
   use the question's phrasing as inspiration (e.g., PAA "What are the advantages
   of CadQuery?" → H2 "What Makes This Different").

**Selection criteria:**
- Only use PAA questions directly relevant to the project
- Skip PAA questions about competitors (e.g., "Is Knifeprint free?" in a claude-knife README)
- Skip off-topic PAA drift (Google's PAA often drifts to unrelated topics)
- Prioritize questions that showcase the project's strengths

## Tone by Intent

| Intent | Tone | Focus |
|--------|------|-------|
| Open Source Community | Welcoming, inclusive | Getting Started prominent, Contributing prominent |
| Professional Portfolio | Polished, impressive | Technical depth, architecture, results |
| Business / Brand | Professional, value-driven | Value proposition, use cases, social proof |
| Internal to Public | Documentation-heavy | Architecture, API reference, deployment |
| Academic / Research | Formal, methodical | Methodology, citation, reproducibility |
| Hobby / Learning | Authentic, casual | Motivation, learning journey, experiments |

**Tone consistency rule:** Pick one tone from the table above at the start and hold it
through the entire README. Every section should read like the same person wrote it. If
the opening is direct and conversational, the Installation section should not suddenly
switch to formal documentation-speak. If the project is professional, the FAQ should not
get casual. Read the finished README top to bottom and check for tone shifts before
presenting the preview.

## Output

When optimizing an existing README, follow this exact sequence:

### Step 1: Score Current README
Present the 7-criterion score table (see Analyze step) with the current total.

### Step 2: Present Plan
Show the optimization plan (see Recommend step) with proposed changes.

### Step 3: Generate and Preview README
Generate the full optimized README.md content (or generate from scratch).
**Display the complete README in the terminal** so the user can review the copy,
headings, keyword placement, and overall flow before anything is written to disk.

Present it inside a markdown code fence so the raw markdown is visible:
````
```markdown
[full README content here]
```
````

Then ask: "Does this look good? I can adjust any section, rewording, or structure
before writing it. Say 'write it' to save, or tell me what to change."

**Do NOT write README.md until the user approves the preview.** The user may want
to iterate on the copy 2-3 times before committing. This is the most important
checkpoint -- the plan (Step 2) shows structure, but the preview shows actual words.

### Step 4: Write README to Disk
After user approval, write the README.md file and generate the banner (if applicable).

### Step 5: Score New README
Re-score the generated README against the same 7 criteria.

### Step 6: Show Delta
```
## Before/After Comparison

| Criterion | Before | After | Delta |
|-----------|--------|-------|-------|
| Structure | X | Y | +Z |
| Content Depth | X | Y | +Z |
| SEO | X | Y | +Z |
| Badges | X | Y | +Z |
| Visual Appeal | X | Y | +Z |
| Completeness | X | Y | +Z |
| AI Citability | X | Y | +Z |
| **Total** | **X** | **Y** | **+Z** |
```

### Deliverables
- Professional banner image saved to `assets/banner.webp` (if KIE_API_KEY available)
- Full README.md content with banner at top
- Before/after score comparison
- List of changes made with reasoning
- Keyword integration summary
- Image format audit: flag any existing repo images using the wrong format or >1MB

### Post-Generation Image Links (REQUIRED)

After generating or placing ANY image (banner, social preview, screenshot), always
output clickable links so the user can access the file immediately:

1. **Local file link:** `file:///[absolute-path]/assets/banner.webp`
2. **Raw GitHub URL** (after push): `https://raw.githubusercontent.com/{owner}/{repo}/main/assets/banner.webp`
3. **If the image doubles as a social preview**, also include the upload instructions:
   ```
   To set as your repo's social preview:
   1. Download: https://raw.githubusercontent.com/{owner}/{repo}/main/{path}
   2. Go to: https://github.com/{owner}/{repo}/settings
   3. Scroll to "Social preview" > "Edit" > "Upload an image"
   4. Save changes
   ```

Replace all placeholders with actual values. Never output just a relative path
like `assets/banner.webp` without the clickable link next to it.

### Next Step

After completing README optimization, always end with this handoff:

```
README optimization complete. All skills have been run.
Recommended final step:
  /github audit -- re-run the audit to measure your improvement and get your new score
```

If running as part of the audit SOP, reference the step number:
"Step 6 complete. Ready for Step 7: `/github audit` to measure your improvement."
