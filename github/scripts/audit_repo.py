#!/usr/bin/env python3
"""Deterministic repository audit helpers for Legends GitHub."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cache_state import write_repo_cache
from github_runtime import gh_release_rows, gh_repo_view, git_recent_commit, git_tags, repo_slug_from_git
from runtime_paths import repo_output_dir


README_CANDIDATES = ["README.md", "README.rst", "readme.md"]
CANONICAL_SOP = [
    ("legal", "github-legal", "Legal Compliance"),
    ("community", "github-community", "Community Health"),
    ("release", "github-release", "Release & Maintenance"),
    ("seo", "github-seo", "SEO & Discoverability"),
    ("meta", "github-meta", "Metadata & Discovery"),
    ("readme", "github-readme", "README Quality"),
]


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    """Return a filesystem-safe slug."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "repo"


def score_rating(score: int) -> str:
    """Return the human-readable rating bucket for a score."""
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 50:
        return "Needs Work"
    if score >= 25:
        return "Poor"
    return "Critical"


def detect_repo_type(repo_root: Path) -> str:
    """Infer repo type from common files."""
    signals = {
        "Skill/Plugin": ["SKILL.md", "AGENTS.md"],
        "Library/Package": ["package.json", "pyproject.toml", "setup.py", "Cargo.toml", "go.mod"],
        "CLI Tool": ["bin", "cli.py", "main.py"],
        "Framework": ["middleware", "plugins"],
        "API/Service": ["openapi.yaml", "openapi.yml", "swagger.json"],
        "Application": ["docker-compose.yml", "docker-compose.yaml", "Dockerfile"],
        "Documentation": ["mkdocs.yml", "docusaurus.config.js"],
    }
    for repo_type, paths in signals.items():
        for relative in paths:
            if (repo_root / relative).exists():
                return repo_type
    return "Application"


def load_readme(repo_root: Path) -> tuple[str, Path | None]:
    """Read the primary README if present."""
    for candidate in README_CANDIDATES:
        path = repo_root / candidate
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace"), path
    return "", None


def file_exists(repo_root: Path, relative: str) -> bool:
    """Return whether a repo-relative path exists."""
    return (repo_root / relative).exists()


def count_readme_badges(readme: str) -> int:
    """Count obvious badge markers in a README."""
    return len(re.findall(r"img\.shields\.io|badge]", readme, flags=re.IGNORECASE))


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks before heading analysis."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def has_heading(readme: str, heading: str) -> bool:
    """Return whether a README contains a heading with the given phrase."""
    readme = strip_code_blocks(readme)
    pattern = rf"^##+\s+.*{re.escape(heading)}.*$"
    return re.search(pattern, readme, flags=re.IGNORECASE | re.MULTILINE) is not None


