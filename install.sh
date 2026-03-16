#!/usr/bin/env bash
set -euo pipefail

# Claude GitHub - Installation Script
# Installs the GitHub optimization skill suite for Claude Code

C='\033[36m'    # cyan
G='\033[32m'    # green
Y='\033[33m'    # yellow
W='\033[97m'    # bright white
D='\033[2m'     # dim
B='\033[1m'     # bold
M='\033[35m'    # magenta
R='\033[0m'     # reset

main() {
    clear 2>/dev/null || true
    echo ""
    echo -e "${C}${B}"
    echo '    ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗'
    echo '   ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝'
    echo '   ██║     ██║     ███████║██║   ██║██║  ██║█████╗  '
    echo '   ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  '
    echo '   ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗'
    echo '    ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝'
    echo ''
    echo '    ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗ '
    echo '   ██╔════╝ ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗'
    echo '   ██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝'
    echo '   ██║   ██║██║   ██║   ██╔══██║██║   ██║██╔══██╗'
    echo '   ╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝'
    echo '    ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ '
    echo -e "${R}"
    echo -e "   ${M}░▒▓${R}${G}${B} v1.2 ${R}${M}▓▒░${R}  ${D}Repository Optimization Skills for Claude Code${R}"
    echo ""

    # Check prerequisites
    if ! command -v gh &>/dev/null; then
        echo -e "   ${Y}[!] GitHub CLI (gh) not detected${R}"
        echo -e "   ${D}    Required for repo operations. Install: https://cli.github.com/${R}"
        echo ""
    fi

    # Determine Claude skills directory
    CLAUDE_DIR="${HOME}/.claude"
    SKILLS_DIR="${CLAUDE_DIR}/skills"
    AGENTS_DIR="${CLAUDE_DIR}/agents"

    # Create directories
    mkdir -p "${SKILLS_DIR}/github/references"
    mkdir -p "${SKILLS_DIR}/github-audit"
    mkdir -p "${SKILLS_DIR}/github-readme"
    mkdir -p "${SKILLS_DIR}/github-legal"
    mkdir -p "${SKILLS_DIR}/github-meta"
    mkdir -p "${SKILLS_DIR}/github-seo"
    mkdir -p "${SKILLS_DIR}/github-community"
    mkdir -p "${SKILLS_DIR}/github-release"
    mkdir -p "${SKILLS_DIR}/github-empire"
    mkdir -p "${AGENTS_DIR}"

    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    echo -e "   ${C}${B}Installing skills...${R}"
    echo ""

    cp "${SCRIPT_DIR}/github/SKILL.md" "${SKILLS_DIR}/github/SKILL.md"
    echo -e "   ${G}${B}[+]${R} Orchestrator        ${D}routes commands to 8 sub-skills${R}"

    cp "${SCRIPT_DIR}/github/references/"*.md "${SKILLS_DIR}/github/references/"
    echo -e "   ${G}${B}[+]${R} 9 Reference Files   ${D}SEO, legal, readme, community guides${R}"

    for skill in github-audit github-legal github-community github-release github-seo github-meta github-readme github-empire; do
        cp "${SCRIPT_DIR}/skills/${skill}/SKILL.md" "${SKILLS_DIR}/${skill}/SKILL.md"
    done
    echo -e "   ${G}${B}[+]${R} 8 Sub-Skills        ${D}audit, legal, community, release, seo, meta, readme, empire${R}"

    for agent in github-legal github-community github-release github-seo github-meta github-readme; do
        cp "${SCRIPT_DIR}/agents/${agent}.md" "${AGENTS_DIR}/${agent}.md"
    done
    echo -e "   ${G}${B}[+]${R} 6 Scoring Agents    ${D}parallel audit across 6 categories${R}"

    echo ""
    echo -e "   ${G}${B}Skills installed.${R}"

    # ─────────────────────────────────────────────────
    # GUIDED SETUP: DataForSEO
    # ─────────────────────────────────────────────────
    echo ""
    echo -e "   ${M}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo -e "   ${Y}${B} SERVICE SETUP${R}"
    echo -e "   ${M}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo ""
    echo -e "   Two services are ${W}${B}strongly recommended${R} to unlock the full suite."
    echo -e "   Setting them up takes about 5 minutes and is well worth it."
    echo ""

    echo -e "   ${M}─── 1/2 ───${R} ${W}${B}DataForSEO${R} ${D}(live keyword data, SERP rankings, AI visibility)${R}"
    echo ""
    echo -e "   This powers real keyword research with actual search volume and"
    echo -e "   difficulty data. Without it, SEO recommendations are best-guess only."
    echo ""

    DATAFORSEO_DONE=false
    read -rp "   Set up DataForSEO now? (y/n): " setup_dfs
    echo ""

    if [[ "${setup_dfs}" =~ ^[Yy] ]]; then
        # Check Node.js
        if ! command -v node &>/dev/null; then
            echo -e "   ${Y}[!] Node.js is required for the DataForSEO MCP server.${R}"
            echo -e "   ${D}    Install it from https://nodejs.org/ and re-run this installer.${R}"
            echo -e "   ${D}    Skipping DataForSEO for now.${R}"
            echo ""
        else
            NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
            if [ "$NODE_VERSION" -lt 20 ]; then
                echo -e "   ${Y}[!] Node.js 20+ required. You have $(node -v).${R}"
                echo -e "   ${D}    Update Node.js and re-run this installer.${R}"
                echo -e "   ${D}    Skipping DataForSEO for now.${R}"
                echo ""
            else
                echo -e "   ${D}If you don't have an account yet:${R}"
                echo -e "   ${D}  1. Sign up free at ${C}https://dataforseo.com${R}"
                echo -e "   ${D}  2. Find your login + password at ${C}https://app.dataforseo.com/api-access${R}"
                echo ""
                read -rp "   DataForSEO Login (email): " DFORSEO_LOGIN
                read -rsp "   DataForSEO Password: " DFORSEO_PASSWORD
                echo ""
                echo ""

                if [ -n "${DFORSEO_LOGIN}" ] && [ -n "${DFORSEO_PASSWORD}" ]; then
                    # Install DataForSEO skill and agent
                    mkdir -p "${SKILLS_DIR}/github-dataforseo"
                    cp "${SCRIPT_DIR}/extensions/dataforseo/skills/github-dataforseo/SKILL.md" "${SKILLS_DIR}/github-dataforseo/SKILL.md"
                    cp "${SCRIPT_DIR}/extensions/dataforseo/agents/github-dataforseo.md" "${AGENTS_DIR}/github-dataforseo.md"

                    # Pre-download MCP server
                    echo -e "   ${D}Downloading DataForSEO MCP server...${R}"
                    npx -y @anthropic/data-for-seo-mcp --version 2>/dev/null || true

                    # Configure MCP server
                    SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
                    python3 -c "
import json, os
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
" 2>/dev/null && {
                        echo -e "   ${G}${B}[+]${R} DataForSEO          ${D}MCP server configured${R}"
                        DATAFORSEO_DONE=true
                    } || {
                        echo -e "   ${Y}[!] Could not auto-configure. You can set it up manually later:${R}"
                        echo -e "   ${D}    claude mcp add dataforseo-mcp-server${R}"
                    }
                else
                    echo -e "   ${D}No credentials entered. Skipping DataForSEO.${R}"
                fi
            fi
        fi
    else
        echo -e "   ${D}Skipped. You can set it up later:${R}"
        echo -e "   ${D}  bash extensions/dataforseo/install.sh${R}"
    fi

    # ─────────────────────────────────────────────────
    # GUIDED SETUP: KIE.ai
    # ─────────────────────────────────────────────────
    echo ""
    echo -e "   ${M}─── 2/2 ───${R} ${W}${B}KIE.ai${R} ${D}(AI-generated banners and profile avatars)${R}"
    echo ""
    echo -e "   This generates professional banner images for READMEs and"
    echo -e "   AI profile avatars for your GitHub account. About 4 cents per image."
    echo -e "   Without it, image generation is skipped entirely."
    echo ""

    ENV_FILE="${SKILLS_DIR}/github/.env"
    KIE_DONE=false
    read -rp "   Set up KIE.ai now? (y/n): " setup_kie
    echo ""

    if [[ "${setup_kie}" =~ ^[Yy] ]]; then
        echo -e "   ${D}If you don't have an account yet:${R}"
        echo -e "   ${D}  1. Go to ${C}https://kie.ai/api-key${R}"
        echo -e "   ${D}  2. Create an account and copy your API key${R}"
        echo ""
        read -rp "   KIE.ai API Key: " KIE_KEY
        echo ""

        if [ -n "${KIE_KEY}" ]; then
            # Write or update .env
            if [ -f "${ENV_FILE}" ] && grep -q 'KIE_API_KEY=' "${ENV_FILE}" 2>/dev/null; then
                # Update existing key
                sed -i.bak "s|^KIE_API_KEY=.*|KIE_API_KEY=${KIE_KEY}|" "${ENV_FILE}"
                rm -f "${ENV_FILE}.bak"
            else
                # Create or append
                echo "KIE_API_KEY=${KIE_KEY}" >> "${ENV_FILE}"
            fi
            echo -e "   ${G}${B}[+]${R} KIE.ai              ${D}API key saved to .env${R}"
            KIE_DONE=true
        else
            echo -e "   ${D}No key entered. Skipping KIE.ai.${R}"
        fi
    else
        echo -e "   ${D}Skipped. You can add your key later to:${R}"
        echo -e "   ${D}  ~/.claude/skills/github/.env${R}"
    fi

    # Create .env template if it doesn't exist yet (user skipped both)
    if [ ! -f "${ENV_FILE}" ]; then
        cat > "${ENV_FILE}" << 'ENVEOF'
