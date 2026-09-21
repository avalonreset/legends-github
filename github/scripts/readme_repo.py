#!/usr/bin/env python3
"""Deterministic README planning for Legends GitHub."""

from __future__ import annotations

import json
import re
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_repo import load_readme, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_repo_view
from local_assets import (
    AssetPreparationError,
    convert_to_webp,
    render_social_preview_from_banner,
)
from meta_repo import social_preview_asset
from runtime_paths import repo_output_dir
from seo_repo import (
    build_repo_snapshot,
    first_paragraph,
    load_manifest_description,
    load_manifest_name,
    run_seo,
)


SECTION_SYNONYMS = {
    "what_it_does": ["what it does", "about", "overview", "features", "why this framework", "why"],
    "installation": ["installation", "install", "getting started", "setup"],
    "quick_start": ["quick start", "quickstart", "usage", "getting started"],
    "commands": ["commands", "command reference", "cli"],
    "usage": ["usage", "examples", "example", "api reference"],
    "configuration": ["configuration", "config", "settings", "environment"],
    "architecture": ["architecture", "how it works", "internals", "design"],
    "faq": ["frequently asked questions", "faq", "troubleshooting", "common issues"],
    "documentation": ["documentation", "docs"],
    "contributing": ["contributing", "community", "support"],
    "license": ["license"],
}


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_text(value: str) -> str:
    """Collapse markdown-ish text into readable plain text."""
    text = re.sub(r"```.*?```", " ", value, flags=re.DOTALL)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r" \1 ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r" \1 ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"`", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sentence_case(value: str) -> str:
    """Return sentence-style casing for one phrase."""
    stripped = value.strip()
    if not stripped:
        return ""
    return stripped[0].upper() + stripped[1:]


def heading_slug(value: str) -> str:
    """Return a GitHub-style heading anchor slug."""
    lowered = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"\s+", "-", lowered.strip())


def normalize_heading(value: str) -> str:
    """Normalize a heading for section lookup."""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def extract_sections(readme: str) -> dict[str, str]:
    """Return H2 section bodies keyed by normalized heading."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in readme.splitlines():
        if line.startswith("## "):
            current = normalize_heading(line[3:].strip())
            sections.setdefault(current, [])
            continue
        if line.startswith("# "):
            current = None
            continue
        if current is not None:
            sections[current].append(line)
    return {heading: "\n".join(lines).strip() for heading, lines in sections.items() if "\n".join(lines).strip()}


def section_body(sections: dict[str, str], names: list[str]) -> str:
    """Return the first matching section body by heading synonym."""
    normalized = {normalize_heading(name) for name in names}
    for heading, body in sections.items():
        if heading in normalized:
            return body.strip()
    return ""


def banner_asset(repo_root: Path) -> str | None:
    """Return the first likely README banner asset path."""
    candidates = [
        repo_root / "assets" / "banner.webp",
        repo_root / "assets" / "banner.png",
        repo_root / "assets" / "banner.jpg",
        repo_root / "assets" / "banner.jpeg",
    ]
    for path in candidates:
        if path.is_file():
            return str(path.relative_to(repo_root)).replace("\\", "/")
    return None


def default_branch_name(metadata: dict[str, Any]) -> str:
    """Return the best default branch name for raw GitHub URLs."""
    branch = str(((metadata.get("defaultBranchRef") or {}).get("name")) or "").strip()
    return branch or "main"


def github_settings_url(repo_slug: str) -> str:
    """Return the GitHub settings URL for a repo slug."""
    if "/" not in repo_slug:
        return ""
    return f"https://github.com/{repo_slug}/settings"


def raw_github_url(repo_slug: str, branch: str, relative_path: str) -> str:
    """Return a raw GitHub URL for a repo-relative asset path."""
    if "/" not in repo_slug or not relative_path:
        return ""
    return f"https://raw.githubusercontent.com/{repo_slug}/{branch}/{relative_path}"


def ensure_readme_assets(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Reuse supplied assets and prepare optional derivatives entirely locally."""
    repo_root = Path(snapshot["repo_root"])
    updates: dict[str, Any] = {
        "banner_generated": False,
        "banner_prepared": False,
        "social_preview_generated": False,
        "asset_tasks": [],
        "asset_notes": [],
    }
    branch = default_branch_name(snapshot["metadata"])

    banner_path = snapshot.get("banner_path")
    if not banner_path:
        original_path = next(
            (repo_root / "assets" / "originals" / f"banner.{suffix}"
             for suffix in ("png", "webp", "jpg", "jpeg")
             if (repo_root / "assets" / "originals" / f"banner.{suffix}").is_file()),
            None,
        )
        if original_path:
            try:
                banner_path_abs = convert_to_webp(original_path, repo_root / "assets" / "banner.webp")
                banner_path = banner_path_abs.relative_to(repo_root).as_posix()
                updates.update({
                    "banner_prepared": True,
                    "banner_original_path": original_path.relative_to(repo_root).as_posix(),
                    "banner_path": banner_path,
                })
            except AssetPreparationError as exc:
                updates["asset_notes"].append(str(exc))
        else:
            updates["asset_notes"].append("No local banner supplied. Artwork is optional; no image service was contacted.")

    social_preview_path = snapshot.get("social_preview_path")
    if not social_preview_path and banner_path:
        banner_abs = repo_root / Path(str(banner_path))
        preview_abs = repo_root / "assets" / "social-preview.jpg"
        try:
            render_social_preview_from_banner(banner_abs, preview_abs)
            social_preview_path = preview_abs.relative_to(repo_root).as_posix()
            updates.update({"social_preview_generated": True, "social_preview_path": social_preview_path})
        except AssetPreparationError as exc:
            updates["asset_notes"].append(str(exc))

    updates["banner_links"] = {
        "local": (repo_root / banner_path).resolve().as_uri() if banner_path else "",
        "raw": raw_github_url(snapshot["repo"], branch, banner_path) if banner_path else "",
    }
    updates["social_preview_links"] = {
        "local": (repo_root / social_preview_path).resolve().as_uri() if social_preview_path else "",
        "raw": raw_github_url(snapshot["repo"], branch, social_preview_path) if social_preview_path else "",
        "settings": github_settings_url(snapshot["repo"]),
    }
    return updates


