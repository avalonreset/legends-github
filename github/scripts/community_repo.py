#!/usr/bin/env python3
"""Deterministic community-health planning for Legends GitHub."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_repo import detect_repo_type, load_readme, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_auth_ok, gh_repo_view, have_command, repo_slug_from_git, run_command
from release_repo import CANONICAL_RELEASE_YML
from runtime_paths import repo_output_dir


CONTRIBUTOR_COVENANT_FALLBACK = """# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the overall
  community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or advances of
  any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email address,
  without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official email address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
[REPLACE: your-email@example.com].
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series of
actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or permanent
ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior, harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within the
community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder](https://github.com/mozilla/diversity).

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.
"""

README_FILE = "README"
DESCRIPTION_FILE = "Description"
LICENSE_FILE = "LICENSE"
SECURITY_FILE = "SECURITY.md"
CONTRIBUTING_FILE = "CONTRIBUTING.md"
CODE_OF_CONDUCT_FILE = "CODE_OF_CONDUCT.md"
SUPPORT_FILE = "SUPPORT.md"
CODEOWNERS_FILE = ".github/CODEOWNERS"
FUNDING_FILE = ".github/FUNDING.yml"
ISSUE_TEMPLATES_FILE = ".github/ISSUE_TEMPLATE/"
PR_TEMPLATE_FILE = ".github/PULL_REQUEST_TEMPLATE.md"
DISCUSSION_TEMPLATES_FILE = ".github/DISCUSSION_TEMPLATE/"
GITATTRIBUTES_FILE = ".gitattributes"
DEVCONTAINER_FILE = ".devcontainer/devcontainer.json"
DEPENDABOT_FILE = ".github/dependabot.yml"
RELEASE_YML_FILE = ".github/release.yml"
CI_WORKFLOW_FILE = ".github/workflows/ci.yml"


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_read_text(path: Path) -> str:
    """Read a text file if present."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_first_email(text: str) -> str:
    """Return the first email address found in text."""
    match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, flags=re.IGNORECASE)
    return match.group(0) if match else ""