# Claude GitHub - API Credentials
#
# KIE.ai -- AI-generated banner images for READMEs
# Get your API key: https://kie.ai/api-key
KIE_API_KEY=
#
# DataForSEO credentials are NOT stored here.
# They are configured via the MCP server installer:
#   bash extensions/dataforseo/install.sh
# See: https://dataforseo.com (free tier available)
ENVEOF
    fi

    # ─────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────
    echo ""
    echo -e "   ${M}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo -e "   ${G}${B} SETUP COMPLETE${R}"
    echo -e "   ${M}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo ""

    # Status line
    if $DATAFORSEO_DONE; then
        DFS_STATUS="${G}${B}active${R}"
    else
        DFS_STATUS="${Y}not configured${R}"
    fi
    if $KIE_DONE; then
        KIE_STATUS="${G}${B}active${R}"
    else
        KIE_STATUS="${Y}not configured${R}"
    fi
    echo -e "   DataForSEO [${DFS_STATUS}]  |  KIE.ai [${KIE_STATUS}]"
    echo ""

    echo -e "   ${W}${B}Next step: restart Claude Code so the new skills load.${R}"
    echo ""
    echo -e "   ${M}How to restart:${R}"
    echo -e "   ${C}1.${R} Type ${W}${B}/exit${R} to quit Claude Code"
    echo -e "   ${C}2.${R} Run ${W}${B}claude${R} again from your project folder"
    echo -e "   ${C}3.${R} ${D}(optional)${R} Type ${W}${B}/resume${R} to pick up where you left off"
    echo ""
    echo -e "   ${M}Important:${R} Run skills from inside the project you want to optimize."
    echo -e "   ${D}The skills read your source code, configs, and git remote to make${R}"
    echo -e "   ${D}informed recommendations. Running from an empty folder won't work well.${R}"
    echo ""
    echo -e "   ${M}Standard Operating Procedure (run in this order):${R}"
    echo ""
    echo -e "   ${W}Step 0${R}  ${C}/github audit${R}       ${D}Diagnose: score 0-100, generates your SOP${R}"
    echo -e "   ${W}Step 1${R}  ${C}/github legal${R}       ${D}Foundation: license, SECURITY.md, CITATION.cff${R}"
    echo -e "   ${W}Step 2${R}  ${C}/github community${R}   ${D}Infrastructure: templates, CoC, devcontainer${R}"
    echo -e "   ${W}Step 3${R}  ${C}/github release${R}     ${D}Versioning: CHANGELOG, badges, releases${R}"
    echo -e "   ${W}Step 4${R}  ${C}/github seo${R}         ${D}Research: keyword data for description + README${R}"
    echo -e "   ${W}Step 5${R}  ${C}/github meta${R}        ${D}Settings: description, topics, features${R}"
    echo -e "   ${W}Step 6${R}  ${C}/github readme${R}      ${D}Capstone: README optimization with SEO keywords${R}"
    echo -e "   ${W}Step 7${R}  ${C}/github audit${R}       ${D}Measure: re-audit to verify improvement${R}"
    echo ""
    echo -e "   ${D}After all repos are optimized:${R}"
    echo -e "           ${C}/github empire${R}      ${D}Portfolio strategy, profile README, avatar${R}"
    echo ""
}

main "$@"