def score_from_checks(checks: list[tuple[bool, int, str, str]]) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Aggregate score, passed notes, failed notes, and detailed checks."""
    total = sum(weight for _, weight, _, _ in checks)
    earned = sum(weight for passed, weight, _, _ in checks if passed)
    score = int(round((earned / total) * 100)) if total else 0
    passed_notes = [success for passed, _, success, _ in checks if passed and success]
    failed_notes = [failure for passed, _, _, failure in checks if not passed and failure]
    details = [
        {"passed": passed, "weight": weight, "success": success, "failure": failure}
        for passed, weight, success, failure in checks
    ]
    return score, passed_notes, failed_notes, details


def score_readme(readme: str, repo_root: Path) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Score README quality deterministically."""
    heading_text = strip_code_blocks(readme)
    h1_count = len(re.findall(r"^#\s+", heading_text, flags=re.MULTILINE))
    h2_count = len(re.findall(r"^##\s+", heading_text, flags=re.MULTILINE))
    code_blocks = len(re.findall(r"```", readme))
    checks = [
        (bool(readme), 10, "README exists.", "Create a substantive README."),
        (h1_count == 1, 8, "README has a single H1.", "Use exactly one H1 in the README."),
        (h2_count >= 4, 8, "README has multiple H2 sections.", "Add at least four H2 sections to structure the README."),
        (has_heading(readme, "install"), 8, "Installation instructions are present.", "Add installation instructions with a code block."),
        (has_heading(readme, "usage") or has_heading(readme, "quick start"), 8, "Usage guidance is present.", "Add a usage or quick start section."),
        (code_blocks >= 2, 8, "README contains code examples.", "Add at least two fenced code blocks for setup or usage."),
        (count_readme_badges(readme) >= 2, 7, "README includes badges.", "Add version, license, or CI badges near the top of the README."),
        ("table of contents" in readme.lower() or "[#installation]" in readme.lower(), 6, "README includes a table of contents.", "Add a table of contents for longer READMEs."),
        (has_heading(readme, "architecture") or has_heading(readme, "how it works"), 6, "README explains implementation details.", "Add an architecture or how-it-works section."),
        (has_heading(readme, "faq") or has_heading(readme, "troubleshooting"), 5, "README addresses common questions.", "Add an FAQ or troubleshooting section."),
        ("CONTRIBUTING.md" in readme or has_heading(readme, "contributing"), 8, "README links to contribution guidance.", "Add a Contributing section or link to CONTRIBUTING.md."),
        ("LICENSE" in readme or has_heading(readme, "license"), 8, "README links to licensing information.", "Add a License section with a link to LICENSE."),
        (file_exists(repo_root, "assets/banner.webp") or file_exists(repo_root, "assets/banner.png") or file_exists(repo_root, "assets/banner.jpg"), 8, "Repo includes a README banner asset.", "Add a banner asset or hero visual for the README."),
    ]
    return score_from_checks(checks)


def score_meta(metadata: dict[str, Any], file_map: dict[str, bool]) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Score metadata and discoverability."""
    topics = metadata.get("topics", [])
    description = (metadata.get("description") or "").strip()
    checks = [
        (bool(description), 20, "Repo description is set.", "Set a repo description with meaningful keywords."),
        (40 <= len(description) <= 180, 10, "Description length is healthy.", "Aim for a description around 40-180 characters."),
        (len(topics) >= 5, 15, "Repo has topic coverage.", "Add at least five repository topics."),
        (8 <= len(topics) <= 15, 10, "Topic count is in the target range.", "Keep repository topics in the 8-15 range."),
        (bool(metadata.get("homepage_url")), 10, "Homepage URL is configured.", "Set a homepage URL or docs link for the repo."),
        (metadata.get("has_issues_enabled", True), 8, "Issues are enabled.", "Enable GitHub Issues unless there is a deliberate alternative."),
        (metadata.get("has_discussions_enabled", False) or metadata.get("repo_type") in {"Library/Package", "CLI Tool", "Skill/Plugin"}, 7, "Repo collaboration settings are reasonable.", "Consider enabling Discussions for support-heavy repos."),
        (metadata.get("uses_custom_open_graph_image", False) or file_map["social_preview"], 10, "Social preview coverage is present.", "Add a custom social preview image or repo social asset."),
        (not metadata.get("is_archived", False), 10, "Repo is active.", "Archived repos rank poorly; unarchive if it is still maintained."),
        (bool(metadata.get("default_branch")), 10, "Default branch is configured.", "Ensure the repo has a default branch configured."),
    ]
    return score_from_checks(checks)


def score_legal(file_map: dict[str, bool], metadata: dict[str, Any]) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Score legal compliance coverage."""
    checks = [
        (file_map["license"], 35, "License file exists.", "Add a LICENSE file."),
        (file_map["security_md"] or metadata.get("is_security_policy_enabled", False), 20, "Security policy exists.", "Add SECURITY.md and enable the security policy."),
        (file_map["citation_cff"], 15, "Citation file exists.", "Add CITATION.cff for citation and attribution."),
        (file_map["notice"], 5, "NOTICE file exists.", "Add NOTICE if the project carries attribution obligations."),
        (file_map["codeowners"], 10, "CODEOWNERS exists.", "Add CODEOWNERS to clarify maintainership."),
        (file_map["support_md"], 15, "Support policy exists.", "Add SUPPORT.md for support boundaries and escalation."),
    ]
    return score_from_checks(checks)


