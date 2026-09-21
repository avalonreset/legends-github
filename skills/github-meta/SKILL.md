---
name: github-meta
description: Review and update GitHub descriptions, topics, homepage links, feature settings, and optional social previews using current repository evidence and scoped authorization.
---

# GitHub metadata and settings

Help the right user recognize the project and reach its working documentation or
demo. Use accurate metadata, not topic quotas or speculative ranking formulas.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" meta --help
python "<GITHUB_HOME>/scripts/run_headless.py" meta --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" meta --path "<TARGET>" --apply
```

Default mode writes `meta-data.json`, `META-REPORT.md`, and `META-SUMMARY.json`.
`--apply` changes live settings. Inspect its exact ready commands and scope before
using it. If a plan includes settings the user did not authorize, apply only the
relevant changes with explicit targeted commands.

## Gather source and current settings

Read the README, implementation, manifests, docs, and stated audience. Confirm
what the project does before summarizing it. Research caches are optional; local
capability evidence is sufficient for truthful descriptions and topics.

Read metadata with an explicit target:

```text
gh repo view OWNER/REPO --json name,description,homepageUrl,repositoryTopics,visibility,defaultBranchRef,isArchived,isTemplate,hasIssuesEnabled,hasWikiEnabled,hasDiscussionsEnabled,hasProjectsEnabled
gh api repos/OWNER/REPO/languages
```

If a field is unsupported by the installed CLI, use documented alternatives or
report it as **unavailable**. Do not convert a failed query to an empty setting.
Refresh the actual target before applying a cached plan.

Inspect whether homepage/docs/demo links work and belong to this project.
Different branding alone does not prove a link is wrong. Check actual content
before proposing removal. Leaving the homepage empty can be appropriate.

## Draft an evidence-based change set

| Setting | Decision criteria | Avoid |
|---|---|---|
| Description | Purpose, user, capability, verified differentiator | Unsupported superlatives or keyword repetition |
| Topics | Language/ecosystem, domain, implemented workflow | Quotas, unrelated high-volume terms, invented capabilities |
| Homepage | Most useful maintained docs, demo, or project page | Guessed URLs or a circular link to the same repository |
| Issues | Actual bug/support routing and maintainer policy | Enabling or disabling from a universal default |
| Discussions | Maintained Q&A/community need | Creating an unattended channel for checklist points |
| Wiki | Current content and documentation strategy | Disabling an active wiki based only on repo files |
| Social preview | Requested share-card/design purpose | Mandatory image generation or assumed account limits |

Provide a current/proposed/reason table. Usually one strong description is enough;
offer alternatives when the user is choosing positioning or tone. Keep it within
GitHub's current field limits, verified when necessary. Do not claim the first ten
words have a known ranking weight.

Choose the smallest useful topic set. Check current GitHub limits and topic
syntax before mutation rather than repeating a hard-coded count from an old
reference. Preserve accurate existing topics. Explain additions and removals by
capability and audience relevance; general search volume is not a measurement of
GitHub topic traffic. Use an `open-source` topic only when the license warrants it.

Comparison and alternative intent belongs in useful, accurate docs and examples;
adding competitor names or unrelated categories as topics is not a substitute.
Use `github-seo` if research would resolve a material positioning question.

## Apply within actual authorization

A request to update a named repository's description/topics authorizes that
specific change. Do not re-ask because it is live. A review request, or a request
to edit README locally, does not authorize changing unrelated live settings.
If additional approval is needed, first prepare the exact text and target changes.

Examples below require replacing placeholders with inspected, authorized values:

```text
gh repo edit OWNER/REPO --description "Accurate project description"
gh repo edit OWNER/REPO --add-topic relevant-topic --remove-topic misleading-topic
gh repo edit OWNER/REPO --homepage "https://verified-project.example/docs"
```

Inspect `gh repo edit --help` for supported feature flags. Avoid interpolating
fetched descriptions into a shell command. Use argument arrays or exact UTF-8
JSON payload files for API requests containing complex text.

Topic PUT APIs replace the entire set. Preserve retained topics, re-read current
state, and avoid overwriting concurrent changes. Do not change repository name,
visibility, archive status, branch policy, or access permissions as incidental
metadata work.

## Optional social preview and language classification

Reuse existing approved artwork. Generate an image only when requested, through
the host's configured image tool; see `GITHUB_HOME/references/banner-generation.md`
for optional asset preparation. If a supported API cannot upload the image,
provide its actual local path and `https://github.com/OWNER/REPO/settings` with
concise current UI steps. Report upload as pending until verified.

Check upload constraints and capability in the actual settings/docs. Visibility
alone does not establish the owner's plan or feature availability. Do not claim
all private repositories lack social previews. Only show raw GitHub image links
when the asset is already confirmed at that ref.

Linguist changes belong in `.gitattributes` only for observed misclassification
of generated, vendored, or documented material. Preserve an accurate language
mix; do not conceal real source files for presentation. Coordinate with
`github-community` when the requested fix also affects local workflow files.

## Verify and deliver

Re-read every changed field after applying it. Report partial success separately;
a successful command exit is not proof all planned changes landed. Verify any
local `.gitattributes` change through its diff and appropriate classification
checks; remote language recalculation may be pending.

Deliver before/after values, exact target, evidence, changed local paths, and
remaining manual steps. Label **observed**, **unavailable**, and
**not_applicable** findings. Do not claim improved ranking from a successful
metadata update or mark a generated social card as uploaded.

## Legends presentation protocol

For authorized Legends presentation work, read `GITHUB_HOME/references/social-preview-sop.md`
and `GITHUB_HOME/references/legends-readme-style.md`. Use
`GITHUB_HOME/scripts/render_social_preview.py` for fixed-size social cards.
Attempt upload with available browser/computer-use tools before a manual handoff.
Preserve approved typography; do not crop or shrink text.
