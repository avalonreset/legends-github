---
name: github-dataforseo
description: Research repository search demand and SERP intent through legends-dataforseo-kit, without MCP.
---

# Repository search research

Use the portable `legends_github.py research` command. Install the toolkit's
`requirements-dataforseo.txt` before live acquisition. Read `docs/SEO-RESEARCH.md`
from the toolkit root. No agent-specific host configuration is required.

1. Inspect the product and audience; propose bounded relevant keyword seeds.
2. Declare location and language. Run an estimate without `--execute` first.
3. Follow the user's authorization for paid research. Execute with an explicit
   `--confirm-cost-usd` ceiling. Never expose credentials or retry paid requests blindly.
4. Preserve exports and timestamps. Inspect search intent and product fit before
   selecting a primary keyword. Missing demand is unknown, not zero.
5. Import the exports with `seo --keyword-data --primary-keyword --serp-data`.
6. Recommend specific copy, topics, examples and comparisons. Report these as
   hypotheses until traffic or ranking measurements support an outcome.

DataForSEO keyword volume describes web search demand, not GitHub internal
search demand. This connector implements keyword overview and Google organic
SERPs; it does not establish AI citation visibility or competitor revenue.
