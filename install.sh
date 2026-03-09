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
R='\033[0m'     # reset

main() {
    clear 2>/dev/null || true
    echo ""
    echo -e "${C}${B}"
    echo '     ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗'
    echo '    ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝'
    echo '    ██║     ██║     ███████║██║   ██║██║  ██║█████╗  '
    echo '    ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  '
    echo '    ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗'
    echo '     ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝'
    echo -e "${G}"
    echo '             ┌──────────────────────────┐'
    echo '             │    G I T H U B   v1.0    │'
    echo '             └──────────────────────────┘'
    echo -e "${R}"
    echo -e "  ${D}Repository Optimization Skills for Claude Code${R}"
    echo ""

    # Check prerequisites
    if ! command -v gh &>/dev/null; then
        echo -e "  ${Y}[!] GitHub CLI (gh) not detected${R}"
        echo -e "  ${D}    Required for repo operations. Install: https://cli.github.com/${R}"
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

    # Install with progress
    echo -e "  ${C}Installing skill suite...${R}"
    echo ""

    cp "${SCRIPT_DIR}/github/SKILL.md" "${SKILLS_DIR}/github/SKILL.md"
    echo -e "  ${G}[+]${R} Orchestrator          ${D}routes commands to 8 sub-skills${R}"

    cp "${SCRIPT_DIR}/github/references/"*.md "${SKILLS_DIR}/github/references/"
    echo -e "  ${G}[+]${R} 9 Reference Files     ${D}SEO, legal, readme, community guides${R}"

    for skill in github-audit github-readme github-legal github-meta github-seo github-community github-release github-empire; do
        cp "${SCRIPT_DIR}/skills/${skill}/SKILL.md" "${SKILLS_DIR}/${skill}/SKILL.md"
    done
    echo -e "  ${G}[+]${R} 8 Sub-Skills          ${D}audit, readme, legal, meta, seo, community, releases, empire${R}"

    for agent in github-readme github-legal github-meta github-community github-release github-seo; do
        cp "${SCRIPT_DIR}/agents/${agent}.md" "${AGENTS_DIR}/${agent}.md"
    done
    echo -e "  ${G}[+]${R} 6 Scoring Agents      ${D}parallel audit across 6 categories${R}"

    echo ""
    echo -e "  ${G}${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo -e "  ${G}${B}  INSTALL COMPLETE${R}"
    echo -e "  ${G}${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo ""
    echo -e "  ${W}${B}Restart Claude Code${R}, then try:"
    echo ""
    echo -e "    ${C}/github audit${R}          ${D}Score your repo 0-100 across 6 categories${R}"
    echo -e "    ${C}/github readme${R}         ${D}Generate a keyword-optimized README${R}"
    echo -e "    ${C}/github legal${R}          ${D}LICENSE, SECURITY.md, CITATION.cff${R}"
    echo -e "    ${C}/github meta${R}           ${D}Description, topics, feature toggles${R}"
    echo -e "    ${C}/github seo${R}            ${D}Live keyword research and SERP analysis${R}"
    echo -e "    ${C}/github community${R}      ${D}Issue templates, CONTRIBUTING, CODE_OF_CONDUCT${R}"
    echo -e "    ${C}/github release${R}       ${D}CHANGELOG, versioning, badges${R}"
    echo -e "    ${C}/github empire${R}          ${D}Portfolio strategy across all repos${R}"

    # DataForSEO setup
    echo ""
    echo -e "  ${G}${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo -e "  ${Y}${B}  RECOMMENDED: DataForSEO + KIE.ai${R}"
    echo -e "  ${G}${B}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${R}"
    echo ""
    echo -e "  ${W}${B}DataForSEO${R} ${D}(live keyword data, SERP rankings, AI visibility)${R}"
    echo ""
    echo -e "    1. Sign up at ${C}https://dataforseo.com${R}"
    echo -e "       ${D}Free tier includes credits for hundreds of analyses.${R}"
    echo ""
    echo -e "    2. Run the DataForSEO installer:"
    echo ""
    echo -e "       ${W}bash extensions/dataforseo/install.sh${R}"
    echo ""
    echo -e "    3. Add your credentials to ${C}~/.claude/skills/github/.env${R}:"
    echo ""
    echo -e "       ${W}DATAFORSEO_LOGIN=your_email@example.com${R}"
    echo -e "       ${W}DATAFORSEO_PASSWORD=your_api_password${R}"
    echo ""
    echo -e "  ${W}${B}KIE.ai${R} ${D}(AI-generated banner images for READMEs)${R}"
    echo ""
    echo -e "    1. Get a key at ${C}https://kie.ai/api-key${R}"
    echo ""
    echo -e "    2. Add to the same ${C}.env${R} file:"
    echo ""
    echo -e "       ${W}KIE_API_KEY=your_key_here${R}"
    echo ""
    echo -e "  ${D}Both services make the suite dramatically more powerful.${R}"
    echo -e "  ${D}Without them, skills still work but rely on codebase analysis only.${R}"
    echo ""
}

main "$@"
