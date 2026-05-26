#!/usr/bin/env python3
"""Deterministic legal planning for Legends GitHub."""

from __future__ import annotations

import json
import re
try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_repo import detect_repo_type, load_readme, slugify
from cache_state import read_repo_cache, write_repo_cache
from github_runtime import gh_repo_view, repo_slug_from_git, run_command
from runtime_paths import repo_output_dir


DISCLAIMER_BLOCK = (
    "> This analysis is automated compliance assistance, not legal advice.\n"
    "> Always verify licensing decisions with your own due diligence.\n"
    "> For complex or high-stakes situations, consult a qualified attorney.\n"
)

LICENSE_FILE = "LICENSE"
SECURITY_FILE = "SECURITY.md"
CITATION_FILE = "CITATION.cff"
NOTICE_FILE = "NOTICE"

LOCAL_LICENSE_TEMPLATES = {
    "MIT": """MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

"License" shall mean the terms and conditions for use, reproduction, and
distribution as defined by Sections 1 through 9 of this document.

"Licensor" shall mean the copyright owner or entity authorized by the copyright
owner that is granting the License.

"Legal Entity" shall mean the union of the acting entity and all other entities
that control, are controlled by, or are under common control with that entity.
For the purposes of this definition, "control" means (i) the power, direct or
indirect, to cause the direction or management of such entity, whether by
contract or otherwise, or (ii) ownership of fifty percent (50%) or more of the
outstanding shares, or (iii) beneficial ownership of such entity.

"You" (or "Your") shall mean an individual or Legal Entity exercising
permissions granted by this License.

"Source" form shall mean the preferred form for making modifications, including
but not limited to software source code, documentation source, and
configuration files.

"Object" form shall mean any form resulting from mechanical transformation or
translation of a Source form, including but not limited to compiled object
code, generated documentation, and conversions to other media types.

"Work" shall mean the work of authorship, whether in Source or Object form,
made available under the License, as indicated by a copyright notice that is
included in or attached to the work.

"Derivative Works" shall mean any work, whether in Source or Object form, that
is based on (or derived from) the Work and for which the editorial revisions,
annotations, elaborations, or other modifications represent, as a whole, an
original work of authorship.

"Contribution" shall mean any work of authorship, including the original
version of the Work and any modifications or additions to that Work or
Derivative Works, that is intentionally submitted to Licensor for inclusion in
the Work by the copyright owner or by an individual or Legal Entity authorized
to submit on behalf of the copyright owner.

"Contributor" shall mean Licensor and any individual or Legal Entity on behalf
of whom a Contribution has been received by Licensor and subsequently
incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of this
License, each Contributor hereby grants to You a perpetual, worldwide,
non-exclusive, no-charge, royalty-free, irrevocable copyright license to
reproduce, prepare Derivative Works of, publicly display, publicly perform,
sublicense, and distribute the Work and such Derivative Works in Source or
Object form.

3. Grant of Patent License. Subject to the terms and conditions of this
License, each Contributor hereby grants to You a perpetual, worldwide,
non-exclusive, no-charge, royalty-free, irrevocable patent license to make,
have made, use, offer to sell, sell, import, and otherwise transfer the Work.

4. Redistribution. You may reproduce and distribute copies of the Work or
Derivative Works thereof in any medium, with or without modifications, and in
Source or Object form, provided that You meet the following conditions:

(a) You must give any other recipients of the Work or Derivative Works a copy
of this License; and

(b) You must cause any modified files to carry prominent notices stating that
You changed the files; and

(c) You must retain, in the Source form of any Derivative Works that You
distribute, all copyright, patent, trademark, and attribution notices from the
Source form of the Work; and

(d) If the Work includes a "NOTICE" text file as part of its distribution, then
any Derivative Works that You distribute must include a readable copy of the
attribution notices contained within such NOTICE file.

5. Submission of Contributions. Unless You explicitly state otherwise, any
Contribution intentionally submitted for inclusion in the Work by You to the
Licensor shall be under the terms and conditions of this License.

6. Trademarks. This License does not grant permission to use the trade names,
trademarks, service marks, or product names of the Licensor, except as
required for reasonable and customary use in describing the origin of the Work.

7. Disclaimer of Warranty. Unless required by applicable law or agreed to in
writing, Licensor provides the Work on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.

8. Limitation of Liability. In no event and under no legal theory shall any
Contributor be liable to You for damages, including any direct, indirect,
special, incidental, or consequential damages arising as a result of this
License or out of the use or inability to use the Work.

9. Accepting Warranty or Additional Liability. While redistributing the Work or
Derivative Works thereof, You may choose to offer, and charge a fee for,
acceptance of support, warranty, indemnity, or other liability obligations.

Copyright {year} {holder}
""",
    "BSD-2-Clause": """Copyright (c) {year}, {holder}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""",
    "BSD-3-Clause": """Copyright (c) {year}, {holder}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""",
    "ISC": """ISC License

Copyright (c) {year}, {holder}

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
""",
    "Unlicense": """This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute
this software, either in source code form or as a compiled binary, for any
purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this
software dedicate any and all copyright interest in the software to the public
domain. We make this dedication for the benefit of the public at large and to
the detriment of our heirs and successors. We intend this dedication to be an
overt act of relinquishment in perpetuity of all present and future rights to
this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
""",
    "LicenseRef-Proprietary": """Proprietary Software License

Copyright (c) {year} {holder}. All rights reserved.

This software and associated documentation files (the "Software") are the
proprietary property of the copyright holder. The Software is licensed, not
sold, to authorized users under the following terms:

1. GRANT OF LICENSE
   You are granted a non-exclusive, non-transferable, revocable license to
   install and use the Software for your own personal or business purposes,
   subject to the terms of this agreement and your active membership in the
   copyright holder's community program.

2. RESTRICTIONS
   You may NOT:
   a) Copy, redistribute, publish, or share the Software or any portion of
      it with any third party, whether for free or for compensation;
   b) Modify, adapt, translate, reverse engineer, decompile, or disassemble
      the Software for the purpose of creating derivative works for
      distribution;
   c) Sublicense, rent, lease, or lend the Software to any third party;
   d) Remove or alter any proprietary notices, labels, or marks on the
      Software;
   e) Use the Software to create a competing product or service.

3. MEMBERSHIP REQUIREMENT
   Access to the Software is contingent upon active membership in the
   copyright holder's authorized community program. Termination or
   expiration of membership automatically revokes this license. Upon
   revocation, you must delete all copies of the Software in your
   possession.

4. OWNERSHIP
   The copyright holder retains all right, title, and interest in and to
   the Software, including all intellectual property rights. This license
   does not transfer any ownership rights to you.

5. NO WARRANTY
   THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS
   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

6. LIMITATION OF LIABILITY
   IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES,
   OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR
   OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR
   THE USE OR OTHER DEALINGS IN THE SOFTWARE.

7. TERMINATION
   This license is effective until terminated. It terminates automatically
   if you fail to comply with any term of this agreement. Upon termination,
   you must destroy all copies of the Software.

8. GOVERNING LAW
   This agreement shall be governed by and construed in accordance with the
   laws of the jurisdiction in which the copyright holder resides.
""",
}

