"""Bounded, local evidence and organic discovery experiments for any repository.

Planning never executes target code, reads credentials, calls a provider, or
changes files. File presence and text signals are leads, not verified claims.
Only write_discovery_artifacts writes the toolkit's usual cache/output paths.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any

from cache_state import write_repo_cache
from runtime_paths import repo_output_dir

SCHEMA_VERSION = "1.0.0"
MAX_TEXT_BYTES = 262_144
MAX_DIRECTORY_ENTRIES = 500
MAX_DIRECTORIES = 30
MAX_DISCOVERED_FILES = 40
MAX_TOTAL_BYTES = 4 * 1024 * 1024
MAX_COMPETITORS = 10
TEXT_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
EXAMPLE_EXTENSIONS = TEXT_EXTENSIONS | {".py", ".js", ".ts", ".sh", ".ps1", ".rs", ".go"}
SKIP_NAMES = {"node_modules", "vendor", "dist", "build", "__pycache__", "secrets", "credentials"}
README_NAMES = ("README.md", "readme.md", "README.rst", "README.txt", "README")
ROOT_FILES = {
    "package.json": "manifest", "pyproject.toml": "manifest", "Cargo.toml": "manifest",
    "go.mod": "manifest", "setup.cfg": "manifest", "SKILL.md": "skill",
    "mkdocs.yml": "documentation_config", "mkdocs.yaml": "documentation_config",
    "docusaurus.config.js": "documentation_config", "docusaurus.config.ts": "documentation_config",
    "openapi.yaml": "service_spec", "openapi.yml": "service_spec",
    "CHANGELOG.md": "release_notes", "CHANGES.md": "release_notes", "HISTORY.md": "release_notes",
    "LICENSE": "license", "LICENSE.md": "license", "LICENSE.txt": "license", "COPYING": "license",
    "CONTRIBUTING.md": "contribution_guide",
}
SIGNALS = {
    "setup": r"\b(?:install(?:ation)?|setup|quick[ -]?start|getting started)\b",
    "example": r"\b(?:example|tutorial|walkthrough|usage|worked example)\b",
    "navigation": r"\b(?:contents|navigation|start here)\b",
    "cost": r"\b(?:pricing|costs?|billing|metered|pay.as.you.go)\b",
    "comparison": r"\b(?:alternatives?|comparison|compare|versus|trade.offs?)\b",
    "limits": r"\b(?:limitations?|unsupported|constraints?|troubleshoot\w*)\b",
    "release": r"\b(?:release|changelog|migration|upgrade)\b",
}
REFERENCES = [
    {"title": "GitHub repository topics", "url": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics"},
    {"title": "GitHub repository traffic", "url": "https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository"},
    {"title": "Google helpful content guidance", "url": "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"},
    {"title": "GitHub release asset counts", "url": "https://docs.github.com/en/rest/releases/assets"},
]


def _context(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text")
    value = " ".join(value.split())
    if len(value) > 240:
        raise ValueError(f"{label} must be at most 240 characters")
    return value


def _safe_path(root: Path, path: Path) -> bool:
    """Reject links/reparse points as well as paths outside the selected root."""
    try:
        if not path.resolve().is_relative_to(root):
            return False
        current = root
        for part in path.relative_to(root).parts:
            current = current / part
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                return False
        return True
    except (OSError, ValueError, RuntimeError):
        return False


def _inventory(root: Path) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    texts: dict[str, str] = {}
    coverage: dict[str, Any] = {"truncated": False, "notes": [], "discovered_files": 0,
                                "text_bytes_read": 0, "directories_visited": 0}

    def add(path: Path, kind: str, read_text: bool = True) -> None:
        relative = path.relative_to(root).as_posix()
        row: dict[str, Any] = {"id": "file:" + relative, "path": relative, "kind": kind,
                               "availability": "available", "signals": []}
        rows.append(row)
        if not _safe_path(root, path):
            row.update(availability="unavailable", reason="unsafe_or_unreadable_path")
            return
        try:
            if not path.is_file():
                row.update(availability="unavailable", reason="not_a_file")
                return
            row["bytes"] = path.stat().st_size
            if not read_text:
                row["inspection"] = "filename_only"
                return
            if row["bytes"] > MAX_TEXT_BYTES or coverage["text_bytes_read"] + row["bytes"] > MAX_TOTAL_BYTES:
                row.update(availability="unavailable", reason="text_size_limit")
                coverage["truncated"] = True
                return
            with path.open("rb") as stream:
                raw = stream.read(MAX_TEXT_BYTES + 1)
            if len(raw) > MAX_TEXT_BYTES or coverage["text_bytes_read"] + len(raw) > MAX_TOTAL_BYTES:
                row.update(availability="unavailable", reason="text_size_limit")
                coverage["truncated"] = True
                return
            coverage["text_bytes_read"] += len(raw)
            row.update(sha256=hashlib.sha256(raw).hexdigest(), inspection="bounded_text_signals")
            text = raw.decode("utf-8", errors="replace")
            texts[relative] = text
            row["nonempty"] = bool(text.strip())
            if kind not in {"manifest", "documentation_config", "service_spec", "license"}:
                for name, pattern in SIGNALS.items():
                    match = re.search(pattern, text, re.I)
                    if match:
                        row["signals"].append({"name": name, "line": text.count("\n", 0, match.start()) + 1})
                row["fenced_example_signal"] = bool(re.search(r"(?m)^\s*(```|~~~)", text))
        except OSError:
            row.update(availability="unavailable", reason="unreadable_file")

    readme = next((root / name for name in README_NAMES if (root / name).exists()), None)
    if readme:
        add(readme, "readme")
    else:
        rows.append({"id": "readme:root", "kind": "readme", "path": None,
                     "availability": "missing", "signals": [], "searched": list(README_NAMES)})
    for name, kind in ROOT_FILES.items():
        if (root / name).exists() or (root / name).is_symlink():
            add(root / name, kind)

    # Only named documentation/example trees, at most two levels below each.
    queue = [(root / name, 0, kind) for name, kind in
             (("docs", "documentation"), ("documentation", "documentation"), ("examples", "example"))
             if (root / name).exists()]
    while queue and coverage["discovered_files"] < MAX_DISCOVERED_FILES:
        folder, depth, kind = queue.pop(0)
        if coverage["directories_visited"] >= MAX_DIRECTORIES:
            coverage["truncated"] = True
            break
        if not _safe_path(root, folder):
            coverage["notes"].append("Skipped unsafe directory: " + folder.relative_to(root).as_posix())
            continue
        try:
            with os.scandir(folder) as stream:
                entries = list(itertools.islice(stream, MAX_DIRECTORY_ENTRIES + 1))
            coverage["directories_visited"] += 1
            if len(entries) > MAX_DIRECTORY_ENTRIES:
                coverage["truncated"] = True
            for entry in sorted(entries[:MAX_DIRECTORY_ENTRIES], key=lambda item: item.name):
                path = Path(entry.path)
                lower = entry.name.lower()
                if lower.startswith(".") or lower in SKIP_NAMES or re.search(r"(?:secret|credential|token|password)", lower):
                    continue
                if not _safe_path(root, path):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if depth < 2:
                        queue.append((path, depth + 1, kind))
                    else:
                        coverage["truncated"] = True
                elif path.suffix.lower() in (EXAMPLE_EXTENSIONS if kind == "example" else TEXT_EXTENSIONS):
                    if coverage["discovered_files"] >= MAX_DISCOVERED_FILES:
                        coverage["truncated"] = True
                        break
                    add(path, kind, read_text=path.suffix.lower() in TEXT_EXTENSIONS)
                    coverage["discovered_files"] += 1
        except OSError:
            coverage["notes"].append("Unreadable directory: " + folder.relative_to(root).as_posix())
    if queue:
        coverage["truncated"] = True
    coverage["limits"] = {"file_bytes": MAX_TEXT_BYTES, "total_text_bytes": MAX_TOTAL_BYTES,
                           "discovered_files": MAX_DISCOVERED_FILES, "directories": MAX_DIRECTORIES,
                           "entries_per_directory": MAX_DIRECTORY_ENTRIES, "directory_depth": 2}
    return rows, texts, coverage


def _profile(rows: list[dict[str, Any]], texts: dict[str, str], audience: str) -> dict[str, Any]:
    available = {row["path"] for row in rows if row["availability"] == "available"}
    types: list[str] = []
    try:
        package = json.loads(texts.get("package.json", "{}"))
    except json.JSONDecodeError:
        package = {}
    if not isinstance(package, dict):
        package = {}
    if "SKILL.md" in available:
        types.append("skill")
    if package.get("bin") or re.search(r"(?m)^\s*\[project\.scripts\]", texts.get("pyproject.toml", "")):
        types.append("cli")
    if any(package.get(name) for name in ("exports", "main", "types")) or available & {"pyproject.toml", "Cargo.toml", "go.mod", "setup.cfg"}:
        types.append("library")
    if any(row["kind"] == "service_spec" and row["availability"] == "available" for row in rows):
        types.append("service")
    if any(row["kind"] == "documentation_config" and row["availability"] == "available" for row in rows) or (
        not types and "package.json" not in available and any(row["kind"] == "documentation" for row in rows)
    ):
        types.append("documentation")
    internal = bool(re.search(r"\b(?:internal|private)\b", audience, re.I)) or package.get("private") is True
    return {"types": types or ["unspecified"], "basis": "bounded local file signals; confirm the project type",
            "visibility": "unknown", "visibility_reason": "GitHub metadata was not collected",
            "distribution_scope": "internal" if internal else "needs_confirmation",
            "distribution_reason": "Audience or package publishing flag suggests internal use; this does not establish GitHub visibility."
            if internal else "Confirm intended distribution and repository visibility before any public sharing."}


def _baseline() -> dict[str, Any]:
    return {
        "availability": "unavailable", "reason": "not_collected_local_only", "observed_at_utc": None,
        "window_start_utc": None, "window_end_utc": None,
        "traffic_14_days": {"views": None, "unique_visitors": None, "clones": None,
                            "unique_cloners": None, "referrers": None, "popular_paths": None},
        "release_assets": None,
        "task_success": {"attempts": None, "completions": None, "blocking_questions": None},
        "manual_collection": [
            {"metric": "views", "argv": ["gh", "api", "repos/OWNER/REPO/traffic/views?per=day"]},
            {"metric": "clones", "argv": ["gh", "api", "repos/OWNER/REPO/traffic/clones?per=day"]},
            {"metric": "referrers", "argv": ["gh", "api", "repos/OWNER/REPO/traffic/popular/referrers"]},
            {"metric": "popular_paths", "argv": ["gh", "api", "repos/OWNER/REPO/traffic/popular/paths"]},
            {"metric": "release_assets", "argv": ["gh", "api", "--paginate", "repos/OWNER/REPO/releases?per_page=100"],
             "fields": ["tag_name", "assets[].id", "assets[].name", "assets[].download_count"]},
        ],
        "protocol": [
            "Replace OWNER/REPO and collect only when live GitHub reads are intended; none of these commands ran.",
            "Save the UTC collection time, raw response, repository, window boundaries and each collection failure.",
            "Traffic covers the preceding 14 days and requires repository push access; inaccessible data stays null.",
            "Snapshot before changing one discovery asset, then compare equal 14-day windows and record release/event confounders.",
            "Do not add overlapping windows or sum daily unique counts into a window unique count.",
            "Record release asset IDs, tags and counts at both times; compare deltas for matching IDs. Replaced/deleted assets break continuity.",
            "Asset downloads are not installations or active users; repositories without downloadable release assets may mark this metric not applicable.",
            "Observe a consenting intended user attempting the example; record success and blockers without collecting personal data.",
            "Traffic and download changes alone do not establish causation. Write continue, revise or stop with the evidence after each window.",
        ],
    }


def run_discovery(repo_root: Path, audience: str = "", category: str = "",
                  competitors: list[str] | None = None) -> dict[str, Any]:
    """Return a deterministic JSON-safe plan; no network, subprocesses or writes."""
    root = Path(repo_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Discovery target must be an existing directory")
    audience, category = _context(audience, "audience"), _context(category, "category")
    if competitors is not None and not isinstance(competitors, (list, tuple)):
        raise ValueError("competitors must be a list of names")
    if len(competitors or []) > MAX_COMPETITORS:
        raise ValueError(f"At most {MAX_COMPETITORS} competitors may be supplied")
    names: list[str] = []
    for value in competitors or []:
        name = _context(value, "competitor")
        if name and name.casefold() not in {item.casefold() for item in names}:
            names.append(name)
    rows, texts, coverage = _inventory(root)
    profile = _profile(rows, texts, audience)
    internal = profile["distribution_scope"] == "internal"
    docs_only = profile["types"] == ["documentation"]

    def evidence(*kinds: str, signal: str = "") -> list[str]:
        return [row["id"] for row in rows if row["kind"] in kinds or (
            signal and any(item["name"] == signal for item in row["signals"]))][:12]

    readme_evidence = evidence("readme")
    example_evidence = evidence("example", signal="example")
    docs_evidence = evidence("documentation")
    costs = evidence(signal="cost")
    project = root.name
    target = audience or "intended users (audience not supplied)"
    context_missing = [key for key, value in (("audience", audience), ("category", category)) if not value]
    experiments: list[dict[str, Any]] = []

    def experiment(identifier: str, title: str, hypothesis: str, sources: list[str],
                   destination: str, outline: list[str], proof: list[str], measure: str,
                   depends_on: list[str] | None = None) -> None:
        experiments.append({"id": identifier, "priority": len(experiments) + 1, "title": title,
                            "status": "planned", "basis": "hypothesis", "hypothesis": hypothesis,
                            "evidence_refs": sources, "depends_on": depends_on or [],
                            "brief": {"audience": target, "destination": destination,
                                      "outline": outline, "proof_required": proof},
                            "completion_check": "Review every proof requirement and record the result before sharing.",
                            "measurement": measure})

    if context_missing:
        experiment("context", "Define the discovery question", "An explicit user task can make the following experiments relevant.",
                   readme_evidence, "Maintainer planning notes",
                   ["Name one intended audience, one problem category and one task they need to complete.",
                    "Confirm whether discovery should be public or internal; identify evidence of existing demand."],
                   ["Record the owner's answers; do not derive market demand from repository terminology."],
                   "One agreed task and audience; revise the remaining briefs if either changes.")
    experiment("baseline", "Capture a baseline before changing discovery assets",
               "A saved baseline and one change per observation window may help distinguish useful work from noise.",
               evidence("release_notes"), "A dated copy of DISCOVERY-METRICS-BASELINE.json",
               ["Record the existing 14-day traffic window, release asset counts and one example attempt.",
                "Choose the experiment's primary outcome and comparison window before starting."],
               ["Use the supplied manual collection recipe; retain null for unavailable values.",
                "Record UTC times, failures, asset IDs and any release or promotion during the window."],
               "A dated baseline with explicit availability, then one equal-window comparison.")
    experiment("example", "Make one useful result reproducible",
               f"A worked task may help {target} decide whether {project} fits their needs.",
               list(dict.fromkeys(readme_evidence + example_evidence)), "Existing example guide, or proposed docs/first-result.md",
               ["State the task, prerequisites and a pinned revision/version.",
                "Show the navigation steps and a worked answer with source references." if docs_only else
                "Show exact supported setup and task commands with safe sample input and expected output.",
                "Document limitations, recovery from one likely failure and any external costs."],
               ["Have an intended reader repeat the task from the documented starting point.",
                "Save the actual result, environment and date; redact secrets and never invent output."],
               "Task completions / attempts and the blocking questions, supported by traffic to the guide.", ["baseline"])
    experiment("documentation", "Answer one consequential user question",
               "A focused explanation of a real blocker may help readers complete the task without additional support.",
               list(dict.fromkeys(docs_evidence + readme_evidence)), "Existing relevant guide, or proposed docs/task-guide.md",
               [f"Address one question about {category or 'the chosen problem category (not supplied)' }.",
                "Link the working example; explain decisions, limitations and troubleshooting.",
                "Link the guide from README navigation using words an intended reader recognizes."],
               ["Confirm the question with an intended user or a supplied issue/support record.",
                "Check the explanation against implementation and the reproducible example; verify local links."],
               "Successful task attempts and fewer repeated blockers; relevant guide referrals as supporting evidence.", ["example"])
    if costs:
        experiment("costs", "Explain the cost of a reproducible workload",
                   "Transparent cost assumptions may help readers evaluate a project that mentions metered or operating costs.",
                   costs, "Existing cost guide, or proposed docs/workload-costs.md",
                   ["Define one workload and distinguish software licensing from hosting, API and maintenance costs.",
                    "Show units consumed, unit prices and a calculation readers can repeat; identify excluded costs.",
                    "State limits, retries, cache effects, free allowances, currency and pricing date."],
                   ["Cite current official prices and the measured workload receipt without secrets.",
                    "Treat documented cost mentions as leads; do not claim a price, savings or free operation until checked."],
                   "Reader reproduces the calculation and identifies whether it fits their workload.", ["example"])
    if names:
        experiment("comparison", "Build an evidence-backed alternatives guide",
                   "A task-equivalent comparison may help readers choose between the explicitly supplied alternatives.",
                   list(dict.fromkeys(readme_evidence + evidence(signal="comparison") + costs)),
                   "Proposed docs/alternatives.md",
                   ["Define the same audience, task and workload for every alternative.",
                    "Fill the evidence matrix with dated official sources and hands-on results; leave unknown cells unverified.",
                    "Describe who each option suits, setup burden, limitations and cost assumptions without declaring a universal winner."],
                   ["Research only the supplied alternatives; names alone establish no features or market position.",
                    "Separate license cost, operating cost and hosted service price; verify licensing before calling a project open source.",
                    "Use task-equivalent features and workload calculations; do not infer savings or feature absence."],
                   "Intended readers can explain which option fits the task and which tradeoff decided it.", ["example"])
    experiment("metadata", "Make purpose and navigation clear",
               "Accurate description and relevant classification may help the intended audience recognize the project.",
               readme_evidence, "README introduction and internal catalog" if internal else "README introduction and GitHub About draft",
               ["Draft: For [audience], [project] helps with [verified task]; start at [working example].",
                "Use only terms supported by the implementation and docs; confirm every topic candidate.",
                "Link a working guide/homepage and remove ambiguous claims."],
               ["Verify actual GitHub metadata and intended visibility separately; no current metadata was collected.",
                "For internal use, avoid sensitive public topic names and use the appropriate internal catalog." if internal else
                "Validate the description and topic candidates with an intended user before applying them."],
               "An intended reader can identify the task and find the example; compare relevant traffic after the change.", ["example"])
    experiment("distribution", "Share one useful artifact with a relevant audience",
               "A task-specific contribution in a place where interested readers opted in may invite useful feedback.",
               list(dict.fromkeys(evidence("contribution_guide", "release_notes") + example_evidence)),
               "Internal team knowledge channel draft" if internal else "An owner-controlled release note or community submission draft",
               ["Choose one audience-matched channel that explicitly welcomes the material.",
                "Lead with the solved task, evidence, limitations and relevant link; disclose the maintainer relationship.",
                "Adapt to community rules and respond to questions; avoid unsolicited messages and repeated promotional drops."],
               ["Keep internal material within authorized internal channels." if internal else
                "Confirm public distribution is intended and check the destination's contribution rules.",
                "Publish or send only when the owner asks; the planner creates no external posts."],
               "Qualified questions, example completions and attributable referrals; review after one observation window.",
               ["example", "documentation", "metadata"])

    dimensions = [
        ("task_fit", "Does the same reproducible task work, and with what limitations?", example_evidence + readme_evidence),
        ("operation", "What setup, hosting, maintenance and support responsibilities remain?", docs_evidence),
        ("cost", "What does the same workload cost, with dated units and exclusions?", costs),
        ("license_and_data", "What licensing, data access and usage terms apply?", evidence("license")),
        ("release_and_limits", "Which version was tested, and what cannot it do?", evidence("release_notes", signal="limits")),
    ]
    matrix = {"status": "unverified" if names else "not_requested", "competitors_source": "user_supplied_only",
              "subjects": [{"id": "project", "name": project}] +
                          [{"id": f"competitor-{i + 1}", "name": name} for i, name in enumerate(names)],
              "rows": [{"dimension": key, "question": question, "cells": [
                  {"subject": subject, "status": "unverified", "claim": None, "checked_at": None,
                   "official_sources": [], "local_leads": list(dict.fromkeys(leads)) if subject == "project" else []}
                  for subject in ["project"] + [f"competitor-{i + 1}" for i in range(len(names))]]}
                  for key, question, leads in dimensions] if names else []}
    category_topic = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-")
    topics = ([{"topic": category_topic, "basis": "user category; relevance still needs confirmation"}]
              if category_topic and len(category_topic) <= 50 and not internal else [])
    return {"operation": "discover", "schema_version": SCHEMA_VERSION, "mode": "local_plan", "repo_root": str(root),
            "project": project, "context": {"audience": audience or None, "category": category or None,
                                           "competitors": names, "missing": context_missing},
            "repository_profile": profile, "evidence_inventory": rows, "coverage": coverage,
            "experiments": experiments, "comparison_matrix": matrix,
            "metadata": {"current": "unavailable: no GitHub read", "topic_candidates": topics,
                         "description_template": "For [audience], [project] helps with [verified task]. Start at [working example]."},
            "metrics_baseline": _baseline(), "references": REFERENCES,
            "limitations": ["Local file signals are leads, not proof of working features, licensing, prices or demand.",
                            "No network calls, external posts, target-code execution, credential reads or tracked-file edits occur during planning.",
                            "Selected root files and shallow docs/examples only; monorepo packages need separate runs.",
                            "No keyword volumes, rankings, competitor facts or outcome guarantees are inferred.",
                            "No imagery, paid service or model provider is required."]}


def _md(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def discovery_report(payload: dict[str, Any]) -> str:
    """Render the same plan as reviewable Markdown without raw source text."""
    context = payload["context"]
    lines = [f"# Discovery plan: {_md(payload['project'])}", "",
             "Local evidence and testable hypotheses. Nothing has been published or measured remotely.", "",
             f"- Audience: {_md(context['audience'] or 'not supplied')}",
             f"- Category: {_md(context['category'] or 'not supplied')}",
             f"- Supplied alternatives: {_md(', '.join(context['competitors']) or 'none')}",
             f"- Distribution: {_md(payload['repository_profile']['distribution_scope'])}; GitHub visibility is unknown.",
             f"- Bounded inventory truncated: {payload['coverage']['truncated']}", "", "## Evidence inventory", "",
             "Text signals identify review locations; file presence does not validate a claim.", "",
             "| File | Kind | Availability | Signal locations |", "| --- | --- | --- | --- |"]
    for row in payload["evidence_inventory"]:
        signals = ", ".join(f"{item['name']}:L{item['line']}" for item in row["signals"])
        lines.append(f"| {_md(row['path'] or 'Root README candidates')} | {_md(row['kind'])} | {_md(row['availability'])} | {_md(signals or row.get('reason', 'none'))} |")
    lines.extend(["", "## Prioritized experiments", ""])
    for exp in payload["experiments"]:
        lines.extend([f"### {exp['priority']}. {_md(exp['title'])}", "", f"Hypothesis: {_md(exp['hypothesis'])}", "",
                      f"Destination: {_md(exp['brief']['destination'])}.", "",
                      f"Evidence leads: {_md(', '.join(exp['evidence_refs']) or 'no matching evidence in this bounded inventory')}.", "",
                      f"Depends on: {_md(', '.join(exp['depends_on']) or 'none')}.", "", "Brief:", ""])
        lines.extend("- " + _md(item) for item in exp["brief"]["outline"])
        lines.extend(["", "Proof required:", ""])
        lines.extend("- " + _md(item) for item in exp["brief"]["proof_required"])
        lines.extend(["", "Measure: " + _md(exp["measurement"]), ""])
    lines.extend(["## Alternatives evidence matrix", "", "All cells start unverified. Local files are leads; alternatives come only from supplied names.", ""])
    matrix = payload["comparison_matrix"]
    if matrix["rows"]:
        lines.append("| Decision question | " + " | ".join(_md(s["name"]) for s in matrix["subjects"]) + " |")
        lines.append("| --- | " + " | ".join("---" for _ in matrix["subjects"]) + " |")
        for row in matrix["rows"]:
            lines.append("| " + _md(row["question"]) + " | " + " | ".join("Unverified" for _ in row["cells"]) + " |")
        lines.extend(["", "Fill claim, official_sources and checked_at in each JSON matrix cell after verification.", ""])
    else:
        lines.extend(["No alternatives supplied; no competitor comparison was generated.", ""])
    lines.extend(["## Metadata draft", "", "Current metadata is uncollected.", "",
                  payload["metadata"]["description_template"], "",
                  "Topic candidates requiring review: " + _md(", ".join(item["topic"] for item in payload["metadata"]["topic_candidates"]) or "none"), "",
                  "## Measurement baseline", "", "All values are null until collected. See DISCOVERY-METRICS-BASELINE.json.", ""])
    lines.extend("- " + _md(item) for item in payload["metrics_baseline"]["protocol"])
    lines.extend(["", "## Limits", ""])
    lines.extend("- " + _md(item) for item in payload["limitations"] + payload["coverage"]["notes"])
    lines.extend(["", "## References", ""])
    lines.extend(f"- [{item['title']}]({item['url']})" for item in payload["references"])
    return "\n".join(lines) + "\n"


def write_discovery_artifacts(repo_root: Path, payload: dict[str, Any]) -> dict[str, str]:
    """Write only configured cache/output artifacts; never edit target documents."""
    repo_root = Path(repo_root).expanduser().resolve()
    if payload.get("repo_root") != str(repo_root):
        raise ValueError("Discovery payload does not belong to the selected repository")
    output_root = repo_output_dir(repo_root)
    output_root.mkdir(parents=True, exist_ok=True)
    # A fresh directory prevents two runs from overwriting reviewed reports.
    out_dir = Path(tempfile.mkdtemp(prefix="discovery-", dir=output_root))
    cache_path = write_repo_cache(repo_root, "discovery-data.json", payload)
    report_path = out_dir / "DISCOVERY-REPORT.md"
    plan_path = out_dir / "DISCOVERY-PLAN.json"
    metrics_path = out_dir / "DISCOVERY-METRICS-BASELINE.json"
    report_path.write_text(discovery_report(payload), encoding="utf-8")
    plan_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    metrics_path.write_text(json.dumps(payload["metrics_baseline"], indent=2) + "\n", encoding="utf-8")
    return {"output_dir": str(out_dir), "discovery_cache": str(cache_path), "report": str(report_path),
            "plan_json": str(plan_path), "metrics_baseline_json": str(metrics_path)}
