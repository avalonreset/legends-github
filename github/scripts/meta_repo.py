#!/usr/bin/env python3
"""Deterministic metadata planning for Codex GitHub."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_repo import detect_repo_type, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_auth_ok, gh_repo_view, repo_slug_from_git, run_command
from runtime_paths import repo_output_dir
from seo_repo import normalize_topic, run_seo, topic_names


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def gh_repo_languages(repo_slug: str) -> dict[str, int]:
    """Fetch repository language bytes through gh if available."""
    if not gh_auth_ok() or "/" not in repo_slug:
        return {}
    result = run_command(["gh", "api", f"repos/{repo_slug}/languages"], check=False)
    if result.returncode != 0:
        return {}
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}
    return {str(key): int(value) for key, value in payload.items()}


def social_preview_asset(repo_root: Path) -> str | None:
    """Return the first likely social preview image path, if present."""
    candidates = [
        repo_root / "social-preview.jpg",
        repo_root / "social-preview.png",
        repo_root / "social-card.jpg",
        repo_root / "social-card.png",
        repo_root / "og-image.jpg",
        repo_root / "og-image.png",
        repo_root / "assets" / "social-preview.jpg",
        repo_root / "assets" / "social-preview.png",
        repo_root / "assets" / "social-card.jpg",
        repo_root / "assets" / "social-card.png",
        repo_root / "screenshots" / "social-preview.jpg",
        repo_root / "screenshots" / "social-preview.png",
    ]
    for path in candidates:
        if path.exists():
            return str(path.relative_to(repo_root)).replace("\\", "/")
    return None


def feature_defaults(repo_type: str) -> dict[str, bool]:
    """Return deterministic feature recommendations by repo type."""
    discussions = repo_type in {"Library/Package", "CLI Tool", "Skill/Plugin", "Framework"}
    return {
        "issues": True,
        "wiki": False,
        "discussions": discussions,
    }


def homepage_recommendation(repo_slug: str, homepage_url: str, repo_name: str) -> tuple[str | None, str | None, str]:
    """Return homepage recommendation tuple of action, recommended value, and reason."""
    current = (homepage_url or "").strip()
    if not current:
        return "review_required", None, "No homepage URL is set. The deterministic runner will not guess one."

    lowered = current.lower()
    repo_tokens = {
        repo_name.lower().replace("-", ""),
        repo_name.lower().replace("_", ""),
        repo_name.lower().replace("-", " "),
        repo_name.lower().replace("_", " "),
    }
    slug_parts = repo_slug.lower().split("/") if "/" in repo_slug else []
    if any(part and part in lowered for part in slug_parts):
        return "keep", current, "Homepage URL already references this repository slug."
    if any(token and token in lowered for token in repo_tokens):
        return "keep", current, "Homepage URL appears aligned with the project name."
    if "github.io" in lowered or "/docs" in lowered or "readthedocs" in lowered:
        return "keep", current, "Homepage URL already looks like a docs or project site."
    return "review_required", None, "Current homepage may be unrelated. Deterministic mode will not clear it automatically."


def gitattributes_recommendation(repo_root: Path, repo_type: str, primary_language: str, languages: dict[str, int]) -> tuple[bool, str]:
    """Return whether a new .gitattributes file should be recommended."""
    if (repo_root / ".gitattributes").exists():
        return False, ".gitattributes already exists."
    if repo_type == "Skill/Plugin":
        if not languages:
            return True, "Skill/plugin repos benefit from Linguist overrides to keep Markdown visible."
        total = sum(max(value, 0) for value in languages.values()) or 1
        markdown_share = languages.get("Markdown", 0) / total
        if primary_language != "Markdown" and markdown_share >= 0.4:
            return True, "Markdown-heavy skill repos benefit from Linguist overrides."
    return False, "Language bar looks acceptable without overrides."


def shell_quote(value: str) -> str:
    """Quote a value for display in a command string."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_command_entry(
    label: str,
    repo_slug: str,
    args: list[str],
    reason: str,
    ready: bool,
    blocked_reason: str | None = None,
) -> dict[str, Any]:
    """Build one planned gh command entry."""
    shell_args = ["gh", "repo", "edit"]
    if repo_slug and "/" in repo_slug:
        shell_args.append(repo_slug)
    shell_args.extend(args)
    rendered = " ".join(shell_quote(value) if " " in value or value == "" else value for value in shell_args)
    return {
        "label": label,
        "command": rendered,
        "args": ["gh", "repo", "edit", *([repo_slug] if repo_slug and "/" in repo_slug else []), *args],
        "reason": reason,
        "status": "ready" if ready else "pending",
        "blocked_reason": blocked_reason,
    }


