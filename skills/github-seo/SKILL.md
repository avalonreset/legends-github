---
name: github-seo
description: Research relevant organic discovery for GitHub projects through user intent, technical examples, fair alternatives/comparisons, metadata, docs, and distribution. Optional live search metrics are source-attributed and never required.
---

# GitHub organic discovery research

Help appropriate users find and evaluate a project. Produce truthful content
recommendations grounded in capabilities and audience needs. Rankings, traffic,
AI citations, adoption, and revenue remain outcomes to measure, not guarantees.

## Runtime and scope

Resolve **GITHUB_HOME** from this skill directory: `../../github` in source,
`../github` when installed. Verify `scripts/run_headless.py` exists and read
`GITHUB_HOME/references/portable-workflows.md`. Resolve **TARGET** separately.

```text
python "<GITHUB_HOME>/scripts/run_headless.py" seo --help
python "<GITHUB_HOME>/scripts/run_headless.py" seo --path "<TARGET>"
python "<GITHUB_HOME>/scripts/run_headless.py" seo --path "<TARGET>" --mode full
python "<GITHUB_HOME>/scripts/run_headless.py" discover --path "<TARGET>" --audience "Intended users" --category "User problem" --competitor "Comparison candidate"
```

The runner creates deterministic local keyword/content suggestions and
`seo-data.json`, `SEO-REPORT.md`, and `SEO-SUMMARY.json`. Neither `quick` nor
`full` implies live paid research. Check reported analysis mode and evidence;
volume, difficulty, search positions, and AI mentions are unavailable unless
actually collected from an identified source. Local terminology can still have
observed relevance to the implementation.

`discover` builds a local, evidence-backed content and experiment plan. It writes
`discovery-data.json`, `DISCOVERY-REPORT.md`, `DISCOVERY-PLAN.json`, and
`DISCOVERY-METRICS-BASELINE.json`. Audience, category, and repeated competitor
arguments define the brief; a named competitor is a research candidate, not a
verified comparison. The baseline contains no measured traffic until collected.
Use `discover` for content/experiment planning and `seo` for the compatibility
keyword cache consumed by other workflows.

## Establish audience, product, and intent

Read code, README, docs, examples, supported platforms, integrations, install
paths, releases, limitations, and alternatives already discussed by the project.
Identify what a user can actually accomplish and who it is suitable for.

Build a small intent map before researching keywords:

| Intent | Example query pattern | Useful destination/evidence |
|---|---|---|
| Discover a category | `[task] open source tool` | Precise purpose, supported workflow, real example |
| Evaluate alternatives | `[product] alternatives`, `[A] vs [B]` | Fair criteria, current sources, limitations, migration path |
| Complete a task | `how to [task] with [ecosystem]` | Reproducible guide with input, command, and output |
| Integrate | `[tool] [framework/provider] integration` | Actual supported integration and working configuration |
| Troubleshoot | `[tool] [specific error]` | Tested fix, version scope, known issue or diagnostic |
| Adopt/distribute | `[language] [library category]`, `[tool] install` | Verified package listing, release, installation |

Private/internal repositories often make public search discovery
**not_applicable**. Their navigation, terminology, and onboarding can still
benefit from the same analysis. Do not leak private repo names or source into
public queries without authorization.

## Collect bounded research

Start with source-derived concepts and actual user questions. If public research
is in scope, inspect official project docs, package listings, GitHub search, and
search results relevant to the objective. Record exact query, date, locale,
language, device if relevant, result depth, and source URL or provider task ID.
Use current official sources for competitor features, limits, and pricing claims.

A configured provider such as DataForSEO is optional. Use it only for requested
capabilities within established authorization/budget. Discover the actual tools
and parameter schemas; do not assume historical tool names or pricing are current.
Do not request credentials, install a provider, or pause unrelated documentation
because no keyword service is present.

For an authorized live pass:

1. Select a few concise category/task seeds from implementation and audience.
   Broaden an empty seed once if useful; stay within the stated query/cost bound.
