#!/usr/bin/env python3
"""Runtime helpers for Codex GitHub headless workflows."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import importlib.util
from pathlib import Path
from typing import Any


GITHUB_REMOTE_RE = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")


def have_command(name: str) -> bool:
    """Return whether a command is available."""
    return shutil.which(name) is not None


def pillow_available() -> bool:
    """Return whether Pillow is importable in the current Python runtime."""
    return importlib.util.find_spec("PIL") is not None


def run_command(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a subprocess and return the completed process."""
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or f"Command failed: {' '.join(args)}")
    return completed


def gh_auth_ok() -> bool:
    """Return whether GitHub CLI appears authenticated."""
    if not have_command("gh"):
        return False
    result = run_command(["gh", "auth", "status"], check=False)
    return result.returncode == 0


def find_git_root(start: Path) -> Path | None:
    """Resolve the git repo root containing the given path."""
    current = start.resolve()
    if current.is_file():
        current = current.parent

    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            return None
        current = current.parent


def parse_remote_slug(remote_url: str) -> str | None:
    """Parse owner/repo from a GitHub remote URL."""
    match = GITHUB_REMOTE_RE.search(remote_url.strip())
    if not match:
        return None
    return f"{match.group('owner')}/{match.group('repo')}"


def repo_slug_from_git(repo_root: Path) -> str | None:
    """Resolve owner/repo from git remote origin."""
    if not have_command("git"):
        return None
    result = run_command(["git", "remote", "get-url", "origin"], cwd=repo_root, check=False)
    if result.returncode != 0:
        return None
    return parse_remote_slug(result.stdout.strip())


def resolve_repo_root(path_arg: str | None = None) -> Path:
    """Resolve a local repo root from an explicit path or the current working directory."""
    candidate = Path(path_arg).expanduser().resolve() if path_arg else Path.cwd().resolve()
    repo_root = find_git_root(candidate)
    if repo_root is None:
        raise ValueError(f"Could not find a git repo from {candidate}")
    return repo_root


def load_env_file(path: Path) -> dict[str, str]:
    """Load one dotenv-style file."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_kie_api_key(repo_root: Path) -> tuple[str, str]:
    """Resolve KIE API key from env or standard dotenv locations."""
    if os.environ.get("KIE_API_KEY", "").strip():
        return os.environ["KIE_API_KEY"].strip(), "env:KIE_API_KEY"

    skill_root = Path(__file__).resolve().parents[1]
    search_paths = [
        repo_root / ".env.local",
        repo_root / ".env",
        skill_root / ".env.local",
        skill_root / ".env",
        Path.home() / ".env.local",
        Path.home() / ".env",
    ]
    for path in search_paths:
        values = load_env_file(path)
        key = values.get("KIE_API_KEY", "").strip()
        if key:
            return key, str(path)
    return "", ""


def gh_repo_view(repo_slug: str) -> dict[str, Any] | None:
    """Fetch repository metadata through gh if available."""
    if not gh_auth_ok():
        return None
    fields = [
        "name",
        "description",
        "url",
        "homepageUrl",
        "repositoryTopics",
        "visibility",
        "defaultBranchRef",
        "licenseInfo",
        "stargazerCount",
        "forkCount",
        "watchers",
        "primaryLanguage",
        "createdAt",
        "updatedAt",
        "isArchived",
        "isFork",
        "parent",
        "hasIssuesEnabled",
        "hasWikiEnabled",
        "hasDiscussionsEnabled",
        "hasProjectsEnabled",
        "isSecurityPolicyEnabled",
        "usesCustomOpenGraphImage",
    ]
    result = run_command(["gh", "repo", "view", repo_slug, "--json", ",".join(fields)], check=False)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def gh_release_rows(repo_slug: str, limit: int = 5) -> list[dict[str, str]]:
    """Fetch a short release listing via gh."""
    if not gh_auth_ok():
        return []
    result = run_command(
        [
            "gh",
            "release",
            "list",
            "--repo",
            repo_slug,
            "--limit",
            str(limit),
            "--json",
            "tagName,name,isDraft,isPrerelease,publishedAt",
        ],
        check=False,
    )
    if result.returncode != 0:
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    releases: list[dict[str, str]] = []
    for row in payload:
        release_type = "Draft" if row.get("isDraft") else "Pre-release" if row.get("isPrerelease") else "Latest"
        releases.append(
            {
                "tag": str(row.get("tagName") or "").strip(),
                "title": str(row.get("name") or "").strip(),
                "type": release_type,
                "published": str(row.get("publishedAt") or "").strip(),
            }
        )
    return releases


def git_recent_commit(repo_root: Path) -> str:
    """Return the most recent commit timestamp if available."""
    if not have_command("git"):
        return ""
    result = run_command(["git", "log", "-1", "--format=%cI"], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_tags(repo_root: Path) -> list[str]:
    """Return local git tags."""
    if not have_command("git"):
        return []
    result = run_command(["git", "tag", "--list"], cwd=repo_root, check=False)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