REMOTE_LICENSE_KEYS = {
    "GPL-3.0-only": "gpl-3.0",
    "AGPL-3.0-only": "agpl-3.0",
    "LGPL-3.0-only": "lgpl-3.0",
    "MPL-2.0": "mpl-2.0",
    "CC0-1.0": "cc0-1.0",
    "CC-BY-4.0": "cc-by-4.0",
}

LICENSE_ALIASES = {
    "mit": "MIT",
    "apache": "Apache-2.0",
    "apache-2": "Apache-2.0",
    "apache-2.0": "Apache-2.0",
    "bsd-2": "BSD-2-Clause",
    "bsd-2-clause": "BSD-2-Clause",
    "bsd-3": "BSD-3-Clause",
    "bsd-3-clause": "BSD-3-Clause",
    "isc": "ISC",
    "mpl": "MPL-2.0",
    "mpl-2.0": "MPL-2.0",
    "gpl": "GPL-3.0-only",
    "gpl-3.0": "GPL-3.0-only",
    "gpl-3.0-only": "GPL-3.0-only",
    "agpl": "AGPL-3.0-only",
    "agpl-3.0": "AGPL-3.0-only",
    "agpl-3.0-only": "AGPL-3.0-only",
    "lgpl": "LGPL-3.0-only",
    "lgpl-3.0": "LGPL-3.0-only",
    "lgpl-3.0-only": "LGPL-3.0-only",
    "unlicense": "Unlicense",
    "cc0": "CC0-1.0",
    "cc0-1.0": "CC0-1.0",
    "cc-by": "CC-BY-4.0",
    "cc-by-4.0": "CC-BY-4.0",
    "proprietary": "LicenseRef-Proprietary",
    "licenseref-proprietary": "LicenseRef-Proprietary",
}

INTENT_LICENSE_DEFAULTS = {
    "open source community": "MIT",
    "professional portfolio": "MIT",
    "business / brand": "Apache-2.0",
    "internal to public": "Apache-2.0",
    "academic / research": "BSD-3-Clause",
    "hobby / learning": "MIT",
    "keep forks open": "GPL-3.0-only",
    "saas / server app": "AGPL-3.0-only",
    "library used by proprietary code": "LGPL-3.0-only",
    "balanced copyleft": "MPL-2.0",
    "public domain / no restrictions": "Unlicense",
    "documentation / data": "CC-BY-4.0",
    "source-available commercial": "BSL-1.1",
}

LICENSE_DETECTION_RULES = [
    ("LicenseRef-Proprietary", re.compile(r"proprietary software license|licensed,\s+not\s+sold|all rights reserved", re.I)),
    ("MIT", re.compile(r"\bmit license\b", re.I)),
    ("Apache-2.0", re.compile(r"\bapache license\b.*\bversion 2\.0\b", re.I | re.S)),
    ("BSD-2-Clause", re.compile(r"redistribution and use in source and binary forms", re.I)),
    ("BSD-3-Clause", re.compile(r"neither the name of the copyright holder nor the names of its contributors", re.I)),
    ("ISC", re.compile(r"\bisc license\b", re.I)),
    ("GPL-3.0-only", re.compile(r"gnu general public license.*version 3", re.I | re.S)),
    ("AGPL-3.0-only", re.compile(r"gnu affero general public license.*version 3", re.I | re.S)),
    ("LGPL-3.0-only", re.compile(r"gnu lesser general public license.*version 3", re.I | re.S)),
    ("MPL-2.0", re.compile(r"mozilla public license.*2\.0", re.I | re.S)),
    ("Unlicense", re.compile(r"free and unencumbered software released into the public domain", re.I)),
    ("CC0-1.0", re.compile(r"creative commons zero", re.I)),
    ("CC-BY-4.0", re.compile(r"creative commons attribution 4\.0", re.I)),
]

