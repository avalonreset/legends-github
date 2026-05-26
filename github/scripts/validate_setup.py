#!/usr/bin/env python3
"""Validate that Legends GitHub is ready for CLI, API, or both."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cache_state import append_run_cache, probe_repo_cache, write_setup_cache
from github_runtime import gh_auth_ok, have_command, pillow_available, repo_slug_from_git, resolve_kie_api_key, resolve_repo_root
from runtime_paths import codex_agents_dir, codex_config_path, codex_skill_dir, runtime_paths_payload


def _check(label: str, passed: bool, detail: str = "") -> dict:
    return {"label": label, "passed": bool(passed), "detail": detail}


def validate_setup(repo_root: Path, mode: str = "both", allow_missing_gh_auth: bool = False) -> dict:
    """Validate Legends GitHub runtime readiness."""
    checks = []
    repo_slug = repo_slug_from_git(repo_root) or ""
    cache_dir, cache_writable = probe_repo_cache(repo_root)
    kie_api_key, kie_source = resolve_kie_api_key(repo_root)

    requires_cli = mode in {"cli", "both"}
    requires_api = mode in {"api", "both"}
    dataforseo_helper = SCRIPT_DIR / "setup_dataforseo.py"
    headless_runner = SCRIPT_DIR / "run_headless.py"
    pillow_ready = pillow_available()

    checks.append(_check("Python runtime available", sys.version_info >= (3, 10), sys.version.split()[0]))
    checks.append(_check("Git installed", have_command("git"), shutil.which("git") or "not found"))
    checks.append(_check("GitHub CLI installed", have_command("gh"), shutil.which("gh") or "not found"))
    checks.append(_check("Node.js installed", have_command("node"), shutil.which("node") or "not found"))
    checks.append(_check("npx available", have_command("npx"), shutil.which("npx") or "not found"))
    checks.append(_check("Repo cache directory writable", cache_writable, str(cache_dir)))
    checks.append(_check("Repo has a git remote", bool(repo_slug), repo_slug or "origin not resolved"))

    if requires_cli:
        checks.append(_check("Installed skill directory present", codex_skill_dir().exists(), str(codex_skill_dir())))
        checks.append(_check("Installed agents directory present", codex_agents_dir().exists(), str(codex_agents_dir())))
        checks.append(_check("Codex config path resolved", True, str(codex_config_path())))

    auth_ok = gh_auth_ok()
    if requires_api or requires_cli:
        if allow_missing_gh_auth:
            checks.append(_check("GitHub CLI authenticated", True, "skipped by --allow-missing-gh-auth"))
        else:
            checks.append(_check("GitHub CLI authenticated", auth_ok, "gh auth status"))

    checks.append(_check("KIE API key discoverable", bool(kie_api_key), kie_source or "not found"))
    checks.append(_check("Pillow available", pillow_ready, "PIL import" if pillow_ready else "not found"))
    checks.append(_check("DataForSEO setup helper present", dataforseo_helper.exists(), str(dataforseo_helper)))
    checks.append(_check("Headless runner present", headless_runner.exists(), str(headless_runner)))

    required_labels = {
        "Python runtime available",
        "Git installed",
        "Repo cache directory writable",
        "Headless runner present",
    }
    if requires_cli:
        required_labels.update(
            {
                "Installed skill directory present",
                "Installed agents directory present",
                "Codex config path resolved",
            }
        )

    ready = all(check["passed"] for check in checks if check["label"] in required_labels)
    warnings: list[str] = []
    if not repo_slug:
        warnings.append("No git remote detected. Deterministic runs will use local-only metadata.")
    if not auth_ok and not allow_missing_gh_auth:
        warnings.append("GitHub CLI is not authenticated. Live GitHub metadata enrichment is unavailable.")
    if not have_command("gh"):
        warnings.append("GitHub CLI is not installed. Deterministic runs can still execute locally without GitHub enrichment.")
    if not kie_api_key:
        warnings.append("KIE_API_KEY not found. Banner and image generation remain unavailable.")
    if not pillow_ready:
        warnings.append("Pillow is not installed. Deterministic banner conversion and social preview generation are unavailable.")
    payload = {
        "mode": mode,
        "ready": ready,
        "repo_root": str(repo_root),
        "repo_slug": repo_slug,
        "checks": checks,
        "kie_api_key_present": bool(kie_api_key),
        "kie_api_key_source": kie_source,
        "capabilities": {
            "banner_generation_ready": bool(kie_api_key) and pillow_ready,
            "image_pipeline_ready": pillow_ready,
            "github_cli_ready": have_command("gh"),
            "github_metadata_ready": auth_ok and bool(repo_slug),
            "local_headless_ready": ready,
            "dataforseo_runtime_ready": have_command("node") and have_command("npx"),
            "dataforseo_setup_ready": dataforseo_helper.exists(),
        },
        "warnings": warnings,
        "runtime_paths": runtime_paths_payload(repo_root),
    }
    write_setup_cache(
        validation_passed=ready,
        repo_root=str(repo_root),
        repo_slug=repo_slug,
        gh_authenticated=auth_ok,
        kie_api_key_present=bool(kie_api_key),
        checked_by=f"validate_setup.py --mode {mode}",
    )
    append_run_cache(
        operation="setup-validate",
        summary=f"Validated Legends GitHub setup for {mode}",
        metadata={"passed": ready, "checks": len(checks), "repo_root": str(repo_root)},
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Legends GitHub for CLI or API execution")
    parser.add_argument("--mode", default="both", choices=["cli", "api", "both"])
    parser.add_argument("--path", default=".", help="Repo root or a path inside the repo")
    parser.add_argument("--allow-missing-gh-auth", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = resolve_repo_root(args.path)
    payload = validate_setup(repo_root, mode=args.mode, allow_missing_gh_auth=args.allow_missing_gh_auth)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Legends GitHub Setup Validation")
        print("=" * 40)
        for check in payload["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            detail = f" -- {check['detail']}" if check["detail"] else ""
            print(f"[{status}] {check['label']}{detail}")
        print("=" * 40)
        print(f"Ready: {'YES' if payload['ready'] else 'NO'}")
    return 0 if payload["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
