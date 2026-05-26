#!/usr/bin/env python3
"""Deterministic headless entrypoint for Legends GitHub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_repo import run_audit, write_audit_artifacts
from cache_state import append_run_cache, read_repo_cache
from community_repo import run_community, write_community_artifacts
from empire_repo import run_empire, write_empire_artifacts
from github_runtime import resolve_repo_root
from legal_repo import run_legal, write_legal_artifacts
from meta_repo import run_meta, write_meta_artifacts
from readme_repo import run_readme, write_readme_artifacts
from release_repo import run_release, write_release_artifacts
from runtime_paths import runtime_paths_payload
from seo_repo import run_seo, write_seo_artifacts
from validate_setup import validate_setup


def run_verify(args: argparse.Namespace) -> dict:
    """Run setup validation."""
    repo_root = resolve_repo_root(args.path)
    payload = validate_setup(repo_root, mode=args.mode, allow_missing_gh_auth=args.allow_missing_gh_auth)
    payload["operation"] = "verify"
    return payload


def run_audit_command(args: argparse.Namespace) -> dict:
    """Run the deterministic audit and write artifacts."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_audit(repo_root)
    artifacts = write_audit_artifacts(repo_root, bundle)
    payload = {
        "operation": "audit",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.repo_context["repo"],
        "overall_score": bundle.audit_data["overall_score"],
        "scores": bundle.audit_data["scores"],
        "action_items": bundle.audit_data["action_items"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-audit",
        summary=f"Audited {bundle.repo_context['repo']}",
        metadata={"repo_root": str(repo_root), "overall_score": bundle.audit_data["overall_score"]},
    )
    return payload


def run_cache_status(args: argparse.Namespace) -> dict:
    """Return the current cache status for a repo."""
    repo_root = resolve_repo_root(args.path)
    payload = {
        "operation": "cache-status",
        "repo_root": str(repo_root),
        "repo_context": read_repo_cache(repo_root, "repo-context.json"),
        "audit_data": read_repo_cache(repo_root, "audit-data.json"),
        "seo_data": read_repo_cache(repo_root, "seo-data.json"),
        "legal_data": read_repo_cache(repo_root, "legal-data.json"),
        "community_data": read_repo_cache(repo_root, "community-data.json"),
        "meta_data": read_repo_cache(repo_root, "meta-data.json"),
        "readme_data": read_repo_cache(repo_root, "readme-data.json"),
        "releases_data": read_repo_cache(repo_root, "releases-data.json"),
        "empire_data": read_repo_cache(repo_root, "empire-data.json"),
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    payload["ready"] = any(
        payload[key] is not None
        for key in ("repo_context", "audit_data", "seo_data", "legal_data", "community_data", "meta_data", "readme_data", "releases_data", "empire_data")
    )
    return payload


def run_seo_command(args: argparse.Namespace) -> dict:
    """Run deterministic SEO analysis and write cache artifacts."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_seo(repo_root, mode=args.mode)
    artifacts = write_seo_artifacts(repo_root, bundle)
    payload = {
        "operation": "seo",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.seo_data["repo"],
        "mode": bundle.seo_data["mode"],
        "analysis_mode": bundle.seo_data["analysis_mode"],
        "primary_keyword": bundle.seo_data["primary_keyword"],
        "recommended_topics": bundle.seo_data["recommended_topics"],
        "recommended_description": bundle.seo_data["recommended_description"],
        "warnings": bundle.seo_data["warnings"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-seo",
        summary=f"Generated SEO cache for {bundle.seo_data['repo']}",
        metadata={
            "repo_root": str(repo_root),
            "analysis_mode": bundle.seo_data["analysis_mode"],
            "primary_keyword": bundle.seo_data["primary_keyword"]["keyword"],
        },
    )
    return payload


def run_meta_command(args: argparse.Namespace) -> dict:
    """Run deterministic metadata planning and optionally apply safe commands."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_meta(repo_root, apply=args.apply)
    artifacts = write_meta_artifacts(repo_root, bundle)
    payload = {
        "operation": "meta",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.meta_data["repo"],
        "mode": bundle.meta_data["mode"],
        "applied": bundle.meta_data["applied"],
        "description_set": bundle.meta_data["description_set"],
        "topics_set": bundle.meta_data["topics_set"],
        "commands": bundle.meta_data["commands"],
        "warnings": bundle.meta_data["warnings"],
        "blocked": bundle.meta_data["blocked"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-meta",
        summary=f"Generated metadata plan for {bundle.meta_data['repo']}",
        metadata={
            "repo_root": str(repo_root),
            "mode": bundle.meta_data["mode"],
            "applied": bundle.meta_data["applied"],
        },
    )
    return payload


def run_community_command(args: argparse.Namespace) -> dict:
    """Run deterministic community planning and optionally write files."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_community(repo_root, write_files=args.write_files)
    artifacts = write_community_artifacts(repo_root, bundle)
    payload = {
        "operation": "community",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.community_data["repo"],
        "mode": bundle.community_data["mode"],
        "scorecard_before": bundle.community_data["scorecard_before"],
        "scorecard_after": bundle.community_data["scorecard_after"],
        "files_created": bundle.community_data["files_created"],
        "files_removed": bundle.community_data["files_removed"],
        "files_updated": bundle.community_data["files_updated"],
        "planned_writes": bundle.community_data["planned_writes"],
        "placeholders": bundle.community_data["placeholders"],
        "warnings": bundle.community_data["warnings"],
        "blocked": bundle.community_data["blocked"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-community",
        summary=f"Generated community plan for {bundle.community_data['repo']}",
        metadata={
            "repo_root": str(repo_root),
            "mode": bundle.community_data["mode"],
            "scorecard_after": bundle.community_data["scorecard_after"],
        },
    )
    return payload


def run_legal_command(args: argparse.Namespace) -> dict:
    """Run deterministic legal planning and optionally write legal files."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_legal(repo_root, write_files=args.write_files, license_id=args.license)
    artifacts = write_legal_artifacts(repo_root, bundle)
    payload = {
        "operation": "legal",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.legal_data["repo"],
        "mode": bundle.legal_data["mode"],
        "compliance_status": bundle.legal_data["compliance_status"],
        "license_type": bundle.legal_data["license_type"],
        "recommended_license_type": bundle.legal_data["recommended_license_type"],
        "planned_writes": bundle.legal_data["planned_writes"],
        "files_created": bundle.legal_data["files_created"],
        "files_updated": bundle.legal_data["files_updated"],
        "dependency_conflicts": bundle.legal_data["dependency_conflicts"],
        "edge_case_flags": bundle.legal_data["edge_case_flags"],
        "warnings": bundle.legal_data["warnings"],
        "blocked": bundle.legal_data["blocked"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-legal",
        summary=f"Generated legal plan for {bundle.legal_data['repo']}",
        metadata={
            "repo_root": str(repo_root),
            "mode": bundle.legal_data["mode"],
            "compliance_status": bundle.legal_data["compliance_status"],
            "recommended_license_type": bundle.legal_data["recommended_license_type"],
        },
    )
    return payload


def run_readme_command(args: argparse.Namespace) -> dict:
    """Run deterministic README planning and optionally write README.md."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_readme(repo_root, write=args.write, generate_assets=args.generate_assets)
    artifacts = write_readme_artifacts(repo_root, bundle)
    payload = {
        "operation": "readme",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.readme_data["repo"],
        "mode": bundle.readme_data["mode"],
        "written": bundle.readme_data["written"],
        "assets_requested": bundle.readme_data["assets_requested"],
        "banner_generated": bundle.readme_data["banner_generated"],
        "banner_path": bundle.readme_data["banner_path"],
        "social_preview_generated": bundle.readme_data["social_preview_generated"],
        "social_preview_path": bundle.readme_data["social_preview_path"],
        "banner_links": bundle.readme_data["banner_links"],
        "social_preview_links": bundle.readme_data["social_preview_links"],
        "score_before": bundle.readme_data["score_before"],
        "score_after": bundle.readme_data["score_after"],
        "sections": bundle.readme_data["sections"],
        "banner_status": bundle.readme_data["banner_status"],
        "keywords_integrated": bundle.readme_data["keywords_integrated"],
        "warnings": bundle.readme_data["warnings"],
        "blocked": bundle.readme_data["blocked"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-readme",
        summary=f"Generated README plan for {bundle.readme_data['repo']}",
        metadata={
            "repo_root": str(repo_root),
            "mode": bundle.readme_data["mode"],
            "written": bundle.readme_data["written"],
            "assets_requested": bundle.readme_data["assets_requested"],
            "banner_generated": bundle.readme_data["banner_generated"],
            "social_preview_generated": bundle.readme_data["social_preview_generated"],
            "score_after": bundle.readme_data["score_after"],
        },
    )
    return payload


def run_release_command(args: argparse.Namespace) -> dict:
    """Run deterministic release planning and optionally apply file or release actions."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_release(
        repo_root,
        write_files=args.write_files,
        create_release=args.create_release,
        publish=args.publish,
    )
    artifacts = write_release_artifacts(repo_root, bundle)
    payload = {
        "operation": "release",
        "status": "ok",
        "repo_root": str(repo_root),
        "repo": bundle.releases_data["repo"],
        "mode": bundle.releases_data["mode"],
        "latest_version": bundle.releases_data["latest_version"],
        "recommended_next_version": bundle.releases_data["recommended_next_version"],
        "recommended_title": bundle.releases_data["recommended_title"],
        "release_verdict": bundle.releases_data["release_verdict"],
        "commits_since_release": bundle.releases_data["commits_since_release"],
        "version_match": bundle.releases_data["version_match"],
        "files_written": bundle.releases_data["files_written"],
        "release_command": bundle.releases_data["release_command"],
        "warnings": bundle.releases_data["warnings"],
        "blocked": bundle.releases_data["blocked"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-release",
        summary=f"Generated release plan for {bundle.releases_data['repo']}",
        metadata={
            "repo_root": str(repo_root),
            "mode": bundle.releases_data["mode"],
            "release_verdict": bundle.releases_data["release_verdict"],
            "recommended_next_version": bundle.releases_data["recommended_next_version"],
        },
    )
    return payload


def run_empire_command(args: argparse.Namespace) -> dict:
    """Run deterministic portfolio planning and optionally generate avatar assets."""
    repo_root = resolve_repo_root(args.path)
    bundle = run_empire(repo_root, username=args.username, generate_avatar=args.generate_avatar)
    artifacts = write_empire_artifacts(repo_root, bundle)
    payload = {
        "operation": "empire",
        "status": "ok",
        "repo_root": str(repo_root),
        "portfolio_owner": bundle.empire_data["portfolio_owner"],
        "mode": bundle.empire_data["mode"],
        "portfolio_size": bundle.empire_data["portfolio_size"],
        "portfolio_health_score": bundle.empire_data["portfolio_health_score"],
        "health_delta": bundle.empire_data["health_delta"],
        "identity": bundle.empire_data["identity"],
        "pinned_repos_recommended": bundle.empire_data["pinned_repos_recommended"],
        "commands": bundle.empire_data["commands"],
        "avatar": bundle.empire_data["avatar"],
        "warnings": bundle.empire_data["warnings"],
        "blocked": bundle.empire_data["blocked"],
        "artifacts": artifacts,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    append_run_cache(
        operation="headless-empire",
        summary=f"Generated empire blueprint for {bundle.empire_data['portfolio_owner']}",
        metadata={
            "repo_root": str(repo_root),
            "portfolio_owner": bundle.empire_data["portfolio_owner"],
            "portfolio_size": bundle.empire_data["portfolio_size"],
            "portfolio_health_score": bundle.empire_data["portfolio_health_score"],
        },
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description="Run Legends GitHub workflows non-interactively")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="Validate CLI/API readiness")
    verify.add_argument("--mode", default="both", choices=["cli", "api", "both"])
    verify.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    verify.add_argument("--allow-missing-gh-auth", action="store_true")

    audit = sub.add_parser("audit", help="Run the deterministic repository audit")
    audit.add_argument("--path", default=".", help="Repo root or a path inside the repo")

    seo = sub.add_parser("seo", help="Generate deterministic SEO cache data for a local repo")
    seo.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    seo.add_argument("--mode", default="quick", choices=["quick", "full"])

    meta = sub.add_parser("meta", help="Plan deterministic metadata updates for a local repo")
    meta.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    meta.add_argument("--apply", action="store_true", help="Apply ready gh repo edit commands")

    community = sub.add_parser("community", help="Plan or write deterministic community-health files for a local repo")
    community.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    community.add_argument("--write-files", action="store_true", help="Write missing or outdated community-health files")

    legal = sub.add_parser("legal", help="Plan or write deterministic legal/compliance files for a local repo")
    legal.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    legal.add_argument("--write-files", action="store_true", help="Write missing or outdated legal/compliance files")
    legal.add_argument("--license", default="", help="Explicit SPDX-like license id to apply when writing")

    readme = sub.add_parser("readme", help="Preview or write a deterministic README for a local repo")
    readme.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    readme.add_argument("--write", action="store_true", help="Write README.md instead of preview-only output")
    readme.add_argument(
        "--generate-assets",
        action="store_true",
        help="Generate missing banner and social preview assets when runtime capabilities are available",
    )

    release = sub.add_parser("release", help="Plan deterministic release/versioning work for a local repo")
    release.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    release.add_argument("--write-files", action="store_true", help="Write CHANGELOG.md and .github/release.yml")
    release.add_argument("--create-release", action="store_true", help="Create a GitHub release after writing files")
    release.add_argument("--publish", action="store_true", help="Publish the release immediately instead of creating a draft")

    empire = sub.add_parser("empire", help="Plan deterministic portfolio branding work for the current GitHub owner")
    empire.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    empire.add_argument("--username", default="", help="Explicit GitHub owner/login to analyze")
    empire.add_argument("--generate-avatar", action="store_true", help="Generate an avatar asset when KIE and Pillow are available")

    cache_status = sub.add_parser("cache-status", help="Show current .github-audit cache state")
    cache_status.add_argument("--path", default=".", help="Repo root or a path inside the repo")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "verify": run_verify,
        "audit": run_audit_command,
        "seo": run_seo_command,
        "meta": run_meta_command,
        "community": run_community_command,
        "legal": run_legal_command,
        "readme": run_readme_command,
        "release": run_release_command,
        "empire": run_empire_command,
        "cache-status": run_cache_status,
    }
    try:
        payload = handlers[args.command](args)
        print(json.dumps(payload, indent=2))
        if payload.get("status") == "error":
            return 1
        if payload.get("operation") == "verify":
            return 0 if payload.get("ready") else 1
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": True, "command": args.command, "message": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
