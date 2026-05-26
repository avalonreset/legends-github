#!/usr/bin/env python3
"""Deterministic portfolio planning for Legends GitHub."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_repo import detect_repo_type, load_readme, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_auth_ok, gh_repo_view, repo_slug_from_git, resolve_kie_api_key, run_command
from kie_assets import (
    AssetGenerationError,
    convert_png_to_jpeg,
    create_kie_task,
    download_binary,
    pillow_available,
    poll_kie_task,
    result_url,
)
from runtime_paths import repo_output_dir
from seo_repo import normalize_topic, topic_names


GENERIC_TOPICS = {
    "open-source",
    "opensource",
    "github",
    "git",
    "developer-tools",
    "devtools",
    "tooling",
    "tools",
    "cli",
    "plugin",
    "skill",
    "automation",
}


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def github_raw_url(repo_slug: str, relative_path: str) -> str:
    """Return a GitHub raw URL for a file path."""
    return f"https://raw.githubusercontent.com/{repo_slug}/main/{relative_path}"


def file_uri(path: Path) -> str:
    """Return a file URI for the given path."""
    return path.resolve().as_uri()


def first_paragraph(text: str) -> str:
    """Return the first prose paragraph from markdown-like text."""
    chunks = re.split(r"\n\s*\n", text)
    for chunk in chunks:
        stripped = chunk.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("|") and not stripped.startswith("```"):
            return re.sub(r"\s+", " ", stripped)
    return ""


def safe_text(value: str, fallback: str = "") -> str:
    """Normalize text for compact markdown/report output."""
    cleaned = re.sub(r"\s+", " ", (value or "").strip())
    return cleaned or fallback


def score_label(score: int) -> str:
    """Return a human label for repo health."""
    if score >= 75:
        return "Strong"
    if score >= 45:
        return "Needs Work"
    return "Weak"


def quote_shell(value: str) -> str:
    """Quote a value for display in a shell command string."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def markdown_escape(value: str) -> str:
    """Escape pipes in markdown tables."""
    return value.replace("|", "\\|")


