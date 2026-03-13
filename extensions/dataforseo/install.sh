#!/usr/bin/env bash
set -euo pipefail

# Claude GitHub -- DataForSEO Extension Installer

main() {
    echo "=== Claude GitHub -- DataForSEO Extension ==="
    echo ""

    # Check that base skill is installed
    CLAUDE_DIR="${HOME}/.claude"
    SKILLS_DIR="${CLAUDE_DIR}/skills"
    AGENTS_DIR="${CLAUDE_DIR}/agents"

    if [ ! -f "${SKILLS_DIR}/github/SKILL.md" ]; then
        echo "ERROR: Claude GitHub base skill not found."
        echo "Please install the base skill first: ./install.sh"
        exit 1
    fi

    # Check for Node.js (required for MCP server)
    if ! command -v node &>/dev/null; then
        echo "ERROR: Node.js is required for the DataForSEO MCP server."
        echo "Install: https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_VERSION" -lt 20 ]; then
        echo "ERROR: Node.js 20+ required. Current: $(node -v)"
        exit 1
    fi

    # Get API credentials
    echo "DataForSEO API credentials required."
    echo "Sign up at: https://app.dataforseo.com/"
    echo ""
    read -rp "DataForSEO API Login: " DFORSEO_LOGIN
    read -rsp "DataForSEO API Password: " DFORSEO_PASSWORD
    echo ""

    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Copy extension skill and agent
    mkdir -p "${SKILLS_DIR}/github-dataforseo"
    cp "${SCRIPT_DIR}/skills/github-dataforseo/SKILL.md" "${SKILLS_DIR}/github-dataforseo/SKILL.md"
    echo "[+] Installed: github-dataforseo skill"

    cp "${SCRIPT_DIR}/agents/github-dataforseo.md" "${AGENTS_DIR}/github-dataforseo.md"
    echo "[+] Installed: github-dataforseo agent"

    # Pre-download MCP server
    echo "[*] Pre-downloading DataForSEO MCP server..."
    npx -y @anthropic/data-for-seo-mcp --version 2>/dev/null || true

    # Configure MCP server in settings.json
    SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
    python3 -c "
import json, os, sys

settings_file = '${SETTINGS_FILE}'
if os.path.exists(settings_file):
    with open(settings_file) as f:
        settings = json.load(f)
else:
    settings = {}

if 'mcpServers' not in settings:
    settings['mcpServers'] = {}

settings['mcpServers']['dataforseo'] = {
    'command': 'npx',
    'args': ['-y', '@anthropic/data-for-seo-mcp'],
    'env': {
        'DATAFORSEO_LOGIN': '${DFORSEO_LOGIN}',
        'DATAFORSEO_PASSWORD': '${DFORSEO_PASSWORD}'
    }
}

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print('[+] Configured MCP server in settings.json')
" || {
        echo "WARNING: Could not auto-configure settings.json."
        echo "Manually add the DataForSEO MCP server configuration."
    }

    echo ""
    echo "=== DataForSEO Extension Installed ==="
    echo ""
    echo "Usage: /github dataforseo keywords 'react state management'"
    echo ""
    echo "Available commands:"
    echo "  keywords, volume, serp, ai-scrape, ai-mentions, competitors, trends"
}

main "$@"
