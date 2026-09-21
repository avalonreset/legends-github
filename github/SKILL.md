---
name: github
description: Improve GitHub repositories through evidence-based audits, documentation, discovery, licensing review, community workflows, releases, and portfolio maintenance. Works with local commands and optional agent tools.
---

# GitHub repository workflows

Help the repository's intended users understand, evaluate, install, and maintain
its project. Choose work from the user's objective and observed problems. A
checklist score, artwork, or a particular agent host is not the objective.

## Start here

1. Resolve this skill's directory as **GITHUB_HOME**, containing `scripts/` and
   `references/`. Resolve the target repository separately as **TARGET**.
2. Read [portable-workflows.md](references/portable-workflows.md) for path
   resolution, evidence handling, authorization, and credentials. Read the
   target's instructions and inspect its status before changing files.
3. Use the stated intent. Infer a reasonable audience and repository type from
   source when clear; ask only when a missing decision materially changes the work.
4. Run the smallest relevant workflow. Read its `--help`; check runtime readiness
   when needed. Missing GitHub access or a research tool does not block independent
   local analysis.
5. Apply authorized changes, inspect the diff, and verify the actual outcome.
   Finish with paths, evidence, unavailable checks, and remaining actions.

Use an available Python executable (`python`, `python3`, or `py -3`). Replace
these absolute placeholders before running commands:

```text
python "<GITHUB_HOME>/scripts/run_headless.py" verify --mode portable --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" audit --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" cache-status --path "<TARGET>"
```

In a source checkout, `python "<SOURCE_ROOT>/legends_github.py" <workflow>` is
also supported. Installed skills need not have that launcher; their
`GITHUB_HOME/scripts/run_headless.py` is the equivalent entry point. Never resolve
runtime paths against the target repository's current directory.

The source launcher exposes `capabilities` as machine-readable workflow metadata.
Its `--offline` option disables external requests; `--artifacts-dir "<OUTPUT>"`
isolates artifacts from the target. Inspect launcher help before using global
options: the installed script may expose configuration through environment
variables instead. `verify --mode api` remains a compatibility alias.

## Route by outcome

| User objective | Skill | Runtime command | Main evidence |
|---|---|---|---|
| Find actionable defects and gaps | `github-audit` | `audit` | Source, examples, settings, verification |
| Explain and demonstrate the project | `github-readme` | `readme` | Implementation, working installation and usage |
| Review licenses and upstream notices | `github-legal` | `legal` | License text, provenance, distribution context |
| Correct description, topics, settings | `github-meta` | `meta` | Current settings, project capabilities |
| Improve relevant organic discovery | `github-seo` | `discover`, `seo` | User questions, comparisons, search observations |
| Make contribution and support usable | `github-community` | `community` | Existing workflows and maintainer capacity |
| Prepare a reliable release | `github-release` | `release` | Tags, diff, package contents, tests |
| Present or maintain related projects | `github-empire` | `empire` | Owner scope, repo purpose, profile, shared users |

Source sub-skills live at `<SOURCE_ROOT>/skills/github-*/SKILL.md`. Installed
sub-skills live beside this `github` directory under the host's skill root.
Load only relevant instructions and references.

For a bare repository request, gather a bounded baseline and give the highest
value findings with supporting evidence. If asked to improve the repository,
continue through authorized fixes. If asked only for an audit, deliver the audit.

## Establish the baseline

- Inspect source, manifests, examples, docs, existing policies, and release
  machinery. A manifest identifies an ecosystem, not the entire repo type.
- Distinguish libraries, CLI tools, services, applications, documentation,
  skills/plugins, research projects, and monorepos. Private/internal visibility
  and archived status change applicability.
- Read local content for a local audit, including uncommitted work. Label the
  checkout and remote branch separately; local edits are not live changes.
- Query relevant live metadata with an explicit `--repo OWNER/REPO` or API path.
  Record errors without exposing authentication.
- Reuse `.github-audit/` context after checking target identity, timestamp,
  revision, dirty state, and whether live claims need refreshing.

## Evidence and priority

Distinguish **observed**, **unavailable**, and **not_applicable** evidence.
Observed absence differs from a failed read. A private-repo API 404 can mean
missing access; it does not by itself prove a file or repository is absent.
Record source, collection time, applicability, and separately labeled inferences.
Never replace unknown measurements with zero.

Prioritize broken installation, misleading capability claims, unusable examples,
incorrect notices, release defects, and inaccessible support paths according to
user impact. Evaluate optional presentation work by usefulness. No minimum badge,
topic, image, section, or community-file count is required.

The runtime preserves compatibility scores and caches. Interpret them alongside
versioned findings and coverage. A score summarizes checks; it does not establish
legal compliance, maintenance quality, search rankings, adoption, or revenue.
Do not recommend work solely to raise a score.

## Compose workflows around actual dependencies

There is no mandatory sequence. A license claim needs verified license text; a
quickstart needs a working command; release notes need an actual diff; a
comparison needs current evidence. Research may inform metadata and README copy,
but paid keyword data is never a prerequisite.

Review sequentially by default. If the task and host explicitly allow delegation
and independent review would help, assign bounded read-only reviews with source
paths, scope, and expected evidence. Reconcile conflicts and report unavailable
reviewers rather than inventing their results. No agent API or model is required.

## Changes and optional capabilities

Planning commands create local reports/caches; inspect returned artifact paths.
Mutation flags are interfaces, not substitutes for user authorization:

| Command | Local changes when requested | External changes when requested |
|---|---|---|
| `readme` | `--write` rewrites README; review its preview first | None by default |
| `legal` | `--write-files`; `--license` selects an explicit license | None by default |
| `community` | `--write-files` prepares community files | None by default |
| `meta` | Plan artifacts | `--apply` applies ready metadata commands |
| `release` | `--write-files` prepares release files | `--create-release` creates a draft; `--publish` requests publication |
| `empire` | Blueprint and profile draft | Follow-up commands need scoped authorization |

Use targeted edits when a full-file generator exceeds the requested scope or
would overwrite curated content. Never push, publish, archive, change visibility,
or send messages merely because a plan suggests it. Do not ask again for clearly
authorized actions.

Organic discovery can use source analysis, official docs, GitHub search, and
configured research tools. Use paid providers for requested capabilities within
established authorization and budget. Do not request keys or install unrelated
services to unblock local work. Keep secrets in their configured credential
store; do not print, source, or broadly import dotenv files.

Artwork is optional. Reuse suitable owner-provided assets or, when generation is
requested, use the host's configured image tool. No mascot, banner, social
preview, avatar, or vendor badge is required. Verify current upload constraints
before preparing an asset for a platform-specific setting.

## References and delivery

`references/portable-workflows.md` is the shared execution and evidence contract.
Domain examples include `license-guide.md`, `readme-framework.md`,
`github-seo-guide.md`, `community-files-guide.md`, `community-templates.md`,
`releases-guide.md`, `repo-type-templates.md`, and `shared-data-cache.md`.
Legacy examples are not current platform documentation or authorization to
execute. Verify factual claims and adapt templates to the task.

Preserve license text, upstream acknowledgments, and provenance when rewriting
content. Do not confuse this suite with similarly named GitHub CLI toolkits or
import content with incompatible licensing.

Deliver changes and verification results, distinguish local artifacts from live
state, and identify any necessary manual step with a real file path and settings
URL. Recommend another workflow only for unresolved parts of the user's objective.