def license_type(repo_root: Path, metadata: dict[str, Any], legal_data: dict[str, Any]) -> str:
    """Return the best-effort license label."""
    value = str(legal_data.get("license_type") or "").strip()
    if value:
        return value
    meta_license = str(((metadata.get("licenseInfo") or {}).get("spdxId")) or "").strip()
    if meta_license:
        return meta_license
    for candidate in ("LICENSE", "LICENSE.md"):
        path = repo_root / candidate
        if path.exists():
            first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()
            return first_line[0].strip() if first_line else "License file present"
    return "Not established"


def docs_url(readme: str, metadata: dict[str, Any]) -> str:
    """Return the best external docs URL if one is obvious."""
    homepage = str(metadata.get("homepageUrl") or "").strip()
    if homepage and any(token in homepage.lower() for token in ("docs", "readthedocs", "github.io")):
        return homepage
    for match in re.finditer(r"https?://\S+", readme):
        url = match.group(0).rstrip(").,")
        lowered = url.lower()
        if any(token in lowered for token in ("docs", "readthedocs", "github.io")):
            return url
    return ""


def workflow_file(repo_root: Path) -> str:
    """Return one workflow file name if available."""
    workflows = sorted((repo_root / ".github" / "workflows").glob("*.y*ml"))
    return workflows[0].name if workflows else ""


def load_package_json(repo_root: Path) -> dict[str, Any]:
    """Load package.json if present."""
    path = repo_root / "package.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_pyproject(repo_root: Path) -> dict[str, Any]:
    """Load pyproject.toml if present."""
    path = repo_root / "pyproject.toml"
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def install_snippet(repo_root: Path, repo_type: str, project_name: str) -> str:
    """Request verified setup instructions without assuming registry publication."""
    manifests = [name for name in ("package.json", "pyproject.toml", "Cargo.toml") if (repo_root / name).is_file()]
    evidence = " Available manifests: " + ", ".join(f"[{name}]({name})" for name in manifests) + "." if manifests else ""
    return "**Draft requirement:** Document the supported installation method and prerequisites, then verify the commands in a clean environment." + evidence


def quick_start_snippet(repo_root: Path, repo_type: str, project_name: str) -> str:
    """Request a tested usage example without guessing an entry point."""
    return "**Draft requirement:** Add one verified example using the project's actual entry point, required inputs, and expected output."


def configuration_snippet(repo_root: Path) -> str:
    """Link observed configuration examples without inventing setup requirements."""
    if (repo_root / ".env.example").is_file():
        return "Review [.env.example](.env.example) for configuration examples. Document which variables are required and how the application loads them."
    for name in ("config.toml", "settings.toml"):
        if (repo_root / name).is_file():
            return f"Configuration file: [{name}]({name}). Document supported settings before changing defaults."
    return ""