def load_seo_payload(repo_root: Path) -> dict[str, Any]:
    """Return seo-data payload, generating fallback data if needed."""
    cached = read_repo_cache(repo_root, "seo-data.json")
    if cached:
        return cached
    return run_seo(repo_root).seo_data


def current_topics(metadata: dict[str, Any], cached_context: dict[str, Any]) -> list[str]:
    """Return actual current topics from repo metadata or cached repo context."""
    raw_topics = metadata.get("repositoryTopics") or metadata.get("topics") or cached_context.get("topics") or []
    return topic_names(raw_topics)


def recommended_topics(existing: list[str], seo_data: dict[str, Any], primary_language: str, repo_type: str) -> list[str]:
    """Build deterministic recommended topics for metadata updates."""
    ordered: list[str] = []

    def add(topic: str) -> None:
        normalized = normalize_topic(topic)
        if normalized and normalized not in ordered:
            ordered.append(normalized)

    if primary_language:
        add(primary_language)
    add("open-source")
    if repo_type == "Skill/Plugin":
        add("skill")
        add("plugin")
    elif repo_type == "CLI Tool":
        add("cli")
        add("developer-tools")
    elif repo_type == "Library/Package":
        add("library")
    for topic in seo_data.get("recommended_topics", []):
        if isinstance(topic, str):
            add(topic)
    for topic in existing:
        add(topic)
    return ordered[:15]


def current_description(metadata: dict[str, Any], cached_context: dict[str, Any]) -> str:
    """Return the actual current description, not the SEO recommendation."""
    return str(metadata.get("description") or cached_context.get("description") or "").strip()


def build_snapshot(repo_root: Path) -> dict[str, Any]:
    """Gather repo signals for metadata planning."""
    cached_context = read_repo_cache(repo_root, "repo-context.json") or {}
    repo_slug = str(cached_context.get("repo") or repo_slug_from_git(repo_root) or repo_root.name)
    metadata = gh_repo_view(repo_slug) if "/" in repo_slug else {}
    if metadata is None:
        metadata = {}
    repo_type = str(cached_context.get("repo_type") or detect_repo_type(repo_root))
    seo_data = load_seo_payload(repo_root)
    languages = gh_repo_languages(repo_slug)
    preview_asset = social_preview_asset(repo_root)
    primary_language = (
        ((metadata.get("primaryLanguage") or {}).get("name"))
        or str(cached_context.get("primary_language") or seo_data.get("primary_language") or "")
    )
    return {
        "repo": repo_slug,
        "repo_root": str(repo_root),
        "repo_name": str(metadata.get("name") or repo_root.name),
        "repo_type": repo_type,
        "metadata": metadata,
        "cached_context": cached_context,
        "seo_data": seo_data,
        "languages": languages,
        "social_preview_asset": preview_asset,
        "primary_language": primary_language,
    }


