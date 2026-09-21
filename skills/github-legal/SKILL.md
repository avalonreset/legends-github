---
name: github-legal
description: Review repository licenses, provenance, upstream notices, dependency licensing questions, security reporting, and optional citation metadata. Prepare scoped changes without declaring legal clearance.
---

# GitHub licensing, provenance, and security policy

Collect verifiable facts and prepare appropriate repository files. This workflow
provides licensing assistance, not a legal opinion. Explain specific unresolved
legal questions and seek qualified review where they materially affect a decision.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" legal --help
python "<GITHUB_HOME>/scripts/run_headless.py" legal --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" legal --path "<TARGET>" --write-files --license MIT
```

The final example is appropriate only when MIT is the established license choice;
it is not a recommendation for every repository. The planning command writes
`legal-data.json`, `LEGAL-REPORT.md`, `LEGAL-PLAN.md`, and `LEGAL-SUMMARY.json`.
Review planned files before `--write-files`; use targeted edits when a plan
would select an unapproved license or add unwanted citation/security files.

## Gather provenance before conclusions

- Read complete existing LICENSE/COPYING/NOTICE files and relevant source headers.
  Preserve both original and modification notices; do not replace an upstream
  copyright holder with the current repository owner.
- Inspect fork/parent metadata and Git remotes when available. Also inspect
  README credits, vendored directories, copied templates, assets, and source
  headers. A repository may reuse upstream material without being a GitHub fork.
- Distinguish a runtime dependency, linked library, wrapper, vendored copy,
  modified derivative, and independently implemented integration. A README
  saying "powered by" is a provenance lead, not proof of a particular obligation.
- Read manifests and lockfiles without executing package setup scripts. Resolve
  licensing for actual package versions and vendored source where practical;
  missing metadata means **unavailable**, not "compatible" or "unlicensed".
- Identify distribution context and the owner's existing license policy. Private
  use, source distribution, binaries, hosted services, data, docs, models, and
  artwork can raise different questions. Do not impose one license across all
  material without checking the applicable rights.
- Inspect effective SECURITY.md and CITATION.cff locations and inherited policies.
  Gather maintained support versions and verified contact channels.

## Analyze narrowly and cite sources

| Question | Evidence needed | Avoid |
|---|---|---|
| Does the stated license match the files? | Exact license text, manifest SPDX expression, README links | Treating GitHub detection as legal clearance |
| Are notices preserved? | Actual upstream terms and supplied NOTICE/header text | Assuming every dependency needs the same notice |
| Can a new license be selected? | Ownership, contributor/upstream terms, intended policy | Inferring consent from repo control or git author config |
| Is a dependency a conflict? | Version, license expression, use/linking/distribution context | Declaring incompatibility from a package name alone |
| Is vulnerability reporting usable? | Confirmed private channel, supported versions, policy | Invented email addresses or response guarantees |
| Is citation metadata useful and accurate? | Research/user need, verified authors/version/date | Generating it for checklist points |

Consult `GITHUB_HOME/references/license-guide.md` for topics to inspect, and verify
any consequential interpretation against the actual license text and current
primary sources. Historical compatibility tables are not definitive. Preserve
SPDX alternatives/conjunctions rather than collapsing them to one guessed license.

Flag material uncertainty around relicensing, missing permissions, patent or
trademark terms, contributor agreements, mixed licenses, and copyleft scope.
Describe the unresolved fact and affected action. Continue independent notice or
documentation repairs instead of blocking the entire task.

Do not choose a license from a generic "business means Apache" or "hobby means
MIT" table. If license selection is requested and unspecified, explain relevant
tradeoffs and obtain the owner's decision before applying it. An existing,
explicitly requested license correction does not need another approval.

## Prepare useful files

### License and notices

Use the approved license's canonical text and verified holder information.
Retain upstream text and obligations; add modification credit only when accurate.
Preserve third-party notices in their appropriate locations. A README credit is
not automatically a substitute for notices required by the applicable terms.

### SECURITY.md

Document a confirmed reporting channel, information reporters should supply,
actual supported versions, and the maintainer's stated disclosure policy. Avoid
asking for public vulnerability details when a private channel exists. Do not
publish personal contact data inferred from commits, invent SLAs, or label all
historical releases supported without evidence.

### CITATION.cff

Create or update it when citation serves the project or the user requests it.
Use verified author/project-entity information; the local committer need not be
the author. Use actual release dates, not today's date as a substitute. Omit
optional unknown fields and list essential unknowns in a draft.

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it using these metadata."
type: software
title: "Verified project title"
authors:
  - name: "Verified project team"
```

This is an illustrative draft, not ready-to-publish metadata. Add verified URL,
version, date, SPDX expression, DOI, or ORCID only when appropriate. Validate
against the current CFF schema when generating a real file.

## Apply, verify, and report

Apply requested local changes after reviewing the diff/plan. Do not add a second
confirmation merely because the skill is invoked directly. Keep unresolved
license choices out of applied changes.

Verify notices were retained, license links resolve, SPDX metadata matches the
actual files, citation syntax/schema is valid, and reporting channels are real.
A successful generated-file write is not a compliance determination.

Report changed paths, confirmed facts and sources, **observed** results,
**unavailable** evidence, **not_applicable** checks, and specific questions left
for the owner or legal reviewer. Preserve runtime cache contracts; place extra
analysis in the report instead of falsifying a PASS/FAIL scalar.