def repo_snapshot_table(snapshot: dict[str, Any], license_label: str) -> str:
    """Render a small project snapshot table."""
    language = snapshot.get("primary_language") or "Unspecified"
    return (
        "| Attribute | Value |\n"
        "|-----------|-------|\n"
        f"| Repo type | {snapshot['repo_type']} |\n"
        f"| Primary language | {language} |\n"
        f"| License | {license_label} |\n"
        f"| SEO mode | {snapshot['seo_data'].get('analysis_mode', 'unknown')} |\n"
    )


def build_tagline(snapshot: dict[str, Any], primary_keyword: str) -> str:
    """Use an observed description rather than inferring the project's purpose."""
    description = clean_text(snapshot.get("description") or snapshot.get("manifest_description") or "")
    return description.split(".")[0].strip() if description else ""


def build_intro(snapshot: dict[str, Any], primary_keyword: str) -> str:
    """Reuse the existing introduction or an observed project description."""
    opening = re.split(r"^##\s+", snapshot.get("current_readme", ""), maxsplit=1, flags=re.MULTILINE)[0]
    summary = first_paragraph(opening) or clean_text(snapshot.get("description") or snapshot.get("manifest_description") or "")
    return summary or "**Draft requirement:** Describe the project's purpose, intended users, and supported capabilities from the implementation."


def existing_links_present(readme: str) -> bool:
    """Return whether the README already links to related resources."""
    return bool(re.search(r"https?://\S+|\[[^\]]+\]\([^)]+\)", readme))


def build_badges(repo_root: Path, repo_slug: str, license_label: str) -> list[str]:
    """Build deterministic badge markdown."""
    if "/" not in repo_slug:
        return []
    owner, repo = repo_slug.split("/", 1)
    badges: list[str] = []
    workflow = workflow_file(repo_root)
    if workflow:
        badges.append(
            f"[![CI](https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow}?label=CI)]"
            f"(https://github.com/{owner}/{repo}/actions/workflows/{workflow})"
        )
    badges.append(
        f"[![Version](https://img.shields.io/github/v/release/{owner}/{repo})]"
        f"(https://github.com/{owner}/{repo}/releases)"
    )
    license_file = next((name for name in ("LICENSE", "LICENSE.md") if (repo_root / name).is_file()), None)
    if license_file:
        license_slug = re.sub(r"[^a-zA-Z0-9]+", "-", license_label).strip("-").lower() or "license"
        badges.append(
            f"[![License](https://img.shields.io/badge/license-{license_slug}-blue)]({license_file})"
        )
    badges.append(
        f"[![Last Commit](https://img.shields.io/github/last-commit/{owner}/{repo})]"
        f"(https://github.com/{owner}/{repo}/commits/main)"
    )
    return badges


def section_order(repo_type: str, docs_link: str) -> list[tuple[str, str]]:
    """Return the H2 section order for a repo type."""
    if repo_type == "Skill/Plugin":
        order = [
            ("What It Does", "what_it_does"),
            ("Project Snapshot", "snapshot"),
            ("Installation", "installation"),
            ("Quick Start", "quick_start"),
            ("Commands", "commands"),
            ("Configuration", "configuration"),
            ("Examples", "usage"),
        ]
    elif repo_type == "CLI Tool":
        order = [
            ("Project Snapshot", "snapshot"),
            ("Installation", "installation"),
            ("Quick Start", "quick_start"),
            ("Commands", "commands"),
            ("Configuration", "configuration"),
            ("Examples", "usage"),
        ]
    elif repo_type == "Library/Package":
        order = [
            ("Features", "what_it_does"),
            ("Project Snapshot", "snapshot"),
            ("Installation", "installation"),
            ("Quick Start", "quick_start"),
            ("Usage", "usage"),
            ("API Reference", "commands"),
            ("Configuration", "configuration"),
        ]
    else:
        order = [
            ("About", "what_it_does"),
            ("Project Snapshot", "snapshot"),
            ("Getting Started", "installation"),
            ("Quick Start", "quick_start"),
            ("Usage", "usage"),
            ("Architecture", "architecture"),
        ]
    if docs_link:
        order.append(("Documentation", "documentation"))
    order.extend([("Frequently Asked Questions", "faq"), ("Contributing", "contributing"), ("License", "license")])
    return order


