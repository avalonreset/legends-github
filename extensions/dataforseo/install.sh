#!/usr/bin/env bash
set -euo pipefail
kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 -m pip install -r "$kit_root/requirements-dataforseo.txt"
echo 'Installed legends-dataforseo-kit. Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in your environment.'
echo 'See docs/SEO-RESEARCH.md. No MCP server or credential file was configured.'
