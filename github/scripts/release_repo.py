#!/usr/bin/env python3
"""Deterministic release planning for Legends GitHub."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_repo import detect_repo_type, load_readme, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_auth_ok, gh_release_rows, repo_slug_from_git, run_command
from runtime_paths import repo_output_dir


SEMVER_RE = re.compile(r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-(?P<pre>[0-9A-Za-z.-]+))?$")
CHANGELOG_VERSION_RE = re.compile(r"^## \[(?!Unreleased)(?P<version>[^\]]+)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?$", re.MULTILINE)
VERSION_BADGE_RE = re.compile(r"img\.shields\.io/github/v/release", re.IGNORECASE)
CI_BADGE_RE = re.compile(r"(actions/workflow/status|badge\.svg)", re.IGNORECASE)
LICENSE_BADGE_RE = re.compile(r"license", re.IGNORECASE)

CANONICAL_RELEASE_YML = """changelog:
  exclude:
    labels:
      - ignore-for-release
    authors:
      - dependabot
      - dependabot[bot]
  categories:
    - title: Breaking Changes
      labels:
        - breaking
    - title: New Features
      labels:
        - enhancement
        - feature
    - title: Bug Fixes
      labels:
        - bug
        - fix
    - title: Security
      labels:
        - security
    - title: Documentation
      labels:
        - docs
        - documentation
    - title: Other Changes
      labels:
        - "*"
"""


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_utc() -> str:
    """Return today's UTC date for changelog entries."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def normalize_version(value: str) -> str:
    """Normalize a version-like value by stripping the leading v."""
    return value.strip().lstrip("v").strip()


def display_version(value: str) -> str:
    """Render a normalized semantic version with a leading v."""
    normalized = normalize_version(value)
    return f"v{normalized}" if normalized else ""


def parse_semver(value: str) -> tuple[int, int, int, str] | None:
    """Parse a semantic version string."""
    match = SEMVER_RE.match(value.strip())
    if not match:
        return None
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        match.group("pre") or "",
    )


def semver_sort_key(value: str) -> tuple[int, int, int, int, str]:
    """Return a sortable tuple for semantic versions."""
    parsed = parse_semver(value)
    if not parsed:
        return (-1, -1, -1, -1, value)
    major, minor, patch, pre = parsed
    return (major, minor, patch, 0 if pre else 1, pre)


def highest_version(*values: str) -> str:
    """Return the highest semantic version among the given values."""
    candidates = [normalize_version(value) for value in values if parse_semver(normalize_version(value))]
    if not candidates:
        return ""
    return max(candidates, key=semver_sort_key)


def classify_commit(subject: str) -> tuple[str, str]:
    """Classify one commit subject and the associated version impact."""
    lowered = subject.lower().strip()
    if not lowered:
        return "other", "none"
    if "breaking change" in lowered or re.search(r"\b\w+!:", lowered) or "drop support" in lowered:
        return "breaking", "major"
    if any(token in lowered for token in ("security", "vulnerability", "cve-")):
        return "security", "patch"
    if re.match(r"^(feat|feature)(\(.+\))?:", lowered) or any(
        phrase in lowered for phrase in (" add ", "adds ", "introduce", "support ", "supports ", "implement", "implements ")
    ):
        return "feature", "minor"
    if re.match(r"^(fix|bugfix)(\(.+\))?:", lowered) or any(
        phrase in lowered for phrase in (" fix ", "fixes ", "bug", "restore", "repair", "correct", "harden", "hardening")
    ):
        return "fix", "patch"
    if re.match(r"^docs?(\(.+\))?:", lowered):
        return "docs", "none"
    if re.match(r"^(test|tests)(\(.+\))?:", lowered):
        return "test", "none"
    if re.match(r"^refactor(\(.+\))?:", lowered):
        return "refactor", "none"
    if re.match(r"^(chore|build|ci)(\(.+\))?:", lowered):
        return "chore", "none"
    return "other", "none"


def clean_commit_subject(subject: str) -> str:
    """Normalize one git subject for report output."""
    cleaned = re.sub(r"^(feat|feature|fix|docs|chore|refactor|test|tests|build|ci)(\(.+\))?:\s*", "", subject, flags=re.I)
    cleaned = cleaned.strip(" -")
    if not cleaned:
        return subject.strip()
    return cleaned[0].upper() + cleaned[1:]