def fallback_section_content(
    key: str,
    snapshot: dict[str, Any],
    license_label: str,
    docs_link: str,
    existing_sections: dict[str, str],
) -> str:
    """Return deterministic body content for one generated section."""
    project_name = snapshot["repo_name"]
    if key == "what_it_does":
        return clean_text(snapshot.get("description") or snapshot.get("manifest_description") or "")

    if key == "snapshot":
        return repo_snapshot_table(snapshot, license_label)

    if key == "installation":
        return install_snippet(Path(snapshot["repo_root"]), snapshot["repo_type"], project_name)

    if key == "quick_start":
        return quick_start_snippet(Path(snapshot["repo_root"]), snapshot["repo_type"], project_name)

    if key in {"commands", "usage", "architecture", "faq"}:
        return ""

    if key == "configuration":
        return configuration_snippet(Path(snapshot["repo_root"]))

    if key == "documentation":
        return f"See [{docs_link}]({docs_link})." if docs_link else ""

    if key == "contributing":
        if (Path(snapshot["repo_root"]) / "CONTRIBUTING.md").exists():
            return "See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines, local setup notes, and review expectations."
        return ""

    if key == "license":
        for name in ("LICENSE", "LICENSE.md"):
            if (Path(snapshot["repo_root"]) / name).is_file():
                return f"See [{name}]({name}) for licensing terms."
        return ""

    return ""