def score_community(file_map: dict[str, bool]) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Score community health files."""
    checks = [
        (file_map["contributing"], 20, "Contributing guidance exists.", "Add CONTRIBUTING.md."),
        (file_map["code_of_conduct"], 15, "Code of conduct exists.", "Add CODE_OF_CONDUCT.md."),
        (file_map["issue_templates"], 20, "Issue templates exist.", "Add issue templates under .github/ISSUE_TEMPLATE/."),
        (file_map["pr_template"], 15, "Pull request template exists.", "Add .github/PULL_REQUEST_TEMPLATE.md."),
        (file_map["devcontainer"], 10, "Devcontainer exists.", "Add a .devcontainer/devcontainer.json for contributor onboarding."),
        (file_map["codeowners"], 10, "CODEOWNERS exists.", "Add CODEOWNERS to route reviews."),
        (file_map["support_md"], 10, "Support guidance exists.", "Add SUPPORT.md for user support expectations."),
    ]
    return score_from_checks(checks)


def score_release(file_map: dict[str, bool], recent_commit: str, releases: list[dict[str, str]], tags: list[str]) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Score release and maintenance posture."""
    recent_ok = False
    if recent_commit:
        try:
            recent_dt = datetime.fromisoformat(recent_commit.replace("Z", "+00:00"))
            recent_ok = (datetime.now(timezone.utc) - recent_dt).days <= 180
        except ValueError:
            recent_ok = False

    checks = [
        (file_map["changelog"], 20, "Changelog exists.", "Add CHANGELOG.md."),
        (file_map["workflows"], 20, "CI workflows exist.", "Add at least one workflow under .github/workflows/."),
        (bool(releases) or bool(tags), 20, "Version history exists.", "Create a release or tag history."),
        (recent_ok, 20, "Repository has recent activity.", "Repository looks stale; ship a release or recent maintenance update."),
        (file_map["dependabot"] or file_map["release_config"], 20, "Maintenance automation exists.", "Add Dependabot or release automation config."),
    ]
    return score_from_checks(checks)


def score_seo(readme: str, metadata: dict[str, Any], file_map: dict[str, bool]) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    """Score SEO and discoverability basics."""
    description = (metadata.get("description") or "").strip()
    topics = metadata.get("topics", [])
    repo_name = (metadata.get("name") or "").strip().lower()
    first_paragraph = ""
    for chunk in re.split(r"\n\s*\n", readme):
        stripped = chunk.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("<"):
            first_paragraph = stripped
            break

    checks = [
        (bool(description), 20, "Description exists for indexing.", "Set a search-friendly description."),
        (len(topics) >= 5, 20, "Topic coverage supports search and Explore.", "Add more repository topics."),
        (bool(first_paragraph) and len(first_paragraph) >= 60, 20, "README opens with a real explanatory paragraph.", "Add a strong first paragraph that explains what the repo is."),
        (repo_name and repo_name.replace("-", " ") in readme.lower(), 10, "README clearly names the project.", "Mention the project name and category in the README opening."),
        (file_map["banner"] or file_map["social_preview"], 10, "Visual assets support social sharing.", "Add a banner or social preview image."),
        (bool(metadata.get("homepage_url")), 10, "Homepage URL gives search engines another destination.", "Set a homepage or docs URL."),
        ("http://" in readme or "https://" in readme, 10, "README links to related resources.", "Add links to docs, demos, or related resources."),
    ]
    return score_from_checks(checks)


