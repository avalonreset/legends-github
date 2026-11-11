#!/usr/bin/env python3
"""Runtime helpers for legends-github headless workflows."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


GITHUB_REMOTE_RE = re.compile(
    r"github\.com[:/](?P<owner>[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$"
)
REPO_SLUG_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?/[A-Za-z0-9_.-]+$")
GITHUB_OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
GIT_TAG_OR_REV_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_./+~^-]{0,127}$")
DISCUSSION_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_MACOS_SYSTEM_SYMLINKS = {Path("/var"), Path("/tmp"), Path("/etc")}


def valid_repo_slug(slug: str | None) -> str:
    """Return a validated OWNER/REPO string or an empty string."""
    if not isinstance(slug, str):
        return ""
    cleaned = slug.strip()
    if not cleaned or cleaned.startswith("-") or not REPO_SLUG_RE.fullmatch(cleaned):
        return ""
    owner, repo = cleaned.split("/", 1)
    if repo in {".", ".."} or ".." in repo:
        return ""
    return f"{owner}/{repo}"


def valid_owner(owner: str | None) -> str:
    """Return a validated GitHub owner/username or an empty string."""
    if not isinstance(owner, str):
        return ""
    cleaned = owner.strip()
    if not cleaned or cleaned.startswith("-") or not GITHUB_OWNER_RE.fullmatch(cleaned):
        return ""
    return cleaned


def valid_git_ref(ref: str | None) -> str:
    """Return a validated git tag or revision range that cannot act as a CLI flag."""
    if not isinstance(ref, str):
        return ""
    cleaned = ref.strip()
    if not cleaned or cleaned.startswith("-") or not GIT_TAG_OR_REV_RE.fullmatch(cleaned):
        return ""
    return cleaned


def valid_discussion_slug(slug: str | None) -> str:
    """Return a validated lowercase discussion category slug or an empty string."""
    if not isinstance(slug, str):
        return ""
    cleaned = slug.strip().lower()
    if not cleaned or not DISCUSSION_SLUG_RE.fullmatch(cleaned):
        return ""
    return cleaned


def _safe_path(first: Path, second: Path | None = None, *, root: Path | None = None) -> bool:
    """Reject symlinks, Windows reparse points, and paths outside root."""
    if second is not None:
        root_path: Path | None = first
        target_path = second
    else:
        root_path = root
        target_path = first
    try:
        safe_local_path(target_path, root=root_path)
        return True
    except (OSError, ValueError, RuntimeError):
        return False


def safe_local_path(value: str | Path, *, root: Path | None = None) -> Path:
    """Validate that a path and its ancestors contain no symlinks or Windows junctions."""
    p = Path(value).expanduser().absolute()
    for idx, part in enumerate((p, *p.parents)):
        if idx > 0 and sys.platform == "darwin" and part in _MACOS_SYSTEM_SYMLINKS:
            continue
        if part.is_symlink() or getattr(part, "is_junction", lambda: False)():
            raise ValueError(f"Refusing to access symlink or junction path: {value}")
        try:
            st = part.lstat()
            if getattr(st, "st_reparse_tag", 0) == 0xA0000003 or (
                getattr(st, "st_file_attributes", 0) & 0x400
            ):
                raise ValueError(f"Refusing to access Windows reparse point: {value}")
        except OSError:
            continue
    if root is not None:
        resolved_root = root.resolve()
        if not p.resolve().is_relative_to(resolved_root):
            raise ValueError(f"Path escapes repository root: {value}")
    return p


def have_command(name: str) -> bool:
    """Return whether a command is available."""
    return shutil.which(name) is not None


def pillow_available() -> bool:
    """Return whether Pillow is importable in the current Python runtime."""
    return importlib.util.find_spec("PIL") is not None


def run_command(args: list[str], cwd: Path | None = None, check: bool = True, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    """Run a subprocess and return the completed process."""
    if offline_mode() and Path(args[0]).stem.lower() == "gh":
        result = subprocess.CompletedProcess(args, 125, "", "GitHub access disabled by --offline")
        if check:
            raise RuntimeError(result.stderr)
        return result
    completed = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=timeout,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or f"Command failed: {' '.join(args)}")
    return completed


def offline_mode() -> bool:
    """Whether optional external requests are disabled for this process."""
    return os.environ.get("LEGENDS_GITHUB_OFFLINE", "").strip().lower() in {"1", "true", "yes"}


def gh_auth_ok() -> bool:
    """Return whether GitHub CLI appears authenticated."""
    if offline_mode() or not have_command("gh"):
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
    slug = valid_repo_slug(f"{match.group('owner')}/{match.group('repo')}")
    return slug or None


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
    candidate = safe_local_path(path_arg) if path_arg else safe_local_path(Path.cwd())
    repo_root = find_git_root(candidate.resolve())
    if repo_root is None:
        raise ValueError(f"Could not find a git repo from {candidate}")
    return repo_root


def gh_repo_view(repo_slug: str) -> dict[str, Any] | None:
    """Fetch repository metadata through gh if available."""
    slug = valid_repo_slug(repo_slug)
    if not slug or not gh_auth_ok():
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
    result = run_command(["gh", "repo", "view", slug, "--json", ",".join(fields)], check=False)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def gh_release_rows(repo_slug: str, limit: int = 5) -> list[dict[str, str]]:
    """Fetch a short release listing via gh."""
    slug = valid_repo_slug(repo_slug)
    if not slug or not gh_auth_ok():
        return []
    result = run_command(
        [
            "gh",
            "release",
            "list",
            "--repo",
            slug,
            "--limit",
            str(int(limit)),
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
    return [line.strip() for line in result.stdout.splitlines() if valid_git_ref(line.strip())]
