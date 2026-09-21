---
name: github-readme
description: Write or improve repository documentation from actual capabilities, verified setup and examples, useful comparisons, and audience needs. Optional artwork and research never block the README.
---

# GitHub README

Make the project understandable and usable for its intended audience. Preserve
accurate existing material, upstream credits, and the owner's voice.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" readme --help
python "<GITHUB_HOME>/scripts/run_headless.py" readme --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" readme --path "<TARGET>" --write
```

Default mode creates `readme-data.json`, `README-REPORT.md`, `README-PREVIEW.md`,
and `README-SUMMARY.json` at returned artifact paths. Inspect the preview before
`--write`, which can replace curated content. A targeted edit is often better
than using an entire generated template. A generated score is not validation.

## Gather before drafting

- Read the existing README in its actual format, including RST or other supported
  formats. Do not convert it merely for consistency with a template.
- Inspect manifests, entrypoints, help output, exports, configuration, tests,
  examples, install scripts, and docs. Establish what works today, what is planned,
  required versions, platform support, and optional integrations.
- Establish the audience's first useful task. Read external docs when they are
  necessary to assess a gateway README; report inaccessible docs as unavailable.
- Verify installation sources, package names, license references, and release
  claims. Do not infer that a package is published merely from its manifest.
- Reuse relevant audit/research context after freshness checks. `seo-data.json`
  is optional. Accurate terminology from implementation is observed evidence,
  even when search-volume measurements are unavailable.
- Inventory existing images and the owner's design direction. No image is
  required to begin or finish documentation work.

## Build the right structure

| Project | First useful path | Additional detail when relevant |
|---|---|---|
| Library | Install, import, minimal working example, output | Supported versions, API links, lifecycle, compatibility |
| CLI | Install, invoke one real command, inspect result | Flags, config precedence, exit codes, troubleshooting |
| Service/application | Run locally, health check, use a workflow | Configuration, persistence, deployment, operational limits |
| Skill/plugin | Install/load, trigger a task, inspect an artifact | Host capabilities, path resolution, permissions, portability |
| Research/data | Reproduce a result or load a sample | Methodology, data origin/license, limitations, citation |
| Documentation | Find the right guide and complete its task | Navigation, prerequisites, version scope, contribution route |

A concise README can link to substantial docs without duplicating them. Use a
clear title, short explanation of purpose and boundaries, a verified first-use
path, relevant examples, and links the user needs. Add sections because they
answer questions, not to reach a heading, table, badge, or word count.

## Support discovery with useful content

Use the terminology the intended audience uses, tied to capabilities present in
the implementation. Explain concrete use cases, expected outputs, limitations,
and supported integrations. Descriptive headings and links should remain natural;
do not force a keyword into every heading or alt text.

When comparison/alternative intent is relevant, include a fair table or dedicated
doc using current primary sources. Choose criteria users actually decide on:
workflow, output, supported platforms, self-hosting, integration surface, cost
model if verified, and known tradeoffs. Cite sources and dates; distinguish
measured tests from vendor statements and unknowns. Link to competitors normally;
do not invent weaknesses, claim superiority without tests, or copy their text.

Include a migration guide or worked example when it helps users evaluate or
switch tools. A reproducible example and candid limitation can be more valuable
than broad positioning. Route deeper query research to `github-seo` only when it
advances the task. Do not promise rankings, search snippets, AI citations, or stars.

## Write and validate

1. Choose a focused outline based on observed gaps. For a rewrite, preserve the
   content that is already correct and useful. State material assumptions.
2. Draft commands against actual source and supported versions. Show expected
   output when checked. Label illustrative output and optional configuration.
   Use placeholder secret names, never credentials or private endpoints.
3. When the user requested generation or improvement, write the authorized
   changes and inspect the diff. A review-only request produces a draft/plan.
   Do not require separate plan, preview, and write confirmations for the same
   authorized work.
4. Validate relative links, headings/anchors, referenced files, code fences, and
   critical commands. Run relevant existing checks. If installation cannot be
   exercised safely or an external dependency is missing, state that limitation.
5. Read the result for accuracy, tone, and needless repetition. Keep roadmap
   claims separate from shipped behavior. Remove placeholders from production
   instructions or clearly list unresolved ones.

Use `GITHUB_HOME/references/readme-framework.md` and `repo-type-templates.md`
for ideas, not mandatory rubrics. Preserve LICENSE and upstream acknowledgments
through structural rewrites. Never fabricate benchmark numbers or compatibility.

## Optional artwork

Use existing approved assets when they help explain the product. Screenshots,
output samples, and small diagrams can be more useful than a decorative banner.
Add accurate alt text, check legibility and file size, and preserve source assets.
Do not delete originals or strip provenance metadata merely to hide generation.

Generate artwork only when requested, using the host's configured image tool.
If unavailable, finish the text and report the missing optional capability.
No provider registration, key request, mascot, banner, avatar, social preview,
or vendor badge is required. The compatibility `--generate-assets` flag performs
local asset reuse/preparation; it is not an image-generation provider. Inspect
its proposed output before using it, since preparation may create derived files.

For a requested social preview, check current platform constraints and account
capability, inspect the final image, and provide its actual path plus repository
settings link. Do not assume a private repository's plan from visibility alone.
Only provide a remote asset link once verified on its actual branch/ref.

## Receipt

Summarize the changed reader journey, useful content added or corrected, and
validation performed. Separate **observed** results, **unavailable** checks, and
**not_applicable** items. Link the edited README or draft. Report any unresolved
claim or setup check; do not substitute a before/after score for evidence.

## Legends presentation protocol

For authorized Legends presentation work, read `GITHUB_HOME/references/social-preview-sop.md`
and `GITHUB_HOME/references/legends-readme-style.md`. Use
`GITHUB_HOME/scripts/render_social_preview.py` for fixed-size social cards.
Attempt upload with available browser/computer-use tools before a manual handoff.
Preserve approved typography; do not crop or shrink text.
