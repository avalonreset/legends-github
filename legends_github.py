#!/usr/bin/env python3
"""Portable, discoverable entry point for Legends GitHub workflows."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import runpy
import sys

ROOT = Path(__file__).resolve().parent
WORKFLOWS = {
    "research": {"purpose": "Estimate or collect DataForSEO search evidence", "effects": ["local_artifacts", "explicit_paid_api_calls"], "mutation_flags": ["--execute"]},
    "discover": {"purpose": "Plan evidence-backed organic discovery experiments", "effects": ["local_artifacts"]},
    "verify": {"purpose": "Check local readiness and optional capabilities", "effects": ["local_artifacts"]},
    "audit": {"purpose": "Collect repository evidence and prioritize findings", "effects": ["local_artifacts", "optional_github_reads"]},
    "seo": {"purpose": "Derive keyword hypotheses from repository evidence", "effects": ["local_artifacts", "optional_github_reads"]},
    "meta": {"purpose": "Plan repository metadata changes", "effects": ["local_artifacts", "optional_github_reads"], "mutation_flags": ["--apply"]},
    "community": {"purpose": "Plan contributor workflow files", "effects": ["local_artifacts", "optional_github_reads"], "mutation_flags": ["--write-files"]},
    "legal": {"purpose": "Inventory licensing and attribution for review", "effects": ["local_artifacts", "optional_github_reads"], "mutation_flags": ["--write-files"]},
    "readme": {"purpose": "Preview README improvements and reuse optional local artwork", "effects": ["local_artifacts", "optional_github_reads"], "mutation_flags": ["--write", "--generate-assets"]},
    "release": {"purpose": "Plan changelog and release preparation", "effects": ["local_artifacts", "optional_github_reads"], "mutation_flags": ["--write-files", "--create-release", "--publish"]},
    "empire": {"purpose": "Plan portfolio presentation", "effects": ["local_artifacts", "optional_github_reads"], "mutation_flags": ["--generate-avatar"]},
    "cache-status": {"purpose": "Inspect saved workflow evidence", "effects": ["local_reads"]},
}

def main():
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--version", action="version", version="legends-github 0.1.0")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--artifacts-dir", type=Path)
    options, args = parser.parse_known_args()
    if options.offline:
        os.environ["LEGENDS_GITHUB_OFFLINE"] = "1"
    if args == ["capabilities"]:
        print(json.dumps({"schema_version": "1.0", "name": "legends-github", "entrypoint": "python legends_github.py", "global_options": ["--offline", "--artifacts-dir"], "workflows": WORKFLOWS, "requires_llm_provider": False, "requires_native_skill_loader": False, "image_generation": "external_host_tool_optional"}, indent=2))
        return 0
    if options.artifacts_dir:
        # Resolve the same repository root as the underlying workflow, even from a subfolder.
        sys.path.insert(0, str(ROOT / "github" / "scripts"))
        from github_runtime import resolve_repo_root
        path_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        path_parser.add_argument("--path", default=".")
        path_args, _ = path_parser.parse_known_args(args)
        target = resolve_repo_root(path_args.path)
        identity = hashlib.sha256(os.path.normcase(str(target)).encode()).hexdigest()[:16]
        destination = options.artifacts_dir.expanduser().resolve()
        os.environ["GITHUB_AUDIT_DIR"] = str(destination / "repos" / identity)
        os.environ["LEGENDS_GITHUB_HOME"] = str(destination / "runtime")
    if os.environ.get("LEGENDS_GITHUB_OFFLINE", "").strip().lower() in {"1", "true", "yes"} and any(flag in args for flag in ("--apply", "--create-release", "--publish")):
        print(json.dumps({"error": True, "message": "Remote mutation flags cannot be used with --offline."}))
        return 2
    if args in (["--help"], ["-h"]):
        print("Portable options: --offline disables external requests; --artifacts-dir PATH isolates caches and reports.\nUse capabilities for the machine-readable workflow contract.\n")
    sys.argv = [str(ROOT / "github" / "scripts" / "run_headless.py"), *args]
    runpy.run_path(sys.argv[0], run_name="__main__")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": True, "message": str(exc)}))
        raise SystemExit(1)
