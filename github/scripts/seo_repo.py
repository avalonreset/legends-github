#!/usr/bin/env python3
"""Deterministic SEO cache generation for Legends GitHub."""

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

from audit_repo import detect_repo_type, load_readme, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_repo_view, repo_slug_from_git
from runtime_paths import repo_output_dir


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "with",
    "your",
}

GENERIC_WORDS = {
    "app",
    "application",
    "align",
    "badge",
    "badges",
    "cli",
    "code",
    "codex",
    "center",
    "file",
    "files",
    "framework",
    "github",
    "http",
    "https",
    "img",
    "library",
    "open",
    "opensource",
    "package",
    "plugin",
    "project",
    "repo",
    "repos",
    "repository",
    "script",
    "service",
    "skill",
    "software",
    "source",
    "src",
    "tool",
    "tools",
    "width",
}

PACKAGE_JSON = "package.json"
PYPROJECT = "pyproject.toml"
SETUP_PY = "setup.py"
CARGO = "Cargo.toml"


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def strip_code_blocks(value: str) -> str:
    """Remove fenced code blocks from markdown-like text."""
    return re.sub(r"```.*?```", " ", value, flags=re.DOTALL)


def clean_text(value: str) -> str:
    """Collapse markdown-ish text into one sentence."""
    text = strip_code_blocks(value)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r" \1 ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r" \1 ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    collapsed = re.sub(r"\s+", " ", text.replace("`", " ").replace("#", " ")).strip()
    return collapsed


def tokenize(value: str) -> list[str]:
    """Split free text into normalized tokens."""
    return [
        token
        for token in re.findall(r"[a-z0-9][a-z0-9\+\-_]*", value.lower())
        if len(token) >= 2 and token not in STOPWORDS
    ]


def extract_heading_lines(readme: str) -> list[str]:
    """Return markdown heading text."""
    lines: list[str] = []
    for line in readme.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            lines.append(clean_text(stripped.lstrip("#").strip()))
    return lines


