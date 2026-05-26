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
from github_runtime import gh_repo_view, pillow_available, resolve_kie_api_key
from kie_assets import (
    AssetGenerationError,
    convert_png_to_webp,
    create_kie_task,
    download_binary,
    poll_kie_task,
    render_social_preview_from_banner,
    result_url,
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
        if path.exists():
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


def banner_prompt(snapshot: dict[str, Any], tagline: str) -> str:
    """Build a deterministic KIE banner prompt."""
    project_name = snapshot["repo_name"]
    repo_type = snapshot["repo_type"]
    primary_keyword = snapshot["seo_data"]["primary_keyword"]["keyword"]
    visual = {
        "Skill/Plugin": "abstract modular command blocks, glowing panels, and subtle code patterns",
        "CLI Tool": "sleek terminal interface with luminous command lines and geometric hardware accents",
        "Library/Package": "interlocking components, clean technical diagrams, and polished glass reflections",
        "Framework": "layered architectural structures and connected luminous pathways",
        "API/Service": "data streams, service nodes, and routed signals in a modern control-plane scene",
        "Application": "product interface panels and cinematic UI surfaces with depth",
        "Documentation": "clean knowledge panels, layered cards, and structured information surfaces",
    }.get(repo_type, "professional technology shapes and cinematic abstract geometry")
    return (
        "Wide cinematic 21:9 GitHub repository banner. "
        f'Left side: large bold clean sans-serif headline "{project_name}", '
        f'smaller supporting line "{tagline}" below, crisp white text, fully legible. '
        f"Right side: {visual}. "
        f"Theme: {primary_keyword}. "
        "Dark background, subtle light bloom, premium product-banner look, centered composition with safe edge padding."
    )


def ensure_readme_assets(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Generate missing banner/social assets when explicit asset generation is requested."""
    repo_root = Path(snapshot["repo_root"])
    updates: dict[str, Any] = {
        "banner_generated": False,
        "social_preview_generated": False,
        "asset_tasks": [],
    }
    branch = default_branch_name(snapshot["metadata"])

    banner_path = snapshot.get("banner_path")
    if not banner_path:
        kie_api_key = snapshot.get("kie_api_key") or ""
        if not kie_api_key:
            raise AssetGenerationError("KIE_API_KEY is required to generate a new banner asset.")
        if not pillow_available():
            raise AssetGenerationError("Pillow is required to convert generated banner assets.")
        task_id = create_kie_task(
            kie_api_key,
            banner_prompt(snapshot, build_tagline(snapshot, snapshot["seo_data"]["primary_keyword"]["keyword"])),
            aspect_ratio="21:9",
        )
        record = poll_kie_task(kie_api_key, task_id)
        source_url = result_url(record)
        original_path = repo_root / "assets" / "originals" / "banner.png"
        download_binary(source_url, original_path)
        banner_path_abs = repo_root / "assets" / "banner.webp"
        convert_png_to_webp(original_path, banner_path_abs)
        banner_path = str(banner_path_abs.relative_to(repo_root)).replace("\\", "/")
        updates.update(
            {
                "banner_generated": True,
                "banner_original_path": str(original_path.relative_to(repo_root)).replace("\\", "/"),
                "banner_path": banner_path,
            }
        )
        updates["asset_tasks"].append({"type": "banner", "task_id": task_id, "source_url": source_url})

    social_preview_path = snapshot.get("social_preview_path")
    if not social_preview_path:
        if not pillow_available():
            raise AssetGenerationError("Pillow is required to generate a social preview from the banner.")
        banner_abs = repo_root / Path(str(banner_path))
        preview_abs = repo_root / "assets" / "social-preview.jpg"
        render_social_preview_from_banner(banner_abs, preview_abs)
        social_preview_path = str(preview_abs.relative_to(repo_root)).replace("\\", "/")
        updates.update({"social_preview_generated": True, "social_preview_path": social_preview_path})

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
    return "See LICENSE"


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
    """Return a best-effort installation block."""
    package_json = load_package_json(repo_root)
    if package_json.get("name"):
        return f"```bash\nnpm install {package_json['name']}\n```"

    pyproject = load_pyproject(repo_root)
    project = pyproject.get("project", {})
    if project.get("name"):
        return f"```bash\npip install {project['name']}\n```"

    if (repo_root / "Cargo.toml").exists():
        cargo_name = ""
        try:
            cargo = tomllib.loads((repo_root / "Cargo.toml").read_text(encoding="utf-8"))
            cargo_name = str((cargo.get("package") or {}).get("name") or "").strip()
        except (OSError, tomllib.TOMLDecodeError):
            cargo_name = ""
        if cargo_name:
            if repo_type == "CLI Tool":
                return f"```bash\ncargo install {cargo_name}\n```"
            return f"```bash\ncargo add {cargo_name}\n```"

    if repo_type == "Skill/Plugin":
        return (
            "```bash\n"
            "git clone https://github.com/OWNER/REPO.git\n"
            "cd REPO\n"
            "bash install.sh\n"
            "```"
        )

    return (
        "```bash\n"
        f"git clone https://github.com/OWNER/{slugify(project_name)}.git\n"
        f"cd {slugify(project_name)}\n"
        "```"
    )


def quick_start_snippet(repo_root: Path, repo_type: str, project_name: str) -> str:
    """Return a best-effort quick-start block."""
    package_json = load_package_json(repo_root)
    scripts = package_json.get("scripts") or {}
    if isinstance(scripts, dict):
        for name in ("start", "dev", "test"):
            if name in scripts:
                return f"```bash\nnpm run {name}\n```"

    if repo_type == "Skill/Plugin":
        return (
            "```bash\n"
            "python3 ~/.codex/skills/github/scripts/run_headless.py verify --mode both --path /path/to/repo\n"
            "```"
        )
    if repo_type == "CLI Tool":
        return f"```bash\n{slugify(project_name)} --help\n```"
    if repo_type == "Library/Package":
        module_name = re.sub(r"[^a-zA-Z0-9_]+", "_", project_name).strip("_") or "project_name"
        return (
            "```python\n"
            f"import {module_name}\n\n"
            f'print("{project_name} is ready")\n'
            "```"
        )
    if (repo_root / "Dockerfile").exists():
        return "```bash\ndocker compose up --build\n```"
    return "```bash\npython main.py\n```"


def configuration_snippet(repo_root: Path) -> str:
    """Return a best-effort configuration block."""
    if (repo_root / ".env.example").exists():
        return (
            "Copy `.env.example` to `.env.local`, then update the variables for your environment.\n\n"
            "```bash\ncp .env.example .env.local\n```"
        )
    if (repo_root / ".env.local").exists() or (repo_root / ".env").exists():
        return "Configuration is environment-driven. Review the existing `.env` files before running locally."
    if (repo_root / "config.toml").exists() or (repo_root / "settings.toml").exists():
        return "Update the TOML configuration file in the repo root before the first real run."
    return "This project keeps configuration minimal. Review the repository files and command flags for environment-specific settings."


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
    """Build a short H1 tagline."""
    project_name = snapshot["repo_name"]
    description = clean_text(snapshot.get("description") or snapshot.get("manifest_description") or "")
    if description:
        short = description.split(".")[0].strip()
        if len(short) <= 60:
            return short

    repo_type = snapshot["repo_type"]
    if repo_type == "Skill/Plugin":
        return f"{sentence_case(primary_keyword)} for Codex and GitHub workflows"
    if repo_type == "CLI Tool":
        return f"{sentence_case(primary_keyword)} for terminal workflows"
    if repo_type == "Library/Package":
        return f"{sentence_case(primary_keyword)} for application developers"
    if repo_type == "Framework":
        return f"{sentence_case(primary_keyword)} for structured projects"
    return f"{project_name} for {primary_keyword}"


def build_intro(snapshot: dict[str, Any], primary_keyword: str) -> str:
    """Build the README opening paragraph."""
    project_name = snapshot["repo_name"]
    summary = clean_text(snapshot.get("description") or snapshot.get("manifest_description") or snapshot.get("readme_intro") or "")
    repo_type = {
        "Skill/Plugin": "skill",
        "CLI Tool": "CLI tool",
        "Library/Package": "library",
        "Framework": "framework",
        "API/Service": "service",
        "Application": "application",
        "Documentation": "documentation project",
    }.get(snapshot["repo_type"], "project")
    sentence_one = f"{project_name} is a {primary_keyword} {repo_type} that helps teams ship a cleaner GitHub experience."
    if summary and primary_keyword.lower() in summary.lower():
        sentence_two = summary.rstrip(".") + "."
    elif summary:
        sentence_two = (
            f"It focuses on {summary[0].lower() + summary[1:].rstrip('.')}"
            if len(summary) > 1
            else summary.rstrip(".")
        )
        sentence_two = sentence_two.rstrip(".") + "."
    else:
        sentence_two = "It gives new users the context, setup path, and next steps they need without digging through the repository."
    sentence_three = "Use this README as the landing page for installation, key workflows, and the fastest path to value."
    return " ".join(part.strip() for part in (sentence_one, sentence_two, sentence_three) if part.strip())


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
    license_slug = re.sub(r"[^a-zA-Z0-9]+", "-", license_label).strip("-").lower() or "license"
    badges.append(
        f"[![License](https://img.shields.io/badge/license-{license_slug}-blue)](LICENSE)"
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
    primary_keyword = snapshot["seo_data"]["primary_keyword"]["keyword"]
    secondary_keywords = [item["keyword"] for item in snapshot["seo_data"].get("secondary_keywords", [])[:2]]
    questions = snapshot["seo_data"].get("paa_questions", [])[:3]

    if key == "what_it_does":
        bullets = [
            f"- Centers the repository around the primary keyword `{primary_keyword}` without stuffing the copy.",
            "- Gives first-time users a clear installation path and a concrete quick start.",
            "- Surfaces the most important workflows before the reader has to inspect the codebase.",
        ]
        if secondary_keywords:
            bullets.append(f"- Weaves secondary topics such as `{secondary_keywords[0]}` into the structure where they fit naturally.")
        return "\n".join(bullets)

    if key == "snapshot":
        return repo_snapshot_table(snapshot, license_label)

    if key == "installation":
        return install_snippet(Path(snapshot["repo_root"]), snapshot["repo_type"], project_name)

    if key == "quick_start":
        return quick_start_snippet(Path(snapshot["repo_root"]), snapshot["repo_type"], project_name)

    if key == "commands":
        if snapshot["repo_type"] == "Skill/Plugin":
            return (
                "| Workflow | When to use it |\n"
                "|----------|----------------|\n"
                "| Audit | Score the current repository state before making changes. |\n"
                "| SEO | Seed keyword data for README and metadata work. |\n"
                "| Meta | Plan repository description, topics, and feature toggles. |\n"
                "| README | Preview or write a deterministic README refresh. |\n"
            )
        return existing_sections.get("commands", "") or existing_sections.get("usage", "") or (
            "Use the quick-start command first, then inspect the repo-specific scripts or CLI help for the full workflow surface."
        )

    if key == "usage":
        return existing_sections.get("usage", "") or (
            "Start with the quick-start example above, then move into the repository's real workflows once the baseline setup succeeds."
        )

    if key == "configuration":
        return configuration_snippet(Path(snapshot["repo_root"]))

    if key == "architecture":
        manifest_description = clean_text(snapshot.get("manifest_description") or "")
        if manifest_description:
            return f"The current implementation centers on {manifest_description.lower()}."
        return "The repository is organized around a small set of entrypoints and supporting assets so contributors can trace the main workflow quickly."

    if key == "documentation":
        return f"External docs are available at [{docs_link}]({docs_link}). Use the README as the landing page, then follow the docs for deeper reference material."

    if key == "faq":
        entries: list[str] = []
        for question in questions:
            entries.append(f"### {question}\n{project_name} answers this in the sections above so users can find the setup path and main workflow without guessing.")
        if not entries:
            entries.append(f"### What problem does {project_name} solve?\nIt gives readers a structured path through the repository with the right level of context for the project type.")
        return "\n\n".join(entries)

    if key == "contributing":
        if (Path(snapshot["repo_root"]) / "CONTRIBUTING.md").exists():
            return "See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines, local setup notes, and review expectations."
        return "Open an issue or pull request with a clear summary of the change, expected behavior, and any validation you ran."

    if key == "license":
        return f"This project is distributed under the [{license_label}](LICENSE) terms."

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
    title = f"# {snapshot['repo_name']} - {tagline}"
    badges = build_badges(repo_root, repo_slug, license_label)
    intro = build_intro(snapshot, snapshot["seo_data"]["primary_keyword"]["keyword"])

    section_specs = section_order(snapshot["repo_type"], docs_link)
    sections: list[tuple[str, str]] = []
    for heading, key in section_specs:
        if key == "snapshot":
            body = fallback_section_content(key, snapshot, license_label, docs_link, existing_sections)
        else:
            body = section_body(existing_sections, SECTION_SYNONYMS.get(key, []))
            if not body:
                body = fallback_section_content(key, snapshot, license_label, docs_link, existing_sections)
        if body:
            sections.append((heading, body.strip()))

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
        banner_block = "<!-- TODO: Add banner image -->\n"
        banner_status = "manual"

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
    kie_api_key, kie_source = resolve_kie_api_key(repo_root)

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
            "kie_api_key": kie_api_key,
            "kie_available": bool(kie_api_key),
            "kie_source": kie_source,
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
    if not snapshot["banner_path"]:
        blocked.append("Banner generation remains manual in deterministic mode. Add assets/banner.webp or use the interactive KIE flow.")
    if not snapshot["social_preview_path"]:
        blocked.append("Social preview image is not set. Upload remains manual after banner work is complete.")
    if generate_assets:
        warnings.append("Deterministic readme asset generation was explicitly enabled for this run.")
    elif snapshot["kie_available"]:
        warnings.append(f"KIE_API_KEY is available via {snapshot['kie_source']}, but deterministic readme will only generate assets when --generate-assets is used.")
    else:
        warnings.append("KIE_API_KEY not found. Banner and social preview generation are unavailable in deterministic mode.")
    if not pillow_available():
        warnings.append("Pillow is not installed. Deterministic banner conversion and social preview generation are unavailable.")
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
        "current_readme_path": snapshot["current_readme_path"],
        "score_before": score_before["total"],
        "score_after": score_after["total"],
        "score_breakdown_before": score_before["breakdown"],
        "score_breakdown_after": score_after["breakdown"],
        "banner_generated": asset_updates.get("banner_generated", False),
        "banner_path": snapshot["banner_path"],
        "banner_status": "generated" if asset_updates.get("banner_generated") else generated_meta["banner_status"],
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

- Banner path: {payload.get('banner_path') or 'None'}
- Banner generated: {payload.get('banner_generated')}
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