def current_login() -> str:
    """Return the authenticated GitHub login if available."""
    if not gh_auth_ok():
        return ""
    result = run_command(["gh", "api", "user", "--jq", ".login"], check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def gh_user_profile(owner: str) -> dict[str, Any]:
    """Fetch a public GitHub profile via gh when available."""
    if not owner or not gh_auth_ok():
        return {}
    result = run_command(["gh", "api", f"users/{owner}"], check=False)
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def gh_repo_list(owner: str) -> list[dict[str, Any]]:
    """Fetch public repositories for one owner via gh."""
    if not owner or not gh_auth_ok():
        return []
    fields = ",".join(
        [
            "name",
            "nameWithOwner",
            "description",
            "repositoryTopics",
            "stargazerCount",
            "forkCount",
            "primaryLanguage",
            "updatedAt",
            "licenseInfo",
            "homepageUrl",
            "isArchived",
            "url",
        ]
    )
    result = run_command(
        ["gh", "repo", "list", owner, "--visibility", "public", "--limit", "100", "--json", fields],
        check=False,
    )
    if result.returncode != 0:
        return []
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def detect_primary_language(repo_root: Path) -> str:
    """Infer a primary language for local-only repos."""
    if (repo_root / "pyproject.toml").exists() or (repo_root / "setup.py").exists():
        return "Python"
    if (repo_root / "package.json").exists():
        return "JavaScript"
    if (repo_root / "Cargo.toml").exists():
        return "Rust"
    if (repo_root / "go.mod").exists():
        return "Go"
    if (repo_root / "README.md").exists():
        return "Markdown"
    return ""


def repo_description_fallback(repo_root: Path, cached_context: dict[str, Any], seo_data: dict[str, Any]) -> str:
    """Return the best available local description."""
    description = safe_text(str(cached_context.get("description") or ""))
    if description:
        return description
    recommended = safe_text(str(seo_data.get("recommended_description") or ""))
    if recommended:
        return recommended
    readme_text, _ = load_readme(repo_root)
    paragraph = first_paragraph(readme_text)
    if paragraph:
        return paragraph[:160].rstrip(".") + "."
    return repo_root.name.replace("-", " ").strip().title()


def local_topics(cached_context: dict[str, Any], seo_data: dict[str, Any]) -> list[str]:
    """Return current or fallback topics for the local repo."""
    topics = topic_names(cached_context.get("topics") or [])
    if topics:
        return topics
    return [normalize_topic(topic) for topic in seo_data.get("recommended_topics", []) if isinstance(topic, str)]


def repo_health_score(repo: dict[str, Any]) -> int:
    """Compute a deterministic health score from coarse repo signals."""
    score = 0
    if repo["description"]:
        score += 20 if len(repo["description"]) >= 40 else 12
    topic_count = len(repo["topics"])
    if topic_count >= 5:
        score += 20
    elif topic_count >= 3:
        score += 12
    elif topic_count >= 1:
        score += 6
    if repo["license"]:
        score += 15
    if repo["homepage_url"]:
        score += 10
    if repo["stars"] > 0:
        score += 10
    if not repo["is_archived"]:
        score += 10
    updated_days = repo["updated_days"]
    if updated_days is not None and updated_days <= 90:
        score += 15
    elif updated_days is not None and updated_days <= 180:
        score += 8
    return min(score, 100)


def days_since_iso(value: str) -> int | None:
    """Return days since an ISO timestamp."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return max((datetime.now(timezone.utc) - dt).days, 0)


def build_local_repo_entry(repo_root: Path) -> dict[str, Any]:
    """Build a repo entry for the current local checkout."""
    cached_context = read_repo_cache(repo_root, "repo-context.json") or {}
    cached_audit = read_repo_cache(repo_root, "audit-data.json") or {}
    seo_data = read_repo_cache(repo_root, "seo-data.json") or {}
    repo_slug = str(cached_context.get("repo") or repo_slug_from_git(repo_root) or repo_root.name)
    metadata = gh_repo_view(repo_slug) if "/" in repo_slug else {}
    readme_text, _ = load_readme(repo_root)
    description = safe_text(str((metadata or {}).get("description") or ""), repo_description_fallback(repo_root, cached_context, seo_data))
    topics = topic_names((metadata or {}).get("repositoryTopics") or []) or local_topics(cached_context, seo_data)
    updated_at = safe_text(str((metadata or {}).get("updatedAt") or cached_context.get("recent_commit") or ""))
    language = (
        safe_text(str(((metadata or {}).get("primaryLanguage") or {}).get("name") or ""))
        or safe_text(str(cached_context.get("primary_language") or ""))
        or detect_primary_language(repo_root)
    )
    license_name = safe_text(str(((metadata or {}).get("licenseInfo") or {}).get("spdxId") or ""))
    if not license_name and (repo_root / "LICENSE").exists():
        license_name = "Present"
    entry = {
        "name": safe_text(str((metadata or {}).get("name") or repo_root.name)),
        "repo": repo_slug,
        "url": safe_text(str((metadata or {}).get("url") or "")) or (f"https://github.com/{repo_slug}" if "/" in repo_slug else ""),
        "description": description,
        "topics": topics,
        "topics_count": len(topics),
        "stars": int((metadata or {}).get("stargazerCount") or 0),
        "forks": int((metadata or {}).get("forkCount") or 0),
        "language": language,
        "license": license_name,
        "homepage_url": safe_text(str((metadata or {}).get("homepageUrl") or cached_context.get("homepage_url") or "")),
        "updated_at": updated_at,
        "updated_days": days_since_iso(updated_at),
        "is_archived": bool((metadata or {}).get("isArchived") or False),
        "audit_score": int(cached_audit.get("overall_score") or 0),
        "readme_first_paragraph": first_paragraph(readme_text),
        "repo_type": safe_text(str(cached_context.get("repo_type") or detect_repo_type(repo_root))),
    }
    entry["score"] = entry["audit_score"] or repo_health_score(entry)
    entry["health"] = score_label(entry["score"])
    return entry


def build_remote_repo_entry(row: dict[str, Any]) -> dict[str, Any]:
    """Build a repo entry from gh repo list output."""
    topics = topic_names(row.get("repositoryTopics") or [])
    updated_at = safe_text(str(row.get("updatedAt") or ""))
    entry = {
        "name": safe_text(str(row.get("name") or "")),
        "repo": safe_text(str(row.get("nameWithOwner") or "")),
        "url": safe_text(str(row.get("url") or "")),
        "description": safe_text(str(row.get("description") or "")),
        "topics": topics,
        "topics_count": len(topics),
        "stars": int(row.get("stargazerCount") or 0),
        "forks": int(row.get("forkCount") or 0),
        "language": safe_text(str((row.get("primaryLanguage") or {}).get("name") or "")),
        "license": safe_text(str((row.get("licenseInfo") or {}).get("spdxId") or "")),
        "homepage_url": safe_text(str(row.get("homepageUrl") or "")),
        "updated_at": updated_at,
        "updated_days": days_since_iso(updated_at),
        "is_archived": bool(row.get("isArchived") or False),
        "audit_score": 0,
        "readme_first_paragraph": "",
        "repo_type": "",
    }
    entry["score"] = repo_health_score(entry)
    entry["health"] = score_label(entry["score"])
    return entry


def portfolio_owner(repo_root: Path, username: str) -> str:
    """Resolve the portfolio owner from explicit input, git remote, or gh auth."""
    if username.strip():
        return username.strip()
    repo_slug = repo_slug_from_git(repo_root) or ""
    if "/" in repo_slug:
        return repo_slug.split("/", 1)[0]
    return current_login()


def topic_authority_map(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return topic authority clusters across the portfolio."""
    counter: Counter[str] = Counter()
    repo_names_by_topic: dict[str, list[str]] = {}
    for repo in repos:
        for topic in repo["topics"]:
            if not topic:
                continue
            counter[topic] += 1
            repo_names_by_topic.setdefault(topic, []).append(repo["name"])
    clusters: list[dict[str, Any]] = []
    for topic, count in counter.most_common():
        if count < 2:
            continue
        strength = "Strong" if count >= 3 else "Building"
        clusters.append(
            {
                "topic": topic,
                "cluster": topic,
                "repos": count,
                "repo_names": sorted(repo_names_by_topic.get(topic, [])),
                "strength": strength,
            }
        )
    return clusters


def dominant_topics(repos: list[dict[str, Any]]) -> list[str]:
    """Return the top non-generic topics in the portfolio."""
    counter: Counter[str] = Counter()
    for repo in repos:
        for topic in repo["topics"]:
            normalized = normalize_topic(topic)
            if normalized and normalized not in GENERIC_TOPICS:
                counter[normalized] += 1
    return [topic for topic, _count in counter.most_common(5)]


def dominant_languages(repos: list[dict[str, Any]]) -> list[str]:
    """Return the top languages in the portfolio."""
    counter: Counter[str] = Counter()
    for repo in repos:
        language = safe_text(repo["language"])
        if language:
            counter[language] += 1
    return [language for language, _count in counter.most_common(4)]


def infer_identity(owner: str, repos: list[dict[str, Any]], seo_data: dict[str, Any]) -> str:
    """Build a concise portfolio identity statement."""
    topics = dominant_topics(repos)
    languages = dominant_languages(repos)
    primary_keyword = safe_text(str((seo_data.get("primary_keyword") or {}).get("keyword") or ""))
    if primary_keyword:
        return f"{owner} builds {primary_keyword} projects and developer tooling with a consistent GitHub-first portfolio."
    if topics:
        if len(topics) == 1:
            return f"{owner} builds {topics[0]} projects with a portfolio centered on practical developer tooling."
        joined = ", ".join(topics[:2])
        return f"{owner} builds {joined} projects and related developer tooling across a focused GitHub portfolio."
    if languages:
        return f"{owner} maintains a {languages[0]}-heavy portfolio of developer projects and GitHub-ready tooling."
    return f"{owner} maintains a portfolio of developer projects that needs stronger GitHub branding and cross-linking."


def featured_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the repos to feature in the blueprint."""
    return sorted(repos, key=lambda item: (item["score"], item["stars"], -item["topics_count"]), reverse=True)[:4]


def pinned_repos(repos: list[dict[str, Any]]) -> list[str]:
    """Return the recommended pin order."""
    ordered = sorted(
        repos,
        key=lambda item: (
            item["score"],
            item["stars"],
            -(item["updated_days"] or 9999),
        ),
        reverse=True,
    )
    return [repo["name"] for repo in ordered[:6]]


def brand_consistency(repos: list[dict[str, Any]]) -> dict[str, Any]:
    """Return coarse branding consistency ratings."""
    count = max(len(repos), 1)
    descriptions = sum(1 for repo in repos if repo["description"])
    homepages = sum(1 for repo in repos if repo["homepage_url"])
    licenses = Counter(repo["license"] for repo in repos if repo["license"])
    dominant_license = licenses.most_common(1)[0][0] if licenses else ""
    consistent_license = sum(1 for repo in repos if repo["license"] == dominant_license) if dominant_license else 0
    avg_topics = sum(repo["topics_count"] for repo in repos) / count
    description_rating = "Strong" if descriptions / count >= 0.8 else "Mixed" if descriptions / count >= 0.5 else "Weak"
    homepage_rating = "Strong" if homepages / count >= 0.6 else "Mixed" if homepages else "Weak"
    license_rating = "Strong" if dominant_license and consistent_license / count >= 0.7 else "Mixed" if dominant_license else "Weak"
    topic_rating = "Strong" if avg_topics >= 5 else "Mixed" if avg_topics >= 3 else "Weak"
    overall = "Strong" if sum(value == "Strong" for value in (description_rating, homepage_rating, license_rating, topic_rating)) >= 3 else "Mixed"
    if overall == "Mixed" and sum(value == "Weak" for value in (description_rating, homepage_rating, license_rating, topic_rating)) >= 2:
        overall = "Weak"
    return {
        "description_consistency": description_rating,
        "homepage_coverage": homepage_rating,
        "license_consistency": license_rating,
        "topic_consistency": topic_rating,
        "overall": overall,
    }


def portfolio_health(
    repos: list[dict[str, Any]],
    profile: dict[str, Any],
    profile_readme_exists: bool,
    authority: list[dict[str, Any]],
    seo_data: dict[str, Any],
) -> int:
    """Compute the deterministic portfolio health score."""
    repo_count = max(len(repos), 1)
    completeness = 0
    if safe_text(str(profile.get("bio") or "")):
        completeness += 6
    if profile_readme_exists:
        completeness += 8
    if safe_text(str(profile.get("blog") or "")):
        completeness += 3
    if safe_text(str(profile.get("location") or "")) or safe_text(str(profile.get("company") or "")):
        completeness += 3

    branding = 0
    descriptions = sum(1 for repo in repos if repo["description"])
    homepages = sum(1 for repo in repos if repo["homepage_url"])
    licenses = sum(1 for repo in repos if repo["license"])
    if descriptions / repo_count >= 0.8:
        branding += 5
    elif descriptions / repo_count >= 0.5:
        branding += 3
    if homepages / repo_count >= 0.6:
        branding += 5
    elif homepages / repo_count >= 0.3:
        branding += 3
    if licenses / repo_count >= 0.8:
        branding += 5
    elif licenses / repo_count >= 0.5:
        branding += 3
    if len(authority) >= 2:
        branding += 5
    elif authority:
        branding += 3

    topic_score = 0
    owned_topics = len(authority)
    avg_topics = sum(repo["topics_count"] for repo in repos) / repo_count
    overtagged = sum(1 for repo in repos if repo["topics_count"] > 15)
    if owned_topics >= 3:
        topic_score += 10
    elif owned_topics >= 1:
        topic_score += 6
    if avg_topics >= 5:
        topic_score += 5
    elif avg_topics >= 3:
        topic_score += 3
    if overtagged == 0:
        topic_score += 5

    health_signals = 0
    if licenses / repo_count >= 0.8:
        health_signals += 5
    if avg_topics >= 5:
        health_signals += 5
    if sum(1 for repo in repos if repo["updated_days"] is not None and repo["updated_days"] <= 90) / repo_count >= 0.5:
        health_signals += 5
    if any(repo["stars"] > 0 for repo in repos):
        health_signals += 5

    discovery = 0
    if safe_text(str((seo_data.get("primary_keyword") or {}).get("keyword") or "")) and safe_text(str(profile.get("bio") or "")):
        discovery += 5
    elif safe_text(str(profile.get("bio") or "")):
        discovery += 3
    if len(repos) > 1:
        discovery += 5
    if profile_readme_exists:
        discovery += 5
    if any(repo["homepage_url"] for repo in repos):
        discovery += 5

    return min(completeness + branding + topic_score + health_signals + discovery, 100)


def profile_bio(identity: str, repos: list[dict[str, Any]]) -> str:
    """Build a recommended GitHub bio."""
    topics = dominant_topics(repos)
    if topics:
        focus = ", ".join(topics[:2])
        return safe_text(f"{identity.split('.', 1)[0]}. Focus: {focus}.")
    return safe_text(identity.split(".", 1)[0] + ".")


def profile_readme_draft(owner: str, profile: dict[str, Any], repos: list[dict[str, Any]], identity: str, seo_data: dict[str, Any]) -> str:
    """Render the deterministic profile README draft."""
    display_name = safe_text(str(profile.get("name") or owner), owner)
    first_line = safe_text(str(profile.get("bio") or "")) or profile_bio(identity, repos)
    primary_keyword = safe_text(str((seo_data.get("primary_keyword") or {}).get("keyword") or ""))
    intro = first_line
    if primary_keyword and primary_keyword.lower() not in intro.lower():
        intro = safe_text(f"{intro} Building around {primary_keyword}.")
    topics = dominant_topics(repos)
    if topics:
        build_narrative = f"My portfolio clusters around {', '.join(topics[:3])}, with each repo contributing to a tighter developer-facing GitHub presence."
    else:
        build_narrative = "My portfolio focuses on practical developer tooling, clean repository presentation, and durable GitHub workflows."
    feature_rows = []
    for repo in featured_repos(repos):
        link = repo["url"] or (f"https://github.com/{repo['repo']}" if "/" in repo["repo"] else "")
        stars = f" {repo['stars']} stars" if repo["stars"] else ""
        feature_rows.append(f"| [{repo['name']}]({link}) | {repo['description'] or 'Needs a stronger description.'} |{stars} |")
    if not feature_rows:
        feature_rows.append("| Project | Description pending | |")
    badges = []
    for language in dominant_languages(repos):
        slug = language.replace("#", "%23").replace("+", "%2B")
        badges.append(f"![{language}](https://img.shields.io/badge/{slug}-active-2d6cdf)")
    connect_lines = []
    if safe_text(str(profile.get("blog") or "")):
        connect_lines.append(f"- Website: {profile['blog']}")
    if safe_text(str(profile.get("twitter_username") or "")):
        connect_lines.append(f"- X/Twitter: https://x.com/{profile['twitter_username']}")
    if safe_text(str(profile.get("location") or "")):
        connect_lines.append(f"- Location: {profile['location']}")
    if not connect_lines:
        connect_lines.append(f"- GitHub: https://github.com/{owner}")
    return (
        f"# Hi, I'm {markdown_escape(display_name)}\n\n"
        f"{intro}\n\n"
        "## What I Build\n\n"
        f"{build_narrative}\n\n"
        "## Featured Projects\n\n"
        "| Project | Description | |\n"
        "|---------|-------------|---|\n"
        + "\n".join(feature_rows)
        + "\n\n## Tech Stack\n\n"
        + (" ".join(badges) if badges else "GitHub-first developer tooling")
        + "\n\n## Connect\n\n"
        + "\n".join(connect_lines)
        + "\n"
    )


def related_repo_targets(anchor: dict[str, Any], repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the best related repositories for cross-linking."""
    shared: list[tuple[int, int, dict[str, Any]]] = []
    anchor_topics = set(anchor["topics"])
    for repo in repos:
        if repo["name"] == anchor["name"]:
            continue
        overlap = len(anchor_topics & set(repo["topics"]))
        shared.append((overlap, repo["score"], repo))
    ordered = sorted(shared, key=lambda item: (item[0], item[1], item[2]["stars"]), reverse=True)
    return [item[2] for item in ordered if item[0] > 0][:3] or [item[2] for item in ordered[:2] if item[2]["name"] != anchor["name"]]


def cross_link_block(anchor: dict[str, Any], related: list[dict[str, Any]]) -> str:
    """Render the exact markdown block for one repo."""
    if not related:
        return ""
    lines = ["## Related Projects", ""]
    for repo in related:
        link = repo["url"] or (f"https://github.com/{repo['repo']}" if "/" in repo["repo"] else "")
        desc = repo["description"] or "Companion project in the same portfolio."
        lines.append(f"- **[{repo['name']}]({link})** - {desc}")
    lines.append("")
    return "\n".join(lines)


def cross_link_plan(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build cross-link recommendations for the featured repos."""
    plan: list[dict[str, Any]] = []
    for repo in featured_repos(repos)[:3]:
        related = related_repo_targets(repo, repos)
        if not related:
            continue
        block = cross_link_block(repo, related)
        for target in related:
            plan.append(
                {
                    "from": repo["name"],
                    "to": target["name"],
                    "reason": "Shared topic cluster" if set(repo["topics"]) & set(target["topics"]) else "Portfolio flagship cross-link",
                    "text": f"Link {repo['name']} to {target['name']} in a Related Projects block.",
                    "markdown_block": block,
                    "insert_after": "first major project section or before License",
                    "target_readme": f"{repo['name']}/README.md",
                }
            )
    return plan


def command_entry(label: str, command: str, reason: str, ready: bool, blocked_reason: str | None = None) -> dict[str, Any]:
    """Build one machine-readable planned command."""
    return {
        "label": label,
        "command": command,
        "reason": reason,
        "status": "ready" if ready else "pending",
        "blocked_reason": blocked_reason,
    }


def repo_topic_sync_commands(owner: str, repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build topic synchronization commands for the strongest repos."""
    core_topics = [topic for topic in dominant_topics(repos)[:3]]
    commands: list[dict[str, Any]] = []
    for repo in featured_repos(repos)[:4]:
        target_topics = list(dict.fromkeys([*repo["topics"], *core_topics]))
        if target_topics == repo["topics"] or not repo["repo"]:
            continue
        topic_flags = " ".join(f"-f names[]={quote_shell(topic)}" for topic in target_topics)
        command = f"gh api repos/{owner}/{repo['name']}/topics -X PUT {topic_flags}"
        commands.append(command_entry("Sync repo topics", command, f"Align {repo['name']} with the portfolio's core topic set.", True))
    return commands


def repo_description_commands(owner: str, repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build description rewrite commands for weak descriptions."""
    commands: list[dict[str, Any]] = []
    focus = dominant_topics(repos)[:2]
    for repo in repos:
        if len(repo["description"]) >= 40:
            continue
        suffix = f" for {', '.join(focus)}" if focus else ""
        description = safe_text(f"{repo['name'].replace('-', ' ').title()}{suffix}.")
        command = f"gh api repos/{owner}/{repo['name']} -X PATCH -f description={quote_shell(description)}"
        commands.append(command_entry("Rewrite repo description", command, f"Replace the weak description on {repo['name']} with consistent portfolio language.", True))
    return commands[:4]


def build_avatar_prompt(owner: str, repos: list[dict[str, Any]]) -> str:
    """Build a concise KIE avatar prompt."""
    topics = dominant_topics(repos)
    subject = topics[0].replace("-", " ") if topics else "developer tooling"
    initial = owner[:1].upper() if owner else "C"
    return (
        "Square 1:1 profile avatar. "
        f"A bold geometric letter \"{initial}\" fused with a minimal {subject} icon. "
        "Flat geometric style, deep navy background, cyan and teal highlights, high contrast. "
        "Simple and iconic, reads well at small sizes."
    )


def generate_avatar_asset(repo_root: Path, repo_slug: str, owner: str, repos: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate an avatar asset when runtime capabilities are available."""
    key, source = resolve_kie_api_key(repo_root)
    if not key:
        raise AssetGenerationError("KIE_API_KEY is not configured for avatar generation.")
    if not pillow_available():
        raise AssetGenerationError("Pillow is required for avatar generation.")
    assets_dir = repo_root / "assets"
    originals_dir = assets_dir / "originals"
    prompt = build_avatar_prompt(owner, repos)
    task_id = create_kie_task(key, prompt, aspect_ratio="1:1")
    record = poll_kie_task(key, task_id)
    source_path = download_binary(result_url(record), originals_dir / "avatar.png")
    avatar_path = convert_png_to_jpeg(source_path, assets_dir / "avatar.jpg")
    relative = str(avatar_path.relative_to(repo_root)).replace("\\", "/")
    return {
        "requested": True,
        "generated": True,
        "prompt": prompt,
        "path": relative,
        "source_path": str(source_path.relative_to(repo_root)).replace("\\", "/"),
        "links": {
            "local": file_uri(avatar_path),
            "raw": github_raw_url(repo_slug, relative) if "/" in repo_slug else "",
            "settings": "https://github.com/settings/profile",
        },
        "key_source": source,
    }


def build_blueprint(payload: dict[str, Any], draft_markdown: str) -> str:
    """Render the deterministic empire blueprint."""
    score = payload["portfolio_health_score"]
    delta = payload["health_delta"]
    delta_text = f" ({delta:+d})" if delta is not None else ""
    pin_list = ", ".join(payload["pinned_repos_recommended"]) or "No strong pin set yet"
    commands = payload["commands"]
    automated_lines = [f"{index}. [AUTO] `{item['command']}`" for index, item in enumerate(commands[:6], start=1)]
    if not automated_lines:
        automated_lines = ["1. [AUTO] No safe live gh commands are ready in this run."]
    manual_lines = [
        f"{len(automated_lines) + 1}. [PIN] Pin these repos in order: {pin_list}",
        f"{len(automated_lines) + 2}. [PHOTO] Upload the generated avatar if you want a new profile photo: https://github.com/settings/profile",
    ]
    tl_dr = (
        f"**TL;DR:** {payload['identity']} "
        f"The biggest portfolio gap is {payload['biggest_gap']}. "
        f"This headless pass built a profile README draft, cross-link plan, and portfolio cache. "
        f"**Portfolio Health: {score}/100{delta_text}.**"
    )
    return (
        "# Empire Blueprint\n\n"
        f"{tl_dr}\n\n"
        "## Build Plan\n\n"
        "### Automated\n"
        + "\n".join(automated_lines)
        + "\n\n### Manual\n"
        + "\n".join(manual_lines)
        + "\n\n## Profile README Draft\n\n"
        + draft_markdown
        + "\n\n## Pinned Repos\n\n"
        + pin_list
        + "\n"
    )


def build_report(payload: dict[str, Any]) -> str:
    """Render the deterministic empire report."""
    repo_rows = []
    for repo in payload["portfolio"]:
        repo_rows.append(
            f"| {markdown_escape(repo['name'])} | {repo['stars']} | {markdown_escape(repo['language'] or 'Unknown')} | {repo['topics_count']} | {markdown_escape(repo['license'] or 'Missing')} | {repo['updated_days'] if repo['updated_days'] is not None else 'Unknown'} days | {repo['health']} |"
        )
    repo_table = "\n".join(repo_rows) or "| None | 0 | Unknown | 0 | Missing | Unknown | Weak |"
    authority_lines = "\n".join(
        f"- `{item['topic']}` - {item['repos']} repos ({item['strength']})"
        for item in payload["topic_authority"]
    ) or "- No multi-repo topic authority yet."
    warning_lines = "\n".join(f"- {item}" for item in payload["warnings"]) or "- None"
    blocked_lines = "\n".join(f"- {item}" for item in payload["blocked"]) or "- None"
    return f"""# GitHub Empire Report

- **Owner:** {payload['portfolio_owner']}
- **Generated at:** {payload['timestamp']}
- **Mode:** {payload['mode']}
- **Portfolio health:** {payload['portfolio_health_score']}/100
- **Portfolio size:** {payload['portfolio_size']}

## Identity

{payload['identity']}

## Portfolio Summary

| Repo | Stars | Language | Topics | License | Updated | Health |
|------|------:|----------|------:|---------|---------|--------|
{repo_table}

## Topic Authority

{authority_lines}

## Branding Assessment

- Description consistency: {payload['branding_assessment']['description_consistency']}
- Homepage coverage: {payload['branding_assessment']['homepage_coverage']}
- License consistency: {payload['branding_assessment']['license_consistency']}
- Topic consistency: {payload['branding_assessment']['topic_consistency']}
- Overall: {payload['branding_assessment']['overall']}

## Recommended Pins

- {", ".join(payload['pinned_repos_recommended']) or 'No strong pin set yet.'}

## Warnings

{warning_lines}

## Blocked / Manual

{blocked_lines}
"""


def biggest_gap(repos: list[dict[str, Any]], branding: dict[str, Any], profile_readme_exists: bool, profile: dict[str, Any]) -> str:
    """Return the single biggest portfolio gap for the TL;DR."""
    if not safe_text(str(profile.get("bio") or "")):
        return "an empty or weak public bio"
    if not profile_readme_exists:
        return "a missing profile README"
    if branding["overall"] == "Weak":
        return "inconsistent repo branding across the portfolio"
    if len(repos) > 1 and not any(repo["homepage_url"] for repo in repos):
        return "missing destination links from the repos back to your broader presence"
    return "missing cross-links and topic authority between related repos"


def build_empire_payload(repo_root: Path, username: str) -> tuple[dict[str, Any], str]:
    """Build the deterministic empire payload and profile README draft."""
    owner = portfolio_owner(repo_root, username)
    local_repo = build_local_repo_entry(repo_root)
    remote_rows = gh_repo_list(owner) if owner else []
    repos = [build_remote_repo_entry(row) for row in remote_rows] if remote_rows else []
    if not any(repo["name"] == local_repo["name"] for repo in repos):
        repos.append(local_repo)
    else:
        repos = [local_repo if repo["name"] == local_repo["name"] else repo for repo in repos]
    repos = sorted({repo["name"]: repo for repo in repos}.values(), key=lambda item: item["name"].lower())

    previous = read_repo_cache(repo_root, "empire-data.json") or {}
    seo_data = read_repo_cache(repo_root, "seo-data.json") or {}
    profile = gh_user_profile(owner) if owner else {}
    profile_readme_exists = any(repo["name"].lower() == owner.lower() for repo in repos) if owner else False
    authority = topic_authority_map(repos)
    identity = infer_identity(owner or local_repo["name"], repos, seo_data)
    branding = brand_consistency(repos)
    health_score = portfolio_health(repos, profile, profile_readme_exists, authority, seo_data)
    previous_score = previous.get("portfolio_health_score")
    health_delta = health_score - int(previous_score) if isinstance(previous_score, int) else None
    profile_readme = profile_readme_draft(owner or local_repo["name"], profile, repos, identity, seo_data)
    links = cross_link_plan(repos)
    login = current_login()
    can_mutate_owner = bool(owner and login and owner.lower() == login.lower())
    recommended_bio = profile_bio(identity, repos)
    profile_commands: list[dict[str, Any]] = []
    if recommended_bio and recommended_bio != safe_text(str(profile.get("bio") or "")):
        command = f"gh api user -X PATCH -f bio={quote_shell(recommended_bio)}"
        profile_commands.append(
            command_entry(
                "Set profile bio",
                command,
                "Align the public profile bio with the portfolio identity.",
                ready=can_mutate_owner,
                blocked_reason=None if can_mutate_owner else "GitHub auth is missing or does not match the portfolio owner.",
            )
        )
    if owner and not profile_readme_exists:
        command = f"gh repo create {owner}/{owner} --public --description {quote_shell('Profile README')}"
        profile_commands.append(
            command_entry(
                "Create profile README repo",
                command,
                "Create the special profile README repository.",
                ready=can_mutate_owner,
                blocked_reason=None if can_mutate_owner else "GitHub auth is missing or does not match the portfolio owner.",
            )
        )
    repo_commands = repo_topic_sync_commands(owner, repos) + repo_description_commands(owner, repos) if owner else []
    if not can_mutate_owner:
        for entry in repo_commands:
            entry["status"] = "pending"
            entry["blocked_reason"] = "GitHub auth is missing or does not match the portfolio owner."
    biggest = biggest_gap(repos, branding, profile_readme_exists, profile)
    payload = {
        "cache_type": "empire-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": "plan",
        "portfolio_owner": owner or local_repo["name"],
        "anchor_repo": local_repo["repo"],
        "portfolio_size": len(repos),
        "portfolio_health_score": health_score,
        "previous_portfolio_health_score": previous_score if isinstance(previous_score, int) else None,
        "health_delta": health_delta,
        "average_score": int(round(sum(repo["score"] for repo in repos) / max(len(repos), 1))),
        "identity": identity,
        "biggest_gap": biggest,
        "portfolio": repos,
        "per_repo_metrics": {
            repo["name"]: {
                "stars": repo["stars"],
                "views": 0,
                "topics_count": repo["topics_count"],
                "topics": repo["topics"],
                "license": repo["license"],
                "language": repo["language"],
                "description": repo["description"],
                "homepage_url": repo["homepage_url"],
                "score": repo["score"],
                "health": repo["health"],
            }
            for repo in repos
        },
        "topic_authority": authority,
        "pinned_repos_recommended": pinned_repos(repos),
        "cross_linking": links,
        "branding_assessment": branding,
        "profile_readme_status": "exists" if profile_readme_exists else "missing",
        "profile_fields_current": {
            "bio": safe_text(str(profile.get("bio") or "")),
            "blog": safe_text(str(profile.get("blog") or "")),
            "company": safe_text(str(profile.get("company") or "")),
            "location": safe_text(str(profile.get("location") or "")),
            "twitter_username": safe_text(str(profile.get("twitter_username") or "")),
        },
        "profile_fields_set": {
            "bio": recommended_bio,
        },
        "commands": profile_commands + repo_commands,
        "actions_executed": [],
        "growth_snapshot": {
            repo["name"]: {"stars": repo["stars"], "views": 0, "topics_count": repo["topics_count"]}
            for repo in repos
        },
        "avatar": {
            "requested": False,
            "generated": False,
            "prompt": "",
            "path": "",
            "source_path": "",
            "links": {"local": "", "raw": "", "settings": "https://github.com/settings/profile"},
            "key_source": "",
        },
        "warnings": [],
        "blocked": [
            f"Pin repo order remains a GitHub web UI step: https://github.com/{owner}?tab=repositories" if owner else "Pin repo order remains a GitHub web UI step.",
            "Profile photo upload remains a GitHub web UI step even when the avatar asset is generated.",
        ],
    }
    if not gh_auth_ok():
        payload["warnings"].append("GitHub CLI is not authenticated. Portfolio analysis is limited to the local repo plus any cached data.")
    elif not remote_rows:
        payload["warnings"].append("No public repo list was returned through gh, so the portfolio view is anchored to the local repo.")
    if not owner:
        payload["warnings"].append("No portfolio owner could be inferred. Commands and profile recommendations are local-only.")
    if (seo_data.get("analysis_mode") or "") == "fallback":
        payload["warnings"].append("Portfolio keyword language is using fallback SEO cache data without live DataForSEO verification.")
    if payload["portfolio_size"] <= 1:
        payload["warnings"].append("Portfolio analysis only sees one repo. Cross-linking and pin recommendations are low-confidence until more repos are visible.")
    return payload, profile_readme


@dataclass
class EmpireBundle:
    """Structured empire output."""

    empire_data: dict[str, Any]
    report_markdown: str
    blueprint_markdown: str
    profile_readme_markdown: str


def run_empire(repo_root: Path, username: str = "", generate_avatar: bool = False) -> EmpireBundle:
    """Build the deterministic empire plan and optionally generate an avatar asset."""
    empire_data, profile_readme = build_empire_payload(repo_root, username)
    if generate_avatar:
        try:
            avatar = generate_avatar_asset(
                repo_root,
                empire_data["anchor_repo"],
                empire_data["portfolio_owner"],
                empire_data["portfolio"],
            )
            empire_data["mode"] = "assets"
            empire_data["avatar"] = avatar
        except AssetGenerationError as exc:
            empire_data["warnings"].append(str(exc))
            empire_data["blocked"].append("Avatar generation could not complete, so profile photo work remains manual.")
    blueprint_markdown = build_blueprint(empire_data, profile_readme)
    report_markdown = build_report(empire_data)
    return EmpireBundle(
        empire_data=empire_data,
        report_markdown=report_markdown,
        blueprint_markdown=blueprint_markdown,
        profile_readme_markdown=profile_readme,
    )


def write_empire_artifacts(repo_root: Path, bundle: EmpireBundle) -> dict[str, str]:
    """Write empire cache and report artifacts for one run."""
    slug = slugify(bundle.empire_data["portfolio_owner"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    empire_cache_path = write_repo_cache(repo_root, "empire-data.json", bundle.empire_data)
    report_path = out_dir / "EMPIRE-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    blueprint_path = out_dir / "EMPIRE-BLUEPRINT.md"
    blueprint_path.write_text(bundle.blueprint_markdown, encoding="utf-8")
    draft_path = out_dir / "PROFILE-README-DRAFT.md"
    draft_path.write_text(bundle.profile_readme_markdown, encoding="utf-8")
    summary_path = out_dir / "EMPIRE-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "empire_cache_path": str(empire_cache_path),
                "mode": bundle.empire_data["mode"],
                "portfolio_owner": bundle.empire_data["portfolio_owner"],
                "portfolio_size": bundle.empire_data["portfolio_size"],
                "portfolio_health_score": bundle.empire_data["portfolio_health_score"],
                "health_delta": bundle.empire_data["health_delta"],
                "pinned_repos_recommended": bundle.empire_data["pinned_repos_recommended"],
                "avatar_generated": bundle.empire_data["avatar"]["generated"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "empire_cache": str(empire_cache_path),
        "report": str(report_path),
        "blueprint": str(blueprint_path),
        "profile_readme_draft": str(draft_path),
        "summary_json": str(summary_path),
    }
