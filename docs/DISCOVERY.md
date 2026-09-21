# Organic discovery planning

`discover` turns a repository's existing documentation and examples into a local
evidence inventory, prioritized experiments and content briefs. It works without
a model provider, image generator, paid research service or GitHub connection.
The aim is to help the right people complete a useful task and evaluate the
project. The output contains hypotheses, not a ranking score or promised results.

## Run against any project

Keep the toolkit path separate from the target path:

```powershell
python E:\tools\legends-github\legends_github.py discover --path E:\your-project --audience "Python developers" --category "data validation"
```

Supply alternatives only when a comparison is relevant. Repeat `--competitor`:

```powershell
python E:\tools\legends-github\legends_github.py discover --path E:\your-project --audience "analysts" --category "data validation" --competitor "Alternative A" --competitor "Alternative B"
```

The sample alternatives above are placeholders. The planner does not invent
competitors or infer their capabilities. Omitted audience/category fields remain
unspecified, with a first experiment to establish context. All operations are
local. No source document, repository metadata, release or external post is
changed by this command.

## Read the artifacts

By default the command writes `.github-audit/discovery-data.json` and a new
`discovery-*` directory under `.github-audit/output/`. `GITHUB_AUDIT_DIR` overrides
that location. Existing report directories remain intact; the cache holds the
latest plan. Keep these local planning files out of commits as appropriate for
the target; the workflow does not edit its `.gitignore`.

- `DISCOVERY-REPORT.md`: evidence locations, experiments, briefs and comparison.
- `DISCOVERY-PLAN.json`: versioned machine-readable plan and evidence hashes.
- `DISCOVERY-METRICS-BASELINE.json`: uncollected metrics and manual collection
  recipes; copy it to a dated record before filling it in.

Inventory entries identify source paths, file hashes and lines with relevant
text signals. A cost heading means there is something to check, not that its
prices are current. A license file is a review lead, not a license determination.
Examples are never executed. Raw document contents are not copied into reports.

Reads are limited to conventional root files and shallow `docs/`,
`documentation/` and `examples/` trees. Limits are 256 KiB per text file, 4 MiB
of text, 40 discovered files, 30 directories, 500 entries per directory and two
directory levels below each selected tree. Hidden paths, credential-like names,
secret directories and links/reparse points are skipped. Example source files
are listed without reading their contents. Coverage reports truncation; missing
evidence outside this scope is not proof of a missing feature. Run separately
against relevant monorepo packages.

## Work through one experiment

1. Confirm the intended audience, task and public or internal distribution.
2. Save a measurement baseline with availability and UTC timestamps.
3. Make one result reproducible: inputs, supported setup, version, exact steps,
   actual output, limitations and troubleshooting. For documentation projects,
   use navigation and a worked answer instead of assuming software installation.
4. Answer one question supported by a real user task. Link the working example
   from the README and check the explanation against the implementation.
5. If comparing alternatives, verify every cell with dated primary sources or
   a repeatable test. Keep unknowns explicitly unverified.
6. Draft accurate metadata and share a useful artifact only in a relevant venue
   that welcomes it, when the owner intends to publish there.
7. Compare the selected outcome after a defined observation window; record
   whether to continue, revise or stop and why.

GitHub topics help classify a repository by purpose or subject. Candidate topics
come only from the supplied category and require review; current metadata is
uncollected. For an internal audience or a package marked `private`, the plan
uses internal distribution and omits public topic candidates. A package's
publishing flag does not establish GitHub visibility. Topic names themselves
are public, including those created from private repositories. See
[GitHub's topic guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics).

The content workflow favors useful answers with direct evidence and a clear
audience. This follows the intent of Google's
[helpful content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).
The experiment ordering is a starting dependency order, not predicted business
impact. Adjust it after observing the project and its users.

## Measure without inventing a baseline

The planner makes no network requests. Metric values start at `null`, never
zero. Each JSON recipe is an argument list for a later intentional `gh api`
read with `OWNER/REPO` replaced. Record failures as unavailable, and retain raw
responses alongside the observation date. GitHub repository traffic covers
the preceding 14 days and requires push access. See
[GitHub's traffic documentation](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository).

Compare equal windows and preserve their UTC boundaries. Avoid double-counting
overlapping windows or adding daily unique counts. Referrers and popular paths
can help locate relevant visits; task completion and concrete feedback help
interpret them. Record release dates and other events that could affect the
comparison. A traffic change by itself does not show the experiment caused it.

Release assets expose `download_count`; retain asset IDs, names and tags so
later snapshots can be compared consistently. Counts are not installations
or active users, and replacements/deletions can break continuity. A repository
without downloadable release assets can mark the metric not applicable. See
[GitHub's release asset API](https://docs.github.com/en/rest/releases/assets).

## Comparing an open source tool with hosted alternatives

For a project such as Legends GeoGrid, the same generic workflow can organize
an evaluation around a repeatable workload and documented costs. Supply its
audience/category and only the alternatives actually under consideration. The
planner has no GeoGrid-specific assumptions or mandatory service integration.

If the repository mentions costs, its brief asks for measured units and dated
official prices. For a DataForSEO-backed workload, that means checking the
actual API usage and current provider price documentation before writing a
claim. Separate software license terms from API charges, hosting and upkeep.
State workload size, cached versus billable operations, retries, currency,
date and excluded costs. A transparent calculation can be useful even when no
option is cheapest. No price or savings claim is generated automatically.

## Python contract

```python
payload = run_discovery(repo_root, audience="", category="", competitors=[])
artifacts = write_discovery_artifacts(repo_root, payload)
```

Import these functions from `github/scripts/discovery_repo.py` with that
directory on the Python import path. The planner returns a JSON-serializable
dictionary, performs no writes and is deterministic for unchanged inputs and
the selected local evidence. The writer adds cache timestamps and creates a
unique output directory using the shared runtime path helpers. The report
schema is versioned independently from legacy audit scores.
