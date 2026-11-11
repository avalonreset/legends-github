#!/usr/bin/env python3
"""Static Gold Standard release gate for legends-github."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_MODULE_ID = "legends-github"

REQUIRED_FILES = [
    ".legends-module",
    ".legends-router-pin",
    "VERSION",
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "SUPPORT.md",
    "CITATION.cff",
    "legends_github.py",
    "docs/GITHUB-RECIPE.md",
    "docs/AGENT-RECIPE.md",
    "skills/cto-legends/SKILL.md",
    "assets/banner.png",
    "assets/banner.webp",
    "assets/preview.png",
    "assets/social-preview.png",
    "assets/manifest.json",
]

FORBIDDEN_PATHS = [
    "skills/legends-github",
    "CLAUDE.md",
    "GEMINI.md",
    "CODEX.md",
    "GROK.md",
    "gemini-extension.json",
    "skill-package.json",
    "SKILL.md",
    ".claude-plugin",
    "assets/ben.webp",
]

FORBIDDEN_EXTENSIONS = {
    ".ps1",
    ".sh",
    ".bat",
    ".cmd",
    ".vbs",
    ".wsf",
    ".hta",
    ".scr",
}

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(r"C:\\Users\\", re.IGNORECASE),
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"rk_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"whsec_[A-Za-z0-9]{16,}"),
    re.compile(r"rankenstein", re.IGNORECASE),
]

EDR_FORBIDDEN_SUBSTRINGS = [
    "Local\\Google\\Chrome\\User Data",
    "Local/Google/Chrome/User Data",
    "Microsoft\\Edge\\User Data",
    "BraveSoftware\\Brave-Browser\\User Data",
    "Login Data",
    "Local State",
    "CryptUnprotectData",
    "win32crypt",
    " Mimikatz",
    "Invoke-Expression",
    "FromBase64String",
    "DownloadString(",
]

FORBIDDEN_CODE_PATTERNS = [
    (re.compile(r"\beval\s*\("), "eval()"),
    (re.compile(r"\bexec\s*\("), "exec()"),
    (re.compile(r"\bpickle\.(?:load|loads)\s*\("), "pickle.load/loads()"),
    (re.compile(r"\byaml\.load\s*\("), "yaml.load()"),
    (re.compile(r"\bshell\s*=\s*True\b"), "shell=True"),
    (re.compile(r"\bos\.system\s*\("), "os.system()"),
]

CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ufffd]")
PNG_FORBIDDEN_CHUNKS = {b"tEXt", b"iTXt", b"zTXt", b"eXIf"}
WEBP_FORBIDDEN_CHUNKS = {b"EXIF", b"XMP "}
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^```[\s\S]*?^```", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def _iter_repo_files():
    skip_dirs = {".git", "__pycache__", ".pytest_cache", "dist", "build", ".venv", "venv", "node_modules"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in skip_dirs or part.endswith(".egg-info") for part in path.parts):
            continue
        yield path


def _check_png_chunks(path: Path, issues: list[str]) -> None:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        issues.append(f"{path.relative_to(ROOT)}: invalid PNG signature")
        return
    offset = 8
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        if chunk_type in PNG_FORBIDDEN_CHUNKS:
            issues.append(f"{path.relative_to(ROOT)}: forbidden PNG metadata chunk {chunk_type.decode('ascii', 'replace')}")
        offset += 12 + length


def _check_webp_chunks(path: Path, issues: list[str]) -> None:
    data = path.read_bytes()
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        issues.append(f"{path.relative_to(ROOT)}: invalid WEBP header")
        return
    offset = 12
    while offset + 8 <= len(data):
        chunk_type = data[offset : offset + 4]
        length = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
        if chunk_type in WEBP_FORBIDDEN_CHUNKS:
            issues.append(f"{path.relative_to(ROOT)}: forbidden WEBP metadata chunk {chunk_type.decode('ascii', 'replace')}")
        offset += 8 + length + (length % 2)


def _check_markdown_links(path: Path, text: str, issues: list[str]) -> None:
    stripped_text = INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))
    root_resolved = ROOT.resolve()
    for match in MD_LINK_RE.finditer(stripped_text):
        raw_target = match.group(1).strip()
        if not raw_target or raw_target.startswith(("#", "http://", "https://", "mailto:", "tel:")):
            continue
        target_part = raw_target.split()[0].strip("<>")
        rel_path = unquote(target_part.split("#", 1)[0].split("?", 1)[0])
        if not rel_path:
            continue
        resolved = (path.parent / rel_path).resolve()
        if not resolved.is_relative_to(root_resolved):
            issues.append(f"{path.relative_to(ROOT)}: markdown link escapes repo root -> {raw_target}")
        elif not resolved.exists():
            issues.append(f"{path.relative_to(ROOT)}: broken relative link -> {raw_target}")


def main() -> int:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            issues.append(f"Missing required file: {rel}")

    for rel in FORBIDDEN_PATHS:
        if (ROOT / rel).exists():
            issues.append(f"Forbidden path exists: {rel}")

    module_file = ROOT / ".legends-module"
    if module_file.is_file():
        if module_file.read_text(encoding="utf-8").strip() != EXPECTED_MODULE_ID:
            issues.append(f".legends-module must equal '{EXPECTED_MODULE_ID}'")

    skills_dir = ROOT / "skills"
    if skills_dir.is_dir():
        children = sorted(p.name for p in skills_dir.iterdir() if not p.name.startswith("."))
        if children != ["cto-legends"]:
            issues.append(f"skills/ must contain only ['cto-legends'], found {children}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog_text and f"## {version}" not in changelog_text:
        issues.append(f"CHANGELOG.md missing heading for {version}")

    cff_text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if f'version: "{version}"' not in cff_text:
        issues.append(f"CITATION.cff version does not match {version}")

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    if "Agent setup (via `cto-legends`)" not in readme_text:
        issues.append("README.md missing 'Agent setup (via `cto-legends`)' heading")
    if f"v{version}" not in readme_text:
        issues.append(f"README.md missing v{version} reference")

    manifest_path = ROOT / "assets" / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for asset_name in ("banner.png", "banner.webp", "preview.png", "social-preview.png"):
            asset_path = ROOT / "assets" / asset_name
            if asset_name not in manifest:
                issues.append(f"assets/manifest.json missing '{asset_name}'")
                continue
            if asset_path.is_file():
                actual_sha = hashlib.sha256(asset_path.read_bytes()).hexdigest()
                if manifest[asset_name].get("sha256") != actual_sha:
                    issues.append(f"assets/manifest.json sha256 mismatch for {asset_name}")

    for path in _iter_repo_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            issues.append(f"Forbidden script/executable extension in repo: {rel}")
        if path.suffix.lower() == ".png":
            _check_png_chunks(path, issues)
        elif path.suffix.lower() == ".webp":
            _check_webp_chunks(path, issues)

        if path.suffix.lower() in {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".cff", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if CONTROL_CHAR_RE.search(text):
                issues.append(f"Control character or replacement character found in {rel}")
            if "\u2014" in text or "\u2013" in text:
                issues.append(f"Em-dash or en-dash found in {rel}")
            if rel != "scripts/check_release.py":
                for pattern in FORBIDDEN_TEXT_PATTERNS:
                    if pattern.search(text):
                        issues.append(f"Forbidden text pattern {pattern.pattern} in {rel}")
                for edr_sub in EDR_FORBIDDEN_SUBSTRINGS:
                    if edr_sub in text:
                        issues.append(f"EDR-sensitive substring '{edr_sub}' in {rel}")
            if path.suffix.lower() == ".py" and rel != "scripts/check_release.py" and not rel.startswith("tests/"):
                for code_re, label in FORBIDDEN_CODE_PATTERNS:
                    if code_re.search(text):
                        issues.append(f"Forbidden code pattern {label} in {rel}")
            if path.suffix.lower() == ".md":
                _check_markdown_links(path, text, issues)

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    print(f"Release checks: PASS (0 issues, version {version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