def build_file_map(repo_root: Path) -> dict[str, bool]:
    """Build a deterministic file existence map."""
    return {
        "readme": any((repo_root / name).exists() for name in README_CANDIDATES),
        "license": file_exists(repo_root, "LICENSE") or file_exists(repo_root, "LICENSE.md"),
        "contributing": file_exists(repo_root, "CONTRIBUTING.md"),
        "code_of_conduct": file_exists(repo_root, "CODE_OF_CONDUCT.md"),
        "security_md": file_exists(repo_root, "SECURITY.md"),
        "support_md": file_exists(repo_root, "SUPPORT.md"),
        "codeowners": file_exists(repo_root, "CODEOWNERS") or file_exists(repo_root, ".github/CODEOWNERS"),
        "funding_yml": file_exists(repo_root, ".github/FUNDING.yml"),
        "issue_templates": (repo_root / ".github" / "ISSUE_TEMPLATE").exists() and any((repo_root / ".github" / "ISSUE_TEMPLATE").glob("*")),
        "pr_template": file_exists(repo_root, ".github/PULL_REQUEST_TEMPLATE.md"),
        "changelog": file_exists(repo_root, "CHANGELOG.md"),
        "citation_cff": file_exists(repo_root, "CITATION.cff"),
        "notice": file_exists(repo_root, "NOTICE"),
        "devcontainer": file_exists(repo_root, ".devcontainer/devcontainer.json"),
        "workflows": (repo_root / ".github" / "workflows").exists() and any((repo_root / ".github" / "workflows").glob("*")),
        "dependabot": file_exists(repo_root, ".github/dependabot.yml"),
        "release_config": file_exists(repo_root, ".github/release.yml"),
        "banner": file_exists(repo_root, "assets/banner.webp") or file_exists(repo_root, "assets/banner.png") or file_exists(repo_root, "assets/banner.jpg"),
        "social_preview": file_exists(repo_root, "assets/social-preview.jpg") or file_exists(repo_root, "assets/social-preview.png"),
    }


@dataclass
class AuditBundle:
    """Structured audit output."""

    repo_context: dict[str, Any]
    audit_data: dict[str, Any]
    report_markdown: str
    action_plan_markdown: str


def build_action_items(scores: dict[str, int], failures: dict[str, list[str]]) -> list[dict[str, str]]:
    """Create prioritized action items from failed checks."""
    category_to_skill = {
        "readme": "github-readme",
        "meta": "github-meta",
        "legal": "github-legal",
        "community": "github-community",
        "release": "github-release",
        "seo": "github-seo",
    }
    priority_labels = ["critical", "high", "high", "medium", "medium", "medium"]
    ordered = sorted(scores.items(), key=lambda item: item[1])
    action_items: list[dict[str, str]] = []
    for index, (category, score) in enumerate(ordered):
        if score >= 90:
            continue
        failure = failures.get(category, [])
        action_items.append(
            {
                "priority": priority_labels[min(index, len(priority_labels) - 1)],
                "category": category,
                "skill": category_to_skill[category],
                "score": str(score),
                "action": failure[0] if failure else f"Improve {category} coverage.",
            }
        )
    return action_items


def markdown_list(items: list[str], fallback: str) -> str:
    """Render a markdown list."""
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def build_sop_rows(audit_data: dict[str, Any]) -> list[dict[str, str]]:
    """Return SOP rows in the documented canonical order."""
    scores = audit_data["scores"]
    action_by_skill = {item["skill"]: item for item in audit_data["action_items"]}
    rows: list[dict[str, str]] = []
    step = 1
    for category, skill, _label in CANONICAL_SOP:
        score = scores[category]
        if score >= 90:
            continue
        item = action_by_skill.get(skill)
        rows.append(
            {
                "step": str(step),
                "command": skill,
                "score": f"{score}/100",
                "reason": item["action"] if item else f"Improve {category} coverage.",
            }
        )
        step += 1
    rows.append(
        {
            "step": str(step),
            "command": "github-audit",
            "score": "--",
            "reason": "Re-audit after changes to confirm the score delta.",
        }
    )
    return rows


def render_sop_table(rows: list[dict[str, str]]) -> str:
    """Render SOP rows as a markdown table."""
    lines = [
        "| Step | Command | Current Score | What It Fixes |",
        "| --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['step']} | `{row['command']}` | {row['score']} | {row['reason']} |")
    return "\n".join(lines)


