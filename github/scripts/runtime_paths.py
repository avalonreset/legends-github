#!/usr/bin/env python3
"""Shared runtime path resolution for legends-github."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    return Path(raw).expanduser() if raw else default


def home_dir() -> Path:
    """Return the current user home directory."""
    try:
        return Path.home()
    except RuntimeError:
        return Path(tempfile.gettempdir())


def github_home() -> Path:
    """Return the global legends-github runtime directory."""
    return _env_path(
        "LEGENDS_GITHUB_HOME",
        home_dir() / ".legends-github",
    )


def github_runs_cache() -> Path:
    """Return the shared run-history cache path."""
    return github_home() / "runs.json"


def github_setup_cache() -> Path:
    """Return the shared setup cache path."""
    return github_home() / "setup.json"


def repo_cache_dir(repo_root: Path) -> Path:
    """Return the per-repo cache directory outside the target repository by default."""
    override = os.environ.get("GITHUB_AUDIT_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    identity = hashlib.sha256(os.path.normcase(str(repo_root.resolve())).encode()).hexdigest()[:16]
    return github_home() / "repos" / identity


def repo_output_dir(repo_root: Path) -> Path:
    """Return the per-repo output directory."""
    return repo_cache_dir(repo_root) / "output"


def runtime_paths_payload(repo_root: Path) -> dict[str, str]:
    """Return a JSON-safe runtime path payload."""
    return {
        "home": str(home_dir()),
        "github_home": str(github_home()),
        "github_runs_cache": str(github_runs_cache()),
        "github_setup_cache": str(github_setup_cache()),
        "repo_root": str(repo_root),
        "repo_cache_dir": str(repo_cache_dir(repo_root)),
        "repo_output_dir": str(repo_output_dir(repo_root)),
    }
