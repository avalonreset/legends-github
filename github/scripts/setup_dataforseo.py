#!/usr/bin/env python3
"""Configure the DataForSEO MCP server for Codex GitHub."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cache_state import append_run_cache
from runtime_paths import codex_config_path


MCP_NAME = "dataforseo"
MCP_PACKAGE = "@anthropic/data-for-seo-mcp"


def load_config(path: Path) -> str:
    """Load the active Codex config file."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def save_config(path: Path, text: str) -> None:
    """Persist the active Codex config file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_server_block(login: str, password: str) -> str:
    """Build the DataForSEO MCP TOML block."""
    return (
        f'[mcp_servers.{MCP_NAME}]\n'
        'command = "npx"\n'
        f'args = ["-y", "{MCP_PACKAGE}"]\n\n'
        f'[mcp_servers.{MCP_NAME}.env]\n'
        f'DATAFORSEO_LOGIN = "{login}"\n'
        f'DATAFORSEO_PASSWORD = "{password}"\n'
    )


def strip_server_block(config_text: str) -> str:
    """Remove the DataForSEO MCP block from config text."""
    lines = config_text.splitlines()
    result = []
    skip = False
    prefixes = {f"[mcp_servers.{MCP_NAME}]", f"[mcp_servers.{MCP_NAME}.env]"}

    for line in lines:
        stripped = line.strip()
        if stripped in prefixes:
            skip = True
            continue
        if skip and stripped.startswith("[") and stripped not in prefixes:
            skip = False
        if not skip:
            result.append(line)
    return "\n".join(result).strip()


def extract_value(config_text: str, key: str) -> str:
    """Extract one env value from the current DataForSEO block."""
    in_env = False
    for line in config_text.splitlines():
        stripped = line.strip()
        if stripped == f"[mcp_servers.{MCP_NAME}.env]":
            in_env = True
            continue
        if stripped.startswith("[") and stripped != f"[mcp_servers.{MCP_NAME}]":
            in_env = False
        if in_env and stripped.startswith(f"{key} = "):
            return stripped.split("=", 1)[1].strip().strip('"')
    return ""


def check_setup() -> dict:
    """Return the current DataForSEO MCP status."""
    config_path = codex_config_path()
    config_text = load_config(config_path)
    configured = f"[mcp_servers.{MCP_NAME}]" in config_text
    return {
        "operation": "check",
        "configured": configured,
        "config_path": str(config_path),
        "package": MCP_PACKAGE if configured else "",
        "login_present": bool(extract_value(config_text, "DATAFORSEO_LOGIN")) if configured else False,
        "password_present": bool(extract_value(config_text, "DATAFORSEO_PASSWORD")) if configured else False,
    }


def setup(login: str, password: str) -> dict:
    """Write the DataForSEO MCP block into the active Codex config."""
    if not login or not password:
        raise ValueError("Both login and password are required.")
    config_path = codex_config_path()
    config_text = strip_server_block(load_config(config_path))
    updated = f"{config_text}\n\n{build_server_block(login, password)}".strip()
    save_config(config_path, updated)
    append_run_cache(
        operation="dataforseo-setup",
        summary="Configured DataForSEO MCP in Codex config",
        metadata={"config_path": str(config_path), "package": MCP_PACKAGE},
    )
    return {
        "operation": "setup",
        "configured": True,
        "config_path": str(config_path),
        "package": MCP_PACKAGE,
    }


def remove() -> dict:
    """Remove the DataForSEO MCP block from the active Codex config."""
    config_path = codex_config_path()
    config_text = load_config(config_path)
    had_block = f"[mcp_servers.{MCP_NAME}]" in config_text
    if had_block:
        save_config(config_path, strip_server_block(config_text))
        append_run_cache(
            operation="dataforseo-remove",
            summary="Removed DataForSEO MCP from Codex config",
            metadata={"config_path": str(config_path)},
        )
    return {"operation": "remove", "removed": had_block, "config_path": str(config_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure DataForSEO MCP for Codex GitHub")
    parser.add_argument("--login")
    parser.add_argument("--password")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        if args.check:
            payload = check_setup()
        elif args.remove:
            payload = remove()
        else:
            login = args.login
            password = args.password
            if not login:
                if not sys.stdin.isatty():
                    raise ValueError("--login is required in non-interactive mode.")
                login = input("DataForSEO login: ").strip()
            if not password:
                if not sys.stdin.isatty():
                    raise ValueError("--password is required in non-interactive mode.")
                password = input("DataForSEO password: ").strip()
            payload = setup(login=login, password=password)

        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(json.dumps(payload, indent=2))
        return 0
    except ValueError as exc:
        payload = {"error": True, "message": str(exc)}
        print(json.dumps(payload, indent=2) if args.json else f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
