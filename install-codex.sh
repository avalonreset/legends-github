#!/usr/bin/env bash
set -euo pipefail

# Codex GitHub - Installation Script
# Installs the GitHub optimization skill suite for Codex.

SKIP_PYTHON_DEPS=false
for arg in "$@"; do
  case "$arg" in
    --skip-python-deps) SKIP_PYTHON_DEPS=true ;;
  esac
done

say_step() {
  printf '   [+] %s\n' "$1"
}

python_cmd() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$@"
  elif command -v python >/dev/null 2>&1; then
    python "$@"
  else
    echo "Python 3.10+ is required for the headless runtime." >&2
    exit 1
  fi
}

echo ""
echo "    CODEX GITHUB"
echo "    GitHub repository optimization skills for Codex"
echo ""

if ! command -v gh >/dev/null 2>&1; then
  echo "   [!] GitHub CLI (gh) not detected"
  echo "       Required for live repo operations. Install: https://cli.github.com/"
  echo ""
fi

CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"
SKILLS_DIR="${CODEX_HOME}/skills"
AGENTS_DIR="${CODEX_HOME}/agents"
GITHUB_SKILL_DIR="${SKILLS_DIR}/github"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${GITHUB_SKILL_DIR}/references" "${GITHUB_SKILL_DIR}/scripts" "${AGENTS_DIR}"
for skill in github-audit github-readme github-legal github-meta github-seo github-community github-release github-empire; do
  mkdir -p "${SKILLS_DIR}/${skill}"
done

cp "${SCRIPT_DIR}/github/SKILL.md" "${GITHUB_SKILL_DIR}/SKILL.md"
cp "${SCRIPT_DIR}/github/requirements.txt" "${GITHUB_SKILL_DIR}/requirements.txt"
cp "${SCRIPT_DIR}/github/references/"*.md "${GITHUB_SKILL_DIR}/references/"
cp "${SCRIPT_DIR}/github/scripts/"*.py "${GITHUB_SKILL_DIR}/scripts/"
say_step "Installed orchestrator, references, and headless runtime"

for skill in github-audit github-legal github-community github-release github-seo github-meta github-readme github-empire; do
  cp "${SCRIPT_DIR}/skills/${skill}/SKILL.md" "${SKILLS_DIR}/${skill}/SKILL.md"
done
say_step "Installed 8 specialized Codex skills"

for agent in github-legal github-community github-release github-seo github-meta github-readme; do
  cp "${SCRIPT_DIR}/agents/${agent}.md" "${AGENTS_DIR}/${agent}.md"
done
say_step "Installed scoring-agent reference files"

if [ "${SKIP_PYTHON_DEPS}" = false ]; then
  python_cmd -m pip install --user -r "${GITHUB_SKILL_DIR}/requirements.txt" || {
    echo "   [!] Python dependency install failed. Run manually:"
    echo "       python3 -m pip install --user -r \"${GITHUB_SKILL_DIR}/requirements.txt\""
  }
fi

ENV_FILE="${GITHUB_SKILL_DIR}/.env"
if [ ! -f "${ENV_FILE}" ]; then
  cat > "${ENV_FILE}" <<'ENVEOF'
# Codex GitHub - API Credentials
#
# KIE.ai -- AI-generated banner images for READMEs
# Get your API key: https://kie.ai/api-key
KIE_API_KEY=
ENVEOF
fi

echo ""
read -rp "   Set up KIE.ai now for banner/social images? (y/n): " setup_kie
if [[ "${setup_kie}" =~ ^[Yy] ]]; then
  read -rp "   KIE.ai API Key: " kie_key
  if [ -n "${kie_key}" ]; then
    if grep -q '^KIE_API_KEY=' "${ENV_FILE}" 2>/dev/null; then
      python_cmd - "${ENV_FILE}" "${kie_key}" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
key = sys.argv[2]
lines = path.read_text(encoding="utf-8").splitlines()
path.write_text("\n".join(("KIE_API_KEY=" + key) if line.startswith("KIE_API_KEY=") else line for line in lines) + "\n", encoding="utf-8")
PY
    else
      echo "KIE_API_KEY=${kie_key}" >> "${ENV_FILE}"
    fi
    say_step "Saved KIE.ai key to ${ENV_FILE}"
  fi
fi

echo ""
read -rp "   Configure DataForSEO MCP for Codex now? (y/n): " setup_dfs
if [[ "${setup_dfs}" =~ ^[Yy] ]]; then
  if ! command -v node >/dev/null 2>&1; then
    echo "   [!] Node.js is required for the DataForSEO MCP server."
  else
    read -rp "   DataForSEO Login: " dfs_login
    read -rsp "   DataForSEO Password: " dfs_password
    echo ""
    if [ -n "${dfs_login}" ] && [ -n "${dfs_password}" ]; then
      python_cmd "${GITHUB_SKILL_DIR}/scripts/setup_dataforseo.py" --login "${dfs_login}" --password "${dfs_password}"
      say_step "Configured DataForSEO in ${CODEX_HOME}/config.toml"
    fi
  fi
fi

echo ""
echo "   Setup complete."
echo "   Restart Codex, then use: github-audit, github-readme, github-meta, github-seo, github-legal, github-community, github-release, github-empire"
echo "   Headless check: python3 \"${GITHUB_SKILL_DIR}/scripts/run_headless.py\" verify --mode cli --path . --allow-missing-gh-auth"