def build_meta_payload(repo_root: Path) -> dict[str, Any]:
    """Build deterministic metadata recommendations for a repo."""
    snapshot = build_snapshot(repo_root)
    metadata = snapshot["metadata"]
    cached_context = snapshot["cached_context"]
    repo_slug = snapshot["repo"]
    seo_data = snapshot["seo_data"]
    repo_type = snapshot["repo_type"]
    primary_language = snapshot["primary_language"]
    existing_topics = current_topics(metadata, cached_context)
    target_topics = recommended_topics(existing_topics, seo_data, primary_language, repo_type)
    topics_to_add = [topic for topic in target_topics if topic not in existing_topics]
    topics_to_remove = [topic for topic in existing_topics if topic not in target_topics]
    current_desc = current_description(metadata, cached_context)
    recommended_desc = str(seo_data.get("recommended_description") or current_desc).strip()
    current_homepage = str(metadata.get("homepageUrl") or "").strip()
    homepage_action, homepage_target, homepage_reason = homepage_recommendation(
        repo_slug=repo_slug,
        homepage_url=current_homepage,
        repo_name=snapshot["repo_name"],
    )
    current_features = {
        "issues": bool(metadata.get("hasIssuesEnabled", True)),
        "wiki": bool(metadata.get("hasWikiEnabled", False)),
        "discussions": bool(metadata.get("hasDiscussionsEnabled", False)),
        "projects": bool(metadata.get("hasProjectsEnabled", True)),
    }
    recommended_features = dict(current_features)
    recommended_features.update(feature_defaults(repo_type))
    recommend_gitattributes, gitattributes_reason = gitattributes_recommendation(
        repo_root=repo_root,
        repo_type=repo_type,
        primary_language=primary_language,
        languages=snapshot["languages"],
    )
    visibility = str(metadata.get("visibility") or "unknown").upper()
    social_preview_manual = visibility == "PRIVATE" and not bool(metadata.get("usesCustomOpenGraphImage", False))
    commands: list[dict[str, Any]] = []
    repo_edit_ready = "/" in repo_slug
    repo_edit_block = None if repo_edit_ready else "No GitHub remote detected for this local repository."

    if recommended_desc and recommended_desc != current_desc:
        commands.append(
            build_command_entry(
                label="Set repository description",
                repo_slug=repo_slug,
                args=["--description", recommended_desc],
                reason="Front-load the primary SEO phrase into the repo description.",
                ready=repo_edit_ready,
                blocked_reason=repo_edit_block,
            )
        )
    if topics_to_add or topics_to_remove:
        topic_args: list[str] = []
        for topic in topics_to_add:
            topic_args.extend(["--add-topic", topic])
        for topic in topics_to_remove:
            topic_args.extend(["--remove-topic", topic])
        commands.append(
            build_command_entry(
                label="Align repository topics",
                repo_slug=repo_slug,
                args=topic_args,
                reason="Bring topic coverage in line with the SEO cache and repo type defaults.",
                ready=repo_edit_ready,
                blocked_reason=repo_edit_block,
            )
        )

    feature_args: list[str] = []
    if current_features["issues"] != recommended_features["issues"]:
        feature_args.append("--enable-issues" if recommended_features["issues"] else "--enable-issues=false")
    if current_features["wiki"] != recommended_features["wiki"]:
        feature_args.append("--enable-wiki" if recommended_features["wiki"] else "--enable-wiki=false")
    if current_features["discussions"] != recommended_features["discussions"]:
        feature_args.append(
            "--enable-discussions" if recommended_features["discussions"] else "--enable-discussions=false"
        )
    if feature_args:
        commands.append(
            build_command_entry(
                label="Adjust repository features",
                repo_slug=repo_slug,
                args=feature_args,
                reason="Match feature toggles to the repo type defaults.",
                ready=repo_edit_ready,
                blocked_reason=repo_edit_block,
            )
        )

    if homepage_action == "keep" and homepage_target:
        homepage_status = "no_change"
    else:
        homepage_status = "pending"

    blocked: list[str] = []
    warnings: list[str] = []
    if homepage_action == "review_required":
        blocked.append(homepage_reason)
    if social_preview_manual:
        blocked.append("Social preview upload remains manual for this repo visibility/settings combination.")
    if seo_data.get("analysis_mode") == "fallback":
        warnings.append("Metadata plan is using fallback SEO cache data without live DataForSEO verification.")
    if not repo_edit_ready:
        warnings.append("No GitHub remote was detected, so live repo edit commands are emitted as pending only.")

    payload = {
        "cache_type": "meta-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": "plan",
        "applied": False,
        "repo": repo_slug,
        "repo_root": str(repo_root),
        "repo_type": repo_type,
        "primary_language": primary_language,
        "analysis_mode": "deterministic-plan",
        "current": {
            "description": current_desc,
            "topics": existing_topics,
            "homepage_url": current_homepage,
            "features": current_features,
            "uses_custom_open_graph_image": bool(metadata.get("usesCustomOpenGraphImage", False)),
            "social_preview_asset": snapshot["social_preview_asset"],
            "visibility": visibility,
            "gitattributes_exists": (repo_root / ".gitattributes").exists(),
        },
        "recommended": {
            "description": recommended_desc,
            "topics": target_topics,
            "homepage_url": homepage_target,
            "features": recommended_features,
            "social_preview_asset": snapshot["social_preview_asset"],
            "create_gitattributes": recommend_gitattributes,
        },
        "description_set": recommended_desc,
        "topics_set": target_topics,
        "homepage_url": homepage_target or current_homepage,
        "features_toggled": recommended_features,
        "gitattributes_created": False,
        "social_preview_set": bool(metadata.get("usesCustomOpenGraphImage", False)),
        "homepage_status": homepage_status,
        "homepage_reason": homepage_reason,
        "gitattributes_reason": gitattributes_reason,
        "topics_to_add": topics_to_add,
        "topics_to_remove": topics_to_remove,
        "commands": commands,
        "warnings": warnings,
        "blocked": blocked,
        "depends_on": {
            "seo_cache": str(seo_data.get("analysis_mode") or "unknown"),
            "gh_metadata_available": bool(metadata),
        },
    }
    return payload