def first_paragraph(readme: str) -> str:
    """Return the first non-heading paragraph from a README."""
    for chunk in re.split(r"\n\s*\n", readme):
        stripped = chunk.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<") or stripped.startswith("```"):
            continue
        if "img.shields.io" in stripped.lower() or stripped.count("](") >= 2:
            continue
        return clean_text(stripped)
    return ""


def load_manifest_description(repo_root: Path) -> str:
    """Extract a best-effort project description from common manifest files."""
    package_json = repo_root / PACKAGE_JSON
    if package_json.exists():
        try:
            payload = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        description = str(payload.get("description") or "").strip()
        if description:
            return clean_text(description)

    pyproject = repo_root / PYPROJECT
    if pyproject.exists():
        try:
            payload = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            payload = {}
        project = payload.get("project", {})
        description = str(project.get("description") or "").strip()
        if description:
            return clean_text(description)

    cargo = repo_root / CARGO
    if cargo.exists():
        try:
            payload = tomllib.loads(cargo.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            payload = {}
        package = payload.get("package", {})
        description = str(package.get("description") or "").strip()
        if description:
            return clean_text(description)

    setup_py = repo_root / SETUP_PY
    if setup_py.exists():
        text = setup_py.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"description\s*=\s*['\"]([^'\"]+)['\"]", text)
        if match:
            return clean_text(match.group(1))

    return ""


def load_manifest_name(repo_root: Path) -> str:
    """Extract a best-effort project name from common manifest files."""
    package_json = repo_root / PACKAGE_JSON
    if package_json.exists():
        try:
            payload = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        name = str(payload.get("name") or "").strip()
        if name:
            return clean_text(name)

    pyproject = repo_root / PYPROJECT
    if pyproject.exists():
        try:
            payload = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            payload = {}
        project = payload.get("project", {})
        name = str(project.get("name") or "").strip()
        if name:
            return clean_text(name)

    cargo = repo_root / CARGO
    if cargo.exists():
        try:
            payload = tomllib.loads(cargo.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            payload = {}
        package = payload.get("package", {})
        name = str(package.get("name") or "").strip()
        if name:
            return clean_text(name)

    setup_py = repo_root / SETUP_PY
    if setup_py.exists():
        text = setup_py.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"name\s*=\s*['\"]([^'\"]+)['\"]", text)
        if match:
            return clean_text(match.group(1))

    return ""


def repo_type_topics(repo_type: str) -> list[str]:
    """Map repo types to sane topic defaults."""
    mapping = {
        "Skill/Plugin": ["skill", "plugin"],
        "Library/Package": ["library", "package"],
        "CLI Tool": ["cli", "developer-tools"],
        "Framework": ["framework"],
        "API/Service": ["api", "service"],
        "Application": ["application"],
        "Documentation": ["documentation"],
    }
    return mapping.get(repo_type, ["application"])


def normalize_topic(value: str) -> str:
    """Normalize text into a GitHub topic slug."""
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized


def topic_names(values: list[Any]) -> list[str]:
    """Normalize GitHub topic payloads into plain strings."""
    names: list[str] = []
    for value in values:
        if isinstance(value, str):
            names.append(value)
        elif isinstance(value, dict):
            name = str(value.get("name") or "").strip()
            if name:
                names.append(name)
    return names


def canonical_project_name(manifest_name: str, readme_h1: str, repo_root: Path) -> str:
    """Return a human-friendly project name for fallback descriptions."""
    if manifest_name:
        return manifest_name
    if readme_h1:
        return re.split(r"\s[-:]\s", readme_h1, maxsplit=1)[0].strip() or readme_h1.strip()
    return repo_root.name.replace("-", " ").replace("_", " ").strip()


def phrase_candidates(text: str, weight: int) -> dict[str, int]:
    """Build weighted bigram and trigram candidates from one source."""
    tokens = tokenize(text)
    results: dict[str, int] = {}
    for size in (2, 3):
        if len(tokens) < size:
            continue
        for index in range(len(tokens) - size + 1):
            gram_tokens = tokens[index : index + size]
            if all(token in GENERIC_WORDS for token in gram_tokens):
                continue
            phrase = " ".join(gram_tokens)
            results[phrase] = results.get(phrase, 0) + weight
    return results


def build_keyword_candidates(
    repo_name: str,
    description: str,
    manifest_description: str,
    readme_h1: str,
    intro: str,
    headings: list[str],
    language: str,
    repo_type: str,
    topics: list[str],
) -> list[str]:
    """Return deterministic ranked keyword candidates."""
    scored: dict[str, int] = {}
    sources = [
        (repo_name.replace("-", " ").replace("_", " "), 6),
        (description, 10),
        (manifest_description, 9),
        (readme_h1, 8),
        (intro, 10),
        (" ".join(headings[:6]), 4),
        (" ".join(topic.replace("-", " ") for topic in topics), 12),
    ]
    for text, weight in sources:
        for phrase, score in phrase_candidates(text, weight).items():
            scored[phrase] = scored.get(phrase, 0) + score

    language_term = normalize_topic(language).replace("-", " ").strip()
    if language_term:
        for topic in repo_type_topics(repo_type):
            phrase = f"{language_term} {topic.replace('-', ' ')}".strip()
            scored[phrase] = scored.get(phrase, 0) + 7

    if description:
        description_tokens = tokenize(description)
        if description_tokens:
            phrase = " ".join(description_tokens[: min(3, len(description_tokens))])
            if len(phrase.split()) >= 2:
                scored[phrase] = scored.get(phrase, 0) + 9

    ranked = sorted(scored.items(), key=lambda item: (-item[1], len(item[0]), item[0]))
    results: list[str] = []
    for phrase, _score in ranked:
        if phrase in results:
            continue
        if len(phrase) < 6:
            continue
        if phrase.startswith("open source "):
            continue
        results.append(phrase)
    return results


def choose_primary_keyword(candidates: list[str], repo_name: str, language: str, repo_type: str) -> str:
    """Pick the best primary keyword or a deterministic fallback."""
    if candidates:
        return candidates[0]

    language_term = normalize_topic(language).replace("-", " ").strip()
    type_terms = repo_type_topics(repo_type)
    if language_term and type_terms:
        return f"{language_term} {type_terms[0].replace('-', ' ')}"
    normalized_name = repo_name.replace("-", " ").replace("_", " ").strip()
    return normalized_name or "open source project"


def choose_secondary_keywords(candidates: list[str], primary_keyword: str) -> list[dict[str, Any]]:
    """Return secondary keyword payloads."""
    secondary: list[dict[str, Any]] = []
    for phrase in candidates:
        if phrase == primary_keyword:
            continue
        secondary.append(
            {
                "keyword": phrase,
                "volume": None,
                "difficulty": None,
                "category": "Unverified",
                "intent": "unknown",
                "source": "codebase-fallback",
            }
        )
        if len(secondary) == 5:
            break
    return secondary


def build_topics(
    repo_name: str,
    primary_keyword: str,
    secondary_keywords: list[dict[str, Any]],
    existing_topics: list[str],
    language: str,
    repo_type: str,
) -> list[str]:
    """Build a deterministic recommended topic list."""
    topics: list[str] = []

    def add(topic: str) -> None:
        normalized = normalize_topic(topic)
        if not normalized or normalized in topics:
            return
        topics.append(normalized)

    for topic in existing_topics:
        add(topic)
    add(repo_name)
    if language:
        add(language)
    for topic in repo_type_topics(repo_type):
        add(topic)
    add("open-source")

    def concise_phrase_topic(value: str) -> bool:
        tokens = tokenize(value)
        slug = normalize_topic(value)
        return bool(tokens) and len(tokens) <= 2 and len(slug) <= 24 and not all(token in GENERIC_WORDS for token in tokens)

    if concise_phrase_topic(primary_keyword):
        add(primary_keyword)
    for keyword in secondary_keywords:
        phrase = keyword["keyword"]
        if concise_phrase_topic(phrase):
            add(phrase)
    for token in tokenize(primary_keyword):
        if token not in GENERIC_WORDS:
            add(token)
    for keyword in secondary_keywords:
        for token in tokenize(keyword["keyword"]):
            if token not in GENERIC_WORDS:
                add(token)

    return topics[:10]


def build_recommended_description(project_name: str, summary: str, primary_keyword: str) -> str:
    """Draft a deterministic SEO-forward repo description."""
    cleaned_summary = clean_text(summary)
    pretty_name = project_name.replace("-", " ").replace("_", " ").strip()
    if cleaned_summary and primary_keyword.lower() in cleaned_summary.lower():
        description = cleaned_summary
    elif cleaned_summary:
        description = cleaned_summary if cleaned_summary.lower().startswith(pretty_name.lower()) else f"{pretty_name}: {cleaned_summary}"
    else:
        description = f"{pretty_name} is an open source project for {primary_keyword}."
    return description[:347].rstrip(" .,;:") + ("..." if len(description) > 347 else "")


def fallback_paa_questions(primary_keyword: str, repo_type: str) -> list[str]:
    """Provide deterministic README FAQ prompts when live SERP data is unavailable."""
    base = primary_keyword.capitalize()
    prompts = [
        f"What does {base} do?",
        f"How do I install or use this {repo_type.lower()}?",
        f"When should I choose this project over alternatives?",
    ]
    return prompts


@dataclass
class SeoBundle:
    """Structured SEO output."""

    seo_data: dict[str, Any]
    report_markdown: str


def build_repo_snapshot(repo_root: Path) -> dict[str, Any]:
    """Gather the repo signals used for deterministic SEO fallback analysis."""
    cached_context = read_repo_cache(repo_root, "repo-context.json") or {}
    repo_slug = cached_context.get("repo") or repo_slug_from_git(repo_root) or repo_root.name
    metadata_raw = gh_repo_view(repo_slug) if "/" in repo_slug else None
    readme, _readme_path = load_readme(repo_root)
    headings = extract_heading_lines(readme)
    intro = first_paragraph(readme)
    manifest_name = load_manifest_name(repo_root)
    readme_h1 = headings[0] if headings else repo_root.name.replace("-", " ").replace("_", " ")
    manifest_description = load_manifest_description(repo_root)
    description = (
        (metadata_raw or {}).get("description")
        or cached_context.get("description")
        or manifest_description
        or intro
    )
    primary_language = (
        ((metadata_raw or {}).get("primaryLanguage") or {}).get("name")
        or cached_context.get("primary_language")
        or ""
    )
    topics = topic_names((metadata_raw or {}).get("repositoryTopics") or cached_context.get("topics") or [])
    repo_type = cached_context.get("repo_type") or detect_repo_type(repo_root)
    project_name = canonical_project_name(manifest_name, readme_h1, repo_root)
    return {
        "repo": repo_slug,
        "repo_root": str(repo_root),
        "repo_name": project_name,
        "description": clean_text(description),
        "manifest_name": manifest_name,
        "manifest_description": manifest_description,
        "primary_language": primary_language,
        "topics": topics,
        "repo_type": repo_type,
        "readme_h1": readme_h1,
        "readme_intro": intro,
        "headings": headings[1:],
        "used_cached_repo_context": bool(cached_context),
        "gh_metadata_available": metadata_raw is not None,
    }


def build_seo_report(snapshot: dict[str, Any], seo_data: dict[str, Any]) -> str:
    """Render a markdown report for deterministic SEO cache generation."""
    secondary = seo_data["secondary_keywords"]
    secondary_lines = "\n".join(f"- {item['keyword']}" for item in secondary) if secondary else "- None"
    topic_lines = "\n".join(f"- `{topic}`" for topic in seo_data["recommended_topics"]) or "- None"
    paa_lines = "\n".join(f"- {question}" for question in seo_data["paa_questions"])
    return f"""# GitHub SEO Report

- **Repository:** {snapshot['repo']}
- **Generated at:** {seo_data['timestamp']}
- **Mode:** {seo_data['mode']}
- **Analysis:** {seo_data['analysis_mode']}

## Warning

This headless SEO run is deterministic fallback analysis. It does not call
DataForSEO MCP, so search volume, difficulty, intent, and SERP position are
unverified.

## Primary Keyword

- `{seo_data['primary_keyword']['keyword']}`

## Secondary Keywords

{secondary_lines}

## Recommended Description

{seo_data['recommended_description']}

## Recommended Topics

{topic_lines}

## FAQ Prompts

{paa_lines}

## Next Step

Run `github meta` or `github readme` with `.github-audit/seo-data.json` already
seeded from this fallback pass.
"""


def run_seo(repo_root: Path, mode: str = "quick") -> SeoBundle:
    """Run deterministic fallback SEO analysis for a local git repository."""
    snapshot = build_repo_snapshot(repo_root)
    candidates = build_keyword_candidates(
        repo_name=snapshot["repo_name"],
        description=snapshot["description"],
        manifest_description=snapshot["manifest_description"],
        readme_h1=snapshot["readme_h1"],
        intro=snapshot["readme_intro"],
        headings=snapshot["headings"],
        language=snapshot["primary_language"],
        repo_type=snapshot["repo_type"],
        topics=snapshot["topics"],
    )
    primary_keyword = choose_primary_keyword(
        candidates=candidates,
        repo_name=snapshot["repo_name"],
        language=snapshot["primary_language"],
        repo_type=snapshot["repo_type"],
    )
    secondary_keywords = choose_secondary_keywords(candidates, primary_keyword)
    recommended_topics = build_topics(
        repo_name=snapshot["repo_name"],
        primary_keyword=primary_keyword,
        secondary_keywords=secondary_keywords,
        existing_topics=snapshot["topics"],
        language=snapshot["primary_language"],
        repo_type=snapshot["repo_type"],
    )
    summary = snapshot["description"] or snapshot["manifest_description"] or snapshot["readme_intro"]
    seo_data = {
        "cache_type": "seo-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": mode,
        "analysis_mode": "fallback",
        "repo": snapshot["repo"],
        "repo_root": snapshot["repo_root"],
        "repo_type": snapshot["repo_type"],
        "primary_language": snapshot["primary_language"],
        "primary_keyword": {
            "keyword": primary_keyword,
            "volume": None,
            "difficulty": None,
            "category": "Unverified",
            "intent": "unknown",
            "source": "codebase-fallback",
        },
        "secondary_keywords": secondary_keywords,
        "skip_keywords": [],
        "recommended_description": build_recommended_description(snapshot["repo_name"], summary, primary_keyword),
        "recommended_topics": recommended_topics,
        "paa_questions": fallback_paa_questions(primary_keyword, snapshot["repo_type"]),
        "ai_visibility": {
            "cited": False,
            "competitors_cited": [],
            "analysis_mode": "unverified",
            "note": "Deterministic fallback analysis without live DataForSEO or LLM citation data.",
        },
        "serp_verified": False,
        "github_in_serp": False,
        "github_serp_position": None,
        "data_sources": [
            "codebase-analysis",
            "readme-analysis",
            "repo-metadata" if snapshot["gh_metadata_available"] else "local-git-metadata",
        ],
        "warnings": [
            "Headless seo uses deterministic fallback analysis and does not call DataForSEO MCP.",
            "Keyword volume, difficulty, intent, and SERP rankings are unverified in this mode.",
        ],
        "cost_receipt": {
            "currency": "USD",
            "estimated_total": 0.0,
            "calls": [],
        },
    }
    report_markdown = build_seo_report(snapshot, seo_data)
    return SeoBundle(seo_data=seo_data, report_markdown=report_markdown)


def write_seo_artifacts(repo_root: Path, bundle: SeoBundle) -> dict[str, str]:
    """Write SEO cache and report artifacts for one run."""
    slug = slugify(bundle.seo_data["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    seo_cache_path = write_repo_cache(repo_root, "seo-data.json", bundle.seo_data)
    report_path = out_dir / "SEO-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    summary_path = out_dir / "SEO-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "seo_cache_path": str(seo_cache_path),
                "primary_keyword": bundle.seo_data["primary_keyword"],
                "recommended_topics": bundle.seo_data["recommended_topics"],
                "recommended_description": bundle.seo_data["recommended_description"],
                "analysis_mode": bundle.seo_data["analysis_mode"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "seo_cache": str(seo_cache_path),
        "report": str(report_path),
        "summary_json": str(summary_path),
    }
