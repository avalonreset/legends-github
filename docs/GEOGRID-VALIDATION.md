# GeoGrid validation example

The modernization was exercised against `avalonreset/legends-geogrid` at commit `2571fae`, using a separate artifact directory. This is a validation of toolkit behavior, not a claim of increased search traffic.

## What was run

All eleven planning commands completed: `verify`, `audit`, `seo`, `meta`, `community`, `legal`, `readme`, `release`, `empire`, `discover`, and `cache-status`. They ran offline with no provider credentials required. Git status and SHA-256 checks of all 74 tracked files matched before and after the run.

A separate read-only live audit collected GitHub metadata. It reported 11 observed checks, no missing checks, no unavailable checks, and two inapplicable checks. The offline audit correctly marked two remote checks unavailable. Neither result certifies application correctness: these are bounded static observations.

The old checklist scored the same checkout differently offline and online (45 versus 63), illustrating why the retained legacy number is unsuitable as the main decision tool. It also demanded installation headings despite usable setup commands under other headings. The new evidence report recognizes those commands without insisting on a particular heading.

## Discovery direction

The test supplied the audience `local SEO practitioners and agencies`, category `local search rank tracking`, and comparison candidate `Local Falcon`. The resulting plan located documented examples and cost discussion, then proposed proof requirements and measurable experiments. It did not fetch competitor prices, invent keyword demand, or publish promotional messages.

For this project, a useful next artifact is a reproducible sample-to-report walkthrough paired with a dated cost comparison. Show data charges and the responsibilities of operating the tool separately from a managed subscription. Existing sample data and report examples are evidence leads; execute the documented recipe before claiming a fresh successful run.

The general workflow also supports libraries, services, documentation, skills, and internal projects. Competitor names, geographic markets, pricing, and promotional intent are supplied per project rather than embedded as defaults.

## Reproduce the toolkit checks

```sh
python legends_github.py --offline --artifacts-dir ./review-output verify --path /path/to/legends-geogrid
python legends_github.py --offline --artifacts-dir ./review-output audit --path /path/to/legends-geogrid
python legends_github.py --offline --artifacts-dir ./review-output discover --path /path/to/legends-geogrid --audience "local SEO practitioners and agencies" --category "local search rank tracking" --competitor "Local Falcon"
```

Select an artifact directory outside the target repository. Inspect the resulting evidence and plans. Omit `--offline` for a separate GitHub-enabled audit when authenticated access is available. Never interpret missing access as an absent repository feature.
