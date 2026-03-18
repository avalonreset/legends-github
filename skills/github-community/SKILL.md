---
name: github-community
description: >
  Set up GitHub community health files and templates. Generates CONTRIBUTING.md,
  CODE_OF_CONDUCT.md, SUPPORT.md, CODEOWNERS, issue templates (YAML forms),
  PR templates, discussion templates, devcontainer configuration, dependabot.yml,
  release.yml, .gitattributes (linguist overrides for accurate language bar),
  and CI workflows (language-appropriate linting via GitHub Actions). Completes
  GitHub's Community Standards checklist. Use when user says "community",
  "github community", "contributing", "code of conduct", "issue template",
  "pr template", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "codeowners",
  "devcontainer", "dependabot", "community standards", "community health",
  "templates", "gitattributes", "ci workflow", or "github actions".
---

# GitHub Community -- Health Files and Templates

## Process (GARE Pattern)

### 1. Gather

**Step 0 -- Check shared data cache:**
Before gathering, check `.github-audit/` for cached data from other skills.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for schemas.

- `repo-context.json` (optional) -- repo type, intent, language, has_discussions.
  If missing, gather yourself via `gh repo view`.
- `legal-data.json` (optional) -- SECURITY.md status. If present, use
  `security_md_exists` to know whether to note "SECURITY.md: already exists" or
  "SECURITY.md: not found -- run `/github legal` to generate." If missing, check
  SECURITY.md existence yourself.

- Check which community files already exist:
  - README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, SUPPORT.md
  - CODEOWNERS, .github/FUNDING.yml
  - .github/ISSUE_TEMPLATE/ (any .yml or .md files)
  - .github/PULL_REQUEST_TEMPLATE.md
  - .github/DISCUSSION_TEMPLATE/
  - .gitattributes
  - .github/workflows/ (any .yml files -- for CI detection)
  - .devcontainer/devcontainer.json
  - .github/dependabot.yml
  - .github/release.yml
- **Case and format fallbacks (important):**
  - PR template: check BOTH `.github/PULL_REQUEST_TEMPLATE.md` (uppercase) AND
    `.github/pull_request_template.md` (lowercase). GitHub accepts either.
  - Community files: check `.rst` fallback for CONTRIBUTING, CODE_OF_CONDUCT,
    SECURITY, SUPPORT (e.g., `CONTRIBUTING.rst`). Some projects (especially
    Python/Sphinx-based) use reStructuredText instead of Markdown.
  - Best approach: list `.github/` directory contents first, then check root files.
    The directory listing catches case variants and unexpected filenames.
- **Org-level `.github` repo:** If the repo belongs to an organization, check
  `{org}/.github` for inherited community health files. GitHub automatically
  inherits CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, SUPPORT, FUNDING.yml from
  the org's `.github` repo. Use: `gh api repos/{org}/.github/contents --jq '.[].name'`
  If inherited files exist, note them as "inherited from org" -- do NOT regenerate them.
- Check GitHub Community Standards: `https://github.com/{owner}/{repo}/community`
- Check if Discussions is enabled: `gh repo view {owner}/{repo} --json hasDiscussionsEnabled`
  - If Discussions is NOT enabled, do NOT link to Discussions in config.yml -- use
    Issues link instead, or omit the contact_links section
- Detect repo type and primary language (for devcontainer and dependabot config)
- Get user intent from orchestrator context

### 2. Analyze

Reference: Read `~/.claude/skills/github/references/community-files-guide.md` for file specs and priorities.
Reference: Read `~/.claude/skills/github/references/community-templates.md` for YAML templates and code.

**Branding consistency check:** For every existing file, verify it references the
correct project name. Forks, ports, and copied templates often contain the upstream
or source project's name (e.g., "codex-seo" in a gemini-seo repo, "wezterm" in a
BenjaminTerm repo). Flag any file where the project name, repo URL, or owner doesn't
match the current repo. These need updating even if the file is otherwise good quality.

Fill in this table for every file. **For files that exist, read their content
and assess quality** -- don't just check existence.

| File | Exists? | Quality | Action Needed |
|------|---------|---------|---------------|
| CONTRIBUTING.md | ? | ? | ? |
| CODE_OF_CONDUCT.md | ? | ? | ? |
| SECURITY.md | ? | ? | ? -- **Handled by /github legal** (note: do NOT generate here, just check existence) |
| SUPPORT.md | ? | ? | ? |
| CODEOWNERS | ? | ? | ? |
| FUNDING.yml | ? | ? | ? |
| Issue templates | ? | ? | ? |
| PR template | ? | ? | ? |
| Discussion templates | ? | ? | ? |
| .gitattributes | ? | ? | ? |
| devcontainer.json | ? | ? | ? |
| dependabot.yml | ? | ? | ? |
| release.yml | ? | ? | ? |

