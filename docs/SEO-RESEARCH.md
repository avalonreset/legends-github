# Use measured keyword research

Live research uses the public [legends-dataforseo-kit](https://github.com/avalonreset/legends-dataforseo-kit) dependency. Install it with `python -m pip install -r requirements-dataforseo.txt`. Set `DATAFORSEO_LOGIN` (or `DATAFORSEO_USERNAME`) and `DATAFORSEO_PASSWORD` in the environment; no MCP server is needed.

Estimate before execution:

```bash
python legends_github.py research --path /path/to/project \
  --keyword "google maps rank checker" --keyword "local rank tracker" \
  --serp "google maps rank checker" --location-code 2840 --language en \
  --artifacts-dir /path/to/research-output
```

The default makes no requests and needs no credentials. After reviewing the estimate, add `--execute --confirm-cost-usd 0.02` to authorize the bounded collection. This example's modeled base estimate is $0.01424; prices may change. The connector accepts at most 30 keywords and three SERPs, checks the remaining budget between requests, preserves raw responses, and does not retry paid requests. `--offline` forbids execution. The ceiling is advisory, not a provider billing limit. Incomplete runs retain a partial receipt for inspection.

Use the returned `keyword_data` and `serp_data` paths in the SEO import below. Choose the primary keyword after reviewing intent and product fit.

The portable `seo` command defaults to local hypotheses. It does not make paid
API calls. To use measured research, collect official DataForSEO JSON exports
through your authorized API client, CLI or agent tools, then import them:

```bash
python legends_github.py seo --path /path/to/project \
  --keyword-data /path/to/keyword-overview.json \
  --primary-keyword "google maps rank checker" \
  --serp-data /path/to/google-organic.json \
  --offline --artifacts-dir /path/to/research-output
```

`--keyword-data` accepts a successful official
`dataforseo_labs/google/keyword_overview/live` response. `--serp-data` accepts a
successful `serp/google/organic/live/advanced` response and can be repeated.
The importer requires matching location/language and an explicit primary term
returned in the keyword dataset. Select it for product fit and observed search
intent, not just the largest volume. Missing values stay unknown; zero remains
zero. Importing makes no DataForSEO requests and needs no credentials.

The SEO cache retains all returned keyword observations, source timestamps,
locale, organic results and historical reported API cost. Keep original exports
as research evidence. Dates may differ between keyword records; fresh collection
does not imply fresh underlying volume estimates. Export validation checks
shape and endpoint, not authenticity. Review the origin of supplied files.

Metadata suggestions remain local hypotheses until reviewed against these
observations. No ranking improvement, AI citation, or future traffic is inferred
from importing evidence. README preservation still applies.

This path works with any agent capable of producing files and running Python.
Legacy extension installers are host-specific and are not required by this
portable workflow. Live acquisition is performed by the explicit `research` command; paid calls are never hidden inside `seo`.

See [the GeoGrid research pilot](GEOGRID-SEARCH-STRATEGY.md) for actual keyword
estimates, SERP interpretation, recommendations and costs.
