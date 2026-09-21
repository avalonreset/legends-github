---
name: github-community
description: Improve contribution, support, issue and pull request workflows with repository-specific policies, templates, dependency updates, and development checks. Add only files that serve maintainers and users.
---

# GitHub community workflows

Make contribution and support practical for the actual maintenance model. A
small internal tool and a public contributor community need different processes.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" community --help
python "<GITHUB_HOME>/scripts/run_headless.py" community --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" community --path "<TARGET>" --write-files
```

Default mode writes `community-data.json`, `COMMUNITY-REPORT.md`,
`COMMUNITY-PLAN.md`, and `COMMUNITY-SUMMARY.json`. It is a planning run with
artifact writes. Review its generated file list before `--write-files`; use
focused edits when the plan adds optional files beyond the request.

## Gather the effective workflow

- Read repository instructions, contribution docs, build/test scripts, policy
  files, templates, CODEOWNERS, workflows, dependency updates, and devcontainers.
- Look for root, `.github`, and `docs` locations and accepted filename/format
  variants. Read directory listings to find case variants and RST documents.
  Check applicable organization defaults before creating duplicate policies;
  verify current GitHub inheritance and precedence for the specific file.
- Inspect current Issues/Discussions settings before linking to those channels.
  Verify an external tracker/support site if the project routes users elsewhere.
- Check how contributors actually install dependencies and run relevant tests.
  Detect package workspaces and monorepo paths before generating automation.
- Determine whether contributions are accepted, who reviews them, and which
  channels maintainers can support. Do not invent staffing, contacts, or SLAs.

Classify evidence as **observed**, **unavailable**, or **not_applicable**. Missing
remote access does not prove policies or channels are absent. Existing upstream
names may be required attribution; correct copied project-specific URLs without
removing provenance.

## Choose files by the friction they remove

| Surface | Useful when | Verify |
|---|---|---|
| CONTRIBUTING | Contributors need setup and review guidance | Commands work; branching/testing matches actual practice |
| Code of conduct | Maintainers adopt and enforce a community policy | Chosen policy version, authorized enforcement contact |
| SUPPORT | Users need routing among docs, issues, support | Links work and match enabled channels |
| Issue templates/forms | Reports lack information needed to reproduce/triage | Relevant fields, valid format, reasonable effort to submit |
| PR template | Reviewers need intent and test evidence | Short prompts aligned with current checks |
| CODEOWNERS | Verified teams/people should review defined paths | Existing identities, permissions, pattern coverage |
| Funding | Maintainer has requested verified funding links | Actual supported account; never infer enrollment from ownership |
| Devcontainer | Supported repeatable environment benefits contributors | Runtime versions, trusted setup command, working build |
| Dependency updates | Dependencies need a maintainable update process | Actual ecosystems, directories, cadence, lockfile compatibility |
| CI | Repeatable checks catch meaningful defects | Existing test/build commands and appropriate permissions |
| `.gitattributes` | Real generated/vendor classification or line-ending needs | Paths and semantics reflect the repository |

Do not generate all missing files. A Markdown issue template can be effective;
YAML forms are an option for structured input, not an automatic quality upgrade.
Blank issues may support valid workflows; disable them only for an agreed routing
policy with a usable alternative.

## File-specific guidance

### Contribution, support, and conduct

Document prerequisites, local setup, focused tests, submission expectations, and
where to ask for help. Link existing detailed guides rather than duplicating
commands likely to drift. Preserve a concise maintenance/contribution policy if
the repository intentionally declines outside changes.

When adding a code of conduct, obtain the chosen policy text from its official
source, preserve attribution, and configure an authorized enforcement channel.
Do not infer a public contact from Git author email. Keep unresolved contacts in
an explicitly labeled draft and report them; do not present placeholders as a
ready operational policy.

### Issues, pull requests, and discussions

Use only fields maintainers need: version, environment, command/input,
reproduction, expected versus actual result, and redacted logs. Warn against
including credentials in report prompts. Avoid asking users to reproduce private
security issues in a public bug form; link the verified security policy.

For YAML forms, validate required IDs, field types, choices, and YAML syntax
against current GitHub documentation. Link only enabled, verified support routes.
Discussion form filenames must match discovered category slugs. If categories
are unavailable, record that and omit speculative forms. Keep PR templates short
and focused on behavior, tests, and compatibility/migration when relevant.

### Automation and environments

Derive CI checks from actual project scripts and meaningful failure modes.
Presence of a workflow or a green badge alone is not proof of correctness.
Use scoped permissions, trusted/pinned actions under repository policy, supported
runtime versions, and checks that run locally. Do not add deployment, publishing,
secrets, or privileged pull-request execution as part of generic community setup.

For dependency updates, inspect manifests and lockfiles in each package directory;
avoid duplicating an existing updater. A devcontainer's install command must be
reviewed and match the dependency manager/version the project uses. Do not run an
untrusted setup hook merely to generate configuration.

Linguist overrides must describe actual generated, vendored, or documentation
files. Do not hide working installer scripts or research notebooks just to change
the visible language percentages. No override is necessary for an honest mix.

## Apply and verify

Use `GITHUB_HOME/references/community-files-guide.md` and
`community-templates.md` for examples, checking current schemas and adapting them
to observed workflows. License, security policy, and citation changes can use
`github-legal`; release-note configuration can use `github-release` without
requiring either entire workflow first.

Write authorized changes, preserve user work, inspect the diff, parse changed
YAML/JSON, verify links and identities, and run relevant project checks. Rendering
or GitHub behavior unavailable locally should be recorded as unverified live,
not silently counted as a success. Publishing remains a separate scoped action.

Report files changed and the contributor/support problem each solves. List
remaining placeholders, skipped files with applicability reasons, and verified
versus unavailable checks. A community checklist can accompany this evidence;
it does not measure whether the community is actually healthy.