#### Quality Assessment Criteria (for existing files)

When a file exists, fetch its content and evaluate:

**Issue Templates:**
| Quality | Criteria |
|---------|----------|
| Good | YAML forms (`.yml`) with required fields, dropdowns, and validation |
| Outdated | Markdown templates (`.md`) with HTML comment prompts -- no structured input |
| Poor | Template exists but is mostly empty or uses default GitHub boilerplate |
Action: if Outdated, recommend upgrading `.md` to `.yml` YAML forms.

**PR Template:**
| Quality | Criteria |
|---------|----------|
| Good | Visible checklists, change type section, testing section |
| Decent | Has structure but uses HTML comments as prompts (invisible when filling in) |
| Poor | Template is empty, too long (>50 lines), or just a single comment block |
Action: if Decent, suggest converting HTML comments to visible markdown sections.

**CONTRIBUTING.md:**
| Quality | Criteria |
|---------|----------|
| Good | Dev setup, PR workflow, code style, links to CoC and templates |
| Basic | Exists but missing dev setup or code style guidance |
| Poor | Just says "PRs welcome" or is a single paragraph |
Action: if Basic/Poor, offer to enhance with missing sections.

**devcontainer.json:**
| Quality | Criteria |
|---------|----------|
| Good | Correct base image for language, postCreateCommand set, VS Code extensions |
| Basic | Has image but no setup command or extensions |
Action: if Basic, offer to add postCreateCommand and extensions.

**config.yml (issue template chooser):**
| Quality | Criteria |
|---------|----------|
| Good | Blank issues disabled, links to Discussions/support channels |
| Basic | Exists but blank issues still enabled |
Action: if Basic, recommend disabling blank issues and adding contact links.

### 3. Recommend

Prioritize based on intent:

| Intent | Must-Have Files | Nice-to-Have |
|--------|----------------|-------------|
| Open Source Community | ALL files | Full template suite, devcontainer |
| Professional Portfolio | LICENSE, README, basic templates | CONTRIBUTING if accepting PRs |
| Business / Brand | SECURITY.md, CONTRIBUTING, templates | FUNDING.yml |
| Internal to Public | SECURITY.md, CONTRIBUTING, CoC | devcontainer, CODEOWNERS |
| Academic / Research | LICENSE, CONTRIBUTING | CITATION.cff (handled by legal) |
| Hobby / Learning | LICENSE, README | Basic issue template |

### 4. Execute (with user approval)

Generate all missing files. For each file:
- Use templates from community-files-guide.md reference
- Adapt to repo type (devcontainer image, dependabot ecosystem)
- Adapt to intent (level of formality, depth of contributing guide)

**FUNDING.yml -- always generate if missing.** It costs nothing and enables the
"Sponsor" button on the repo page. Detect the GitHub username from the repo owner
and pre-fill it. If the user doesn't have GitHub Sponsors set up, comment out that
line and leave the file as a ready-to-activate template.

```yaml
# .github/FUNDING.yml
# Uncomment the platforms you use:
github: [OWNER_USERNAME]
# patreon: # Replace with your Patreon username
# open_collective: # Replace with your Open Collective username
# ko_fi: # Replace with your Ko-fi username
# custom: ["https://example.com/donate"]
```

Replace `[OWNER_USERNAME]` with the actual repo owner's GitHub username. If you can
confirm they have GitHub Sponsors enabled (`gh api users/{owner} --jq .is_sponsor`),
uncomment the `github:` line. If not, leave it commented with a note.

**Placeholder rule:** Some files require user-specific information that cannot be
guessed. Use clearly marked placeholders so the user knows what to fill in:

| Field | Placeholder | Where Used |
|-------|------------|------------|
| Enforcement email | `[REPLACE: your-email@example.com]` | CODE_OF_CONDUCT.md |
| Funding username | `[REPLACE: your-github-username]` | FUNDING.yml |
| CODEOWNERS paths | `[REPLACE: @your-team]` | CODEOWNERS (if org repo) |

After generating all files, include a **"Placeholders to Fill In"** section listing
every placeholder that needs user action. Do not guess emails or usernames.

## File Generation Details

