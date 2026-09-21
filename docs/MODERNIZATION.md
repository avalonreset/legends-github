# Modernization and reconciliation plan

Date: 2026-09-20. Baseline: public `avalonreset/legends-github` commit `968e253`.

## Decision

Keep skills as optional, discoverable instructions. Make the portable command runtime and evidence contract the foundation. Better reasoning models can improve interpretation; they cannot repair stale rubrics, missing tests, or unclear execution contracts by themselves.

## Reconciled sources

- The public Legends repository contains the combined skill suite, Python headless runtime, Claude/Codex installers, and Gemini manifest.
- Local `E:/claude-github` is an older, dirty checkout pointing at the same public repository. Preserve its artwork and unpublished files; do not copy it over the current source.
- Local `E:/codex-github` is a separate proprietary-branded port with additional tests. Review individual changes and provenance before selecting any for the MIT public repository; do not bulk-import it.
- `legends-github-kit` is the house GitHub CLI operator toolkit, a separate product. Reuse its CLI discipline without conflating its branding, installation, or scope with this suite.
- This working checkout is isolated from all three: `E:/legends-github-refresh`.

## Findings

1. The public runtime already executes independently of an LLM provider. Rewriting it from scratch is unnecessary.
2. README positioning and orchestration text are tied to particular hosts, while `verify --mode cli/both` checks Codex installation paths. `--mode api` provides the existing host-independent readiness path.
3. The score rewards badges and standard files with fixed weights. A README example labels missing badges critical. This is a checklist, not evidence that those changes improve user outcomes.
4. README promises about search visibility, universal evidence quality, and turnaround time exceed the demonstrated evidence.
5. The root CI checks Markdown only; it does not run the Python workflows. There is no tracked root test suite in this baseline.
6. The orchestrator includes broad dotenv loading, provider setup before unrelated tasks, and assumptions about parallel agents. Those need deliberate migration rather than a cosmetic rename.
7. Legacy workflow outputs and shared caches need contract tests before changing scores or installer behavior.

## Milestone 1: portable foundation

Deliver now:

- Remove README artwork and vendor badges; retain credits and licensing.
- Replace marketing guarantees with precise capabilities and limitations.
- Add a neutral `AGENTS.md` entry point with sequential fallback and optional providers.
- Add `legends_github.py` over the existing runtime; preserve existing script paths.
- Verify command routing from outside the toolkit, all workflow help, and isolated readiness.

This milestone does not certify every agent host, redesign the scoring engine, or replace a published release.

## Milestone 2: evidence and prioritization

- Introduce a versioned findings schema: check ID, evidence, source, collection time, availability, applicability, confidence, impact, effort, and verification.
- Separate unavailable evidence from failed checks. Mark inapplicable checks explicitly and exclude them from denominators.
- Build repository profiles for libraries, CLI tools, services, documentation, skills, and private/internal projects.
- Prioritize broken installation, misleading claims, unusable examples, and release defects above decoration.
- Preserve legacy score outputs during migration; publish the scoring version and explain changes.
- Add fixtures for missing auth, no network, private repos, missing remotes, monorepos, stale cache, and conflicting evidence.

Acceptance: repeatable results on fixtures; no invented facts; each recommendation links to observed evidence or is labeled a hypothesis.

## Milestone 3: shared runtime and adapters

- Replace Codex-centric readiness with capability probes while retaining compatibility aliases.
- Audit credential loading, optional network calls, cache isolation, overwrite behavior, and error exit codes.
- Move executable rules out of duplicated prompts; let skills route to tested commands.
- Keep Claude, Codex, and Gemini adapters; add other host adapters only after verifying their real interfaces.
- Test Grok, Cursor, and other requested hosts through their supported file/command mechanisms. Treat Meta Muse as unverified until its available tool interface is established.

Acceptance: same fixture and JSON contract across tested hosts; no paid key required for local operations; sequential operation works without subagents.

## Milestone 4: product and release proof

- Create a public example showing evidence, prioritized fixes, a patch, and verification.
- Add Python tests and Windows/Linux checks to CI, with isolated caches and no credentials required for offline tests.
- Run a stronger-model review against the same fixtures and human acceptance criteria. Model preference may be Astra at extra-high reasoning where available; do not confuse the review model with a product dependency.
- Review installers, help, README examples, source packaging, and migration notes together.
- Publish a new release only after the runtime and adapter acceptance checks pass.

## Not part of the refresh

No repository rename, license change, removal of attribution, mandatory image generator, automatic paid research, or promise of compatibility with every AI service. Do not optimize the project merely to maximize its own checklist score.

## First-pass verification

- Three launcher regression tests pass, covering invocation from another directory, all ten workflow help contracts, and invalid-command failure.
- Portable readiness passes with isolated cache paths and without requiring an installed host skill.
- The existing audit executes successfully through the new launcher and produces artifacts.
- README, agent entry point, and this plan pass Markdown lint.
- Windows/Linux and Python 3.10/3.12 launcher jobs are added to CI; remote execution remains pending publication of the branch.

The legacy audit assigns this revised repository 88/100. That number is recorded only as a smoke-test output, not as validation of the new methodology.

## Implemented refresh

The portable runtime, evidence engine, discovery planner, optional local artwork, shared skill contract, specialist reviewers, and safety fixes are implemented on the refresh branch. See [GeoGrid validation](GEOGRID-VALIDATION.md) for the eleven-workflow real-project check and [discovery](DISCOVERY.md) for the new experiment contract. The original score fields remain available but are explicitly legacy.

Native host certification remains unclaimed. The command interface has been exercised through this agent; other services need file and command access. No published release has been replaced by this refresh.