UPSTREAM_SIGNAL_RE = re.compile(
    r"\b(port of|based on|built on|fork of|powered by|distribution of|wrapper around|extends)\b",
    re.I,
)


def utcnow_iso() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_utc() -> str:
    """Return today's UTC date."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def safe_read_text(path: Path | None) -> str:
    """Read a text file when it exists."""
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def git_config_value(repo_root: Path, key: str) -> str:
    """Return one git config value."""
    result = run_command(["git", "config", "--get", key], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_latest_tag(repo_root: Path) -> str:
    """Return the latest reachable tag if present."""
    result = run_command(["git", "describe", "--tags", "--abbrev=0"], cwd=repo_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_tag_date(repo_root: Path, tag: str) -> str:
    """Return the commit date for one tag."""
    if not tag:
        return ""
    result = run_command(["git", "log", "-1", "--format=%cI", tag], cwd=repo_root, check=False)
    if result.returncode != 0:
        return ""
    raw = result.stdout.strip()
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def normalize_license(value: str) -> str:
    """Normalize a user-provided license token to one SPDX-like identifier."""
    lowered = value.strip().lower()
    if not lowered:
        return ""
    return LICENSE_ALIASES.get(lowered, value.strip())


def find_first_existing(repo_root: Path, candidates: list[str]) -> Path | None:
    """Return the first matching path within the repo."""
    for relative in candidates:
        path = repo_root / relative
        if path.exists():
            return path
    return None


def split_author_name(name: str) -> tuple[str, str]:
    """Split one human name into given/family components."""
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return "", parts[0]
    return " ".join(parts[:-1]), parts[-1]


def project_name(repo_root: Path, metadata: dict[str, Any]) -> str:
    """Return the best display title for the repo."""
    readme_text, _ = load_readme(repo_root)
    for line in readme_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return str(metadata.get("name") or repo_root.name).strip() or repo_root.name


def infer_intent(cached_context: dict[str, Any], repo_type: str) -> str:
    """Return the best-effort intent."""
    intent = str(cached_context.get("intent") or "").strip()
    if intent:
        return intent
    if repo_type in {"Application", "API/Service"}:
        return "Business / Brand"
    if repo_type in {"Library/Package", "CLI Tool", "Skill/Plugin", "Framework"}:
        return "Open Source Community"
    return "Professional Portfolio"


def parse_existing_license(text: str, metadata: dict[str, Any]) -> str:
    """Return the current license identifier when recognizable."""
    if not text.strip():
        spdx = str(((metadata.get("licenseInfo") or {}).get("spdxId")) or "").strip()
        return spdx
    for spdx, pattern in LICENSE_DETECTION_RULES:
        if pattern.search(text):
            return spdx
    spdx = str(((metadata.get("licenseInfo") or {}).get("spdxId")) or "").strip()
    if spdx:
        return spdx
    if re.search(r"business source license", text, re.I):
        return "BSL-1.1"
    return "Custom"


def quality_security(text: str) -> tuple[str, str]:
    """Assess SECURITY.md quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create SECURITY.md with reporting instructions and response timelines."
    if "reporting a vulnerability" in lowered and "response timeline" in lowered:
        return "good", "Keep the current security policy."
    if "security" in lowered and "report" in lowered:
        return "basic", "Expand SECURITY.md with supported versions and response timelines."
    return "poor", "Replace the weak security policy with a clearer vulnerability reporting process."


def quality_citation(text: str) -> tuple[str, str]:
    """Assess CITATION.cff quality."""
    lowered = text.lower()
    if not text.strip():
        return "missing", "Create CITATION.cff."
    required = ("cff-version", "title:", "authors:", "license:")
    if all(token in lowered for token in required):
        return "good", "Keep the current citation file."
    if "cff-version" in lowered:
        return "basic", "Expand CITATION.cff with title, authors, version, and license."
    return "poor", "Replace the invalid citation file with a valid CFF payload."


def quality_notice(text: str) -> tuple[str, str]:
    """Assess NOTICE quality."""
    if not text.strip():
        return "missing", "Create NOTICE when attribution or upstream obligations exist."
    if len(text.splitlines()) >= 3:
        return "good", "Keep the current NOTICE file."
    return "basic", "Expand NOTICE with attribution details."


def detect_upstream_signals(readme_text: str, description: str) -> list[str]:
    """Return upstream/fork-like evidence snippets from README or description."""
    evidence: list[str] = []
    for source in [description, *readme_text.splitlines()]:
        stripped = source.strip()
        lowered = stripped.lower()
        if not stripped:
            continue
        if "based on this" in lowered or "based on your" in lowered or "based on analysis" in lowered:
            continue
        if UPSTREAM_SIGNAL_RE.search(stripped):
            evidence.append(stripped[:200])
    return evidence[:5]