def build_markdown_report(repo_context: dict[str, Any], audit_data: dict[str, Any], releases: list[dict[str, str]]) -> str:
    """Create the main markdown report."""
    scores = audit_data["scores"]
    weights = audit_data["weights"]
    rating = score_rating(audit_data["overall_score"])
    summary = [
        f"Repo type: {repo_context['repo_type']}",
        f"Description set: {'yes' if repo_context['description'] else 'no'}",
        f"Topics configured: {len(repo_context['topics'])}",
        f"Recent releases: {len(releases)}",
    ]
    action_lines = [f"[{item['priority']}] {item['skill']}: {item['action']}" for item in audit_data["action_items"]]
    sop_rows = build_sop_rows(audit_data)
    return f"""# GitHub Audit Report

- **Repository:** {repo_context['repo']}
- **Overall score:** {audit_data['overall_score']}/100 ({rating})
- **Generated at:** {audit_data['timestamp']}

## Summary

{markdown_list(summary, 'No summary available.')}

## Scorecard

| Category | Score | Weight | Weighted |
| --- | ---: | ---: | ---: |
| README Quality | {scores['readme']} | 25% | {scores['readme'] * weights['readme']:.1f} |
| Metadata & Discovery | {scores['meta']} | 20% | {scores['meta'] * weights['meta']:.1f} |
| Legal Compliance | {scores['legal']} | 15% | {scores['legal'] * weights['legal']:.1f} |
| Community Health | {scores['community']} | 15% | {scores['community'] * weights['community']:.1f} |
| Release & Maintenance | {scores['release']} | 15% | {scores['release'] * weights['release']:.1f} |
| SEO & Discoverability | {scores['seo']} | 10% | {scores['seo'] * weights['seo']:.1f} |

## Priority Actions

{markdown_list(action_lines, 'No action items.')}

## Recommended Next Steps

{render_sop_table(sop_rows)}
"""


def build_action_plan(repo_context: dict[str, Any], audit_data: dict[str, Any]) -> str:
    """Create a deterministic SOP markdown file."""
    rows = build_sop_rows(audit_data)
    return f"""# Action Plan

- **Repository:** {repo_context['repo']}
- **Overall score:** {audit_data['overall_score']}/100

## Standard Operating Procedure

{render_sop_table(rows)}
"""