### CONTRIBUTING.md
- Adapt fork/PR workflow to repo's branching strategy
- Include development setup based on detected language/framework
- Reference code style tools already in the project (eslint, black, rustfmt)
- Link to issue templates and CoC

### CODE_OF_CONDUCT.md
- **IMPORTANT: Do NOT write the Contributor Covenant text inline.** The full text
  triggers content filters and causes API errors. Instead, fetch it from GitHub's
  built-in API and write the file via Bash:
  ```bash
  gh api codes_of_conduct/contributor_covenant --jq '.body' \
    | sed 's/\[INSERT CONTACT METHOD\]/CONTACT_EMAIL/g' \
    > CODE_OF_CONDUCT.md
  ```
  Replace `CONTACT_EMAIL` with the user's enforcement email. If unknown, use
  the email from the LICENSE file, git config, or ask the user.
- This produces the standard Contributor Covenant v2.1 (most widely adopted)
- Verify the file was written: `wc -l CODE_OF_CONDUCT.md` (should be ~128 lines)
- Verify contact was substituted: `grep -c 'INSERT CONTACT' CODE_OF_CONDUCT.md`
  (should return 0)

### Issue Templates (YAML Forms)
Generate at minimum:
1. Bug Report (`bug_report.yml`)
2. Feature Request (`feature_request.yml`)
3. Config file (`config.yml`) -- disable blank issues, link to Discussions

Adapt fields to repo type:
- CLI tools: add "Command used" field
- Libraries: add "Version" and "Environment" fields
- Applications: add "Browser/OS" fields

### PR Template
- Include change type checklist (bug fix, feature, breaking, docs)
- Include testing checklist
- Keep concise -- long templates discourage contributions

### devcontainer.json
Select base image by language:
| Language | Image |
|----------|-------|
| JavaScript/TypeScript | `mcr.microsoft.com/devcontainers/javascript-node` |
| Python | `mcr.microsoft.com/devcontainers/python` |
| Rust | `mcr.microsoft.com/devcontainers/rust` |
| Go | `mcr.microsoft.com/devcontainers/go` |
| Java | `mcr.microsoft.com/devcontainers/java` |
| Default | `mcr.microsoft.com/devcontainers/base:ubuntu` |

Set `postCreateCommand` to the project's install command.

### dependabot.yml
Detect package ecosystem from repo:
| File | Ecosystem |
|------|-----------|
| package.json | npm |
| requirements.txt / setup.py | pip |
| Cargo.toml | cargo |
| go.mod | gomod |
| pom.xml | maven |
| build.gradle | gradle |
| Gemfile | bundler |
| .github/workflows/*.yml | github-actions |

### .gitattributes (Language Bar Accuracy)

**Always generate .gitattributes** if one does not already exist. The language bar on
GitHub's repo page is controlled by Linguist, and incorrect detection makes projects
look unprofessional (e.g., a markdown-heavy skill project showing as "Shell 60%"
because of install scripts).

**Detection logic:**
1. Check the language breakdown: `gh api repos/{owner}/{repo}/languages`
2. Compare against the repo's actual purpose (from repo-context or README)
3. If the primary language shown does not match the project's core language, generate
   overrides

**Common patterns by repo type:**

| Repo Type | Problem | .gitattributes Fix |
|-----------|---------|-------------------|
| Skill/Plugin (markdown-heavy) | Shell/PowerShell inflated by install scripts | `*.sh linguist-documentation`<br>`*.ps1 linguist-documentation`<br>`install.* linguist-documentation` |
| JavaScript/TypeScript | HTML/CSS from dist/ or docs/ | `dist/** linguist-generated`<br>`docs/** linguist-documentation` |
| Python | Jupyter notebooks inflating JSON | `*.ipynb linguist-generated` |
| Any | Vendored dependencies | `vendor/** linguist-vendored`<br>`third_party/** linguist-vendored` |
| Any | Generated files | `*.min.js linguist-generated`<br>`*.min.css linguist-generated` |

**Template (adapt based on detection):**
```
# .gitattributes - GitHub Linguist overrides for accurate language detection

# Generated/vendored files (excluded from language stats)
*.min.js linguist-generated
*.min.css linguist-generated
dist/** linguist-generated
vendor/** linguist-vendored
third_party/** linguist-vendored

# Documentation/config files (excluded from language stats)
# [Add repo-specific overrides here based on detection]
```

**Critical: verify the language bar won't go blank.** After writing exclusion rules
(linguist-documentation, linguist-generated, linguist-vendored), check whether any
recognized language remains. If excluding Shell/PowerShell/etc. leaves NO detectable
source language, you MUST add an explicit language override for the project's actual
content type. Common fallbacks:

| Repo Type | Override |
|-----------|---------|
| Markdown-heavy (skills, docs) | `*.md linguist-detectable` |
| Config-heavy (YAML/JSON) | `*.yml linguist-detectable` |
| Mixed with no clear primary | `*.md linguist-language=Markdown` |

An empty language bar looks worse than an inaccurate one. Always leave something visible.

If the language bar is already accurate and no overrides are needed, still generate
a minimal .gitattributes with just the standard vendored/generated rules. Having the
file is better than not -- it prevents future language bar drift as the project grows.

### CI Workflow (Basic Linting)

**Generate a basic CI workflow** (`.github/workflows/ci.yml`) if no workflows exist
in `.github/workflows/`. The audit scores CI presence, and having even a basic lint
workflow signals active maintenance.

**Do NOT generate if:**
- Workflows already exist (check `.github/workflows/` directory)
- The repo is archived
- The user explicitly says they don't want CI

**Detection logic for workflow type:**

| Primary Language / Repo Type | Workflow | Linter/Check |
|------------------------------|----------|-------------|
| Markdown-heavy (skills, docs) | Markdown lint | `markdownlint-cli2` via npx |
| Shell scripts | Shell lint | `shellcheck` |
| JavaScript/TypeScript | JS lint | `eslint` or `biome` (check package.json) |
| Python | Python lint | `ruff` or `flake8` (check pyproject.toml) |
| Rust | Rust checks | `cargo clippy` + `cargo fmt --check` |
| Go | Go checks | `go vet` + `golangci-lint` |
| Mixed/Unknown | YAML + Markdown lint | `yamllint` + `markdownlint-cli2` |

**Template for markdown-heavy repos (skills, documentation):**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint Markdown
        uses: DavidAnson/markdownlint-cli2-action@v19
        with:
          globs: "**/*.md"
