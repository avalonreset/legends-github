"""Versioned, bounded repository observations; never execute repository code.

The legacy scorecard remains a separate compatibility surface. These checks
describe collected evidence, not software correctness, legal compliance, search
ranking, or the business value of a change. No cache is used as current evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from github_runtime import have_command, run_command

SCHEMA_VERSION = "1.0.0"
SCORING_VERSION = "legacy-checklist-v1"
MAX_TEXT_BYTES = 1_000_000
GITHUB_FIELDS = (
    "name,description,homepageUrl,repositoryTopics,visibility,defaultBranchRef,"
    "licenseInfo,stargazerCount,forkCount,watchers,primaryLanguage,createdAt,"
    "updatedAt,isArchived,isFork,hasIssuesEnabled,hasWikiEnabled"
)
PROFILE_LABELS = {
    "library": "Library/Package", "cli": "CLI Tool", "service": "API/Service",
    "documentation": "Documentation", "skill": "Skill/Plugin", "application": "Application",
}


def observation(source: str, collected_at: str, value: Any = None, reason: str = "") -> dict[str, Any]:
    """Keep an empty successful result distinct from unavailable evidence."""
    return {"source": source, "collected_at": collected_at,
            "availability": "unavailable" if reason else "available", "reason": reason, "value": value}


def command_observation(args: list[str], collected_at: str, cwd: Path | None = None,
                        json_result: bool = False) -> dict[str, Any]:
    """Collect bounded CLI output without copying potentially sensitive errors."""
    source = " ".join(args)
    if not have_command(args[0]):
        return observation(source, collected_at, reason="command_unavailable")
    try:
        result = run_command(args, cwd=cwd, check=False)
    except subprocess.TimeoutExpired:
        return observation(source, collected_at, reason="timeout")
    except OSError:
        return observation(source, collected_at, reason="command_unavailable")
    if result.returncode:
        return observation(source, collected_at, reason="command_failed")
    if json_result:
        try:
            value = json.loads(result.stdout)
        except (json.JSONDecodeError, TypeError):
            return observation(source, collected_at, reason="invalid_response")
    else:
        value = result.stdout.strip()
    return observation(source, collected_at, value)


def collect_remote(repo_slug: str | None, collected_at: str) -> dict[str, dict[str, Any]]:
    """Collect GitHub metadata and releases independently, with failure reasons."""
    reason = ""
    if not repo_slug:
        reason = "no_github_remote"
    elif os.environ.get("LEGENDS_GITHUB_OFFLINE", "").lower() in {"1", "true", "yes"}:
        reason = "offline"
    elif not have_command("gh"):
        reason = "command_unavailable"
    else:
        auth = command_observation(["gh", "auth", "status"], collected_at)
        if auth["availability"] == "unavailable":
            reason = "authentication_unavailable" if auth["reason"] == "command_failed" else auth["reason"]
    if reason:
        return {key: observation(source, collected_at, reason=reason) for key, source in
                (("metadata", "github:repository"), ("releases", "github:releases"))}
    metadata = command_observation(["gh", "repo", "view", repo_slug, "--json", GITHUB_FIELDS],
                                   collected_at, json_result=True)
    releases = command_observation(["gh", "release", "list", "--repo", repo_slug, "--limit", "5",
                                   "--json", "tagName,name,isDraft,isPrerelease,publishedAt"],
                                  collected_at, json_result=True)
    if metadata["availability"] == "available" and not isinstance(metadata["value"], dict):
        metadata = observation(metadata["source"], collected_at, reason="invalid_response")
    elif metadata["availability"] == "available":
        shapes = {"repositoryTopics": list, "watchers": dict, "defaultBranchRef": dict,
                  "licenseInfo": dict, "primaryLanguage": dict, "description": str,
                  "name": str, "homepageUrl": str, "visibility": str}
        if any(metadata["value"].get(key) is not None and not isinstance(metadata["value"][key], shape)
               for key, shape in shapes.items()):
            metadata = observation(metadata["source"], collected_at, reason="invalid_response")
    if releases["availability"] == "available" and (not isinstance(releases["value"], list) or
            any(not isinstance(row, dict) for row in releases["value"])):
        releases = observation(releases["source"], collected_at, reason="invalid_response")
    return {"metadata": metadata, "releases": releases}


def collect_git(repo_root: Path, collected_at: str) -> dict[str, dict[str, Any]]:
    """Local Git observations have their own availability, independent of GitHub."""
    tags = command_observation(["git", "tag", "--list"], collected_at, repo_root)
    if tags["availability"] == "available":
        tags["value"] = tags["value"].splitlines()
    commit = command_observation(["git", "log", "-1", "--format=%cI"], collected_at, repo_root)
    return {"tags": tags, "recent_commit": commit}


class LocalEvidence:
    """Read only bounded, explicitly selected files inside the repository."""

    def __init__(self, repo_root: Path, collected_at: str):
        self.root = repo_root.resolve()
        self.collected_at = collected_at

    def text(self, relative: str) -> dict[str, Any]:
        path = self.root / relative
        source = "file:" + relative.replace("\\", "/")
        try:
            if not path.resolve().is_relative_to(self.root):
                return observation(source, self.collected_at, reason="outside_repository")
            if not path.exists():
                return observation(source, self.collected_at, "") | {"exists": False}
            if not path.is_file():
                return observation(source, self.collected_at, reason="not_a_file")
            if path.stat().st_size > MAX_TEXT_BYTES:
                return observation(source, self.collected_at, reason="file_too_large")
            raw = path.read_bytes()
        except OSError:
            return observation(source, self.collected_at, reason="unreadable_file")
        return observation(source, self.collected_at, raw.decode("utf-8", errors="replace")) | {
            "exists": True, "sha256": hashlib.sha256(raw).hexdigest()}

    def paths(self, candidates: list[str]) -> dict[str, Any]:
        found = []
        try:
            for relative in candidates:
                path = self.root / relative
                if not path.resolve().is_relative_to(self.root):
                    return observation("filesystem", self.collected_at, reason="outside_repository")
                if path.is_file():
                    found.append(relative)
        except OSError:
            return observation("filesystem", self.collected_at, reason="unreadable_path")
        return observation("filesystem", self.collected_at, found) | {"searched": candidates}


def infer_profile(local: LocalEvidence, metadata: dict[str, Any]) -> dict[str, Any]:
    """Infer types from meaningful signals; AGENTS.md alone is not a skill."""
    signals: dict[str, list[str]] = {}
    package_obs = local.text("package.json")
    package: dict[str, Any] = {}
    try:
        parsed = json.loads(package_obs["value"] or "{}")
        if isinstance(parsed, dict):
            package = parsed
    except (TypeError, json.JSONDecodeError):
        pass
    pyproject = local.text("pyproject.toml")["value"] or ""
    def add(kind: str, paths: list[str]) -> None:
        if paths:
            signals.setdefault(kind, []).extend(paths)
    add("skill", local.paths(["SKILL.md", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"])["value"] or [])
    add("skill", [p.relative_to(local.root).as_posix() for p in sorted(local.root.glob("skills/*/SKILL.md"))[:100]])
    add("documentation", local.paths(["mkdocs.yml", "mkdocs.yaml", "docusaurus.config.js",
                                      "docusaurus.config.ts", ".readthedocs.yaml"])["value"] or [])
    add("service", local.paths(["openapi.yaml", "openapi.yml", "swagger.json"])["value"] or [])
    if package.get("bin"):
        add("cli", ["package.json#bin"])
    if re.search(r"(?m)^\s*\[(?:project\.scripts|tool\.poetry\.scripts)\]", pyproject):
        add("cli", ["pyproject.toml#scripts"])
    add("cli", local.paths(["cli.py", "__main__.py"])["value"] or [])
    if package and (package.get("exports") or package.get("main") or package.get("types")):
        add("library", ["package.json#exports/main/types"])
    if pyproject and re.search(r"(?m)^\s*\[(?:project|tool\.poetry)\]", pyproject):
        add("library", ["pyproject.toml"])
    add("library", local.paths(["setup.py", "setup.cfg", "Cargo.toml", "go.mod"])["value"] or [])
    if not signals:
        add("application", ["package.json"] if package else ["fallback: no decisive type signal"])
    priority = ("skill", "documentation", "service", "cli", "library", "application")
    primary = next(kind for kind in priority if kind in signals)
    raw = metadata["value"] or {} if metadata["availability"] == "available" else {}
    visibility = str(raw.get("visibility") or "unknown").lower()
    if visibility not in {"private", "internal", "public"}:
        visibility = "unknown"
    audience = "internal" if visibility in {"private", "internal"} else visibility
    monorepo = bool(package.get("workspaces") or (local.root / "pnpm-workspace.yaml").is_file() or
                    re.search(r"(?m)^\s*\[workspace\]", local.text("Cargo.toml")["value"] or ""))
    return {"primary": primary, "types": [kind for kind in priority if kind in signals],
            "audience": audience, "visibility": visibility, "monorepo": monorepo,
            "scope": "repository root; package-level audits are separate" if monorepo else "repository root",
            "confidence": 0.4 if signals.get("application") == ["fallback: no decisive type signal"] else 0.85,
            "signals": signals, "visibility_source": metadata["source"],
            "limitations": ["Profile is inferred from bounded file signals and can require human correction."]}


def _proof(obs: dict[str, Any], detail: str) -> dict[str, Any]:
    """Never include entire file contents or command errors in public evidence."""
    return {key: obs[key] for key in ("source", "collected_at", "availability", "reason", "sha256", "searched")
            if key in obs} | {"detail": detail}


def _finding(check_id: str, category: str, title: str, obs: dict[str, Any], present: bool,
             recommendation: str, detail: str, *, applicable: bool = True, why: str = "Applies to this repository.",
             impact: str = "medium", effort: str = "small", confidence: float = 0.95,
             basis: str = "observed_evidence",
             verification: str = "Inspect the referenced evidence after the change.") -> dict[str, Any]:
    status = ("not_applicable" if not applicable else "unavailable" if obs["availability"] != "available"
              else "observed" if present else "missing")
    priority = impact if status == "missing" else "none"
    return {"id": check_id, "category": category, "title": title, "status": status,
            "availability": obs["availability"], "source": obs["source"], "collected_at": obs["collected_at"],
            "applicability": {"applicable": applicable, "reason": why}, "confidence": confidence,
            "impact": impact, "effort": effort, "priority": priority, "evidence": [_proof(obs, detail)],
            "recommendation": recommendation if status == "missing" else "",
            "recommendation_basis": basis if status == "missing" else "none",
            "verification": {"status": "not_run", "method": verification},
            "limitations": "Static observation only; runtime behavior and user outcomes were not verified."}


def _section_present(text: str, pattern: str) -> bool:
    """Require some section content, rather than rewarding an empty heading."""
    text = re.sub(r"```.*?```|~~~.*?~~~", "\n[code example]\n", text, flags=re.S)
    sections = re.split(r"(?m)^#{1,6}\s+", text)
    return any(re.search(pattern, section.split("\n", 1)[0], re.I) and
               len(section.split("\n", 1)) > 1 and bool(section.split("\n", 1)[1].strip()) for section in sections[1:])


SETUP_COMMAND = re.compile(
    r"(?im)^\s*(?:\$\s+)?(?:python(?:3)?\s+-m\s+pip\s+install|pip(?:3)?\s+install|"
    r"(?:npm|pnpm)\s+(?:install|ci)|yarn(?:\s+install)?\s*$|uv\s+(?:sync|pip\s+install)|"
    r"poetry\s+install|cargo\s+(?:install|build)|go\s+(?:install|build)|docker\s+compose\s+up)\b"
)


def _code_examples(text: str) -> list[str]:
    return [match.group(2) for match in re.finditer(r"(?m)^\s*(```|~~~)[^\n]*\n(.*?)^\s*\1\s*$", text, flags=re.S)]


def _usage_example_present(text: str) -> bool:
    """Recognize non-setup code examples without requiring a particular heading."""
    for block in _code_examples(text):
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//", "$env:", "export ", "git clone ", "cd ")):
                continue
            if SETUP_COMMAND.match(stripped):
                continue
            # Avoid treating arbitrary prose, credentials, and generic fence text as executable examples.
            if re.match(r"(?:\$\s+)?(?:python(?:3)?\s+(?!-m\s+pip)|(?:npm|pnpm)\s+(?:run\s+)?[\w:-]+|"
                        r"node\s+|curl\s+|docker\s+run\s+|import\s+|from\s+\w+\s+import\s+|"
                        r"const\s+|let\s+|print\(|[\w.]+\([^)]*\))", stripped):
                return True
    return False


def _relative_link_findings(local: LocalEvidence, readme: dict[str, Any], readme_name: str) -> list[dict[str, Any]]:
    """Check explicit local Markdown links only; external links and anchors are skipped."""
    if readme["availability"] != "available" or not readme["value"]:
        return []
    text = re.sub(r"```.*?```|~~~.*?~~~", "", readme["value"], flags=re.S)
    broken, checked = [], 0
    skipped = 0
    for match in re.finditer(r"(?<!!)\[[^\]\n]+\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)", text):
        target = match.group(1)
        try:
            parts = urlsplit(target)
        except ValueError:
            skipped += 1
            continue
        if parts.scheme or parts.netloc or not parts.path or parts.path.startswith("/"):
            continue
        relative = unquote(parts.path)
        candidate = local.root / Path(readme_name).parent / relative
        try:
            if not candidate.resolve().is_relative_to(local.root):
                skipped += 1
                continue
            checked += 1
            if not candidate.exists():
                broken.append(relative)
        except OSError:
            skipped += 1
    if not checked:
        return []
    detail = f"Checked {checked} local link targets; {len(broken)} missing; {skipped} unsafe or unreadable targets skipped."
    if broken:
        detail += " Missing targets: " + ", ".join(sorted(set(broken))[:20])
    return [_finding("readme.local_links", "readme", "README local link targets resolve", readme, not broken,
                     "Repair the missing local README link targets or update the links.", detail,
                     impact="medium", verification="Re-run the local-link check; manually follow critical onboarding links.")]


def _entrypoint_finding(local: LocalEvidence) -> dict[str, Any]:
    obs = local.text("package.json")
    try:
        package = json.loads(obs["value"] or "{}")
    except (TypeError, json.JSONDecodeError):
        package = None
    if package is not None and not isinstance(package, dict):
        package = None
    if obs["availability"] == "available" and package is None:
        return _finding("package.manifest", "release", "Node package manifest parses", obs, False,
                        "Correct package.json so package tools can parse it.", "package.json is not a JSON object.",
                        impact="high", verification="Parse package.json and run the documented package installation in an isolated environment.")
    targets = []
    if package:
        entry = package.get("bin", {})
        targets = [entry] if isinstance(entry, str) else list(entry.values()) if isinstance(entry, dict) else []
    missing, skipped = [], []
    for target in targets:
        if not isinstance(target, str):
            skipped.append("non-string bin value")
            continue
        path = local.root / target
        try:
            if not path.resolve().is_relative_to(local.root):
                skipped.append("target outside repository")
            elif not path.is_file():
                missing.append(target)
        except OSError:
            skipped.append("unreadable target")
    generated = bool(package and isinstance(package.get("scripts"), dict) and any(
        key in package["scripts"] for key in ("build", "prepare", "prepack", "prepublishOnly")))
    # A build step can legitimately create the file. Inspect the package artifact before alleging a defect.
    if skipped or (missing and generated):
        obs = observation(obs["source"], obs["collected_at"], reason="build_artifact_not_verified" if generated else "target_not_verifiable")
    return _finding("package.entrypoints", "release", "Declared Node CLI targets exist", obs, not missing,
                    "Restore the declared CLI target or correct package.json bin before publishing.",
                    "Declared bin targets: " + str(len(targets)) + "; missing: " + ", ".join(missing),
                    applicable=bool(targets) or obs["availability"] == "unavailable",
                    why="Applies when package.json declares CLI targets; generated targets require a build artifact check.",
                    impact="high", verification="Build and inspect the package archive, then run the installed command in a disposable environment.")


def build_findings(repo_root: Path, collected_at: str, remote: dict[str, dict[str, Any]],
                   git: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return the evidence contract without reading caches or executing target code."""
    local = LocalEvidence(repo_root, collected_at)
    profile = infer_profile(local, remote["metadata"])
    docs_only = profile["primary"] == "documentation" and not set(profile["types"]) & {"library", "cli", "service", "skill"}
    internal = profile["audience"] == "internal"
    readme_name = next((name for name in ("README.md", "README.rst", "readme.md", "README", "README.txt")
                        if (repo_root / name).exists()), "README.md")
    readme = local.text(readme_name)
    text = readme["value"] or ""
    findings = [_finding("readme.present", "readme", "Repository introduction exists", readme, bool(text.strip()),
                         "Write a repository introduction with its purpose and the first usable step.",
                         "Nonempty README found." if text.strip() else "No nonempty root README found.", impact="high")]
    findings.append(_finding("readme.installation", "readme", "Setup guidance signal is present", readme,
                             _section_present(text, r"install|setup|getting started|quick\s*start") or bool(SETUP_COMMAND.search(text)),
                             "Review setup guidance; if absent, document the supported setup path and prerequisites or link to that guide.",
                             "Checked setup section content and common package-install commands; linked guides and prose may require manual review.",
                             applicable=not docs_only, why="Documentation-only repositories do not necessarily install software.",
                             confidence=0.7, basis="hypothesis", verification="Follow the documented setup from a clean environment; section presence does not prove installation works."))
    findings.append(_finding("readme.usage", "readme", "Usage or navigation signal is present", readme,
                             _section_present(text, r"usage|quick\s*start|getting started|example|navigation|contents|how to") or _usage_example_present(text),
                             "Review first-use guidance; if absent, add a concrete example or a clear route into the documentation.",
                             "Checked usage/navigation section content and fenced command or code examples; alternative formats may need manual review.",
                             confidence=0.7, basis="hypothesis", verification="Have a new user complete the documented example; no examples were executed by this audit."))
    findings.extend(_relative_link_findings(local, readme, readme_name))
    findings.append(_entrypoint_finding(local))
    local_checks = [
        ("license.present", "legal", "License file is discoverable", ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"],
         not internal, "Internal repositories may intentionally reserve rights; a public distribution needs an explicit licensing decision.",
         "Review the intended distribution terms and provide the corresponding license file.", "medium"),
        ("security.contact", "legal", "Security reporting guidance is discoverable", ["SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"],
         not docs_only, "Software repositories benefit from a private vulnerability reporting route.",
         "Document a security reporting contact or link to the organization's applicable policy.", "medium"),
        ("contributing.guidance", "community", "Contribution guidance is discoverable", ["CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"],
         not internal, "Public collaboration guidance is optional for internal repositories.",
         "Document the contribution workflow if outside contributions are supported.", "low"),
        ("release.changelog", "release", "Change history is discoverable", ["CHANGELOG.md", "CHANGES.md", "HISTORY.md"],
         not docs_only, "Documentation-only repositories may use Git history directly.",
         "Provide a change summary for consumers, or link to the project's release history.", "low"),
    ]
    for check_id, category, title, paths, applicable, why, action, impact in local_checks:
        obs = local.paths(paths)
        findings.append(_finding(check_id, category, title, obs, bool(obs["value"]), action,
                                 "Found: " + ", ".join(obs["value"] or []) if obs["value"] else "No file found at the listed candidate paths; other locations or organization policies may apply.",
                                 applicable=applicable, why=why, impact=impact, confidence=0.85))
    workflow_paths = sorted(p.relative_to(repo_root).as_posix() for pattern in ("*.yml", "*.yaml")
                            for p in (repo_root / ".github/workflows").glob(pattern))
    workflows = local.paths(workflow_paths)
    workflows["searched"] = [".github/workflows/*.yml", ".github/workflows/*.yaml"]
    findings.append(_finding("automation.workflows", "release", "GitHub workflow files are present", workflows, bool(workflows["value"]),
                             "Review how changes are validated; add appropriate automation if no external CI already covers this repository.",
                             "Workflow presence only; workflow syntax, test coverage, external CI, and latest run results were not checked.",
                             impact="low", confidence=0.8, verification="Inspect the workflows and a recent successful run with checks appropriate to the repository."))
    metadata = remote["metadata"]
    raw = metadata["value"] or {} if metadata["availability"] == "available" else {}
    for key, check_id, title, action, impact in [
        ("description", "metadata.description", "GitHub description is set", "Set a concise repository description for intended users.", "medium"),
        ("repositoryTopics", "metadata.topics", "GitHub topics are set", "Add relevant topics if public discovery is an objective; no topic-count quota applies.", "low"),
    ]:
        obs = metadata if metadata["availability"] == "unavailable" or key in raw else observation(
            metadata["source"], collected_at, reason="field_unavailable")
        findings.append(_finding(check_id, "meta", title, obs, bool(raw.get(key)), action,
                                 f"GitHub field {key}: " + ("present" if raw.get(key) else "empty or not collected"),
                                 applicable=not internal, why="Public discovery metadata is outside the internal-repository profile.", impact=impact))
    # Positive evidence from either source suffices; absence requires both sources to be available.
    tags, releases = git["tags"], remote["releases"]
    present = bool(tags["value"]) or bool(releases["value"])
    version_obs = tags if tags["value"] else releases if releases["value"] else tags
    if not present and any(o["availability"] != "available" for o in (tags, releases)):
        version_obs = observation("git:tags + github:releases", collected_at, reason="incomplete_version_history")
    versioned = bool(set(profile["types"]) & {"cli", "library", "skill"}) and not internal
    version = _finding("release.version_history", "release", "Version history is observable", version_obs, present,
                       "Choose a versioning policy and publish an intentional version when ready for consumers.",
                       "Local tags or GitHub releases were checked; local tags can be incomplete and releases are limited to five rows.",
                       applicable=versioned, why="Distributed libraries, CLIs, and skills commonly need consumer-facing versions.",
                       impact="medium", verification="Inspect the published artifact and its tag; a tag alone does not prove a working release.")
    version["evidence"] = [_proof(tags, "Local Git tags."), _proof(releases, "Recent GitHub releases.")]
    findings.append(version)
    counts = {status: sum(f["status"] == status for f in findings)
              for status in ("observed", "missing", "unavailable", "not_applicable")}
    evaluated = counts["observed"] + counts["missing"]
    actions = [{key: f[key] for key in ("id", "category", "priority", "impact", "effort", "confidence",
                                       "recommendation", "recommendation_basis", "evidence", "verification")}
               for f in findings if f["status"] == "missing"]
    rank = {"high": 0, "medium": 1, "low": 2}
    actions.sort(key=lambda item: (rank[item["priority"]], -item["confidence"], item["id"]))
    return {"evidence_schema_version": SCHEMA_VERSION, "scoring_version": SCORING_VERSION,
            "repository_profile": profile, "findings": findings, "prioritized_actions": actions,
            "evidence_coverage": {"counts": counts, "evaluated": evaluated, "applicable": evaluated + counts["unavailable"],
                                  "observed_fraction": round(counts["observed"] / evaluated, 4) if evaluated else None,
                                  "meaning": "Evidence coverage, not a quality score; unavailable and inapplicable checks are excluded from the evaluated denominator."},
            "collection": {"collected_at": collected_at, "cache_policy": "fresh observations; existing caches are not evidence",
                           "github": {key: _proof(obs, "Live collection result.") for key, obs in remote.items()},
                           "git": {key: _proof(obs, "Local collection result.") for key, obs in git.items()}},
            "limitations": ["No repository code, installation commands, examples, builds, or workflows were executed.",
                            "Root file signals are bounded; monorepo packages and organization-level policies may require separate review.",
                            "Legacy checklist scores may include unavailable or inapplicable checks; use findings for recommendations."]}