def git_output(repo_root: Path, *args: str) -> str:
    """Run a git command and return stdout."""
    result = run_command(["git", *args], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_latest_tag(repo_root: Path) -> str:
    """Return the latest reachable tag."""
    return git_output(repo_root, "describe", "--tags", "--abbrev=0")


def git_commit_count(repo_root: Path, rev_range: str | None = None) -> int:
    """Return commit count for the full repo or a revision range."""
    args = ["rev-list", "--count"]
    args.append(rev_range or "HEAD")
    value = git_output(repo_root, *args)
    try:
        return int(value)
    except ValueError:
        return 0


def git_commit_log(repo_root: Path, rev_range: str | None = None) -> list[dict[str, str]]:
    """Return commit summaries for the repo or a revision range."""
    args = ["log", "--format=%H%x09%s%x09%cI"]
    if rev_range:
        args.append(rev_range)
    output = git_output(repo_root, *args)
    commits: list[dict[str, str]] = []
    for line in output.splitlines():
        sha, _, rest = line.partition("\t")
        subject, _, committed_at = rest.partition("\t")
        if sha and subject:
            commits.append(
                {
                    "sha": sha,
                    "short_sha": sha[:7],
                    "subject": subject.strip(),
                    "committed_at": committed_at.strip(),
                }
            )
    return commits


def git_first_commit_date(repo_root: Path) -> str:
    """Return the oldest commit date."""
    return git_output(repo_root, "log", "--reverse", "--format=%cI", "--max-count=1")


def git_tag_commit_date(repo_root: Path, tag: str) -> str:
    """Return the commit date for a tag."""
    return git_output(repo_root, "log", "-1", "--format=%cI", tag)


def iso_to_date(value: str) -> str:
    """Convert ISO 8601 datetime to YYYY-MM-DD when possible."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def days_since(value: str) -> int | None:
    """Return days elapsed since an ISO timestamp or date string."""
    if not value:
        return None
    if value.startswith("0001-01-01"):
        return None
    try:
        if "T" in value:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return max((datetime.now(timezone.utc) - dt).days, 0)


def changelog_versions(text: str) -> list[dict[str, str]]:
    """Extract release headings from a changelog."""
    return [match.groupdict(default="") for match in CHANGELOG_VERSION_RE.finditer(text)]


def parse_badge_state(readme: str) -> dict[str, bool]:
    """Return coarse badge presence for the top of the README."""
    head = "\n".join(readme.splitlines()[:15])
    return {
        "version": bool(VERSION_BADGE_RE.search(head)),
        "ci": bool(CI_BADGE_RE.search(head)),
        "license": bool(LICENSE_BADGE_RE.search(head)),
    }


def list_workflows(repo_root: Path) -> list[str]:
    """Return workflow file paths."""
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.exists():
        return []
    return sorted(str(path.relative_to(repo_root)).replace("\\", "/") for path in workflows_dir.glob("*.y*ml"))


def detect_registry(repo_root: Path) -> dict[str, str]:
    """Return a best-effort package registry assessment."""
    table = [
        ("package.json", "npm / GitHub Packages", "npm publish", "package"),
        ("pyproject.toml", "PyPI", "python -m build && twine upload dist/*", "package"),
        ("setup.py", "PyPI", "python -m build && twine upload dist/*", "package"),
        ("Cargo.toml", "crates.io", "cargo publish", "package"),
        ("go.mod", "Go module proxy", "git tag push", "package"),
        ("Dockerfile", "GHCR / Docker Hub", "docker push", "container"),
        (".csproj", "NuGet", "dotnet nuget push", "package"),
    ]
    for relative, registry, command, kind in table:
        if relative.startswith("."):
            if any(repo_root.glob(f"**/*{relative}")):
                return {"registry": registry, "publish_command": command, "kind": kind, "path": relative}
        elif (repo_root / relative).exists():
            return {"registry": registry, "publish_command": command, "kind": kind, "path": relative}
    return {"registry": "N/A", "publish_command": "", "kind": "none", "path": ""}


def detect_publish_workflows(repo_root: Path) -> list[str]:
    """Return workflows that look like package publishing."""
    matches: list[str] = []
    for relative in list_workflows(repo_root):
        text = (repo_root / relative).read_text(encoding="utf-8", errors="replace").lower()
        if any(token in text for token in ("publish", "registry", "npm publish", "docker push", "twine", "cargo publish")):
            matches.append(relative)
    return matches


def release_cadence(dates: list[str]) -> str:
    """Classify cadence from release dates."""
    parsed = [datetime.strptime(value, "%Y-%m-%d") for value in dates if value]
    if len(parsed) < 2:
        return "None" if not parsed else "Irregular"
    intervals = [(parsed[index] - parsed[index + 1]).days for index in range(len(parsed) - 1)]
    return "Regular" if max(intervals) - min(intervals) <= 45 else "Irregular"


def status_for_commits(count: int) -> str:
    """Return dashboard status for unreleased commit count."""
    if count >= 50:
        return "OVERDUE"
    if count >= 20:
        return "REVIEW"
    return "OK"


def status_for_days(count: int | None) -> str:
    """Return dashboard status for release recency."""
    if count is None:
        return "MISSING"
    if count >= 180:
        return "DORMANT"
    if count >= 90:
        return "STALE"
    return "OK"


def infer_first_version(repo_root: Path) -> str:
    """Choose 0.1.0 or 1.0.0 for a first release."""
    file_signals = [
        (repo_root / "README.md").exists(),
        (repo_root / "LICENSE").exists(),
        (repo_root / ".github" / "workflows" / "ci.yml").exists(),
        (repo_root / "CONTRIBUTING.md").exists(),
    ]
    return "1.0.0" if sum(1 for signal in file_signals if signal) >= 3 and git_commit_count(repo_root) >= 5 else "0.1.0"


def bump_version(current: str, impact: str, repo_root: Path) -> str:
    """Return the next semantic version for the proposed release."""
    normalized = normalize_version(current)
    parsed = parse_semver(normalized)
    if not parsed:
        return infer_first_version(repo_root)
    major, minor, patch, _ = parsed
    if impact == "major":
        return f"{major + 1}.0.0"
    if impact == "minor":
        return f"{major}.{minor + 1}.0"
    if impact == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return normalized


def theme_title(commits: list[dict[str, str]], highest_impact: str, first_release: bool) -> str:
    """Return a human-readable release title."""
    if first_release:
        return "Initial Release"
    subjects = " ".join(commit["subject"].lower() for commit in commits)
    if "security" in subjects:
        return "Security Hardening"
    if any(token in subjects for token in ("headless", "api", "deterministic")):
        return "API and Headless Hardening"
    if "readme" in subjects:
        return "README and Documentation Updates"
    if highest_impact == "major":
        return "Breaking Changes"
    if highest_impact == "minor":
        return "Feature Updates"
    if highest_impact == "patch":
        return "Maintenance and Fixes"
    return "Maintenance Update"


def changelog_sections(commits: list[dict[str, str]]) -> dict[str, list[str]]:
    """Group commits into Keep a Changelog sections."""
    sections = {
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Security": [],
    }
    for commit in commits:
        category, _ = classify_commit(commit["subject"])
        summary = clean_commit_subject(commit["subject"])
        if category == "feature":
            sections["Added"].append(summary)
        elif category == "breaking":
            sections["Changed"].append(f"Breaking: {summary}")
        elif category == "fix":
            sections["Fixed"].append(summary)
        elif category == "security":
            sections["Security"].append(summary)
        elif category in {"refactor", "other"}:
            sections["Changed"].append(summary)
    return {name: values for name, values in sections.items() if values}


def build_changelog_entry(version: str, commits: list[dict[str, str]]) -> str:
    """Render a Keep a Changelog entry."""
    sections = changelog_sections(commits)
    if not sections:
        sections = {"Changed": ["Maintenance-only release with no user-facing changes."]}
    lines = [f"## [{normalize_version(version)}] - {today_utc()}", ""]
    for title, items in sections.items():
        lines.append(f"### {title}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_release_notes(version: str, title: str, commits: list[dict[str, str]], highest_impact: str) -> str:
    """Render concise release notes."""
    count = len(commits)
    if count == 0:
        return f"{display_version(version)} - {title}\n\nNo new user-facing changes are queued for release."
    highlights = [clean_commit_subject(commit["subject"]) for commit in commits[:5]]
    summary = ", ".join(highlights[:3])
    impact_phrase = {
        "major": "breaking changes",
        "minor": "new features",
        "patch": "fixes and maintenance updates",
        "none": "maintenance updates",
    }[highest_impact]
    return (
        f"{display_version(version)} - {title}\n\n"
        f"This release packages {count} unreleased commits centered on {impact_phrase}. "
        f"Highlights include {summary}."
    )


def recommended_badges(repo_slug: str, repo_type: str, current_badges: dict[str, bool]) -> list[str]:
    """Return recommended badge markdown strings."""
    owner_repo = repo_slug if "/" in repo_slug else "owner/repo"
    badges: list[str] = []
    if repo_type in {"Skill/Plugin", "CLI Tool", "Library/Package", "Framework", "API/Service"}:
        badges.append(f"[![Version](https://img.shields.io/github/v/release/{owner_repo})](https://github.com/{owner_repo}/releases)")
    badges.append(
        f"[![CI](https://img.shields.io/github/actions/workflow/status/{owner_repo}/ci.yml?label=CI)]"
        f"(https://github.com/{owner_repo}/actions)"
    )
    badges.append(f"[![License](https://img.shields.io/github/license/{owner_repo})](https://github.com/{owner_repo}/blob/main/LICENSE)")
    if repo_type in {"Framework", "Application"}:
        badges.append(f"[![Last Commit](https://img.shields.io/github/last-commit/{owner_repo})](https://github.com/{owner_repo}/commits/main)")
    unique: list[str] = []
    for badge in badges:
        if badge not in unique:
            unique.append(badge)
    return unique


def build_changelog_file(repo_slug: str, existing_text: str, draft_entry: str, version: str) -> str:
    """Return the full changelog content after applying deterministic updates."""
    version_heading = f"## [{normalize_version(version)}]"
    if not existing_text.strip():
        lines = [
            "# Changelog",
            "",
            "All notable changes to this project will be documented in this file.",
            "",
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),",
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
            "",
            "## [Unreleased]",
            "",
            draft_entry.strip(),
            "",
        ]
        if "/" in repo_slug:
            lines.extend(
                [
                    f"[Unreleased]: https://github.com/{repo_slug}/compare/{display_version(version)}...HEAD",
                    f"[{normalize_version(version)}]: https://github.com/{repo_slug}/releases/tag/{display_version(version)}",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"

    text = existing_text
    if "## [Unreleased]" not in text:
        marker = "and this project adheres"
        if marker in text:
            text = text.replace(marker + ".", marker + ".\n\n## [Unreleased]\n", 1)
        else:
            text = text.rstrip() + "\n\n## [Unreleased]\n"
    if version_heading not in text:
        text = text.replace("## [Unreleased]\n", f"## [Unreleased]\n\n{draft_entry.strip()}\n\n", 1)
    if "/" in repo_slug:
        lines = text.rstrip().splitlines()
        release_link = f"[{normalize_version(version)}]: https://github.com/{repo_slug}/releases/tag/{display_version(version)}"
        unreleased_link = f"[Unreleased]: https://github.com/{repo_slug}/compare/{display_version(version)}...HEAD"
        if not any(line.startswith("[Unreleased]:") for line in lines):
            lines.append(unreleased_link)
        if release_link not in lines:
            lines.append(release_link)
        return "\n".join(lines).rstrip() + "\n"
    return text.rstrip() + "\n"


def create_github_release(repo_slug: str, version: str, title: str, notes: str, publish: bool) -> dict[str, Any]:
    """Create a draft or published GitHub release via gh."""
    command = [
        "gh",
        "release",
        "create",
        display_version(version),
        "--repo",
        repo_slug,
        "--title",
        f"{display_version(version)} - {title}",
        "--notes",
        notes,
    ]
    if not publish:
        command.append("--draft")
    result = run_command(command, check=False)
    return {
        "requested": True,
        "publish": publish,
        "status": "created" if result.returncode == 0 else "failed",
        "command": " ".join(command),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def update_github_release(repo_slug: str, version: str, title: str, notes: str, publish: bool) -> dict[str, Any]:
    """Update an existing GitHub release via gh."""
    command = [
        "gh",
        "release",
        "edit",
        display_version(version),
        "--repo",
        repo_slug,
        "--title",
        f"{display_version(version)} - {title}",
        "--notes",
        notes,
        "--target",
        "HEAD",
    ]
    command.append("--draft=false" if publish else "--draft")
    result = run_command(command, check=False)
    return {
        "requested": True,
        "publish": publish,
        "status": "updated" if result.returncode == 0 else "failed",
        "command": " ".join(command),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def build_snapshot(repo_root: Path) -> dict[str, Any]:
    """Gather release-related repo signals."""
    repo_context = read_repo_cache(repo_root, "repo-context.json") or {}
    repo_slug = str(repo_context.get("repo") or repo_slug_from_git(repo_root) or repo_root.name)
    changelog_path = repo_root / "CHANGELOG.md"
    readme, _ = load_readme(repo_root)
    changelog_text = changelog_path.read_text(encoding="utf-8", errors="replace") if changelog_path.exists() else ""
    changelog_entries = changelog_versions(changelog_text)
    latest_changelog_version = changelog_entries[0]["version"] if changelog_entries else ""
    latest_tag = git_latest_tag(repo_root)
    releases = gh_release_rows(repo_slug, limit=10) if "/" in repo_slug else []
    latest_release = releases[0]["tag"] if releases else ""
    baseline = highest_version(latest_release, latest_tag, latest_changelog_version)
    rev_range = f"{display_version(baseline)}..HEAD" if baseline else None
    commits = git_commit_log(repo_root, rev_range=rev_range)
    workflows = list_workflows(repo_root)
    registry = detect_registry(repo_root)
    badge_state = parse_badge_state(readme)
    publish_workflows = detect_publish_workflows(repo_root)
    release_published = releases[0]["published"] if releases else ""
    if release_published.startswith("0001-01-01"):
        release_published = ""
    latest_release_date = release_published or (git_tag_commit_date(repo_root, latest_tag) if latest_tag else "")
    first_commit_date = git_first_commit_date(repo_root)
    cadence_dates = [iso_to_date(row.get("published", "")) for row in releases if row.get("published")]
    if latest_tag and not cadence_dates:
        cadence_dates = [iso_to_date(git_tag_commit_date(repo_root, latest_tag))]
    return {
        "repo": repo_slug,
        "repo_root": str(repo_root),
        "repo_type": str(repo_context.get("repo_type") or detect_repo_type(repo_root)),
        "intent": str(repo_context.get("intent") or ""),
        "changelog_text": changelog_text,
        "latest_changelog_version": latest_changelog_version,
        "changelog_entries": changelog_entries,
        "latest_tag": latest_tag,
        "latest_release": latest_release,
        "latest_release_type": releases[0]["type"] if releases else "",
        "latest_release_date": latest_release_date,
        "commits": commits,
        "commits_since_release": len(commits) if baseline else git_commit_count(repo_root),
        "total_commit_count": git_commit_count(repo_root),
        "first_commit_date": first_commit_date,
        "workflow_files": workflows,
        "release_yml_exists": (repo_root / ".github" / "release.yml").exists(),
        "badge_state": badge_state,
        "registry": registry,
        "publish_workflows": publish_workflows,
        "releases": releases,
        "cadence": release_cadence(cadence_dates),
        "version_match": bool(
            baseline
            and all(
                not value or normalize_version(value) == normalize_version(baseline)
                for value in (latest_release, latest_tag, latest_changelog_version)
            )
        ),
    }


def build_release_payload(repo_root: Path) -> dict[str, Any]:
    """Build deterministic release recommendations for a repo."""
    snapshot = build_snapshot(repo_root)
    commits = snapshot["commits"]
    counts = {
        "breaking": 0,
        "feature": 0,
        "fix": 0,
        "security": 0,
        "docs": 0,
        "chore": 0,
        "refactor": 0,
        "test": 0,
        "other": 0,
    }
    highest_impact = "none"
    impact_rank = {"none": 0, "patch": 1, "minor": 2, "major": 3}
    for commit in commits:
        category, impact = classify_commit(commit["subject"])
        counts[category] = counts.get(category, 0) + 1
        if impact_rank[impact] > impact_rank[highest_impact]:
            highest_impact = impact

    base_version = highest_version(snapshot["latest_release"], snapshot["latest_tag"], snapshot["latest_changelog_version"])
    first_release = not base_version
    draft_refresh = bool(snapshot["latest_release"]) and snapshot["latest_release_type"].lower() == "draft"
    if draft_refresh and base_version:
        recommended_version = normalize_version(base_version)
    else:
        recommended_version = bump_version(base_version, highest_impact, repo_root) if (first_release or commits) else normalize_version(base_version)
    release_title = theme_title(commits, highest_impact, first_release)
    draft_entry = build_changelog_entry(recommended_version, commits)
    release_notes = build_release_notes(recommended_version, release_title, commits, highest_impact)
    badges = recommended_badges(snapshot["repo"], snapshot["repo_type"], snapshot["badge_state"])

    if first_release:
        verdict = "first_release"
        proposal_kind = "first_release"
    elif draft_refresh:
        verdict = "draft_refresh_recommended"
        proposal_kind = "draft_refresh"
    elif snapshot["latest_changelog_version"] and snapshot["latest_release"] and normalize_version(snapshot["latest_changelog_version"]) != normalize_version(snapshot["latest_release"]):
        verdict = "catch_up"
        proposal_kind = "catch_up"
    elif snapshot["commits_since_release"] == 0 or highest_impact == "none":
        verdict = "up_to_date"
        proposal_kind = "up_to_date"
    else:
        verdict = "release_recommended"
        proposal_kind = "next_release"

    warnings: list[str] = []
    blocked: list[str] = []
    if not snapshot["version_match"] and base_version:
        warnings.append("CHANGELOG, git tags, and GitHub Releases are not fully aligned.")
    if snapshot["latest_release_type"].lower() == "draft":
        warnings.append(f"Latest GitHub release {snapshot['latest_release']} is still a draft.")
    if draft_refresh and snapshot["commits_since_release"] > 0:
        warnings.append(
            f"{display_version(recommended_version)} exists only as a draft release and {snapshot['commits_since_release']} commits landed after that tag. "
            "Refresh the draft instead of bumping the version if the release has not been publicized."
        )
    if "/" not in snapshot["repo"]:
        warnings.append("No GitHub remote detected. Deterministic release planning is using local tags and files only.")
    if snapshot["registry"]["kind"] == "none":
        warnings.append("No package registry is applicable for this repository type.")
    if not gh_auth_ok():
        warnings.append("GitHub CLI is not authenticated, so live release creation is unavailable.")
    if not snapshot["release_yml_exists"]:
        blocked.append("release.yml is missing until file writes are enabled.")
    if not snapshot["badge_state"]["version"]:
        blocked.append("README is missing a version badge recommendation.")

    latest_release_age = days_since(snapshot["latest_release_date"])
    changelog_state = "OK" if snapshot["latest_changelog_version"] else "MISSING"
    latest_release_state = "MISSING" if not snapshot["latest_release"] and not snapshot["latest_tag"] else status_for_days(latest_release_age)
    version_match_state = "OK" if snapshot["version_match"] else "MISMATCH"
    versioning_scheme = "semver" if parse_semver(base_version or recommended_version) else "unknown"

    summary_lines = []
    if proposal_kind == "first_release":
        summary_lines.append(
            f"Based on {snapshot['total_commit_count']} commits and the current repo infrastructure, I recommend the first release {display_version(recommended_version)}."
        )
    elif proposal_kind == "draft_refresh":
        summary_lines.append(
            f"{display_version(recommended_version)} already exists as a draft release. Refresh that draft instead of bumping the version."
        )
    elif proposal_kind == "catch_up":
        summary_lines.append(
            f"Your changelog and GitHub Releases disagree. Publish the missing release path around {display_version(recommended_version)} to reconcile history."
        )
    elif proposal_kind == "up_to_date":
        summary_lines.append(
            f"No release is needed right now. There are {snapshot['commits_since_release']} commits since {display_version(base_version)}, but none justify a new version."
        )
    else:
        summary_lines.append(
            f"{snapshot['commits_since_release']} commits have landed since {display_version(base_version)}. The highest-impact change level is {highest_impact.upper()}."
        )
    summary_lines.append(f"Recommended title: {display_version(recommended_version)} - {release_title}")

    payload = {
        "cache_type": "releases-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": "plan",
        "repo": snapshot["repo"],
        "repo_root": snapshot["repo_root"],
        "repo_type": snapshot["repo_type"],
        "intent": snapshot["intent"],
        "latest_version": display_version(base_version),
        "latest_release": snapshot["latest_release"],
        "latest_tag": snapshot["latest_tag"],
        "latest_release_date": snapshot["latest_release_date"],
        "latest_release_age_days": latest_release_age,
        "changelog_created": False,
        "release_yml_created": False,
        "changelog_latest_version": snapshot["latest_changelog_version"],
        "version_match": snapshot["version_match"],
        "commits_since_release": snapshot["commits_since_release"],
        "total_commit_count": snapshot["total_commit_count"],
        "release_verdict": verdict,
        "recommended_next_version": display_version(recommended_version),
        "recommended_title": f"{display_version(recommended_version)} - {release_title}",
        "release_notes": release_notes,
        "draft_changelog_entry": draft_entry,
        "badges": badges,
        "badge_state": snapshot["badge_state"],
        "versioning_scheme": versioning_scheme,
        "release_cadence": snapshot["cadence"],
        "package_distribution": snapshot["registry"],
        "publish_workflows": snapshot["publish_workflows"],
        "workflow_files": snapshot["workflow_files"],
        "release_yml_path": ".github/release.yml",
        "proposal_kind": proposal_kind,
        "draft_refresh": draft_refresh,
        "proposal_summary": summary_lines,
        "proposal_markdown": "",
        "dashboard": {
            "latest_release": {"value": display_version(base_version) or "None", "status": latest_release_state},
            "latest_changelog_version": {"value": snapshot["latest_changelog_version"] or "None", "status": changelog_state},
            "version_match": {"value": "Yes" if snapshot["version_match"] else "No", "status": version_match_state},
            "commits_since_release": {"value": snapshot["commits_since_release"], "status": status_for_commits(snapshot["commits_since_release"])},
            "days_since_last_release": {"value": latest_release_age if latest_release_age is not None else "None", "status": status_for_days(latest_release_age)},
            "release_cadence": {"value": snapshot["cadence"], "status": "--"},
            "semver_compliance": {"value": "Yes" if versioning_scheme == "semver" else "No", "status": "OK" if versioning_scheme == "semver" else "FIX"},
        },
        "commit_analysis": {
            "counts": counts,
            "highest_impact": highest_impact,
            "commits": commits,
        },
        "files": {
            "changelog_exists": bool(snapshot["changelog_text"]),
            "release_yml_exists": snapshot["release_yml_exists"],
            "release_yml_missing": not snapshot["release_yml_exists"],
        },
        "files_written": [],
        "release_command": {
            "requested": False,
            "publish": False,
            "status": "not-requested",
            "command": "",
            "stdout": "",
            "stderr": "",
        },
        "warnings": warnings,
        "blocked": blocked,
    }
    payload["proposal_markdown"] = build_release_proposal(payload)
    return payload


def build_release_proposal(payload: dict[str, Any]) -> str:
    """Render the yes/no release proposal."""
    kind = payload["proposal_kind"]
    version = payload["recommended_next_version"]
    title = payload["recommended_title"]
    notes = payload["release_notes"]
    entry = payload["draft_changelog_entry"]
    commit_count = payload["commits_since_release"]
    latest = payload["latest_version"] or "no prior release"

    if kind == "first_release":
        return (
            f"## Proposed First Release: {title}\n\n"
            f"Based on {payload['total_commit_count']} commits and the current repo infrastructure, I recommend your first release.\n\n"
            f"**Version:** {version}\n"
            f"**Title:** \"{title.split(' - ', 1)[1]}\"\n"
            f"**Release notes:**\n> {notes.splitlines()[-1]}\n\n"
            f"**Draft changelog entry:**\n\n{entry}\n"
            "Ready to create this release? Say **yes** to proceed, or tell me what to change.\n"
        )
    if kind == "catch_up":
        return (
            "## Proposed: Publish Missing Release Metadata\n\n"
            f"Your CHANGELOG and release history disagree around {payload['changelog_latest_version']} and {payload['latest_release'] or payload['latest_version']}.\n\n"
            f"**Recommended version to reconcile:** {version}\n"
            f"**Title:** \"{title.split(' - ', 1)[1]}\"\n"
            f"**Draft changelog entry:**\n\n{entry}\n"
            "Ready to publish this release state? Say **yes** to proceed, or tell me what to change.\n"
        )
    if kind == "draft_refresh":
        return (
            f"## Proposed Draft Refresh: {title}\n\n"
            f"{version} already exists as a draft release and has not been finalized.\n\n"
            f"**Recommended action:** keep the version at {version} and refresh the existing draft instead of bumping.\n"
            f"**Title:** \"{title.split(' - ', 1)[1]}\"\n"
            f"**Release notes:**\n> {notes.splitlines()[-1]}\n\n"
            f"**Draft changelog entry:**\n\n{entry}\n"
            "Ready to refresh this draft release? Say **yes** to proceed, or tell me what to change.\n"
        )
    if kind == "up_to_date":
        return (
            "## Release Status: Up to Date\n\n"
            f"No release is needed right now. {commit_count} commits since {latest}, but they do not justify a version bump.\n\n"
            "**Next release trigger:** When you add a user-facing feature or fix, rerun `github-release`.\n"
        )
    commit_lines = "\n".join(f"- {clean_commit_subject(commit['subject'])}" for commit in payload["commit_analysis"]["commits"][:6]) or "- None"
    return (
        f"## Proposed Release: {title}\n\n"
        f"{commit_count} commits since {latest}. Here's what changed:\n"
        f"{commit_lines}\n\n"
        f"**Version:** {version} ({payload['commit_analysis']['highest_impact'].upper()} because of the detected commit mix)\n"
        f"**Title:** \"{title.split(' - ', 1)[1]}\"\n"
        f"**Release notes:**\n> {notes.splitlines()[-1]}\n\n"
        f"**Draft changelog entry:**\n\n{entry}\n"
        "Ready to cut this release? Say **yes** to proceed, or tell me what to change.\n"
    )


def apply_release_plan(repo_root: Path, payload: dict[str, Any], create_release: bool, publish: bool) -> dict[str, Any]:
    """Apply file-level release changes and optionally create the GitHub release."""
    written: list[str] = []
    changelog_path = repo_root / "CHANGELOG.md"
    release_yml_path = repo_root / ".github" / "release.yml"
    changelog_preexisting = changelog_path.exists()

    existing_changelog = changelog_path.read_text(encoding="utf-8", errors="replace") if changelog_preexisting else ""
    changelog_content = build_changelog_file(
        repo_slug=payload["repo"],
        existing_text=existing_changelog,
        draft_entry=payload["draft_changelog_entry"],
        version=payload["recommended_next_version"],
    )
    if existing_changelog != changelog_content:
        changelog_path.write_text(changelog_content, encoding="utf-8")
        written.append("CHANGELOG.md")
        payload["changelog_created"] = not changelog_preexisting

    release_yml_path.parent.mkdir(parents=True, exist_ok=True)
    existing_release_yml = release_yml_path.read_text(encoding="utf-8", errors="replace") if release_yml_path.exists() else ""
    if existing_release_yml != CANONICAL_RELEASE_YML:
        release_yml_path.write_text(CANONICAL_RELEASE_YML, encoding="utf-8")
        written.append(".github/release.yml")
        payload["release_yml_created"] = not bool(existing_release_yml)

    payload["mode"] = "write"
    payload["files_written"] = written
    payload["files"]["changelog_exists"] = True
    payload["files"]["release_yml_exists"] = True
    payload["files"]["release_yml_missing"] = False
    payload["blocked"] = [item for item in payload["blocked"] if item != "release.yml is missing until file writes are enabled."]

    if create_release:
        if "/" not in payload["repo"]:
            payload["blocked"].append("Cannot create a GitHub release without a GitHub remote.")
        elif not gh_auth_ok():
            payload["blocked"].append("Cannot create a GitHub release because gh is not authenticated.")
        elif payload["proposal_kind"] == "up_to_date":
            payload["blocked"].append("No release was created because the plan is up to date.")
        elif payload["proposal_kind"] == "draft_refresh":
            payload["release_command"] = update_github_release(
                repo_slug=payload["repo"],
                version=payload["recommended_next_version"],
                title=payload["recommended_title"].split(" - ", 1)[1],
                notes=payload["release_notes"],
                publish=publish,
            )
            if payload["release_command"]["status"] == "updated":
                payload["mode"] = "publish" if publish else "draft"
        else:
            payload["release_command"] = create_github_release(
                repo_slug=payload["repo"],
                version=payload["recommended_next_version"],
                title=payload["recommended_title"].split(" - ", 1)[1],
                notes=payload["release_notes"],
                publish=publish,
            )
            if payload["release_command"]["status"] == "created":
                payload["mode"] = "publish" if publish else "draft"
    return payload


def build_release_report(payload: dict[str, Any]) -> str:
    """Render a markdown report for deterministic release planning."""
    dashboard = payload["dashboard"]
    warning_lines = "\n".join(f"- {item}" for item in payload["warnings"]) or "- None"
    blocked_lines = "\n".join(f"- {item}" for item in payload["blocked"]) or "- None"
    files_written = "\n".join(f"- {item}" for item in payload["files_written"]) or "- None"
    badge_lines = "\n".join(f"- `{item}`" for item in payload["badges"]) or "- None"
    commit_counts = payload["commit_analysis"]["counts"]
    return f"""# GitHub Release Report

- **Repository:** {payload['repo']}
- **Generated at:** {payload['timestamp']}
- **Mode:** {payload['mode']}
- **Verdict:** {payload['release_verdict']}
- **Recommended version:** {payload['recommended_next_version']}

## Release Health Dashboard

| Metric | Value | Status |
|--------|-------|--------|
| Latest GitHub Release | {dashboard['latest_release']['value']} | {dashboard['latest_release']['status']} |
| Latest CHANGELOG version | {dashboard['latest_changelog_version']['value']} | {dashboard['latest_changelog_version']['status']} |
| Version match | {dashboard['version_match']['value']} | {dashboard['version_match']['status']} |
| Commits since last release | {dashboard['commits_since_release']['value']} | {dashboard['commits_since_release']['status']} |
| Days since last release | {dashboard['days_since_last_release']['value']} | {dashboard['days_since_last_release']['status']} |
| Release cadence | {dashboard['release_cadence']['value']} | -- |
| Semver compliance | {dashboard['semver_compliance']['value']} | {dashboard['semver_compliance']['status']} |

## Commit Analysis

- Breaking: {commit_counts['breaking']}
- Features: {commit_counts['feature']}
- Fixes: {commit_counts['fix']}
- Security: {commit_counts['security']}
- Docs: {commit_counts['docs']}
- Chore: {commit_counts['chore']}
- Refactor: {commit_counts['refactor']}
- Tests: {commit_counts['test']}

## File Writes

{files_written}

## Recommended Badges

{badge_lines}

## Warnings

{warning_lines}

## Blocked / Manual

{blocked_lines}
"""


@dataclass
class ReleaseBundle:
    """Structured release output."""

    releases_data: dict[str, Any]
    report_markdown: str


def run_release(repo_root: Path, write_files: bool = False, create_release: bool = False, publish: bool = False) -> ReleaseBundle:
    """Build a deterministic release plan and optionally apply it."""
    releases_data = build_release_payload(repo_root)
    if write_files or create_release:
        releases_data = apply_release_plan(repo_root, releases_data, create_release=create_release, publish=publish)
    report_markdown = build_release_report(releases_data)
    return ReleaseBundle(releases_data=releases_data, report_markdown=report_markdown)


def write_release_artifacts(repo_root: Path, bundle: ReleaseBundle) -> dict[str, str]:
    """Write release cache and report artifacts for one run."""
    slug = slugify(bundle.releases_data["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    release_cache_path = write_repo_cache(repo_root, "releases-data.json", bundle.releases_data)
    report_path = out_dir / "RELEASE-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    proposal_path = out_dir / "RELEASE-PROPOSAL.md"
    proposal_path.write_text(bundle.releases_data["proposal_markdown"], encoding="utf-8")
    summary_path = out_dir / "RELEASE-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "release_cache_path": str(release_cache_path),
                "mode": bundle.releases_data["mode"],
                "release_verdict": bundle.releases_data["release_verdict"],
                "latest_version": bundle.releases_data["latest_version"],
                "recommended_next_version": bundle.releases_data["recommended_next_version"],
                "commits_since_release": bundle.releases_data["commits_since_release"],
                "files_written": bundle.releases_data["files_written"],
                "release_command_status": bundle.releases_data["release_command"]["status"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "release_cache": str(release_cache_path),
        "report": str(report_path),
        "proposal": str(proposal_path),
        "summary_json": str(summary_path),
    }
