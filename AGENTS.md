# legends-github agent entry point

Use this workflow with any agent that can read files and execute commands. No particular model, native skill loader, or subagent framework is required.

## Work on a target repository

1. Resolve the toolkit and target as separate absolute paths. Read the target's instructions and check its Git status. Preserve existing user work.
2. Establish the user's objective, audience, repository type, and authorized changes. Inspect the actual implementation before recommending templates.
3. Run `python <toolkit>/legends_github.py verify --mode portable --path <target>`. All readiness modes check the portable runtime without requiring a host installation. Use `--offline --artifacts-dir <outside-target>` for an isolated local review. Optional provider failures do not block unrelated local work.
4. Run `python <toolkit>/legends_github.py audit --path <target>`, then inspect the evidence and proposed actions. These commands write local caches and reports. An audit score is a checklist, not proof of quality or ranking potential.
5. Choose the smallest relevant workflow using its `--help`. Distinguish observed facts, unavailable evidence, and hypotheses. Do not promote checklist points directly into business priorities.
6. Make authorized changes, inspect the diff, and run relevant checks. External mutations, paid services, and publishing must follow the user's actual authorization. Do not repeat approval requests for already authorized work.
7. Report concrete changes, verification, and remaining limitations. Do not promise higher rankings, stars, revenue, or universal host compatibility.

## Optional instructions and tools

Read `docs/GITHUB-RECIPE.md` and the pinned router copy at `skills/cto-legends/SKILL.md` when useful. Legacy host-specific paths, mandatory multi-agent language, and optional-provider setup prompts are not requirements of this portable entry point. Translate supported operations into the current host's tools; run sequentially when delegation is unavailable or unnecessary.

Use configured providers only for requested capabilities. Never print credentials or load arbitrary dotenv contents into a shell command. Keep artwork optional and follow the repository owner's design direction.

## Contributing to this toolkit

Keep executable behavior in `github/scripts/`, with `legends_github.py` as the public launcher. Add regression tests for behavior changes. Keep host adapters thin and document their tested status. Do not remove legacy installers or change cache formats without a migration plan. Follow `docs/MODERNIZATION.md` for reconciliation scope.

## DataForSEO research dependency

For measured demand and SERP research, install `requirements-dataforseo.txt` and use `research` to estimate before explicit execution. This uses the public legends-dataforseo-kit; no MCP installation is required. Follow `docs/SEO-RESEARCH.md`, preserve locale and observation dates, and import collected exports through `seo`. Offline audits remain independent of provider credentials.

## Full SEO optimization means research and application

For an authorized full optimization, keyword optimization, or DataForSEO-backed
GitHub pass, presentation alone is incomplete. Run this sequence:

1. Inspect the actual product and identify audiences and task/category queries.
2. Check DataForSEO Kit readiness and preview research. Collect live demand and
   SERPs through `research`; import them through `seo`. A local keyword list or
   a `--mode full` analysis is not live research.
3. Research distinct relevant intent clusters. Continue finite batches when an
   unresolved decision warrants another query. Stop when positioning, primary
   and supporting terms, competing result types, and exclusions are justified.
4. Apply justified README opening/headings, description, topics, and helpful
   documentation within authorization. Preserve approved branding and content.
5. Save query/locale/date/source/cost evidence, keyword choices and exclusions,
   before/after changes, and verification. Never claim improved rankings from
   publishing copy. Report actual cost and unmeasured outcomes.

Honor the user's spending scope. Do not invent a tiny dollar ceiling or equate
cheap research with completion. With explicit no-ceiling authorization, use
`research --execute --no-cost-ceiling`; each batch remains finite and retains
actual costs. Otherwise use the approved `--confirm-cost-usd` ceiling. Preview
remains the default and paid calls are never implicit in `seo`. If access fails,
finish independent work and label live optimization incomplete. Artwork-only
requests remain artwork-only; never represent them as a completed SEO pass.
