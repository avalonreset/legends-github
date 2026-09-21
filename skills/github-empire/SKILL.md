---
name: github-empire
description: Review and improve a scoped GitHub portfolio, profile, related-project navigation, and metadata. Prepare concrete local drafts and apply only authorized account or repository changes.
---

# GitHub portfolio and profile workflows

Help visitors understand related projects and choose a useful starting point.
Keep individual repository differences and maintenance commitments visible.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" empire --help
python "<GITHUB_HOME>/scripts/run_headless.py" empire --path "<TARGET>" --username OWNER
```

The runtime writes `empire-data.json`, `EMPIRE-REPORT.md`, `EMPIRE-BLUEPRINT.md`,
`PROFILE-README-DRAFT.md`, and `EMPIRE-SUMMARY.json`. The blueprint and emitted
commands do not automatically apply account changes. Inspect portfolio coverage,
source freshness, and intended owner before treating its conclusions as complete.

A user profile, organization profile, and repository collection are different
targets. Resolve the user's intended owner and included repositories. Do not
expand a public portfolio task to private repositories or unrelated accounts.

## Gather a bounded portfolio view

- Read the owner/profile and requested repository inventory from current GitHub
  data when available. Use explicit owner/repo arguments and appropriate limits.
  Identify truncation, pagination, filters, forks, archived repos, and omitted items.
- Inspect descriptions, primary audience, capabilities, docs, installation,
  maintenance policy, release/distribution routes, and relevant local changes.
- Read existing profile README content before proposing a replacement. Account
  biography fields and verified public links are useful; private contact details
  or inferred personal attributes are not portfolio copy.
- Use prior audits/research as optional context after identity and freshness
  checks. A full audit of every repository is not a prerequisite for a profile
  edit. A lightweight inventory is not a full source-quality audit.
- For large collections, select deeper reviews by the user's priorities and
  representative project types, state the sample, and preserve coverage gaps.
  Stars and recency can be context but should not be the only selection rule.

Record **observed**, **unavailable**, and **not_applicable** per finding. Missing
access to traffic or profile settings is unavailable, never a zero or a failed
quality check. A private repository need not participate in a public portfolio.

## Shape a useful portfolio

| Area | Look for | Action when supported |
|---|---|---|
| Identity | Actual work, audience, verified expertise | Concise bio/profile copy linking relevant projects |
| Featured projects | Working, distinctive projects serving the objective | Recommend a useful order with a reason per selection |
| Project grouping | Shared audience or complementary workflows | Group by user problem and explain differences |
| Topics/descriptions | Accurate common concepts and project-specific features | Correct mismatches while retaining meaningful differences |
| Cross-links | A reader's logical next step | Link docs, companion tools, examples, or integrations |
| Support/maintenance | Stated ownership, support channels, superseded tools | Clarify current status and maintained alternatives |
| Distribution | Actual install and release paths | Fix missing navigation to verified artifacts/docs |

Do not clone the same topics or positioning onto all repositories. Do not infer
that a collection needs more projects to fill a marketing matrix. Recommend
archiving, merging, unpinning, or visibility changes only when supported by the
owner's intent and actual project state, never from low stars or age alone.
Those actions require exact target authorization.

Cross-links should serve readers. Describe the concrete relationship and where
to continue; avoid reciprocal link schemes, repeated promotional blocks, and
claims that inbound link direction establishes ranking authority.

## Prepare a concrete change set

Produce a concise table with target, current state, proposed text/diff, evidence,
and local versus external effect. Prepare profile copy, README edits, and payloads
before any required approval. If edits are already authorized, proceed through
verification without a redundant blueprint approval ritual.

A profile README can include a short accurate introduction, useful project groups,
a small featured-project table, and verified public links. Badges, metrics,
avatars, keyword quotas, and claims of authority are optional. Retain original
credits and avoid publishing private plans or invented experience.

For personal profiles, verify the supported owner/owner repository convention.
For organization profiles, verify the current `.github/profile/README.md` layout
and applicable default-policy inheritance before creating content. Creating a
public repository or changing account settings is distinct from writing a local
draft and must be within the request.

## Apply safely to the intended identity

Before authenticated profile edits, check that the current authenticated identity
matches the intended account. `gh api user` targets that authenticated user;
changing its fields will not update an arbitrary username or organization.
Use the correct documented organization endpoint for organization changes.

Use exact UTF-8 JSON payload files or structured arguments for complex text.
Examples below are external operations and require the scoped user request:

```text
gh api user --method PATCH --input "<APPROVED_PROFILE_PAYLOAD.json>"
gh repo edit OWNER/REPO --description "Accurate project-specific description"
gh api repos/OWNER/REPO/topics --method PUT --input "<APPROVED_TOPICS_PAYLOAD.json>"
```

Only include fields intentionally changing. Topic PUT replaces the full set;
re-read live state and retain accurate existing topics. Use boolean JSON values
for feature flags, not guessed string-valued API fields.

Work on local README files or an isolated checkout. Inspect diffs and preserve
unrelated changes. Do not automatically commit or push cross-links/profile files
because their local draft was approved. If repository creation, publication,
archiving, or visibility changes are requested, execute only the named targets
and verify each mutation. Report partial completion and avoid blind batch retries.

## Optional visuals and manual steps

Reuse approved artwork. Generate an avatar or social card only on request using
the host's configured image tool; no specific provider/key is required. Review
legibility at small display size, contrast, cropping, and actual upload constraints.
Keep source artwork; do not delete originals or strip provenance merely to hide
its origin. A configured tool's absence does not block portfolio copy or analysis.

The compatibility `empire --generate-avatar` flag prepares/reuses a supplied
local asset. It does not invoke an image provider. Inspect its output and keep
generation through a requested host image tool distinct from local conversion.

For requested actions unavailable through the supported automation interface,
provide an actual file link, exact profile/repository settings URL, and concise
current steps. Pin recommendations need not fill every slot. Do not claim a
photo, social preview, or pin order is live until checked. Do not promise a
universal UI path or completion time without verifying it.

## Verify and measure

Re-read each changed profile field and repository setting; verify every modified
repository, not just a sample of a batch. Validate local links and content, and
only label README changes published after confirming the remote revision.

For requested growth tracking, record accessible metrics with collection time,
query scope, and reporting window. Compare compatible windows and repository
sets. Missing traffic access stays unavailable; a change in stars/views does not
establish that portfolio edits caused it. Do not compare legacy health scores
across changed methodology or call topic counts authority.

Deliver a concise receipt of local files, verified live changes, unavailable
checks, and pending manual work. Link concrete artifacts. Recommend deeper
repository work only where it advances the user's objective; a complete
portfolio transformation is not promised for a scoped review or profile edit.