def run_audit(repo_root: Path) -> AuditBundle:
    """Run a deterministic audit for a local git repository."""
    repo_slug = repo_slug_from_git(repo_root) or repo_root.name
    metadata_raw = gh_repo_view(repo_slug) if "/" in repo_slug else None
    readme, readme_path = load_readme(repo_root)
    file_map = build_file_map(repo_root)
    releases = gh_release_rows(repo_slug) if "/" in repo_slug else []
    tags = git_tags(repo_root)
    recent_commit = git_recent_commit(repo_root)
    repo_type = detect_repo_type(repo_root)

    metadata = {
        "name": metadata_raw.get("name") if metadata_raw else repo_root.name,
        "description": metadata_raw.get("description") if metadata_raw else "",
        "homepage_url": metadata_raw.get("homepageUrl") if metadata_raw else "",
        "topics": metadata_raw.get("repositoryTopics") if metadata_raw else [],
        "visibility": metadata_raw.get("visibility") if metadata_raw else "",
        "default_branch": (metadata_raw.get("defaultBranchRef") or {}).get("name") if metadata_raw else "",
        "license": ((metadata_raw.get("licenseInfo") or {}).get("spdxId") if metadata_raw else "") or "",
        "stars": metadata_raw.get("stargazerCount") if metadata_raw else 0,
        "forks": metadata_raw.get("forkCount") if metadata_raw else 0,
        "watchers": metadata_raw.get("watchers", {}).get("totalCount") if metadata_raw else 0,
        "primary_language": ((metadata_raw.get("primaryLanguage") or {}).get("name") if metadata_raw else "") or "",
        "created_at": metadata_raw.get("createdAt") if metadata_raw else "",
        "updated_at": metadata_raw.get("updatedAt") if metadata_raw else "",
        "is_archived": metadata_raw.get("isArchived") if metadata_raw else False,
        "is_fork": metadata_raw.get("isFork") if metadata_raw else False,
        "has_issues_enabled": metadata_raw.get("hasIssuesEnabled", True) if metadata_raw else True,
        "has_wiki_enabled": metadata_raw.get("hasWikiEnabled", False) if metadata_raw else False,
        "has_discussions_enabled": metadata_raw.get("hasDiscussionsEnabled", False) if metadata_raw else False,
        "has_projects_enabled": metadata_raw.get("hasProjectsEnabled", False) if metadata_raw else False,
        "is_security_policy_enabled": metadata_raw.get("isSecurityPolicyEnabled", False) if metadata_raw else False,
        "uses_custom_open_graph_image": metadata_raw.get("usesCustomOpenGraphImage", False) if metadata_raw else False,
        "repo_type": repo_type,
    }

    readme_score, _, readme_failures, readme_checks = score_readme(readme, repo_root)
    meta_score, _, meta_failures, meta_checks = score_meta(metadata, file_map)
    legal_score, _, legal_failures, legal_checks = score_legal(file_map, metadata)
    community_score, _, community_failures, community_checks = score_community(file_map)
    release_score, _, release_failures, release_checks = score_release(file_map, recent_commit, releases, tags)
    seo_score, _, seo_failures, seo_checks = score_seo(readme, metadata, file_map)

    scores = {
        "readme": readme_score,
        "meta": meta_score,
        "legal": legal_score,
        "community": community_score,
        "release": release_score,
        "seo": seo_score,
    }
    weights = {"readme": 0.25, "meta": 0.2, "legal": 0.15, "community": 0.15, "release": 0.15, "seo": 0.1}
    overall_score = int(round(sum(scores[key] * weight for key, weight in weights.items())))
    failures = {
        "readme": readme_failures,
        "meta": meta_failures,
        "legal": legal_failures,
        "community": community_failures,
        "release": release_failures,
        "seo": seo_failures,
    }
    action_items = build_action_items(scores, failures)

    repo_context = {
        "cache_type": "repo-context",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "repo": repo_slug,
        "repo_root": str(repo_root),
        "repo_type": repo_type,
        "description": metadata["description"],
        "topics": metadata["topics"],
        "primary_language": metadata["primary_language"],
        "homepage_url": metadata["homepage_url"],
        "default_branch": metadata["default_branch"],
        "is_fork": metadata["is_fork"],
        "readme_path": str(readme_path) if readme_path else "",
        "recent_commit": recent_commit,
    }
    audit_data = {
        "cache_type": "audit-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "overall_score": overall_score,
        "scores": scores,
        "weights": weights,
        "action_items": action_items,
        "file_existence": file_map,
        "releases": releases,
        "tags": tags,
        "checks": {
            "readme": readme_checks,
            "meta": meta_checks,
            "legal": legal_checks,
            "community": community_checks,
            "release": release_checks,
            "seo": seo_checks,
        },
    }

    report_markdown = build_markdown_report(repo_context, audit_data, releases)
    action_plan_markdown = build_action_plan(repo_context, audit_data)
    return AuditBundle(repo_context=repo_context, audit_data=audit_data, report_markdown=report_markdown, action_plan_markdown=action_plan_markdown)


def write_audit_artifacts(repo_root: Path, bundle: AuditBundle) -> dict[str, str]:
    """Write cache and output artifacts for one audit run."""
    slug = slugify(bundle.repo_context["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    repo_context_path = write_repo_cache(repo_root, "repo-context.json", bundle.repo_context)
    audit_data_path = write_repo_cache(repo_root, "audit-data.json", bundle.audit_data)

    report_path = out_dir / "GITHUB-AUDIT-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    action_plan_path = out_dir / "ACTION-PLAN.md"
    action_plan_path.write_text(bundle.action_plan_markdown, encoding="utf-8")
    summary_path = out_dir / "SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "repo_context_path": str(repo_context_path),
                "audit_data_path": str(audit_data_path),
                "overall_score": bundle.audit_data["overall_score"],
                "scores": bundle.audit_data["scores"],
                "action_items": bundle.audit_data["action_items"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "report": str(report_path),
        "action_plan": str(action_plan_path),
        "summary_json": str(summary_path),
        "repo_context_cache": str(repo_context_path),
        "audit_cache": str(audit_data_path),
    }