def manifest_summary(repo_root: Path) -> list[dict[str, str]]:
    """Return dependency-manifest presence and any project-level license signals."""
    manifests: list[dict[str, str]] = []
    candidates = [
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "requirements.txt",
        "Gemfile",
        "pom.xml",
        "build.gradle",
        "composer.json",
        "Package.swift",
    ]
    for relative in candidates:
        path = repo_root / relative
        if not path.exists():
            continue
        declared_license = ""
        if relative == "package.json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload.get("license"), str):
                    declared_license = payload["license"].strip()
            except json.JSONDecodeError:
                declared_license = ""
        elif relative == "pyproject.toml":
            try:
                payload = tomllib.loads(path.read_text(encoding="utf-8"))
                project = payload.get("project") or {}
                license_obj = project.get("license")
                if isinstance(license_obj, dict):
                    declared_license = str(license_obj.get("text") or license_obj.get("file") or "").strip()
                elif isinstance(license_obj, str):
                    declared_license = license_obj.strip()
            except tomllib.TOMLDecodeError:
                declared_license = ""
        elif relative == "Cargo.toml":
            try:
                payload = tomllib.loads(path.read_text(encoding="utf-8"))
                package = payload.get("package") or {}
                declared_license = str(package.get("license") or "").strip()
            except tomllib.TOMLDecodeError:
                declared_license = ""
        elif relative == "composer.json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                value = payload.get("license")
                if isinstance(value, str):
                    declared_license = value.strip()
                elif isinstance(value, list):
                    declared_license = ", ".join(str(item).strip() for item in value if str(item).strip())
            except json.JSONDecodeError:
                declared_license = ""
        manifests.append({"path": relative, "declared_license": declared_license})
    return manifests


def detect_vendored_licenses(repo_root: Path) -> list[dict[str, str]]:
    """Return vendored license file signals."""
    findings: list[dict[str, str]] = []
    for relative in ("vendor", "third_party", "third-party", "lib/external"):
        root = repo_root / relative
        if not root.exists():
            continue
        for path in root.rglob("LICENSE*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            findings.append(
                {
                    "path": str(path.relative_to(repo_root)).replace("\\", "/"),
                    "license_type": parse_existing_license(text, {}),
                }
            )
    return findings[:25]


def choose_recommended_license(existing_license: str, intent: str, requested_license: str) -> str:
    """Return the recommended license identifier."""
    if requested_license:
        return requested_license
    if existing_license and existing_license not in {"Custom"}:
        return existing_license
    return INTENT_LICENSE_DEFAULTS.get(intent.lower(), "MIT")


def need_notice(recommended_license: str, notice_exists: bool, upstream_detected: bool) -> bool:
    """Return whether NOTICE should exist."""
    return recommended_license == "Apache-2.0" or notice_exists or upstream_detected


def compatibility_conflicts(project_license: str, vendored: list[dict[str, str]]) -> list[str]:
    """Return obvious vendored-license conflict warnings."""
    conflicts: list[str] = []
    permissive = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "LicenseRef-Proprietary"}
    if project_license not in permissive:
        return conflicts
    for item in vendored:
        vendored_license = item["license_type"]
        if vendored_license in {"GPL-3.0-only", "AGPL-3.0-only", "LGPL-3.0-only"}:
            conflicts.append(
                f"Vendored code at {item['path']} appears to be {vendored_license}; verify compatibility with {project_license}."
            )
    return conflicts


