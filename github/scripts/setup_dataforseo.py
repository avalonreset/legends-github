#!/usr/bin/env python3
"""Inspect the shared DataForSEO dependency without modifying agent configuration."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def check_setup():
    installed = importlib.util.find_spec("legends_dataforseo") is not None
    credentials = False
    if installed:
        from legends_dataforseo import credential_status
        credentials = bool(credential_status().get("present"))
    return {"package": "legends-dataforseo-kit", "installed": installed,
            "configured": installed and credentials, "credentials_present": credentials,
            "network_checked": False, "mcp_required": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--login", help=argparse.SUPPRESS)
    parser.add_argument("--password", help=argparse.SUPPRESS)
    parser.add_argument("--remove", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.login or args.password or args.remove:
        print(json.dumps({"error": True, "message": "Legacy MCP setup has been retired. Set credentials in the environment. Existing host configuration was not changed. See docs/SEO-RESEARCH.md."}))
        return 2
    if args.install:
        script = Path(__file__).resolve()
        candidates = [script.parents[2] / "requirements-dataforseo.txt", script.parents[1] / "requirements-dataforseo.txt"]
        requirements = next((p for p in candidates if p.is_file()), None)
        if requirements is None:
            raise RuntimeError("Dependency manifest missing; run installation from the toolkit checkout")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], check=True)
    print(json.dumps(check_setup(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
