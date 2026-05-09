#!/usr/bin/env python3
"""Shared runtime path resolution for Codex GitHub."""

from __future__ import annotations

import os
from pathlib import Path


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    return Path(raw).expanduser() if raw else default


def home_dir() -> Path:
    """Return the current user home directory."""
    return Path.home()


def codex_home() -> Path:
    """Return the active Codex home directory."""
    return _env_path("CODEX_HOME", home_dir() / ".codex")


def codex_config_path() -> Path:
    """Return the active Codex config path."""
    return codex_home() / "config.toml"


def codex_skill_dir() -> Path:
    """Return the installed GitHub skill directory."""
    return codex_home() / "skills" / "github"


def codex_agents_dir() -> Path:
    """Return the installed agents directory."""
    return codex_home() / "agents"


def github_home() -> Path:
    """Return the global Codex GitHub runtime directory."""
    return _env_path("CODEX_GITHUB_HOME", home_dir() / ".codex-github")


def github_runs_cache() -> Path:
    """Return the shared run-history cache path."""
    return github_home() / "runs.json"


def github_setup_cache() -> Path:
    """Return the shared setup cache path."""
    return github_home() / "setup.json"


def repo_cache_dir(repo_root: Path) -> Path:
    """Return the per-repo cache directory."""
    override = os.environ.get("GITHUB_AUDIT_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return repo_root / ".github-audit"


def repo_output_dir(repo_root: Path) -> Path:
    """Return the per-repo output directory."""
    return repo_cache_dir(repo_root) / "output"


def runtime_paths_payload(repo_root: Path) -> dict[str, str]:
    """Return a JSON-safe runtime path payload."""
    return {
        "home": str(home_dir()),
        "codex_home": str(codex_home()),
        "codex_config": str(codex_config_path()),
        "codex_skill_dir": str(codex_skill_dir()),
        "codex_agents_dir": str(codex_agents_dir()),
        "github_home": str(github_home()),
        "github_runs_cache": str(github_runs_cache()),
        "github_setup_cache": str(github_setup_cache()),
        "repo_root": str(repo_root),
        "repo_cache_dir": str(repo_cache_dir(repo_root)),
        "repo_output_dir": str(repo_output_dir(repo_root)),
    }
