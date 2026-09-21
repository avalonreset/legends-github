#!/usr/bin/env python3
"""Shared cache helpers for Legends GitHub."""

from __future__ import annotations

import json
import os
import tempfile
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
    """Compatibility no-op: cache writes must never edit a target's tracked files."""
    return None


def _atomic_json(path: Path, payload: Any) -> None:
    """Replace complete JSON atomically so an interrupted write cannot truncate it."""
    fd, temporary = tempfile.mkstemp(prefix=".json-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def ensure_repo_cache(repo_root: Path) -> Path:
    """Create the repo cache directory if needed."""
    cache_dir = repo_cache_dir(repo_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
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
    _atomic_json(path, enriched)
    return path


def write_setup_cache(**payload: Any) -> Path:
    """Write the global setup status cache."""
    github_home().mkdir(parents=True, exist_ok=True)
    path = github_setup_cache()
    enriched = dict(payload)
    enriched["timestamp"] = now_iso()
    enriched["analyzed_at"] = enriched["timestamp"]
    _atomic_json(path, enriched)
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
    _atomic_json(path, payload)
    return path