```

**Template for JavaScript/TypeScript:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
```

**Template for Python:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .
```

Keep CI workflows minimal. The goal is a green badge and a signal of active
maintenance, not a full test suite. Users can expand it later.

## Output

### Community Standards Scorecard (Before/After)

GitHub checks 8 items at `/{owner}/{repo}/community`. Track completion:

| Item | Before | After |
|------|--------|-------|
| Description | ? | ? |
| README | ? | ? |
| Code of Conduct | ? | ? |
| Contributing | ? | ? |
| License | ? | ? |
| Security Policy | ? | ? |
| Issue Templates | ? | ? |
| Pull Request Template | ? | ? |
| **Completion** | **X/8** | **Y/8** |

Also list bonus files (not on GitHub's checklist but valuable):

| Bonus File | Status |
|-----------|--------|
| SUPPORT.md | Created / Existed / Skipped |
| CODEOWNERS | Created / Existed / Skipped |
| FUNDING.yml | Created / Existed / Skipped |
| .gitattributes | Created / Existed / Skipped |
| CI workflow | Created / Existed / Skipped |
| devcontainer.json | Created / Existed / Skipped |
| dependabot.yml | Created / Existed / Skipped |
| release.yml | Created / Existed / Skipped |

### Write to Shared Data Cache

After generating all files, write `.github-audit/community-data.json`:
```bash
mkdir -p .github-audit
grep -qxF '.github-audit/' .gitignore 2>/dev/null || echo '.github-audit/' >> .gitignore
```
Include: timestamp, files_created array, files_skipped object (with reasons),
scorecard_before, scorecard_after, placeholders array.
Reference: `~/.claude/skills/github/references/shared-data-cache.md` for exact schema.

### Deliverables

- List of files created/updated with paths
- Community Standards scorecard (before and after)
- **Placeholders to Fill In** -- list every `[REPLACE: ...]` marker with the file path
  and what the user needs to provide. Example:
  ```
  Placeholders to Fill In:
  1. CODE_OF_CONDUCT.md line 65: [REPLACE: your-email@example.com] -- enforcement contact email
  2. FUNDING.yml line 2: [REPLACE: your-github-username] -- GitHub Sponsors username
  ```
  If no placeholders exist (e.g., solo repo where owner is obvious), state "No placeholders -- all files are ready to commit."

### Next Step

After completing community file generation, always end with this handoff:

```
Community health files complete. Next recommended step:
  /github release -- versioning, CHANGELOG, badges, and release strategy
```

If running as part of the audit SOP, reference the step number:
"Step 2 complete. Ready for Step 3: `/github release`"