def fetch_remote_license_template(spdx_id: str, year: str, holder: str) -> tuple[str, str]:
    """Fetch a license template body from GitHub's license API when needed."""
    api_key = REMOTE_LICENSE_KEYS.get(spdx_id)
    if not api_key:
        return "", f"No bundled or remote template is available for {spdx_id}."
    url = f"https://api.github.com/licenses/{api_key}"
    request = urllib.request.Request(url, headers={"User-Agent": "legends-github-qa"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return "", f"Could not fetch the {spdx_id} template from GitHub: {exc}"
    body = str(payload.get("body") or "").strip()
    if not body:
        return "", f"GitHub returned an empty template for {spdx_id}."
    replacements = {
        "[year]": year,
        "[yyyy]": year,
        "[fullname]": holder,
        "[name of copyright owner]": holder,
        "<year>": year,
        "<copyright holders>": holder,
    }
    for placeholder, value in replacements.items():
        body = body.replace(placeholder, value)
    return body.strip() + "\n", ""


def render_license_text(spdx_id: str, year: str, holder: str) -> tuple[str, str]:
    """Return one rendered license text plus any blocking reason."""
    if spdx_id in LOCAL_LICENSE_TEMPLATES:
        return LOCAL_LICENSE_TEMPLATES[spdx_id].format(year=year, holder=holder).rstrip() + "\n", ""
    return fetch_remote_license_template(spdx_id, year, holder)


def generate_security(snapshot: dict[str, Any]) -> str:
    """Return deterministic SECURITY.md content."""
    repo = snapshot["repo"]
    advisories_url = f"https://github.com/{repo}/security/advisories/new" if "/" in repo else ""
    contact = snapshot["contact_email"] or "[REPLACE: security-contact@example.com]"
    if advisories_url:
        report_line = (
            f"2. Email `{contact}` or use [GitHub Security Advisories]({advisories_url}) to report privately.\n"
        )
    else:
        report_line = f"2. Email `{contact}` to report privately.\n"
    return (
        "# Security Policy\n\n"
        "## Supported Versions\n\n"
        "| Version | Supported |\n"
        "|---------|-----------|\n"
        "| latest  | yes |\n\n"
        "## Reporting a Vulnerability\n\n"
        f"If you discover a security vulnerability in {snapshot['project_name']}, please report it responsibly:\n\n"
        "1. Do not open a public GitHub issue for security vulnerabilities.\n"
        f"{report_line}"
        "3. Include a description of the issue, affected versions, reproduction steps, and potential impact.\n\n"
        "## Response Timeline\n\n"
        "- Acknowledgment: Within 48 hours\n"
        "- Initial assessment: Within 7 days\n"
        "- Fix or mitigation: Prioritized based on severity\n"
    )


def generate_citation(snapshot: dict[str, Any], license_type: str) -> str:
    """Return deterministic CITATION.cff content."""
    tag = snapshot["latest_tag"].lstrip("v")
    version = tag or "0.1.0"
    released = snapshot["latest_tag_date"] or today_utc()
    given, family = split_author_name(snapshot["author_name"])
    repo_url = f"https://github.com/{snapshot['repo']}" if "/" in snapshot["repo"] else ""
    description = snapshot["description"] or f"Repository for {snapshot['project_name']}."
    lines = [
        "cff-version: 1.2.0",
        'message: "If you use this software, please cite it as below."',
        f'title: "{snapshot["project_name"]}"',
        f'abstract: "{description.replace(chr(34), chr(39))}"',
        "type: software",
        "authors:",
    ]
    if family:
        lines.append(f'  - family-names: "{family}"')
        if given:
            lines.append(f'    given-names: "{given}"')
    else:
        lines.append(f'  - name: "{snapshot["author_name"]}"')
    if repo_url:
        lines.append(f'repository-code: "{repo_url}"')
    lines.extend(
        [
            f'version: "{version}"',
            f'date-released: "{released}"',
            f'license: "{license_type}"',
        ]
    )
    return "\n".join(lines) + "\n"


def generate_notice(snapshot: dict[str, Any]) -> str:
    """Return deterministic NOTICE content."""
    lines = [
        snapshot["project_name"],
        f"Copyright (c) {snapshot['copyright_year']} {snapshot['copyright_holder']}",
    ]
    if snapshot["upstream_detected"]:
        lines.extend(["", "Upstream and attribution notes:"])
        for item in snapshot["upstream_evidence"]:
            lines.append(f"- {item}")
    else:
        lines.extend(["", "This project may include third-party materials. Preserve required notices when redistributing."])
    return "\n".join(lines).rstrip() + "\n"


def current_license_path(repo_root: Path) -> Path | None:
    """Return the existing license file path."""
    return find_first_existing(repo_root, ["LICENSE", "LICENSE.md", "LICENSE.txt"])


def current_security_path(repo_root: Path) -> Path | None:
    """Return the existing security policy path."""
    return find_first_existing(repo_root, ["SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"])


def current_citation_path(repo_root: Path) -> Path | None:
    """Return the existing citation file path."""
    return find_first_existing(repo_root, ["CITATION.cff", ".github/CITATION.cff", "docs/CITATION.cff"])


def current_notice_path(repo_root: Path) -> Path | None:
    """Return the existing notice path."""
    return find_first_existing(repo_root, ["NOTICE", "NOTICE.md", "docs/NOTICE"])


def collect_placeholders(repo_root: Path, targets: list[str]) -> list[dict[str, Any]]:
    """Collect placeholder markers from written files."""
    pattern = re.compile(r"\[REPLACE:[^\]]+\]")
    placeholders: list[dict[str, Any]] = []
    for relative in targets:
        path = repo_root / relative
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for match in pattern.finditer(line):
                placeholders.append(
                    {
                        "file": relative.replace("\\", "/"),
                        "line": line_no,
                        "placeholder": match.group(0),
                        "description": "Replace the placeholder with repo-specific legal contact information.",
                    }
                )
    return placeholders


def build_snapshot(repo_root: Path, requested_license: str) -> dict[str, Any]:
    """Collect repo signals for legal planning."""
    cached_context = read_repo_cache(repo_root, "repo-context.json") or {}
    repo_slug = str(cached_context.get("repo") or repo_slug_from_git(repo_root) or repo_root.name)
    metadata = gh_repo_view(repo_slug) if "/" in repo_slug else {}
    if metadata is None:
        metadata = {}
    repo_type = str(cached_context.get("repo_type") or detect_repo_type(repo_root))
    intent = infer_intent(cached_context, repo_type)
    description = str(metadata.get("description") or cached_context.get("description") or "").strip()
    readme_text, _ = load_readme(repo_root)
    license_path = current_license_path(repo_root)
    security_path = current_security_path(repo_root)
    citation_path = current_citation_path(repo_root)
    notice_path = current_notice_path(repo_root)
    license_text = safe_read_text(license_path)
    security_text = safe_read_text(security_path)
    citation_text = safe_read_text(citation_path)
    notice_text = safe_read_text(notice_path)
    existing_license = parse_existing_license(license_text, metadata)
    upstream_evidence = detect_upstream_signals(readme_text, description)
    is_fork = bool(metadata.get("isFork") or cached_context.get("is_fork"))
    upstream_detected = is_fork or bool(upstream_evidence)
    author_name = (
        git_config_value(repo_root, "user.name")
        or str(cached_context.get("owner") or "").strip()
        or repo_slug.split("/", 1)[0]
        or "Project Maintainer"
    )
    email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", security_text, re.I)
    contact_email = email_match.group(0) if email_match else git_config_value(repo_root, "user.email")
    latest_tag = git_latest_tag(repo_root)
    snapshot = {
        "repo": repo_slug,
        "repo_root": str(repo_root),
        "repo_type": repo_type,
        "intent": intent,
        "project_name": project_name(repo_root, metadata),
        "description": description,
        "requested_license": requested_license,
        "license_path": str(license_path.relative_to(repo_root)).replace("\\", "/") if license_path else None,
        "security_path": str(security_path.relative_to(repo_root)).replace("\\", "/") if security_path else None,
        "citation_path": str(citation_path.relative_to(repo_root)).replace("\\", "/") if citation_path else None,
        "notice_path": str(notice_path.relative_to(repo_root)).replace("\\", "/") if notice_path else None,
        "license_text": license_text,
        "security_text": security_text,
        "citation_text": citation_text,
        "notice_text": notice_text,
        "existing_license": existing_license,
        "recommended_license": choose_recommended_license(existing_license, intent, requested_license),
        "security_quality": quality_security(security_text),
        "citation_quality": quality_citation(citation_text),
        "notice_quality": quality_notice(notice_text),
        "manifest_summary": manifest_summary(repo_root),
        "vendored_licenses": detect_vendored_licenses(repo_root),
        "is_fork": is_fork,
        "upstream_detected": upstream_detected,
        "upstream_evidence": upstream_evidence,
        "fork_compliant": None,
        "author_name": author_name,
        "contact_email": contact_email,
        "latest_tag": latest_tag,
        "latest_tag_date": git_tag_date(repo_root, latest_tag),
        "copyright_year": str(datetime.now(timezone.utc).year),
        "copyright_holder": author_name,
        "warnings": [],
    }
    if "/" not in repo_slug:
        snapshot["warnings"].append("No GitHub remote detected. Legal planning is using local files only.")
    if not snapshot["contact_email"]:
        snapshot["warnings"].append("No maintainer email was detected. SECURITY.md will include a placeholder contact.")
    if not snapshot["manifest_summary"]:
        snapshot["warnings"].append("No dependency manifest was found. License compatibility checks are limited.")
    return snapshot


def planned_writes(snapshot: dict[str, Any]) -> tuple[list[dict[str, str]], list[str], list[str], list[str], list[str]]:
    """Return planned writes plus warnings, blocked items, and edge-case flags."""
    writes: list[dict[str, str]] = []
    warnings = list(snapshot["warnings"])
    blocked: list[str] = []
    edge_case_flags: list[str] = []

    if snapshot["existing_license"] == "Custom" and not snapshot["requested_license"]:
        warnings.append("A custom existing license was detected. The deterministic runner will preserve it unless you pass --license explicitly.")

    if snapshot["requested_license"] == "BSL-1.1" or snapshot["recommended_license"] == "BSL-1.1":
        blocked.append("BSL-1.1 is not generated automatically. Review and add that license text manually.")

    if not snapshot["license_path"]:
        writes.append({"path": LICENSE_FILE, "reason": f"Create LICENSE using {snapshot['recommended_license']}."})
    elif snapshot["requested_license"] and snapshot["requested_license"] != snapshot["existing_license"]:
        writes.append({"path": LICENSE_FILE, "reason": f"Replace LICENSE with the requested {snapshot['requested_license']} text."})

    security_quality, security_action = snapshot["security_quality"]
    if security_quality in {"missing", "poor", "basic"}:
        writes.append({"path": SECURITY_FILE, "reason": security_action})

    citation_quality, citation_action = snapshot["citation_quality"]
    if citation_quality in {"missing", "poor", "basic"}:
        writes.append({"path": CITATION_FILE, "reason": citation_action})

    notice_required = need_notice(snapshot["recommended_license"], bool(snapshot["notice_path"]), snapshot["upstream_detected"])
    if notice_required and snapshot["notice_quality"][0] in {"missing", "basic", "poor"}:
        writes.append({"path": NOTICE_FILE, "reason": snapshot["notice_quality"][1]})

    if snapshot["upstream_detected"]:
        acknowledged = bool(snapshot["notice_text"].strip()) or "licensed under" in snapshot["license_text"].lower()
        snapshot["fork_compliant"] = acknowledged
        if not acknowledged:
            blocked.append("Upstream or fork-like signals were detected, but no attribution notice is present.")

    if snapshot["requested_license"] in {"GPL-3.0-only", "AGPL-3.0-only", "LGPL-3.0-only", "MPL-2.0", "CC0-1.0", "CC-BY-4.0"}:
        warnings.append(f"{snapshot['requested_license']} generation may require a network fetch from GitHub's license API.")

    if snapshot["requested_license"] == "LicenseRef-Proprietary":
        edge_case_flags.append("Custom or proprietary licensing should still receive human review before distribution.")

    if snapshot["upstream_detected"] and snapshot["recommended_license"] == "LicenseRef-Proprietary":
        edge_case_flags.append("Upstream-derived proprietary distributions may carry separate trademark or redistribution constraints.")

    return writes, warnings, blocked, edge_case_flags, compatibility_conflicts(snapshot["recommended_license"], snapshot["vendored_licenses"])


def build_legal_payload(repo_root: Path, requested_license: str = "") -> dict[str, Any]:
    """Build deterministic legal recommendations."""
    requested = normalize_license(requested_license)
    snapshot = build_snapshot(repo_root, requested)
    writes, warnings, blocked, edge_case_flags, dependency_conflicts = planned_writes(snapshot)
    status = "PASS"
    if blocked or dependency_conflicts:
        status = "FAIL"
    elif edge_case_flags:
        status = "REVIEW"
    return {
        "cache_type": "legal-data",
        "timestamp": utcnow_iso(),
        "analyzed_at": utcnow_iso(),
        "mode": "plan",
        "repo": snapshot["repo"],
        "repo_root": str(repo_root),
        "repo_type": snapshot["repo_type"],
        "intent": snapshot["intent"],
        "disclaimer": DISCLAIMER_BLOCK.strip(),
        "compliance_status": status,
        "requested_license": requested,
        "license_type": snapshot["existing_license"] if snapshot["existing_license"] != "Custom" else "Custom",
        "recommended_license_type": snapshot["recommended_license"],
        "license_file_exists": bool(snapshot["license_path"]),
        "license_file_path": snapshot["license_path"],
        "security_md_exists": bool(snapshot["security_path"]),
        "security_md_path": snapshot["security_path"],
        "citation_cff_exists": bool(snapshot["citation_path"]),
        "citation_cff_path": snapshot["citation_path"],
        "notice_file_exists": bool(snapshot["notice_path"]),
        "notice_file_path": snapshot["notice_path"],
        "is_fork": snapshot["is_fork"],
        "upstream_detected": snapshot["upstream_detected"],
        "upstream_evidence": snapshot["upstream_evidence"],
        "fork_compliant": snapshot["fork_compliant"],
        "dependency_manifests": snapshot["manifest_summary"],
        "vendored_licenses": snapshot["vendored_licenses"],
        "dependency_conflicts": dependency_conflicts,
        "planned_writes": writes,
        "files_created": [],
        "files_updated": [],
        "placeholders": [],
        "edge_case_flags": edge_case_flags,
        "warnings": warnings,
        "blocked": blocked,
    }


def generated_content(snapshot: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    """Return canonical file contents plus blocking reasons for files we cannot render."""
    content: dict[str, str] = {}
    blocked = list(payload["blocked"])
    license_target = payload["requested_license"] or payload["recommended_license_type"]
    if any(item["path"] == LICENSE_FILE for item in payload["planned_writes"]):
        license_text, error = render_license_text(license_target, snapshot["copyright_year"], snapshot["copyright_holder"])
        if error:
            blocked.append(error)
        else:
            content[LICENSE_FILE] = license_text
    if any(item["path"] == SECURITY_FILE for item in payload["planned_writes"]):
        content[SECURITY_FILE] = generate_security(snapshot)
    if any(item["path"] == CITATION_FILE for item in payload["planned_writes"]):
        content[CITATION_FILE] = generate_citation(snapshot, license_target or payload["license_type"] or "MIT")
    if any(item["path"] == NOTICE_FILE for item in payload["planned_writes"]):
        content[NOTICE_FILE] = generate_notice(snapshot)
    return content, blocked


def write_if_changed(path: Path, content: str) -> bool:
    """Write a file when content changes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = safe_read_text(path)
    if existing == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def apply_legal_plan(repo_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Write planned legal files."""
    snapshot = build_snapshot(repo_root, payload["requested_license"])
    content, blocked = generated_content(snapshot, payload)
    if blocked != payload["blocked"]:
        payload["blocked"] = blocked
        payload["compliance_status"] = "FAIL"
    created: list[str] = []
    updated: list[str] = []
    written_targets: list[str] = []
    if payload["blocked"]:
        payload["mode"] = "write"
        payload["files_created"] = created
        payload["files_updated"] = updated
        payload["planned_writes"] = [item for item in payload["planned_writes"] if item["path"] not in content]
        return payload

    for entry in payload["planned_writes"]:
        relative = entry["path"]
        body = content.get(relative)
        if body is None:
            continue
        path = repo_root / relative
        existed = path.exists()
        changed = write_if_changed(path, body)
        if not changed:
            continue
        written_targets.append(relative)
        if existed:
            updated.append(relative)
        else:
            created.append(relative)

    refreshed = build_legal_payload(repo_root, payload["requested_license"])
    refreshed["mode"] = "write"
    refreshed["files_created"] = created
    refreshed["files_updated"] = updated
    refreshed["planned_writes"] = []
    refreshed["placeholders"] = collect_placeholders(repo_root, written_targets)
    return refreshed


def build_legal_report(payload: dict[str, Any]) -> str:
    """Render a markdown legal report."""
    planned = "\n".join(f"- `{item['path']}`: {item['reason']}" for item in payload["planned_writes"]) or "- None"
    created = "\n".join(f"- `{item}`" for item in payload["files_created"]) or "- None"
    updated = "\n".join(f"- `{item}`" for item in payload["files_updated"]) or "- None"
    conflicts = "\n".join(f"- {item}" for item in payload["dependency_conflicts"]) or "- None"
    warnings = "\n".join(f"- {item}" for item in payload["warnings"]) or "- None"
    blocked = "\n".join(f"- {item}" for item in payload["blocked"]) or "- None"
    edge_cases = "\n".join(f"- {item}" for item in payload["edge_case_flags"]) or "- None"
    placeholders = "\n".join(
        f"- {item['file']} line {item['line']}: `{item['placeholder']}`" for item in payload["placeholders"]
    ) or "- None"
    upstream = "\n".join(f"- {item}" for item in payload["upstream_evidence"]) or "- None"
    manifest_rows = "\n".join(
        f"| {item['path']} | {item['declared_license'] or 'unknown'} |" for item in payload["dependency_manifests"]
    ) or "| None | -- |"
    return f"""# GitHub Legal Report

{DISCLAIMER_BLOCK}

- **Repository:** {payload['repo']}
- **Generated at:** {payload['timestamp']}
- **Mode:** {payload['mode']}
- **Compliance status:** {payload['compliance_status']}
- **Current license:** {payload['license_type'] or 'None'}
- **Recommended license:** {payload['recommended_license_type']}

## File Status

| File | Exists? | Path |
|------|---------|------|
| LICENSE | {'Yes' if payload['license_file_exists'] else 'No'} | {payload['license_file_path'] or '--'} |
| SECURITY.md | {'Yes' if payload['security_md_exists'] else 'No'} | {payload['security_md_path'] or '--'} |
| CITATION.cff | {'Yes' if payload['citation_cff_exists'] else 'No'} | {payload['citation_cff_path'] or '--'} |
| NOTICE | {'Yes' if payload['notice_file_exists'] else 'No'} | {payload['notice_file_path'] or '--'} |

## Planned Writes

{planned}

## Files Created

{created}

## Files Updated

{updated}

## Dependency Manifest Scan

| Manifest | Declared License |
|----------|------------------|
{manifest_rows}

## Dependency Conflicts

{conflicts}

## Upstream Signals

{upstream}

## Edge Cases

{edge_cases}

## Placeholders

{placeholders}

## Warnings

{warnings}

## Blocked / Manual Review

{blocked}
"""


@dataclass
class LegalBundle:
    """Structured legal output."""

    legal_data: dict[str, Any]
    report_markdown: str


def run_legal(repo_root: Path, write_files: bool = False, license_id: str = "") -> LegalBundle:
    """Build or apply deterministic legal work."""
    legal_data = build_legal_payload(repo_root, license_id)
    if write_files:
        legal_data = apply_legal_plan(repo_root, legal_data)
    report_markdown = build_legal_report(legal_data)
    return LegalBundle(legal_data=legal_data, report_markdown=report_markdown)


def write_legal_artifacts(repo_root: Path, bundle: LegalBundle) -> dict[str, str]:
    """Write legal cache and report artifacts."""
    slug = slugify(bundle.legal_data["repo"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = repo_output_dir(repo_root) / f"{slug}-{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cache_path = write_repo_cache(repo_root, "legal-data.json", bundle.legal_data)
    report_path = out_dir / "LEGAL-REPORT.md"
    report_path.write_text(bundle.report_markdown, encoding="utf-8")
    plan_path = out_dir / "LEGAL-PLAN.md"
    planned = bundle.legal_data["planned_writes"] or [
        {"path": path, "reason": "written"} for path in (bundle.legal_data["files_created"] + bundle.legal_data["files_updated"])
    ]
    plan_path.write_text(
        DISCLAIMER_BLOCK
        + "\n# GitHub Legal Plan\n\n"
        + ("\n".join(f"- `{item['path']}`: {item['reason']}" for item in planned) or "- No planned writes."),
        encoding="utf-8",
    )
    summary_path = out_dir / "LEGAL-SUMMARY.json"
    summary_path.write_text(
        json.dumps(
            {
                "legal_cache_path": str(cache_path),
                "mode": bundle.legal_data["mode"],
                "compliance_status": bundle.legal_data["compliance_status"],
                "license_type": bundle.legal_data["license_type"],
                "recommended_license_type": bundle.legal_data["recommended_license_type"],
                "files_created": bundle.legal_data["files_created"],
                "files_updated": bundle.legal_data["files_updated"],
                "dependency_conflict_count": len(bundle.legal_data["dependency_conflicts"]),
                "blocked_count": len(bundle.legal_data["blocked"]),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "output_dir": str(out_dir),
        "legal_cache": str(cache_path),
        "report": str(report_path),
        "plan": str(plan_path),
        "summary_json": str(summary_path),
    }
