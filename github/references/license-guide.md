<!-- Updated: 2026-03-08 -->
# License Guide — Types, Compatibility, and Fork Obligations

## Overview

Choosing the right license is a legal and strategic decision. The license affects adoption,
contribution, and fork compliance. GitHub auto-detects SPDX-compliant license files.

## License Types

### Permissive Licenses (recommended for maximum adoption)

| License | SPDX ID | Key Terms | Best For |
|---------|---------|-----------|----------|
| MIT | MIT | Do anything, keep copyright notice | Libraries, tools, most projects |
| Apache 2.0 | Apache-2.0 | Like MIT + patent grant + NOTICE file | Enterprise, patent-sensitive projects |
| BSD 2-Clause | BSD-2-Clause | Like MIT, simpler | Minimal legal overhead |
| BSD 3-Clause | BSD-3-Clause | BSD-2 + no endorsement clause | Academic projects |
| ISC | ISC | Functionally identical to MIT | Minimal, npm default |
| Unlicense | Unlicense | Public domain dedication | Maximum freedom, no attribution required |

### Copyleft Licenses (require derivative works to use same license)

| License | SPDX ID | Key Terms | Best For |
|---------|---------|-----------|----------|
| GPL v3 | GPL-3.0-only | Derivatives must be GPL, patent grant | Ensuring all forks stay open |
| GPL v2 | GPL-2.0-only | Derivatives must be GPL, no patent grant | Legacy compatibility (Linux kernel) |
| LGPL v3 | LGPL-3.0-only | Linking exception for libraries | Libraries used by proprietary software |
| AGPL v3 | AGPL-3.0-only | GPL + network use triggers copyleft | SaaS/server-side software |
| MPL 2.0 | MPL-2.0 | File-level copyleft (weaker than GPL) | Balance between permissive and copyleft |

### Other

| License | SPDX ID | Key Terms | Best For |
|---------|---------|-----------|----------|
| CC0 1.0 | CC0-1.0 | Public domain (no copyright) | Data, documentation |
| CC BY 4.0 | CC-BY-4.0 | Attribution required | Documentation, creative content |
| BSL 1.1 | BSL-1.1 | Source-available, converts to open after delay | Commercial projects with delayed open source |

## License Compatibility Matrix

When your project depends on other projects, licenses must be compatible:

| Your License | Can use MIT? | Can use Apache? | Can use GPL v3? | Can use AGPL? |
|-------------|-------------|----------------|----------------|---------------|
| MIT | Yes | Yes | No (output must be GPL) | No |
| Apache 2.0 | Yes | Yes | No (output must be GPL) | No |
| GPL v3 | Yes | Yes | Yes | No |
| AGPL v3 | Yes | Yes | Yes | Yes |
| MPL 2.0 | Yes | Yes | Yes (larger work) | No |

**Rule of thumb:** Permissive licenses are compatible with everything. Copyleft licenses
are only compatible with the same or stronger copyleft.

## Fork Compliance

When forking a project, you MUST:

1. **Keep the original license** — You cannot relicense unless the original allows it
2. **Preserve copyright notices** — Original author's copyright stays in LICENSE and file headers
3. **Maintain NOTICE file** — If Apache 2.0, copy and preserve the NOTICE file
4. **Add your own copyright** — Add your copyright line below the original
5. **Document changes** — Some licenses (Apache, GPL) require documenting modifications

### Fork License File Template

```
[Original license text]

Copyright (c) [original year] [original author]
Copyright (c) [your year] [your name] (modifications)
```

### What You Can Change in a Fork

| License | Can relicense? | Can make proprietary? | Must share source? |
|---------|---------------|----------------------|-------------------|
| MIT | Yes (permissive) | Yes | No |
| Apache 2.0 | Yes (permissive) | Yes | No |
| GPL v3 | No (must stay GPL) | No | Yes |
| AGPL v3 | No (must stay AGPL) | No | Yes (including network use) |
| MPL 2.0 | Modified files stay MPL | New files can be proprietary | Modified files only |

## Upstream Project Detection (Non-Fork Dependencies)

Not all derivative works are GitHub "forks." Many projects are built on top of, wrap,
or distribute another project without using the Fork button. These still have license
obligations.

### Signals That Indicate an Upstream Project
- README says "powered by," "built on," "based on," "fork of," "distribution of"
- Config files for another tool (e.g., wezterm.lua, .eslintrc, vimrc)
- Package manifests listing a single core dependency that IS the project
- Description mentions another project by name as the foundation
- Source code is a modified copy of another project's codebase

### Upstream License Obligations
When an upstream project is detected, the same rules as fork compliance apply:
- You must comply with the upstream license terms
- You cannot choose a license incompatible with upstream
- Attribution and copyright preservation requirements still apply
- NOTICE files (Apache 2.0) must be preserved

## SPDX License Identifiers

GitHub recognizes SPDX identifiers in the LICENSE file. Use the exact SPDX ID for
automatic detection. Full list: https://spdx.org/licenses/

Common SPDX IDs GitHub auto-detects:
MIT, Apache-2.0, GPL-2.0-only, GPL-3.0-only, AGPL-3.0-only, LGPL-3.0-only,
MPL-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense, CC0-1.0, CC-BY-4.0, BSL-1.1,
0BSD, Artistic-2.0, Zlib, PostgreSQL, WTFPL, ECL-2.0

## Intent-Based Recommendations

| Intent | Recommended License | Why |
|--------|-------------------|-----|
| Open Source Community | MIT or Apache 2.0 | Maximum adoption, minimal friction |
| Professional Portfolio | MIT | Simple, universally understood |
| Business / Brand | Apache 2.0 | Patent protection for enterprise users |
| Internal to Public | Apache 2.0 | Patent grant protects company and users |
| Academic / Research | MIT or BSD-3-Clause | Academic tradition, simple attribution |
| Hobby / Learning | MIT | Simplest option, no complications |
| Ensure forks stay open | GPL v3 or AGPL v3 | Copyleft ensures derivatives are open |
| SaaS / Server app | AGPL v3 | Network use triggers copyleft |
| Library for proprietary use | LGPL v3 | Linking exception for proprietary apps |
| Balanced copyleft | MPL 2.0 | File-level copyleft, new files can be anything |
| Public domain | Unlicense or CC0 | Zero restrictions |
| Documentation / data | CC BY 4.0 or CC0 | Creative Commons for non-code |
| Source-available commercial | BSL 1.1 | Visible but restricted; converts to open later |

## Edge Cases — Flag for Human Review

These situations are too nuanced for automated analysis:
- **Dual licensing** (e.g., MIT OR Apache-2.0) — valid but users must understand implications
- **CLA requirements** — some upstream projects require contributor agreements
- **Trademark usage** — using a project's name in your project name (e.g., "XTerm" in name)
- **Patent implications** — especially with Apache 2.0 patent grant clauses
- **AGPL network boundary** — what counts as "network interaction" is debated
- **GPL linking** — what constitutes "linking" vs "mere aggregation" is legally gray
- **Mixed-license repos** — different licenses for different directories
- **License header requirements** — GPL/Apache may require headers in every source file