def build_readme_content(snapshot: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    """Build deterministic README markdown plus metadata."""
    repo_root = Path(snapshot["repo_root"])
    current_readme = snapshot["current_readme"]
    existing_sections = extract_sections(current_readme)
    license_label = snapshot["license_label"]
    docs_link = snapshot["docs_link"]
    repo_slug = snapshot["repo"]
    tagline = build_tagline(snapshot, snapshot["seo_data"]["primary_keyword"]["keyword"])
    original_title = re.search(r"^# [^\n]+", current_readme, flags=re.MULTILINE)
    title = original_title.group(0) if original_title else f"# {snapshot['repo_name']}" + (f" - {tagline}" if tagline else "")
    badges = build_badges(repo_root, repo_slug, license_label)
    intro = build_intro(snapshot, snapshot["seo_data"]["primary_keyword"]["keyword"])

    section_specs = section_order(snapshot["repo_type"], docs_link)
    sections: list[tuple[str, str]] = []
    consumed: set[str] = set()
    original_headings = {normalize_heading(heading): heading.strip() for heading in re.findall(r"^## (.+)$", current_readme, flags=re.MULTILINE)}
    for heading, key in section_specs:
        candidates = {normalize_heading(name) for name in SECTION_SYNONYMS.get(key, [])}
        candidates.add(normalize_heading(heading))
        matched = next((name for name in existing_sections if name in candidates), None)
        if matched:
            if matched in consumed:
                continue
            consumed.add(matched)
            body = existing_sections[matched]
            heading = original_headings.get(matched, heading)
        else:
            body = fallback_section_content(key, snapshot, license_label, docs_link, existing_sections)
        if body:
            sections.append((heading, body.strip()))
    for name, body in existing_sections.items():
        if name not in consumed and name != "table of contents":
            sections.append((original_headings.get(name, name), body))

    toc_lines = [f"- [{heading}](#{heading_slug(heading)})" for heading, _ in sections]
    banner_path = snapshot["banner_path"]
    if banner_path:
        banner_block = (
            "<p align=\"center\">\n"
            f"  <img src=\"{banner_path}\" alt=\"{snapshot['repo_name']} banner\" width=\"100%\">\n"
            "</p>\n"
        )
        banner_status = "existing"
    else:
        banner_block = ""
        banner_status = "not_supplied"

    parts = [banner_block.rstrip(), "", title]
    if badges:
        parts.extend(["", " ".join(badges)])
    parts.extend(["", intro, "", "## Table of Contents", "", *toc_lines])
    for heading, body in sections:
        parts.extend(["", f"## {heading}", "", body])

    readme_text = "\n".join(parts).strip() + "\n"
    secondary_in_h2 = [
        heading
        for heading, _body in sections
        for keyword in snapshot["seo_data"].get("secondary_keywords", [])
        if isinstance(keyword, dict) and keyword.get("keyword") and keyword["keyword"].lower() in heading.lower()
    ]
    metadata = {
        "title": title,
        "banner_status": banner_status,
        "badges": badges,
        "intro": intro,
        "secondary_in_h2": secondary_in_h2,
    }
    return readme_text, [heading for heading, _ in sections], metadata


def proper_heading_hierarchy(readme: str) -> bool:
    """Return whether headings move in reasonable order."""
    levels = [len(match.group(1)) for match in re.finditer(r"^(#{1,6})\s+", readme, flags=re.MULTILINE)]
    previous = 0
    for level in levels:
        if previous and level > previous + 1:
            return False
        previous = level
    return True


def expected_sections(repo_type: str, docs_link: str) -> list[str]:
    """Return the expected section headings for scoring."""
    return [heading for heading, _ in section_order(repo_type, docs_link)]


def image_alt_text_ok(readme: str) -> bool:
    """Return whether image alt text is present for obvious image tags."""
    image_matches = re.findall(r"!\[([^\]]*)\]\([^)]+\)", readme)
    html_matches = re.findall(r"<img[^>]*alt=\"([^\"]*)\"", readme, flags=re.IGNORECASE)
    values = image_matches + html_matches
    if not values:
        return True
    return all(value.strip() for value in values)


def descriptive_links_ok(readme: str) -> bool:
    """Return whether markdown links avoid generic anchor text."""
    links = re.findall(r"\[([^\]]+)\]\([^)]+\)", readme)
    bad = {"click here", "here", "link", "this", "more"}
    return all(label.strip().lower() not in bad for label in links)


def short_paragraphs_ok(readme: str) -> bool:
    """Return whether prose avoids long wall-of-text paragraphs."""
    for chunk in re.split(r"\n\s*\n", readme):
        stripped = chunk.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|") or stripped.startswith("```"):
            continue
        if stripped.count(".") + stripped.count("!") + stripped.count("?") > 5:
            return False
    return True


def definition_statement_ok(readme: str) -> bool:
    """Return whether the opening includes a simple definition sentence."""
    opening = " ".join(first_paragraph(readme).split()[:40]).lower()
    return " is " in opening and (" helps " in opening or " that " in opening or " for " in opening)


def faq_answer_first_ok(readme: str) -> bool:
    """Return whether the README has explicit FAQ answers."""
    return bool(re.search(r"^### .+\n.+", readme, flags=re.MULTILINE))


def specific_facts_ok(readme: str) -> bool:
    """Return whether the README contains quantifiable facts."""
    return bool(re.search(r"\b\d+\b", readme))


def score_readme_candidate(readme: str, repo_type: str, seo_data: dict[str, Any], docs_link: str) -> dict[str, Any]:
    """Score one README using the github-readme rubric."""
    primary_keyword = str((seo_data.get("primary_keyword") or {}).get("keyword") or "").strip().lower()
    secondary_keywords = [
        str(item.get("keyword") or "").strip().lower()
        for item in seo_data.get("secondary_keywords", [])
        if isinstance(item, dict)
    ]
    headings = re.findall(r"^(#{1,6})\s+(.+)$", readme, flags=re.MULTILINE)
    h1_lines = [text.strip() for level, text in headings if level == "#"]
    h2_lines = [text.strip() for level, text in headings if level == "##"]
    intro = first_paragraph(readme).lower()
    sections_needed = expected_sections(repo_type, docs_link)

    structure = 0
    if len(h1_lines) == 1:
        structure += 4
    if h1_lines and (" - " in h1_lines[0] or ": " in h1_lines[0]):
        structure += 4
    if proper_heading_hierarchy(readme):
        structure += 4
    if len(h2_lines) >= 4:
        structure += 4
    if "## Table of Contents" in readme:
        structure += 4

    content = 0
    if re.search(r"^##\s+(installation|install|getting started)\b", readme, flags=re.IGNORECASE | re.MULTILINE):
        content += 5
    if len(re.findall(r"```[a-zA-Z0-9_-]*\n", readme)) >= 2:
        content += 5
    if any(name in [normalize_heading(h2) for h2 in h2_lines] for name in {"configuration", "config", "commands", "api reference"}):
        content += 4
    if re.search(r"^##\s+(architecture|how it works|what it does|features|about)\b", readme, flags=re.IGNORECASE | re.MULTILINE):
        content += 3
    if re.search(r"^##\s+(frequently asked questions|faq|troubleshooting|common issues)\b", readme, flags=re.IGNORECASE | re.MULTILINE):
        content += 3

    seo = 0
    h1_text = h1_lines[0].lower() if h1_lines else ""
    if primary_keyword and primary_keyword in h1_text:
        seo += 6
    if primary_keyword and primary_keyword in intro:
        seo += 4
    matched_secondary = [heading for heading in h2_lines if any(keyword and keyword in heading.lower() for keyword in secondary_keywords)]
    if len(matched_secondary) >= 2:
        seo += 4
    if image_alt_text_ok(readme):
        seo += 3
    if descriptive_links_ok(readme):
        seo += 3

    badges = 0
    badge_count = len(re.findall(r"img\.shields\.io|badge", readme, flags=re.IGNORECASE))
    if badge_count >= 1:
        badges += 3
    if "license" in readme.lower():
        badges += 2
    if re.search(r"github/v/release|version", readme, flags=re.IGNORECASE):
        badges += 2
    if re.search(r"workflow/status|label=ci|build", readme, flags=re.IGNORECASE):
        badges += 3

    visuals = 0
    if "assets/banner" in readme or "<img src=" in readme:
        visuals += 4
    if len(re.findall(r"```[a-zA-Z0-9_-]+\n", readme)) >= 2:
        visuals += 2
    if "|" in readme and re.search(r"^\|.+\|$", readme, flags=re.MULTILINE):
        visuals += 2
    if short_paragraphs_ok(readme):
        visuals += 2

    completeness = 0
    normalized_h2 = {normalize_heading(value) for value in h2_lines}
    expected_present = 0
    for heading in sections_needed:
        if normalize_heading(heading) in normalized_h2:
            expected_present += 1
    if sections_needed and expected_present >= max(4, len(sections_needed) - 2):
        completeness += 4
    if "contributing" in normalized_h2 or "[CONTRIBUTING.md]".lower() in readme.lower():
        completeness += 2
    if "license" in normalized_h2 and "(LICENSE)" in readme:
        completeness += 2
    if docs_link or existing_links_present(readme):
        completeness += 2

    ai = 0
    if definition_statement_ok(readme):
        ai += 4
    if re.search(r"^\|.+\|$", readme, flags=re.MULTILINE):
        ai += 2
    if faq_answer_first_ok(readme):
        ai += 2
    if specific_facts_ok(readme):
        ai += 2

    breakdown = {
        "structure": structure,
        "content_depth": content,
        "seo": seo,
        "badges": badges,
        "visual_appeal": visuals,
        "completeness": completeness,
        "ai_citability": ai,
    }
    total = sum(breakdown.values())
    return {"total": total, "breakdown": breakdown, "secondary_in_h2": matched_secondary}


def load_seo_payload(repo_root: Path) -> dict[str, Any]:
    """Return a repo SEO payload, generating a fallback if needed."""
    cached = read_repo_cache(repo_root, "seo-data.json")
    if cached:
        return cached
    return run_seo(repo_root).seo_data


def build_snapshot(repo_root: Path) -> dict[str, Any]:
    """Gather repo signals for deterministic README generation."""
    snapshot = build_repo_snapshot(repo_root)
    repo_slug = snapshot["repo"]
    metadata = gh_repo_view(repo_slug) if "/" in repo_slug else {}
    if metadata is None:
        metadata = {}
    current_readme, readme_path = load_readme(repo_root)
    seo_data = load_seo_payload(repo_root)
    audit_data = read_repo_cache(repo_root, "audit-data.json") or {}
    legal_data = read_repo_cache(repo_root, "legal-data.json") or {}
    manifest_name = load_manifest_name(repo_root)
    manifest_description = load_manifest_description(repo_root)
    project_name = manifest_name or snapshot["repo_name"] or repo_root.name
    banner_path = banner_asset(repo_root)
    preview_asset = social_preview_asset(repo_root)

    enriched = dict(snapshot)
    enriched.update(
        {
            "repo": repo_slug,
            "repo_root": str(repo_root),
            "repo_name": project_name,
            "current_readme": current_readme,
            "current_readme_path": str(readme_path) if readme_path else str(repo_root / "README.md"),
            "seo_data": seo_data,
            "audit_data": audit_data,
            "legal_data": legal_data,
            "metadata": metadata,
            "license_label": license_type(repo_root, metadata, legal_data),
            "docs_link": docs_url(current_readme, metadata),
            "manifest_name": manifest_name,
            "manifest_description": manifest_description,
            "banner_path": banner_path,
            "social_preview_path": preview_asset,
        }
    )
    return enriched


def build_readme_payload(repo_root: Path, generate_assets: bool = False) -> dict[str, Any]:
    """Build deterministic README recommendations for a repo."""
    snapshot = build_snapshot(repo_root)
    asset_updates: dict[str, Any] = {}
    if generate_assets:
        asset_updates = ensure_readme_assets(snapshot)
        snapshot.update(
            {
                "banner_path": asset_updates.get("banner_path", snapshot.get("banner_path")),
                "social_preview_path": asset_updates.get("social_preview_path", snapshot.get("social_preview_path")),
            }
        )
    generated_readme, sections, generated_meta = build_readme_content(snapshot)
    score_before = score_readme_candidate(
        snapshot["current_readme"],
        snapshot["repo_type"],
        snapshot["seo_data"],
        snapshot["docs_link"],
    )
    score_after = score_readme_candidate(
        generated_readme,
        snapshot["repo_type"],
        snapshot["seo_data"],
        snapshot["docs_link"],
    )

    warnings: list[str] = []
    blocked: list[str] = []
    if snapshot["seo_data"].get("analysis_mode") == "fallback":
        warnings.append("README plan is using fallback SEO cache data without live DataForSEO verification.")
    if generate_assets:
        warnings.extend(asset_updates.get("asset_notes", []))
    if "/" not in snapshot["repo"]:
        warnings.append("No GitHub remote detected, so badge URLs and raw GitHub asset links may need manual adjustment.")

    payload = {
        "cache_type": "readme-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": "preview",
        "written": False,
        "repo": snapshot["repo"],
        "repo_root": snapshot["repo_root"],
        "repo_type": snapshot["repo_type"],
        "analysis_mode": "deterministic-preview",
        "assets_requested": generate_assets,
        "asset_mode": "local-only",
        "current_readme_path": snapshot["current_readme_path"],
        "score_before": score_before["total"],
        "score_after": score_after["total"],
        "score_breakdown_before": score_before["breakdown"],
        "score_breakdown_after": score_after["breakdown"],
        "banner_generated": asset_updates.get("banner_generated", False),
        "banner_prepared": asset_updates.get("banner_prepared", False),
        "banner_path": snapshot["banner_path"],
        "banner_status": "prepared" if asset_updates.get("banner_prepared") else generated_meta["banner_status"],
        "social_preview_generated": asset_updates.get("social_preview_generated", False),
        "social_preview_path": snapshot["social_preview_path"],
        "banner_links": asset_updates.get("banner_links", {}),
        "social_preview_links": asset_updates.get("social_preview_links", {}),
        "asset_tasks": asset_updates.get("asset_tasks", []),
        "keywords_integrated": {
            "primary_keyword": snapshot["seo_data"]["primary_keyword"]["keyword"],
            "primary_in_h1": snapshot["seo_data"]["primary_keyword"]["keyword"].lower() in generated_meta["title"].lower(),
            "primary_in_first_paragraph": snapshot["seo_data"]["primary_keyword"]["keyword"].lower() in generated_meta["intro"].lower(),
            "secondary_in_h2": generated_meta["secondary_in_h2"],
        },
        "sections": sections,
        "badges": generated_meta["badges"],
        "docs_link": snapshot["docs_link"],
        "warnings": warnings,
        "blocked": blocked,
        "data_sources": [
            "existing-readme" if snapshot["current_readme"] else "no-readme",
            "seo-cache",
            "audit-cache" if snapshot["audit_data"] else "repo-scan",
            "legal-cache" if snapshot["legal_data"] else "license-file-scan",
            "gh-metadata" if snapshot["metadata"] else "local-git-metadata",
        ],
        "generated_readme": generated_readme,
    }
    return payload


def apply_readme_plan(repo_root: Path, payload: dict[str, Any]) -> str:
    """Write the generated README to disk."""
    readme_path = repo_root / "README.md"
    readme_path.write_text(payload["generated_readme"], encoding="utf-8")
    return str(readme_path)


def build_readme_report(payload: dict[str, Any]) -> str:
    """Render a markdown report for deterministic README planning."""
    section_lines = "\n".join(f"- {section}" for section in payload["sections"]) or "- None"
    warning_lines = "\n".join(f"- {item}" for item in payload["warnings"]) or "- None"
    blocked_lines = "\n".join(f"- {item}" for item in payload["blocked"]) or "- None"
    banner_links = payload.get("banner_links") or {}
    preview_links = payload.get("social_preview_links") or {}
    asset_tasks = payload.get("asset_tasks") or []
    task_lines = "\n".join(
        f"- {task.get('type', 'asset')}: task `{task.get('task_id', '')}`"
        for task in asset_tasks
    ) or "- None"
    return f"""# GitHub README Report

- **Repository:** {payload['repo']}
- **Generated at:** {payload['timestamp']}
- **Mode:** {payload['mode']}
- **Written:** {payload['written']}

## Score Delta

| Criterion | Before | After |
|-----------|--------|-------|
| Structure | {payload['score_breakdown_before']['structure']} | {payload['score_breakdown_after']['structure']} |
| Content Depth | {payload['score_breakdown_before']['content_depth']} | {payload['score_breakdown_after']['content_depth']} |
| SEO | {payload['score_breakdown_before']['seo']} | {payload['score_breakdown_after']['seo']} |
| Badges | {payload['score_breakdown_before']['badges']} | {payload['score_breakdown_after']['badges']} |
| Visual Appeal | {payload['score_breakdown_before']['visual_appeal']} | {payload['score_breakdown_after']['visual_appeal']} |
| Completeness | {payload['score_breakdown_before']['completeness']} | {payload['score_breakdown_after']['completeness']} |
| AI Citability | {payload['score_breakdown_before']['ai_citability']} | {payload['score_breakdown_after']['ai_citability']} |
| **Total** | **{payload['score_before']}** | **{payload['score_after']}** |

## Generated Sections

{section_lines}

## Image Assets

- Asset mode: {payload.get('asset_mode', 'local-only')}
- Banner path: {payload.get('banner_path') or 'None'}
- Banner generated: {payload.get('banner_generated')}
- Banner prepared locally: {payload.get('banner_prepared', False)}
- Banner local link: {banner_links.get('local') or 'None'}
- Banner raw link: {banner_links.get('raw') or 'None'}
- Social preview path: {payload.get('social_preview_path') or 'None'}
- Social preview generated: {payload.get('social_preview_generated')}
- Social preview local link: {preview_links.get('local') or 'None'}
- Social preview raw link: {preview_links.get('raw') or 'None'}
- Settings URL: {preview_links.get('settings') or 'None'}

## Asset Tasks

{task_lines}

## Warnings

{warning_lines}

## Blocked / Manual

{blocked_lines}
"""


@dataclass
class ReadmeBundle:
    """Structured README output."""

    readme_data: dict[str, Any]
    report_markdown: str


def run_readme(repo_root: Path, write: bool = False, generate_assets: bool = False) -> ReadmeBundle:
    """Build a deterministic README plan and optionally write it to disk."""
    readme_data = build_readme_payload(repo_root, generate_assets=generate_assets)
    if write:
        written_path = apply_readme_plan(repo_root, readme_data)
        readme_data["mode"] = "write"
        readme_data["written"] = True
        readme_data["written_path"] = written_path
    report_markdown = build_readme_report(readme_data)
    return ReadmeBundle(readme_data=readme_data, report_markdown=report_markdown)


def write_readme_artifacts(repo_root: Path, bundle: ReadmeBundle) -> dict[str, str]:
    """Write README cache and report artifacts for one run."""
    slug = slugify(bundle.readme_data["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    readme_cache_path = write_repo_cache(
        repo_root,
        "readme-data.json",
        {key: value for key, value in bundle.readme_data.items() if key != "generated_readme"},
    )
    report_path = out_dir / "README-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    preview_path = out_dir / "README-PREVIEW.md"
    preview_path.write_text(bundle.readme_data["generated_readme"], encoding="utf-8")
    summary_path = out_dir / "README-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "readme_cache_path": str(readme_cache_path),
                "mode": bundle.readme_data["mode"],
                "written": bundle.readme_data["written"],
                "score_before": bundle.readme_data["score_before"],
                "score_after": bundle.readme_data["score_after"],
                "sections": bundle.readme_data["sections"],
                "banner_status": bundle.readme_data["banner_status"],
                "banner_generated": bundle.readme_data["banner_generated"],
                "banner_prepared": bundle.readme_data["banner_prepared"],
                "banner_path": bundle.readme_data["banner_path"],
                "social_preview_generated": bundle.readme_data["social_preview_generated"],
                "social_preview_path": bundle.readme_data["social_preview_path"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "readme_cache": str(readme_cache_path),
        "report": str(report_path),
        "preview": str(preview_path),
        "summary_json": str(summary_path),
    }