def apply_meta_plan(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Apply ready gh commands from a metadata plan."""
    if not gh_auth_ok():
        raise RuntimeError("GitHub CLI is not authenticated; cannot apply metadata changes.")
    executed: list[str] = []
    for command in payload.get("commands", []):
        if command.get("status") != "ready":
            continue
        run_command(command["args"])
        executed.append(command["command"])
    return True, executed


def build_meta_report(payload: dict[str, Any]) -> str:
    """Render a markdown report for deterministic metadata planning."""
    add_lines = "\n".join(f"- `{topic}`" for topic in payload["topics_to_add"]) or "- None"
    remove_lines = "\n".join(f"- `{topic}`" for topic in payload["topics_to_remove"]) or "- None"
    command_lines = "\n".join(
        f"{index}. `{entry['command']}` - {entry['status']}"
        for index, entry in enumerate(payload["commands"], start=1)
    ) or "1. No live metadata edits are required."
    warning_lines = "\n".join(f"- {item}" for item in payload["warnings"]) or "- None"
    blocked_lines = "\n".join(f"- {item}" for item in payload["blocked"]) or "- None"
    return f"""# GitHub Meta Report

- **Repository:** {payload['repo']}
- **Generated at:** {payload['timestamp']}
- **Mode:** {payload['mode']}
- **Applied:** {payload['applied']}

## Current vs Recommended

| Setting | Current | Recommended |
|---------|---------|-------------|
| Description | {payload['current']['description']} | {payload['recommended']['description']} |
| Topics | {", ".join(payload['current']['topics']) or "None"} | {", ".join(payload['recommended']['topics']) or "None"} |
| Homepage URL | {payload['current']['homepage_url'] or "None"} | {payload['recommended']['homepage_url'] or "Review required"} |
| Issues | {payload['current']['features']['issues']} | {payload['recommended']['features']['issues']} |
| Wiki | {payload['current']['features']['wiki']} | {payload['recommended']['features']['wiki']} |
| Discussions | {payload['current']['features']['discussions']} | {payload['recommended']['features']['discussions']} |

## Topic Changes

### Add
{add_lines}

### Remove
{remove_lines}

## Commands

{command_lines}

## Warnings

{warning_lines}

## Blocked / Manual

{blocked_lines}
"""


@dataclass
class MetaBundle:
    """Structured metadata output."""

    meta_data: dict[str, Any]
    report_markdown: str


def run_meta(repo_root: Path, apply: bool = False) -> MetaBundle:
    """Build a deterministic metadata plan and optionally apply ready commands."""
    meta_data = build_meta_payload(repo_root)
    if apply:
        applied, executed = apply_meta_plan(meta_data)
        meta_data["mode"] = "apply"
        meta_data["applied"] = applied
        meta_data["executed_commands"] = executed
    report_markdown = build_meta_report(meta_data)
    return MetaBundle(meta_data=meta_data, report_markdown=report_markdown)


def write_meta_artifacts(repo_root: Path, bundle: MetaBundle) -> dict[str, str]:
    """Write metadata cache and report artifacts for one run."""
    slug = slugify(bundle.meta_data["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_cache_path = write_repo_cache(repo_root, "meta-data.json", bundle.meta_data)
    report_path = out_dir / "META-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    summary_path = out_dir / "META-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "meta_cache_path": str(meta_cache_path),
                "mode": bundle.meta_data["mode"],
                "applied": bundle.meta_data["applied"],
                "description_set": bundle.meta_data["description_set"],
                "topics_set": bundle.meta_data["topics_set"],
                "commands": bundle.meta_data["commands"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "meta_cache": str(meta_cache_path),
        "report": str(report_path),
        "summary_json": str(summary_path),
    }