2. Collect candidate phrases and available metrics in the selected locale.
   Deduplicate candidates and discard unrelated products/domains before analysis.
3. Inspect a bounded set of promising queries directly. Record repository URLs,
   docs, package pages, discussions, and commercial results separately.
4. Collect related questions or AI-overview content only if actually returned.
   Treat these as observed outputs, not proof of how many people ask a question.
5. Stop at the agreed bound. Report missing measurements instead of issuing
   speculative follow-up calls until a favorable result appears.

Search-volume estimates describe a provider dataset and period; they are not
exact demand or expected repository traffic. Difficulty is a provider heuristic.
A missing value is unknown, not zero. A zero reported volume is a dataset result,
not proof there are no users, especially for niche or new projects.

## Interpret evidence without ranking folklore

A GitHub result in one SERP demonstrates that result at that time; it does not
prove another repo can achieve its position. No GitHub result in the checked
window is observed absence in that sample, not a permanent inability to rank.
Do not mark unchecked spelling variants or query clusters as verified. They may
share a working hypothesis, clearly labeled as such.

Separate these evidence states per query or claim:

- **observed**: exact query/source inspected; record the result and scope.
- **unavailable**: no measurement, failed tool, unknown locale, or inaccessible source.
- **not_applicable**: measurement does not serve this project's objective; explain why.

Prioritize relevance and user usefulness, then evidence strength, feasible content,
maintenance effort, and measured demand where available. Do not multiply guessed
volume, intent, difficulty, or arbitrary GitHub-viability numbers into a supposedly
objective opportunity score. Legacy scores may be labeled heuristics, not forecasts.

A repo owner controls README/content, description, topics, links, release/package
presentation, and any separately maintained docs site. GitHub controls its rendered
page markup and crawling behavior. Verify specific current platform claims when
they affect a decision. Do not claim backlinks to repository pages are impossible
or recommend manufactured link exchanges.

## Turn research into useful material

Prepare a compact plan with target user/question, current gap, source evidence,
proposed content, destination, effort, and verification:

- A precise opening and description state implemented capabilities and scope.
- A working example demonstrates one meaningful workflow with expected output.
- A comparison or alternatives page uses fair, current criteria. Explain who
  each option suits and where this project falls short. Cite vendor claims and
  separate them from your own tests. Never invent a rival's limitation.
- A migration guide explains concrete differences, supported import/export, and
  known gaps; verify its commands against actual versions.
- Docs answer recurring configuration, integration, or troubleshooting questions.
  Do not create a page for every keyword variant or duplicate a guide merely to
  capture another phrase.
- Topics describe actual use cases and ecosystem. No minimum count is required.
- Distribution work can clarify package/release listings and existing docs links.
  Community participation or outreach is a separate action requiring explicit
  authorization; do not post unsolicited promotional messages.

Route local copy changes to `github-readme`, live metadata to `github-meta`, and
artifact/distribution preparation to `github-release` as needed. Preserve each
action's authorization boundary; research does not authorize publishing.

## AI discovery and measurement

Clear definitions, cited technical claims, accessible documentation, and useful
examples help readers evaluate the project. They are not a proven recipe for AI
citations. If asked to measure AI visibility, record model/platform, query, date,
settings when known, and the exact observed mention/citation. One response does
not establish universal visibility; an unqueried system is unavailable, not "no."

Keep a dated baseline only for metrics actually accessible. Compare matching
scope/time windows; label incomplete traffic retention and attribution limits.
Do not credit a metadata edit for star/traffic changes without causal evidence.

## Report and cache

Deliver relevant opportunities with source-attributed observations, recommended
content, and limitations. Preserve runtime cache fields; put richer interactive
research in a cited report/sidecar instead of inventing measured cache values.
`GITHUB_HOME/references/github-seo-guide.md` supplies additional patterns, subject
to current evidence and the shared contract.

When paid research was used, include provider, calls, reported charges, and any
estimated/unknown cost separately. With no provider calls, state that only if
relevant; do not show fabricated per-call prices or label all local analysis
unverified merely because paid search metrics were unavailable.