def git_config_value(repo_root: Path, key: str) -> str:
    """Return a git config value if available."""
    result = run_command(["git", "config", "--get", key], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def detect_primary_language(repo_root: Path, cached_context: dict[str, Any], metadata: dict[str, Any]) -> str:
    """Return the best-effort primary language."""
    name = ((metadata.get("primaryLanguage") or {}).get("name")) or cached_context.get("primary_language")
    if isinstance(name, str) and name.strip():
        return name.strip()
    if (repo_root / "pyproject.toml").exists() or (repo_root / "requirements.txt").exists() or (repo_root / "setup.py").exists():
        return "Python"
    if (repo_root / "package.json").exists():
        if any(path.suffix == ".ts" for path in repo_root.rglob("*.ts")):
            return "TypeScript"
        return "JavaScript"
    if (repo_root / "Cargo.toml").exists():
        return "Rust"
    if (repo_root / "go.mod").exists():
        return "Go"
    if (repo_root / "pom.xml").exists() or (repo_root / "build.gradle").exists():
        return "Java"
    if (repo_root / "SKILL.md").exists() or (repo_root / "AGENTS.md").exists():
        return "Markdown"
    return "Markdown"


def detect_intent(cached_context: dict[str, Any], repo_type: str) -> str:
    """Return the best-effort repo intent."""
    cached = cached_context.get("intent")
    if isinstance(cached, str) and cached.strip():
        return cached.strip()
    if repo_type in {"Skill/Plugin", "Library/Package", "CLI Tool", "Framework"}:
        return "Open Source Community"
    return "Professional Portfolio"


def find_first_existing(repo_root: Path, candidates: list[str]) -> Path | None:
    """Return the first matching path."""
    for relative in candidates:
        path = repo_root / relative
        if path.exists():
            return path
    return None


def readme_exists(repo_root: Path) -> bool:
    """Return whether any canonical README exists."""
    readme_text, readme_path = load_readme(repo_root)
    return bool(readme_text) and readme_path is not None


def find_contributing(repo_root: Path) -> Path | None:
    """Return the contributing guide path, if any."""
    return find_first_existing(repo_root, ["CONTRIBUTING.md", "CONTRIBUTING.rst", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"])


def find_code_of_conduct(repo_root: Path) -> Path | None:
    """Return the code of conduct path, if any."""
    return find_first_existing(repo_root, ["CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.rst", ".github/CODE_OF_CONDUCT.md", "docs/CODE_OF_CONDUCT.md"])


def find_security(repo_root: Path) -> Path | None:
    """Return the security policy path, if any."""
    return find_first_existing(repo_root, ["SECURITY.md", "SECURITY.rst", ".github/SECURITY.md", "docs/SECURITY.md"])


def find_support(repo_root: Path) -> Path | None:
    """Return the support guide path, if any."""
    return find_first_existing(repo_root, ["SUPPORT.md", "SUPPORT.rst", ".github/SUPPORT.md", "docs/SUPPORT.md"])


def find_codeowners(repo_root: Path) -> Path | None:
    """Return the CODEOWNERS path, if any."""
    return find_first_existing(repo_root, [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"])


def find_pr_template(repo_root: Path) -> Path | None:
    """Return the pull request template path, if any."""
    return find_first_existing(repo_root, [".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"])


def list_issue_templates(repo_root: Path) -> list[Path]:
    """Return issue template files."""
    issue_dir = repo_root / ".github" / "ISSUE_TEMPLATE"
    if not issue_dir.exists():
        return []
    return sorted(path for path in issue_dir.iterdir() if path.is_file() and path.suffix.lower() in {".yml", ".yaml", ".md"})


def list_discussion_templates(repo_root: Path) -> list[Path]:
    """Return discussion template files."""
    discussion_dir = repo_root / ".github" / "DISCUSSION_TEMPLATE"
    if not discussion_dir.exists():
        return []
    return sorted(path for path in discussion_dir.iterdir() if path.is_file())


def list_workflows(repo_root: Path) -> list[Path]:
    """Return workflow files."""
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.exists():
        return []
    return sorted(path for path in workflows_dir.glob("*.y*ml") if path.is_file())


def quality_contributing(text: str) -> tuple[str, str]:
    """Assess CONTRIBUTING quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create a contributing guide with setup and workflow details."
    if any(token in lowered for token in ("reporting bugs", "bug report", "requesting features", "feature request")) and any(
        token in lowered for token in ("pull request", "contributing code", "contributing")
    ):
        if any(token in lowered for token in ("code style", "lint", "format", "security", "code of conduct")):
            return "good", "Keep the current contributing guide."
    if "development" in lowered or "setup" in lowered:
        return "basic", "Expand CONTRIBUTING.md with code style guidance and contribution links."
    if "prs welcome" in lowered or len(text.splitlines()) <= 6:
        return "poor", "Replace the placeholder contribution note with real setup and workflow guidance."
    return "basic", "Expand CONTRIBUTING.md with development setup details."


def quality_code_of_conduct(text: str) -> tuple[str, str]:
    """Assess code of conduct quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create CODE_OF_CONDUCT.md."
    if "contributor covenant" in lowered and "version 2.1" in lowered:
        if "[insert contact method]" in lowered or "[replace:" in lowered:
            return "basic", "Replace the enforcement contact placeholder before publishing."
        return "good", "Keep the current code of conduct."
    if "contributor covenant" in lowered:
        return "basic", "Refresh the code of conduct to the current Contributor Covenant v2.1 template."
    return "poor", "Replace the custom code of conduct with a recognized standard."


def quality_support(text: str) -> tuple[str, str]:
    """Assess support guide quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create SUPPORT.md."
    if all(token in lowered for token in ("github", "issue", "security")):
        return "good", "Keep the current support guide."
    return "basic", "Expand SUPPORT.md with questions, bug reporting, and security guidance."


def quality_codeowners(text: str) -> tuple[str, str]:
    """Assess CODEOWNERS quality."""
    stripped = text.strip()
    if not stripped:
        return "missing", "Create CODEOWNERS."
    if "@" in stripped and "*" in stripped:
        if "[replace:" in stripped.lower():
            return "basic", "Replace CODEOWNERS placeholders with real reviewer handles."
        return "good", "Keep the current CODEOWNERS mapping."
    return "poor", "Replace the placeholder CODEOWNERS content with real ownership patterns."


def quality_funding(text: str) -> tuple[str, str]:
    """Assess FUNDING quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create FUNDING.yml."
    if "github:" in lowered:
        if "[replace:" in lowered:
            return "basic", "Replace the funding username placeholder."
        return "good", "Keep the current funding config."
    return "basic", "Add at least one funding platform or leave a ready-to-activate template."


def quality_issue_templates(repo_root: Path) -> tuple[str, str, list[str]]:
    """Assess issue template quality and return issue template names."""
    templates = list_issue_templates(repo_root)
    if not templates:
        return "missing", "Create YAML issue templates and config.yml.", []
    names = [path.name.lower() for path in templates]
    bug_exists = any("bug" in name for name in names)
    feature_exists = any("feature" in name for name in names)
    config_path = repo_root / ".github" / "ISSUE_TEMPLATE" / "config.yml"
    config_text = safe_read_text(config_path).lower()
    markdown_only = all(path.suffix.lower() == ".md" for path in templates if path.name.lower() != "config.yml")
    if bug_exists and feature_exists and "blank_issues_enabled: false" in config_text:
        if markdown_only:
            return "outdated", "Upgrade markdown issue templates to YAML forms.", names
        return "good", "Keep the current issue templates.", names
    if markdown_only:
        return "outdated", "Replace markdown issue templates with YAML forms and disable blank issues.", names
    return "basic", "Add missing bug/feature forms and disable blank issues.", names


def quality_pr_template(text: str) -> tuple[str, str]:
    """Assess PR template quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create a PR template."
    visible_checks = lowered.count("- [ ]")
    if visible_checks >= 4 and "type of change" in lowered and "testing" in lowered:
        return "good", "Keep the current PR template."
    if "<!--" in lowered or "html" in lowered:
        return "basic", "Replace hidden comment prompts with visible markdown sections."
    return "basic", "Add visible change-type and testing checklists."


def quality_discussion_templates(paths: list[Path]) -> tuple[str, str]:
    """Assess discussion template coverage."""
    if not paths:
        return "missing", "Create discussion templates when discussion categories are known."
    if any(path.suffix.lower() == ".md" for path in paths):
        return "outdated", "Replace markdown discussion templates with YAML category forms."
    return "good", "Keep the current discussion templates."


def quality_gitattributes(text: str) -> tuple[str, str]:
    """Assess .gitattributes quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create .gitattributes for stable language-bar behavior."
    if "linguist" in lowered:
        return "good", "Keep the current Linguist overrides."
    return "basic", "Add Linguist overrides to .gitattributes."


def quality_devcontainer(text: str) -> tuple[str, str]:
    """Assess devcontainer quality."""
    if not text.strip():
        return "missing", "Create a devcontainer for contributor onboarding."
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return "poor", "Fix the invalid devcontainer.json."
    if payload.get("image") and payload.get("postCreateCommand"):
        return "good", "Keep the current devcontainer."
    return "basic", "Add a base image and postCreateCommand to devcontainer.json."


def quality_dependabot(text: str) -> tuple[str, str]:
    """Assess Dependabot config quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create dependabot.yml."
    if "version: 2" in lowered and "updates:" in lowered:
        return "good", "Keep the current Dependabot config."
    return "poor", "Replace the invalid Dependabot config."


def quality_release_yml(text: str) -> tuple[str, str]:
    """Assess release.yml quality."""
    if not text.strip():
        return "missing", "Create release.yml."
    if "categories:" in text and "changelog:" in text:
        return "good", "Keep the current release config."
    return "basic", "Refresh release.yml to the deterministic canonical template."


def quality_ci(paths: list[Path], repo_root: Path) -> tuple[str, str]:
    """Assess CI workflow coverage."""
    if not paths:
        return "missing", "Create a basic CI workflow."
    ci_path = next((path for path in paths if path.name.lower() == "ci.yml"), paths[0])
    text = safe_read_text(ci_path).lower()
    if any(token in text for token in ("markdownlint", "ruff", "eslint", "cargo clippy", "go vet", "yamllint", "unittest")):
        return "good", "Keep the current CI workflow."
    return "basic", "Add at least one lint or test step to CI."


def inferred_description(metadata: dict[str, Any], cached_context: dict[str, Any]) -> str:
    """Return repo description from metadata or cache."""
    description = str(metadata.get("description") or cached_context.get("description") or "").strip()
    return description


def has_license(repo_root: Path) -> bool:
    """Return whether a license file exists."""
    return any((repo_root / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"))


def support_url(repo_slug: str, has_discussions: bool) -> str:
    """Return the support URL for generated files."""
    if repo_slug and "/" in repo_slug and has_discussions:
        return f"https://github.com/{repo_slug}/discussions"
    if repo_slug and "/" in repo_slug:
        return f"https://github.com/{repo_slug}/issues"
    return ""


def issue_template_url(repo_slug: str, template: str) -> str:
    """Return the issue creation URL when available."""
    if repo_slug and "/" in repo_slug:
        return f"https://github.com/{repo_slug}/issues/new?template={template}"
    return "https://github.com/OWNER/REPO/issues"


def project_name(repo_root: Path, metadata: dict[str, Any]) -> str:
    """Return the current project display name."""
    readme_text, _ = load_readme(repo_root)
    for line in readme_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return str(metadata.get("name") or repo_root.name).strip() or repo_root.name


def issue_template_options(repo_root: Path, repo_type: str) -> list[str]:
    """Return bug-template fields by repo type."""
    options = []
    if repo_type in {"CLI Tool", "Skill/Plugin"}:
        options.append("command")
    if repo_type in {"Library/Package", "CLI Tool", "API/Service"}:
        options.append("version")
    if repo_type in {"Application", "API/Service"}:
        options.append("environment")
    return options


def workflow_type(repo_type: str, primary_language: str, repo_root: Path) -> str:
    """Choose the simplest workflow template."""
    language = primary_language.lower()
    if repo_type == "Skill/Plugin" or language == "markdown":
        return "markdown"
    if language == "python":
        return "python"
    if language in {"javascript", "typescript"}:
        return "node"
    if language == "rust":
        return "rust"
    if language == "go":
        return "go"
    return "mixed"


def devcontainer_image(primary_language: str) -> str:
    """Return the preferred devcontainer image."""
    mapping = {
        "javascript": "mcr.microsoft.com/devcontainers/javascript-node",
        "typescript": "mcr.microsoft.com/devcontainers/javascript-node",
        "python": "mcr.microsoft.com/devcontainers/python",
        "rust": "mcr.microsoft.com/devcontainers/rust",
        "go": "mcr.microsoft.com/devcontainers/go",
        "java": "mcr.microsoft.com/devcontainers/java",
    }
    return mapping.get(primary_language.lower(), "mcr.microsoft.com/devcontainers/base:ubuntu")


def post_create_command(repo_root: Path, primary_language: str) -> str:
    """Return a deterministic postCreateCommand."""
    if primary_language.lower() == "python":
        if (repo_root / "requirements.txt").exists():
            return "python -m pip install -r requirements.txt"
        if (repo_root / "pyproject.toml").exists():
            return "python -m pip install -e ."
    if primary_language.lower() in {"javascript", "typescript"} and (repo_root / "package.json").exists():
        return "npm install"
    if primary_language.lower() == "rust" and (repo_root / "Cargo.toml").exists():
        return "cargo fetch"
    if primary_language.lower() == "go" and (repo_root / "go.mod").exists():
        return "go mod download"
    return "echo 'Dev container ready'"


def detect_ecosystems(repo_root: Path) -> list[tuple[str, str]]:
    """Return Dependabot ecosystems and directories."""
    ecosystems: list[tuple[str, str]] = []
    if (repo_root / "package.json").exists():
        ecosystems.append(("npm", "/"))
    if (repo_root / "requirements.txt").exists() or (repo_root / "pyproject.toml").exists() or (repo_root / "setup.py").exists():
        ecosystems.append(("pip", "/"))
    if (repo_root / "Cargo.toml").exists():
        ecosystems.append(("cargo", "/"))
    if (repo_root / "go.mod").exists():
        ecosystems.append(("gomod", "/"))
    if (repo_root / "pom.xml").exists():
        ecosystems.append(("maven", "/"))
    if (repo_root / "build.gradle").exists():
        ecosystems.append(("gradle", "/"))
    if list_workflows(repo_root):
        ecosystems.append(("github-actions", "/"))
    seen: set[tuple[str, str]] = set()
    ordered: list[tuple[str, str]] = []
    for entry in ecosystems:
        if entry not in seen:
            seen.add(entry)
            ordered.append(entry)
    return ordered


def gh_discussion_categories(repo_slug: str) -> list[dict[str, str]]:
    """Fetch discussion categories when gh auth is available."""
    if not gh_auth_ok() or "/" not in repo_slug:
        return []
    owner, repo = repo_slug.split("/", 1)
    query = (
        "query($owner: String!, $repo: String!) { "
        "repository(owner: $owner, name: $repo) { "
        "discussionCategories(first: 20) { nodes { id name slug isAnswerable } } } }"
    )
    result = run_command(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"repo={repo}",
        ],
        check=False,
    )
    if result.returncode != 0:
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    nodes = (((payload.get("data") or {}).get("repository") or {}).get("discussionCategories") or {}).get("nodes") or []
    categories: list[dict[str, str]] = []
    for node in nodes:
        categories.append(
            {
                "name": str(node.get("name") or "").strip(),
                "slug": str(node.get("slug") or "").strip(),
                "is_answerable": bool(node.get("isAnswerable")),
            }
        )
    return categories


def fetch_contributor_covenant() -> str:
    """Fetch Contributor Covenant text with a local fallback."""
    if have_command("gh"):
        result = run_command(["gh", "api", "codes_of_conduct/contributor_covenant", "--jq", ".body"], check=False)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    request = urllib.request.Request(
        "https://api.github.com/codes_of_conduct/contributor_covenant",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "legends-github-community-runner"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            body = str(payload.get("body") or "").strip()
            if body:
                return body
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        pass
    return CONTRIBUTOR_COVENANT_FALLBACK.strip()


def canonical_code_of_conduct(enforcement_email: str) -> str:
    """Return Contributor Covenant text with contact substituted."""
    contact = enforcement_email.strip() or "[REPLACE: your-email@example.com]"
    body = fetch_contributor_covenant().replace("[INSERT CONTACT METHOD]", contact)
    body = body.replace("YOUR_EMAIL", contact)
    body = body.replace("\r\n", "\n").strip()
    if "version 2.1" not in body.lower():
        body = CONTRIBUTOR_COVENANT_FALLBACK.replace("[REPLACE: your-email@example.com]", contact).strip()
    return body + "\n"


def generate_contributing(snapshot: dict[str, Any]) -> str:
    """Render CONTRIBUTING.md."""
    repo = snapshot["project_name"]
    repo_slug = snapshot["repo"]
    bug_url = issue_template_url(repo_slug, "bug_report.yml")
    feature_url = issue_template_url(repo_slug, "feature_request.yml")
    support_link = support_url(repo_slug, snapshot["has_discussions"])
    setup_line = "Run the relevant setup or install command for this repository before contributing."
    if snapshot["primary_language"] == "Python":
        setup_line = "Set up a Python environment and run `python -m unittest discover -s tests -v` before opening a PR."
    elif snapshot["primary_language"] in {"JavaScript", "TypeScript"}:
        setup_line = "Install dependencies with `npm install` and run the project's lint/test commands before opening a PR."
    elif snapshot["repo_type"] == "Skill/Plugin":
        setup_line = "Test the affected skill against a real repository and verify installed-state behavior before opening a PR."
    return (
        f"# Contributing to {repo}\n\n"
        "Thank you for contributing. This guide explains how to report bugs, propose improvements, and send pull requests.\n\n"
        "## Reporting Bugs\n\n"
        f"Open a [Bug Report]({bug_url}) with clear reproduction steps, expected behavior, and actual behavior.\n\n"
        "## Requesting Features\n\n"
        f"Open a [Feature Request]({feature_url}) and describe the problem you are trying to solve.\n\n"
        "## Development Setup\n\n"
        f"- {setup_line}\n"
        "- Keep changes focused on one logical improvement per pull request.\n"
        "- Update docs and tests when behavior changes.\n\n"
        "## Pull Request Workflow\n\n"
        "1. Fork the repository and create a branch from `main`.\n"
        "2. Make the smallest coherent change that solves the problem.\n"
        "3. Run the relevant validation commands locally.\n"
        "4. Open a pull request with a clear summary and testing notes.\n\n"
        "## Code Style\n\n"
        "- Follow the existing conventions already present in the repository.\n"
        "- Prefer small diffs over broad rewrites.\n"
        "- Do not commit credentials, API keys, or local environment files.\n\n"
        "## Code of Conduct\n\n"
        f"Please follow the [Code of Conduct]({CODE_OF_CONDUCT_FILE}).\n\n"
        "## Support\n\n"
        f"Use [Support]({support_link or 'SUPPORT.md'}) for questions and troubleshooting.\n"
    )


def generate_support(snapshot: dict[str, Any]) -> str:
    """Render SUPPORT.md."""
    repo_slug = snapshot["repo"]
    discussions = support_url(repo_slug, True) if snapshot["has_discussions"] else ""
    issues = f"https://github.com/{repo_slug}/issues" if repo_slug and "/" in repo_slug else "GitHub Issues"
    bug_url = issue_template_url(repo_slug, "bug_report.yml")
    feature_url = issue_template_url(repo_slug, "feature_request.yml")
    security_target = "See SECURITY.md for private vulnerability reporting instructions."
    return (
        "# Support\n\n"
        "## Getting Help\n\n"
        "Use the right channel so maintainers can respond efficiently.\n\n"
        "### Questions and Discussion\n\n"
        f"{f'Use [GitHub Discussions]({discussions}) for questions, troubleshooting, and general conversation.' if discussions else 'Use the project issue tracker for support questions until Discussions is enabled.'}\n\n"
        "### Bug Reports\n\n"
        f"Use the [bug report template]({bug_url}) for confirmed bugs and reproducible failures.\n\n"
        "### Feature Requests\n\n"
        f"Use the [feature request template]({feature_url}) for feature ideas and workflow improvements.\n\n"
        "### Security Issues\n\n"
        f"{security_target}\n\n"
        "## Response Expectations\n\n"
        "- Questions and troubleshooting requests may take longer than confirmed bug reports.\n"
        "- Please include environment details, error output, and the command or workflow that failed.\n"
        f"- Keep duplicate reports to a minimum by checking existing issues first: {issues}.\n"
    )


def generate_codeowners(snapshot: dict[str, Any]) -> str:
    """Render CODEOWNERS."""
    owner = snapshot["owner_handle"] or "[REPLACE: @your-team]"
    return f"# Global owner for this repository\n* {owner}\n"


def generate_funding(snapshot: dict[str, Any]) -> str:
    """Render FUNDING.yml."""
    owner = snapshot["owner_username"] or "[REPLACE: your-github-username]"
    github_line = f"github: [{owner}]"
    if owner.startswith("[REPLACE:"):
        github_line = f"# {github_line}"
    return (
        "# .github/FUNDING.yml\n"
        "# Uncomment the platforms you use:\n"
        f"{github_line}\n"
        "# patreon: # Replace with your Patreon username\n"
        "# open_collective: # Replace with your Open Collective username\n"
        "# ko_fi: # Replace with your Ko-fi username\n"
        "# custom: [\"https://example.com/donate\"]\n"
    )


def generate_bug_template(snapshot: dict[str, Any]) -> str:
    """Render bug_report.yml."""
    body = [
        "name: Bug Report",
        "description: Report a bug or unexpected behavior",
        'title: "[Bug]: "',
        'labels: ["bug"]',
        "body:",
        "  - type: markdown",
        "    attributes:",
        '      value: "Thanks for reporting. Please fill in the details below so we can reproduce the problem."',
        "  - type: textarea",
        "    id: description",
        "    attributes:",
        "      label: Bug Description",
        "      description: What happened?",
        "      placeholder: Describe the bug...",
        "    validations:",
        "      required: true",
        "  - type: textarea",
        "    id: reproduction",
        "    attributes:",
        "      label: Steps to Reproduce",
        "      description: How can we reproduce this?",
        "      value: |",
        "        1.",
        "        2.",
        "        3.",
        "    validations:",
        "      required: true",
        "  - type: textarea",
        "    id: expected",
        "    attributes:",
        "      label: Expected Behavior",
        "      description: What should have happened?",
        "    validations:",
        "      required: true",
    ]
    options = issue_template_options(snapshot["repo_root"], snapshot["repo_type"])
    if "command" in options:
        body.extend(
            [
                "  - type: input",
                "    id: command",
                "    attributes:",
                "      label: Command Used",
                "      placeholder: e.g., github audit --path /repo",
            ]
        )
    if "version" in options:
        body.extend(
            [
                "  - type: input",
                "    id: version",
                "    attributes:",
                "      label: Version",
                "      placeholder: e.g., 1.0.0",
            ]
        )
    if "environment" in options:
        body.extend(
            [
                "  - type: input",
                "    id: environment",
                "    attributes:",
                "      label: Environment",
                "      placeholder: e.g., Windows 11, Chrome 126, Node 22",
            ]
        )
    body.extend(
        [
            "  - type: dropdown",
            "    id: os",
            "    attributes:",
            "      label: Operating System",
            "      options:",
            "        - Windows",
            "        - macOS",
            "        - Linux",
            "        - Other",
            "  - type: textarea",
            "    id: additional",
            "    attributes:",
            "      label: Additional Context",
            "      description: Error output, screenshots, links, or anything else that helps.",
        ]
    )
    return "\n".join(body) + "\n"


def generate_feature_template() -> str:
    """Render feature_request.yml."""
    return (
        "name: Feature Request\n"
        "description: Suggest a new feature or improvement\n"
        'title: "[Feature]: "\n'
        'labels: ["enhancement"]\n'
        "body:\n"
        "  - type: textarea\n"
        "    id: problem\n"
        "    attributes:\n"
        "      label: Problem Statement\n"
        "      description: What problem does this solve?\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: solution\n"
        "    attributes:\n"
        "      label: Proposed Solution\n"
        "      description: How should this work?\n"
        "    validations:\n"
        "      required: true\n"
        "  - type: textarea\n"
        "    id: alternatives\n"
        "    attributes:\n"
        "      label: Alternatives Considered\n"
        "      description: Other approaches or workarounds you have considered.\n"
    )


def generate_issue_config(snapshot: dict[str, Any]) -> str:
    """Render config.yml for issue templates."""
    lines = ["blank_issues_enabled: false"]
    url = support_url(snapshot["repo"], snapshot["has_discussions"])
    if url:
        label = "Questions & Help" if snapshot["has_discussions"] else "Support"
        about = (
            "Use Discussions for questions and troubleshooting."
            if snapshot["has_discussions"]
            else "Use this support link for questions before opening a new issue."
        )
        lines.extend(
            [
                "contact_links:",
                f"  - name: {label}",
                f"    url: {url}",
                f"    about: {about}",
            ]
        )
    return "\n".join(lines) + "\n"


def generate_pr_template() -> str:
    """Render pull request template."""
    return (
        "## Summary\n\n"
        "Briefly describe what changed and why.\n\n"
        "## Type of Change\n\n"
        "- [ ] Bug fix\n"
        "- [ ] New feature\n"
        "- [ ] Breaking change\n"
        "- [ ] Documentation update\n"
        "- [ ] Maintenance / tooling update\n\n"
        "## Testing\n\n"
        "- [ ] Tests pass locally\n"
        "- [ ] Relevant manual checks completed\n"
        "- [ ] Documentation updated if behavior changed\n\n"
        "## Checklist\n\n"
        "- [ ] Changes are scoped and focused\n"
        "- [ ] No credentials or local env files were committed\n"
        "- [ ] I reviewed the diff before opening this PR\n"
    )


def generate_discussion_templates(snapshot: dict[str, Any]) -> dict[str, str]:
    """Render discussion templates when categories are known."""
    templates: dict[str, str] = {}
    for category in snapshot["discussion_categories"]:
        slug = category["slug"]
        name = category["name"]
        if not slug:
            continue
        prompt = "What are you trying to accomplish?" if category.get("is_answerable") else "What should the community discuss?"
        templates[f".github/DISCUSSION_TEMPLATE/{slug}.yml"] = (
            f'title: "[{name}] "\n'
            f'labels: ["discussion:{slug}"]\n'
            "body:\n"
            "  - type: markdown\n"
            "    attributes:\n"
            "      value: |\n"
            "        Share the context, what you have already tried, and the outcome you need.\n"
            "  - type: textarea\n"
            "    id: details\n"
            "    attributes:\n"
            "      label: Details\n"
            f"      description: {prompt}\n"
            "      placeholder: Add the relevant details here.\n"
            "    validations:\n"
            "      required: true\n"
            "  - type: input\n"
            "    id: goal\n"
            "    attributes:\n"
            "      label: Desired Outcome\n"
            "      description: What would a helpful answer or resolution look like?\n"
        )
    return templates


def generate_gitattributes(snapshot: dict[str, Any]) -> str:
    """Render .gitattributes."""
    lines = [
        "# .gitattributes - GitHub Linguist overrides for accurate language detection",
        "",
        "# Generated and vendored files",
        "*.min.js linguist-generated",
        "*.min.css linguist-generated",
        "dist/** linguist-generated",
        "vendor/** linguist-vendored",
        "third_party/** linguist-vendored",
        "",
    ]
    if snapshot["repo_type"] == "Skill/Plugin" or snapshot["primary_language"] == "Markdown":
        lines.extend(
            [
                "# Markdown-heavy skill and documentation repo",
                "*.sh linguist-documentation",
                "*.ps1 linguist-documentation",
                "install.* linguist-documentation",
                "*.md linguist-detectable",
            ]
        )
    else:
        lines.extend(
            [
                "# Documentation and generated output",
                "docs/** linguist-documentation",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def generate_devcontainer(snapshot: dict[str, Any]) -> str:
    """Render devcontainer.json."""
    payload = {
        "name": f"{snapshot['project_name']} Dev",
        "image": devcontainer_image(snapshot["primary_language"]),
        "features": {},
        "postCreateCommand": post_create_command(snapshot["repo_root"], snapshot["primary_language"]),
        "customizations": {
            "vscode": {
                "extensions": [
                    "yzhang.markdown-all-in-one",
                    "DavidAnson.vscode-markdownlint",
                ]
            }
        },
    }
    if snapshot["primary_language"] == "Python":
        payload["customizations"]["vscode"]["extensions"].append("ms-python.python")
    if snapshot["primary_language"] in {"JavaScript", "TypeScript"}:
        payload["customizations"]["vscode"]["extensions"].append("dbaeumer.vscode-eslint")
    return json.dumps(payload, indent=2) + "\n"


def generate_dependabot(snapshot: dict[str, Any]) -> str:
    """Render dependabot.yml."""
    ecosystems = detect_ecosystems(snapshot["repo_root"])
    if not ecosystems:
        ecosystems = [("github-actions", "/")]
    lines = ["version: 2", "updates:"]
    for ecosystem, directory in ecosystems:
        lines.extend(
            [
                f'  - package-ecosystem: "{ecosystem}"',
                f'    directory: "{directory}"',
                "    schedule:",
                '      interval: "weekly"',
                "    open-pull-requests-limit: 5",
            ]
        )
    return "\n".join(lines) + "\n"


def generate_ci_workflow(snapshot: dict[str, Any]) -> str:
    """Render a basic CI workflow."""
    choice = workflow_type(snapshot["repo_type"], snapshot["primary_language"], snapshot["repo_root"])
    if choice == "python":
        return (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  lint:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: \"3.12\"\n"
            "      - run: python -m pip install ruff\n"
            "      - run: ruff check .\n"
        )
    if choice == "node":
        return (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  lint:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-node@v4\n"
            "        with:\n"
            "          node-version: 22\n"
            "      - run: npm install\n"
            "      - run: npm run lint --if-present\n"
        )
    if choice == "rust":
        return (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  checks:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - run: cargo fmt --check\n"
            "      - run: cargo clippy --all-targets --all-features -- -D warnings\n"
        )
    if choice == "go":
        return (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  checks:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-go@v5\n"
            "        with:\n"
            "          go-version: stable\n"
            "      - run: go vet ./...\n"
        )
    if choice == "mixed":
        return (
            "name: CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  lint:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Lint Markdown\n"
            "        uses: DavidAnson/markdownlint-cli2-action@v19\n"
            "        with:\n"
            "          globs: \"**/*.md\"\n"
        )
    return (
        "name: CI\n\n"
        "on:\n"
        "  push:\n"
        "    branches: [main]\n"
        "  pull_request:\n"
        "    branches: [main]\n\n"
        "jobs:\n"
        "  lint:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - name: Lint Markdown\n"
        "        uses: DavidAnson/markdownlint-cli2-action@v19\n"
        "        with:\n"
        "          globs: \"**/*.md\"\n"
    )


def write_if_changed(path: Path, content: str) -> bool:
    """Write a file when content changes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = safe_read_text(path)
    if existing == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def collect_placeholders(repo_root: Path, targets: list[str]) -> list[dict[str, Any]]:
    """Collect placeholder markers from generated files."""
    pattern = re.compile(r"\[REPLACE:[^\]]+\]")
    placeholders: list[dict[str, Any]] = []
    for relative in targets:
        path = repo_root / relative
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for match in pattern.finditer(line):
                placeholders.append(
                    {
                        "file": relative.replace("\\", "/"),
                        "line": line_no,
                        "placeholder": match.group(0),
                        "description": "Replace the placeholder with repo-specific information.",
                    }
                )
    return placeholders


def community_scorecard(snapshot: dict[str, Any]) -> tuple[dict[str, bool], int]:
    """Return GitHub Community Standards item states and completion count."""
    items = {
        "Description": bool(snapshot["description"]),
        "README": snapshot["readme_exists"],
        "Code of Conduct": snapshot["files"][CODE_OF_CONDUCT_FILE]["exists"],
        "Contributing": snapshot["files"][CONTRIBUTING_FILE]["exists"],
        "License": snapshot["license_exists"],
        "Security Policy": snapshot["security_exists"],
        "Issue Templates": snapshot["files"][ISSUE_TEMPLATES_FILE]["exists"],
        "Pull Request Template": snapshot["files"][PR_TEMPLATE_FILE]["exists"],
    }
    return items, sum(1 for value in items.values() if value)


def analyze_files(repo_root: Path, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Analyze file existence and quality."""
    files: dict[str, dict[str, Any]] = {}
    contributing_path = find_contributing(repo_root)
    conduct_path = find_code_of_conduct(repo_root)
    support_path = find_support(repo_root)
    codeowners_path = find_codeowners(repo_root)
    funding_path = repo_root / ".github" / "FUNDING.yml"
    pr_template_path = find_pr_template(repo_root)
    gitattributes_path = repo_root / ".gitattributes"
    devcontainer_path = repo_root / ".devcontainer" / "devcontainer.json"
    dependabot_path = repo_root / ".github" / "dependabot.yml"
    release_yml_path = repo_root / ".github" / "release.yml"
    issue_paths = list_issue_templates(repo_root)
    discussion_paths = list_discussion_templates(repo_root)
    workflow_paths = list_workflows(repo_root)

    for label, path, assessor in [
        (CONTRIBUTING_FILE, contributing_path, quality_contributing),
        (CODE_OF_CONDUCT_FILE, conduct_path, quality_code_of_conduct),
        (SUPPORT_FILE, support_path, quality_support),
        (CODEOWNERS_FILE, codeowners_path, quality_codeowners),
        (FUNDING_FILE, funding_path if funding_path.exists() else None, quality_funding),
        (PR_TEMPLATE_FILE, pr_template_path, quality_pr_template),
        (GITATTRIBUTES_FILE, gitattributes_path if gitattributes_path.exists() else None, quality_gitattributes),
        (DEVCONTAINER_FILE, devcontainer_path if devcontainer_path.exists() else None, quality_devcontainer),
        (DEPENDABOT_FILE, dependabot_path if dependabot_path.exists() else None, quality_dependabot),
        (RELEASE_YML_FILE, release_yml_path if release_yml_path.exists() else None, quality_release_yml),
    ]:
        text = safe_read_text(path) if path else ""
        quality, action = assessor(text)
        files[label] = {
            "path": str(path.relative_to(repo_root)).replace("\\", "/") if path else label,
            "exists": bool(path and path.exists()),
            "quality": quality,
            "action": action,
        }

    issue_quality, issue_action, issue_names = quality_issue_templates(repo_root)
    files[ISSUE_TEMPLATES_FILE] = {
        "path": ISSUE_TEMPLATES_FILE,
        "exists": bool(issue_paths),
        "quality": issue_quality,
        "action": issue_action,
        "templates": issue_names,
    }
    discussion_quality, discussion_action = quality_discussion_templates(discussion_paths)
    files[DISCUSSION_TEMPLATES_FILE] = {
        "path": DISCUSSION_TEMPLATES_FILE,
        "exists": bool(discussion_paths),
        "quality": discussion_quality,
        "action": discussion_action,
        "templates": [path.name for path in discussion_paths],
    }
    ci_quality, ci_action = quality_ci(workflow_paths, repo_root)
    files[CI_WORKFLOW_FILE] = {
        "path": CI_WORKFLOW_FILE,
        "exists": bool(workflow_paths),
        "quality": ci_quality,
        "action": ci_action,
        "templates": [str(path.relative_to(repo_root)).replace("\\", "/") for path in workflow_paths],
    }
    return files


def build_snapshot(repo_root: Path) -> dict[str, Any]:
    """Collect repo signals for community planning."""
    cached_context = read_repo_cache(repo_root, "repo-context.json") or {}
    legal_data = read_repo_cache(repo_root, "legal-data.json") or {}
    repo_slug = str(cached_context.get("repo") or repo_slug_from_git(repo_root) or repo_root.name)
    metadata = gh_repo_view(repo_slug) if "/" in repo_slug else {}
    if metadata is None:
        metadata = {}
    repo_type = str(cached_context.get("repo_type") or detect_repo_type(repo_root))
    primary_language = detect_primary_language(repo_root, cached_context, metadata)
    intent = detect_intent(cached_context, repo_type)
    owner_username = repo_slug.split("/", 1)[0] if "/" in repo_slug else ""
    discussion_categories = gh_discussion_categories(repo_slug)
    has_discussions = bool(metadata.get("hasDiscussionsEnabled")) or bool(cached_context.get("has_discussions"))
    if discussion_categories:
        has_discussions = True
    project = project_name(repo_root, metadata)
    existing_conduct = safe_read_text(find_code_of_conduct(repo_root) or repo_root / CODE_OF_CONDUCT_FILE)
    enforcement_email = extract_first_email(existing_conduct) or git_config_value(repo_root, "user.email")
    snapshot = {
        "repo": repo_slug,
        "repo_root": repo_root,
        "repo_type": repo_type,
        "primary_language": primary_language,
        "intent": intent,
        "project_name": project,
        "description": inferred_description(metadata, cached_context),
        "readme_exists": readme_exists(repo_root),
        "license_exists": has_license(repo_root),
        "security_exists": bool(find_security(repo_root)) or bool(legal_data.get("security_md_exists")),
        "has_discussions": has_discussions,
        "discussion_categories": discussion_categories,
        "owner_username": owner_username,
        "owner_handle": f"@{owner_username}" if owner_username else "",
        "enforcement_email": enforcement_email,
        "metadata": metadata,
        "cached_context": cached_context,
        "legal_data": legal_data,
        "warnings": [],
    }
    if "/" not in repo_slug:
        snapshot["warnings"].append("No GitHub remote detected. Community planning is using local files only.")
    if has_discussions and not discussion_categories:
        snapshot["warnings"].append("Discussions are enabled, but category metadata was not available. Discussion templates will be skipped.")
    return snapshot


def generated_content(snapshot: dict[str, Any]) -> dict[str, str]:
    """Return canonical file contents for deterministic write mode."""
    content = {
        CONTRIBUTING_FILE: generate_contributing(snapshot),
        CODE_OF_CONDUCT_FILE: canonical_code_of_conduct(snapshot["enforcement_email"]),
        SUPPORT_FILE: generate_support(snapshot),
        CODEOWNERS_FILE: generate_codeowners(snapshot),
        FUNDING_FILE: generate_funding(snapshot),
        ".github/ISSUE_TEMPLATE/bug_report.yml": generate_bug_template(snapshot),
        ".github/ISSUE_TEMPLATE/feature_request.yml": generate_feature_template(),
        ".github/ISSUE_TEMPLATE/config.yml": generate_issue_config(snapshot),
        PR_TEMPLATE_FILE: generate_pr_template(),
        GITATTRIBUTES_FILE: generate_gitattributes(snapshot),
        DEVCONTAINER_FILE: generate_devcontainer(snapshot),
        DEPENDABOT_FILE: generate_dependabot(snapshot),
        RELEASE_YML_FILE: CANONICAL_RELEASE_YML,
        CI_WORKFLOW_FILE: generate_ci_workflow(snapshot),
    }
    if snapshot["has_discussions"] and snapshot["discussion_categories"]:
        content.update(generate_discussion_templates(snapshot))
    return content


def planned_writes(snapshot: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Return planned write operations and skip reasons."""
    files = snapshot["files"]
    writes: list[dict[str, Any]] = []
    skipped: dict[str, str] = {}
    content = generated_content(snapshot)

    def schedule(path: str, reason: str) -> None:
        writes.append({"path": path, "reason": reason})

    for label, quality_key in [
        (CONTRIBUTING_FILE, CONTRIBUTING_FILE),
        (CODE_OF_CONDUCT_FILE, CODE_OF_CONDUCT_FILE),
        (SUPPORT_FILE, SUPPORT_FILE),
        (CODEOWNERS_FILE, CODEOWNERS_FILE),
        (FUNDING_FILE, FUNDING_FILE),
        (PR_TEMPLATE_FILE, PR_TEMPLATE_FILE),
        (GITATTRIBUTES_FILE, GITATTRIBUTES_FILE),
        (DEVCONTAINER_FILE, DEVCONTAINER_FILE),
        (DEPENDABOT_FILE, DEPENDABOT_FILE),
        (RELEASE_YML_FILE, RELEASE_YML_FILE),
        (CI_WORKFLOW_FILE, CI_WORKFLOW_FILE),
    ]:
        quality = files[quality_key]["quality"]
        if quality in {"missing", "poor", "basic", "outdated"}:
            schedule(label, files[quality_key]["action"])
        else:
            skipped[label] = "Already in good shape."

    issue_quality = files[ISSUE_TEMPLATES_FILE]["quality"]
    if issue_quality in {"missing", "basic", "outdated"}:
        for relative in (".github/ISSUE_TEMPLATE/bug_report.yml", ".github/ISSUE_TEMPLATE/feature_request.yml", ".github/ISSUE_TEMPLATE/config.yml"):
            schedule(relative, files[ISSUE_TEMPLATES_FILE]["action"])
    else:
        skipped[ISSUE_TEMPLATES_FILE] = "Issue templates are already in good shape."

    discussion_quality = files[DISCUSSION_TEMPLATES_FILE]["quality"]
    if snapshot["has_discussions"] and snapshot["discussion_categories"]:
        if discussion_quality in {"missing", "basic", "outdated", "poor"}:
            for relative in sorted(path for path in content if path.startswith(".github/DISCUSSION_TEMPLATE/")):
                schedule(relative, "Create discussion templates for known discussion categories.")
        else:
            skipped[DISCUSSION_TEMPLATES_FILE] = "Discussion templates are already in good shape."
    elif snapshot["has_discussions"]:
        skipped[DISCUSSION_TEMPLATES_FILE] = "Discussions are enabled but category metadata was unavailable."
    else:
        skipped[DISCUSSION_TEMPLATES_FILE] = "Discussions are disabled, so no discussion templates are needed."

    skipped[SECURITY_FILE] = "Handled by github-legal."
    if not snapshot["description"]:
        skipped[DESCRIPTION_FILE] = "Repository description is handled by github-meta."
    return writes, skipped


def predicted_after_scorecard(snapshot: dict[str, Any], writes: list[dict[str, Any]]) -> tuple[dict[str, bool], int]:
    """Return post-write community scorecard prediction."""
    after, _ = community_scorecard(snapshot)
    write_set = {entry["path"] for entry in writes}
    if CONTRIBUTING_FILE in write_set:
        after["Contributing"] = True
    if CODE_OF_CONDUCT_FILE in write_set:
        after["Code of Conduct"] = True
    if any(path.startswith(".github/ISSUE_TEMPLATE/") for path in write_set):
        after["Issue Templates"] = True
    if PR_TEMPLATE_FILE in write_set:
        after["Pull Request Template"] = True
    return after, sum(1 for value in after.values() if value)


def build_community_payload(repo_root: Path) -> dict[str, Any]:
    """Build deterministic community recommendations."""
    snapshot = build_snapshot(repo_root)
    snapshot["files"] = analyze_files(repo_root, snapshot)
    before_items, before_count = community_scorecard(snapshot)
    writes, skipped = planned_writes(snapshot)
    after_items, after_count = predicted_after_scorecard(snapshot, writes)
    placeholders = []
    if not snapshot["enforcement_email"]:
        placeholders.append(
            {
                "file": CODE_OF_CONDUCT_FILE,
                "line": 0,
                "placeholder": "[REPLACE: your-email@example.com]",
                "description": "Set the enforcement contact email for the code of conduct.",
            }
        )
    if not snapshot["owner_username"]:
        placeholders.append(
            {
                "file": FUNDING_FILE,
                "line": 0,
                "placeholder": "[REPLACE: your-github-username]",
                "description": "Set the GitHub Sponsors username if funding is enabled.",
            }
        )
    if not snapshot["owner_handle"]:
        placeholders.append(
            {
                "file": CODEOWNERS_FILE,
                "line": 0,
                "placeholder": "[REPLACE: @your-team]",
                "description": "Set the CODEOWNERS reviewer handle.",
            }
        )

    bonus_status = {
        "SUPPORT.md": "Exists" if snapshot["files"][SUPPORT_FILE]["exists"] else "Planned" if any(item["path"] == SUPPORT_FILE for item in writes) else "Skipped",
        "CODEOWNERS": "Exists" if snapshot["files"][CODEOWNERS_FILE]["exists"] else "Planned" if any(item["path"] == CODEOWNERS_FILE for item in writes) else "Skipped",
        "FUNDING.yml": "Exists" if snapshot["files"][FUNDING_FILE]["exists"] else "Planned" if any(item["path"] == FUNDING_FILE for item in writes) else "Skipped",
        ".gitattributes": "Exists" if snapshot["files"][GITATTRIBUTES_FILE]["exists"] else "Planned" if any(item["path"] == GITATTRIBUTES_FILE for item in writes) else "Skipped",
        "CI workflow": "Exists" if snapshot["files"][CI_WORKFLOW_FILE]["exists"] else "Planned" if any(item["path"] == CI_WORKFLOW_FILE for item in writes) else "Skipped",
        "devcontainer.json": "Exists" if snapshot["files"][DEVCONTAINER_FILE]["exists"] else "Planned" if any(item["path"] == DEVCONTAINER_FILE for item in writes) else "Skipped",
        "dependabot.yml": "Exists" if snapshot["files"][DEPENDABOT_FILE]["exists"] else "Planned" if any(item["path"] == DEPENDABOT_FILE for item in writes) else "Skipped",
        "release.yml": "Exists" if snapshot["files"][RELEASE_YML_FILE]["exists"] else "Planned" if any(item["path"] == RELEASE_YML_FILE for item in writes) else "Skipped",
        "discussion templates": "Exists" if snapshot["files"][DISCUSSION_TEMPLATES_FILE]["exists"] else "Planned" if any(item["path"].startswith(".github/DISCUSSION_TEMPLATE/") for item in writes) else "Skipped",
    }

    return {
        "cache_type": "community-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": "plan",
        "repo": snapshot["repo"],
        "repo_root": str(repo_root),
        "repo_type": snapshot["repo_type"],
        "intent": snapshot["intent"],
        "primary_language": snapshot["primary_language"],
        "description_present": bool(snapshot["description"]),
        "license_present": snapshot["license_exists"],
        "security_present": snapshot["security_exists"],
        "has_discussions": snapshot["has_discussions"],
        "community_standards_before": before_items,
        "community_standards_after": after_items,
        "scorecard_before": before_count,
        "scorecard_after": after_count,
        "files": snapshot["files"],
        "files_created": [],
        "files_removed": [],
        "files_updated": [],
        "files_skipped": skipped,
        "planned_writes": writes,
        "bonus_status": bonus_status,
        "placeholders": placeholders,
        "warnings": snapshot["warnings"],
        "blocked": [],
    }


def apply_community_plan(repo_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Write planned community files."""
    snapshot = build_snapshot(repo_root)
    snapshot["files"] = analyze_files(repo_root, snapshot)
    content = generated_content(snapshot)
    created: list[str] = []
    removed: list[str] = []
    updated: list[str] = []
    written_targets: list[str] = []
    for entry in payload["planned_writes"]:
        relative = entry["path"]
        if relative not in content:
            continue
        path = repo_root / relative
        existed = path.exists()
        changed = write_if_changed(path, content[relative])
        if not changed:
            continue
        written_targets.append(relative)
        if existed:
            updated.append(relative)
        else:
            created.append(relative)

    discussion_dir = repo_root / ".github" / "DISCUSSION_TEMPLATE"
    if snapshot["has_discussions"] and snapshot["discussion_categories"] and discussion_dir.exists():
        for stale in sorted(discussion_dir.glob("*.md")):
            stale.unlink(missing_ok=True)
            removed.append(str(stale.relative_to(repo_root)).replace("\\", "/"))

    refreshed = build_community_payload(repo_root)
    refreshed["mode"] = "write"
    refreshed["files_created"] = created
    refreshed["files_removed"] = removed
    refreshed["files_updated"] = updated
    refreshed["planned_writes"] = []
    refreshed["placeholders"] = collect_placeholders(repo_root, written_targets)
    return refreshed


def build_community_report(payload: dict[str, Any]) -> str:
    """Render markdown report."""
    def score_line(items: dict[str, bool]) -> str:
        rows = []
        for key, value in items.items():
            rows.append(f"| {key} | {'Yes' if value else 'No'} |")
        return "\n".join(rows)

    file_rows = []
    for key in [
        CONTRIBUTING_FILE,
        CODE_OF_CONDUCT_FILE,
        SUPPORT_FILE,
        CODEOWNERS_FILE,
        FUNDING_FILE,
        ISSUE_TEMPLATES_FILE,
        PR_TEMPLATE_FILE,
        DISCUSSION_TEMPLATES_FILE,
        GITATTRIBUTES_FILE,
        DEVCONTAINER_FILE,
        DEPENDABOT_FILE,
        RELEASE_YML_FILE,
        CI_WORKFLOW_FILE,
    ]:
        info = payload["files"].get(key, {})
        file_rows.append(f"| {key} | {'Yes' if info.get('exists') else 'No'} | {info.get('quality', 'n/a')} | {info.get('action', '')} |")
    warnings = "\n".join(f"- {item}" for item in payload["warnings"]) or "- None"
    placeholders = "\n".join(
        f"- {item['file']} line {item['line'] or '?'}: `{item['placeholder']}`"
        for item in payload["placeholders"]
    ) or "- None"
    planned = "\n".join(f"- `{item['path']}`: {item['reason']}" for item in payload["planned_writes"]) or "- None"
    created = "\n".join(f"- `{item}`" for item in payload["files_created"]) or "- None"
    removed = "\n".join(f"- `{item}`" for item in payload["files_removed"]) or "- None"
    updated = "\n".join(f"- `{item}`" for item in payload["files_updated"]) or "- None"
    return f"""# GitHub Community Report

- **Repository:** {payload['repo']}
- **Generated at:** {payload['timestamp']}
- **Mode:** {payload['mode']}
- **Repo type:** {payload['repo_type']}
- **Intent:** {payload['intent']}

## Community Standards Before

| Item | Present |
|------|---------|
{score_line(payload['community_standards_before'])}
| Completion | {payload['scorecard_before']}/8 |

## Community Standards After

| Item | Present |
|------|---------|
{score_line(payload['community_standards_after'])}
| Completion | {payload['scorecard_after']}/8 |

## File Analysis

| File | Exists? | Quality | Action Needed |
|------|---------|---------|---------------|
{chr(10).join(file_rows)}

## Planned Writes

{planned}

## Files Created

{created}

## Files Updated

{updated}

## Files Removed

{removed}

## Placeholders

{placeholders}

## Warnings

{warnings}
"""


@dataclass
class CommunityBundle:
    """Structured community output."""

    community_data: dict[str, Any]
    report_markdown: str


def run_community(repo_root: Path, write_files: bool = False) -> CommunityBundle:
    """Build or apply deterministic community health work."""
    community_data = build_community_payload(repo_root)
    if write_files:
        community_data = apply_community_plan(repo_root, community_data)
    report_markdown = build_community_report(community_data)
    return CommunityBundle(community_data=community_data, report_markdown=report_markdown)


def write_community_artifacts(repo_root: Path, bundle: CommunityBundle) -> dict[str, str]:
    """Write community cache and report artifacts."""
    slug = slugify(bundle.community_data["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cache_path = write_repo_cache(repo_root, "community-data.json", bundle.community_data)
    report_path = out_dir / "COMMUNITY-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    plan_path = out_dir / "COMMUNITY-PLAN.md"
    planned = bundle.community_data["planned_writes"] or [
        {"path": path, "reason": "written"} for path in (bundle.community_data["files_created"] + bundle.community_data["files_updated"])
    ]
    plan_path.write_text(
        "# GitHub Community Plan\n\n"
        + ("\n".join(f"- `{item['path']}`: {item['reason']}" for item in planned) or "- No planned writes."),
        encoding="utf-8",
    )
    summary_path = out_dir / "COMMUNITY-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "community_cache_path": str(cache_path),
                "mode": bundle.community_data["mode"],
                "scorecard_before": bundle.community_data["scorecard_before"],
                "scorecard_after": bundle.community_data["scorecard_after"],
                "files_created": bundle.community_data["files_created"],
                "files_removed": bundle.community_data["files_removed"],
                "files_updated": bundle.community_data["files_updated"],
                "placeholder_count": len(bundle.community_data["placeholders"]),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "community_cache": str(cache_path),
        "report": str(report_path),
        "plan": str(plan_path),
        "summary_json": str(summary_path),
    }
