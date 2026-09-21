---
name: github-release
description: Assess release readiness from actual changes, versions, tags, tests, and artifacts; prepare changelogs and distribution plans, then execute only authorized release actions.
---

# GitHub release preparation

Help users obtain the intended, tested artifact with accurate version and change
information. A release is justified by the project's delivery model and changes,
not a commit-count, badge, or time-since-release threshold.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" release --help
python "<GITHUB_HOME>/scripts/run_headless.py" release --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" release --path "<TARGET>" --write-files
python "<GITHUB_HOME>/scripts/run_headless.py" release --path "<TARGET>" --create-release
python "<GITHUB_HOME>/scripts/run_headless.py" release --path "<TARGET>" --create-release --publish
```

These show increasing mutation scope, not a sequence to run. Default mode writes
`releases-data.json`, `RELEASE-REPORT.md`, `RELEASE-PROPOSAL.md`, and
`RELEASE-SUMMARY.json`. Review the plan before writing. `--write-files` prepares
local files; `--create-release` requests an external draft and may prepare files;
adding `--publish` requests publication. Inspect the current command contract and
confirm exact tag/commit/artifact choices before invoking external actions.

## Establish the release baseline

1. Inspect instructions, Git status, version policy, tags, package manifests,
   changelog, release configuration, build scripts, and publish workflows.
2. Read live releases with an explicit repository when available:

   ```text
   gh release list --repo OWNER/REPO --limit 20
   gh release view TAG --repo OWNER/REPO --json tagName,targetCommitish,isDraft,isPrerelease,publishedAt,assets,url
   ```

3. Resolve the last relevant stable/prerelease tag to a commit. Identify the
   intended target commit and branch. Do not substitute the default branch for
   a historical version or assume the latest-looking tag applies to every package.
4. Review both commit messages and actual diffs since the baseline. Verify which
   user-visible changes shipped, what remains uncommitted, and which changes
   affect compatibility. A `refactor` label does not prove compatibility.
5. Compare package versions, tags, changelog headings, release records, and
   published artifacts. Determine whether mismatches are intended development
   state, independent monorepo releases, or defects.
6. Inspect tests and build/package contents at the intended commit, supported
   platforms, migrations, known issues, checksums/signatures where applicable,
   and the repository's existing artifact provenance policy.

Missing network/auth is **unavailable**, not "no releases." A shallow checkout
can have incomplete tags/history. A missing GitHub Release is not necessarily a
missing package release. Do not claim dependencies or users are vulnerable merely
because an unreleased commit mentions security.

## Recommend a version and delivery action

Preserve the project's version scheme (SemVer, CalVer, package-specific, or
another documented policy). Explain the recommendation from observed compatibility
and user impact. For SemVer projects, inspect the declared public API; pre-1.0 and
prerelease behavior must follow the project's policy rather than a blind prefix
rule. Document installation/runtime support changes as well as API changes.

A valid result can be prepare a first release, publish a specific next release,
create a prerelease for testing, repair a confirmed historical record, or make no
release. Old dates alone do not imply abandonment; many commits alone do not
prove a release is overdue. Documentation fixes may matter to a docs product.

For a historical catch-up release, require a verified historical tag/commit and
notes for that artifact. Never create every old changelog version from today's
HEAD. Do not move existing tags or replace published artifacts incidentally.

Present the exact target, version, stable/prerelease/draft state, meaningful
changes, checks, and remaining blockers. If the user already authorized that
specific release action, execute after verification without another approval loop.
Otherwise prepare the concrete notes/diff before requesting the needed decision.

## Prepare changelog and release configuration

Preserve curated history and the chosen format. Write changes for users:
compatibility/migration, features, fixes, security information appropriate for
public disclosure, and known limitations. Link supporting commits/PRs when useful.
Do not expose private issue content or embargoed details in public notes.

When generating release-note categories, align labels with actual repository use.
Do not automatically exclude dependency bot changes; they can include meaningful
security or compatibility updates. An existing manually maintained release process
need not acquire `.github/release.yml` for checklist completeness.

Badges are optional links to useful live state. If requested, verify each target
and displayed meaning. Do not add badges instead of checking the build/artifact.
Use `GITHUB_HOME/references/releases-guide.md` for examples, verifying current
platform and ecosystem behavior as needed.

## Package and distribution strategy

| Project | Evidence to inspect | Possible delivery route |
|---|---|---|
| Library | Package name, metadata, included files, install/import | Existing language registry and documented version |
| CLI | Entrypoint, supported OS/architectures, install/uninstall | Registry package or tested release binaries |
| Container/service | Image build, base image, runtime config | Existing container registry/deployment pipeline |
| Skill/plugin | Source layout, loader/install behavior, assets | Supported package/extension system or source installer |
| Docs/data | Build outputs, data schema/license, versioning | Docs site, source archive, or dataset release |
| Internal project | Access model and existing registry policy | Authorized private distribution channel |

A manifest alone does not prove a package is published or should be. Inspect the
actual registry/package record before making a current distribution claim. Do not
assume a nonexistent generic repository-packages API; use current documented APIs
for the relevant owner and package type.

New registry accounts, paid services, public publishing, and credential changes
are separate from local release preparation. Never print tokens or write them
into a workflow. Use the repository's approved credential/provenance model.

## Execute and verify precisely

Prefer the existing release pipeline when it is the supported route. For explicit
GitHub CLI creation, use an exact notes file and an existing verified tag:

```text
gh release create TAG --repo OWNER/REPO --verify-tag --draft --title "Release title" --notes-file "<NOTES_FILE>"
```

This example creates an external draft; it is not permission to do so. Add assets
or publish only within the request. If a tag needs creating, establish the exact
commit and authorization first. Never use a publish flag to bypass a failed check.

After execution, re-read release state and verify tag target, notes, assets,
draft/prerelease status, and registry version if part of the task. Separate local
file generation, external draft creation, published release, and tested install.
Report partial failure with the completed state; do not blindly retry publication
or recreate an existing release.

Deliver paths/URLs, version and target, relevant checks, unresolved evidence, and
only necessary next actions. Use **observed**, **unavailable**, and
**not_applicable** distinctions; a proposal is not a shipped release.
