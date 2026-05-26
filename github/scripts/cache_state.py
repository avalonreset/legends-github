#!/usr/bin/env python3
"""Shared cache helpers for Legends GitHub."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_paths import github_home, github_runs_cache, github_setup_cache, repo_cache_dir


def now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def ensure_cache_gitignore(repo_root: Path) -> None:
    """Ensure .github-audit stays ignored in the target repo."""
    gitignore_path = repo_root / ".gitignore"
    entry = ".github-audit/"
    lines: list[str] = []
    if gitignore_path.exists():
        lines = gitignore_path.read_text(encoding="utf-8").splitlines()
        if entry in {line.strip() for line in lines}:
            return

    lines.append(entry)
    gitignore_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def ensure_repo_cache(repo_root: Path) -> Path:
    """Create the repo cache directory if needed."""
    cache_dir = repo_cache_dir(repo_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    ensure_cache_gitignore(repo_root)
    return cache_dir


def probe_repo_cache(repo_root: Path) -> tuple[Path, bool]:
    """Check whether the repo cache path is writable without leaving repo changes behind."""
    cache_dir = repo_cache_dir(repo_root)
    created_dir = False
    try:
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            created_dir = True
        probe_path = cache_dir / f".write-test-{uuid.uuid4().hex}"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink()
        if created_dir:
            cache_dir.rmdir()
        return cache_dir, True
    except OSError:
        if created_dir and cache_dir.exists():
            try:
                cache_dir.rmdir()
            except OSError:
                pass
        return cache_dir, False


def read_repo_cache(repo_root: Path, filename: str) -> dict[str, Any] | None:
    """Read one per-repo cache file if it exists."""
    path = repo_cache_dir(repo_root) / filename
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_repo_cache(repo_root: Path, filename: str, payload: dict[str, Any]) -> Path:
    """Write one per-repo cache file."""
    cache_dir = ensure_repo_cache(repo_root)
    path = cache_dir / filename
    enriched = dict(payload)
    enriched.setdefault("timestamp", now_iso())
    enriched.setdefault("analyzed_at", enriched["timestamp"])
    path.write_text(json.dumps(enriched, indent=2), encoding="utf-8")
    return path


def write_setup_cache(**payload: Any) -> Path:
    """Write the global setup status cache."""
    github_home().mkdir(parents=True, exist_ok=True)
    path = github_setup_cache()
    enriched = dict(payload)
    enriched["timestamp"] = now_iso()
    enriched["analyzed_at"] = enriched["timestamp"]
    path.write_text(json.dumps(enriched, indent=2), encoding="utf-8")
    return path


def append_run_cache(operation: str, summary: str, metadata: dict[str, Any] | None = None) -> Path:
    """Append one runtime event to the shared runs cache."""
    github_home().mkdir(parents=True, exist_ok=True)
    path = github_runs_cache()
    payload = _load_json(path, {"runs": []})
    payload.setdefault("runs", [])
    payload["runs"].append(
        {
            "timestamp": now_iso(),
            "analyzed_at": now_iso(),
            "operation": operation,
            "summary": summary,
            "metadata": metadata or {},
        }
    )
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
