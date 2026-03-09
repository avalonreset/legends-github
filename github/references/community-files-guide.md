<!-- Updated: 2026-03-08 -->
# Community Files Guide — Standard Files and Best Practices

## Overview

GitHub's Community Standards checklist (visible at `/{owner}/{repo}/community`) checks
for these files. Completing all items signals a well-maintained, contributor-friendly project.

## Community Standards Checklist

| File | Required for Green Check? | Location Options |
|------|--------------------------|-----------------|
| Description | Yes | Repo settings (About) |
| README | Yes | Root, docs/, .github/ |
| Code of Conduct | Yes | Root, docs/, .github/ |
| Contributing | Yes | Root, docs/, .github/ |
| License | Yes | Root |
| Security Policy | Yes | Root, docs/, .github/ |
| Issue Templates | Yes (at least one) | .github/ISSUE_TEMPLATE/ |
| Pull Request Template | Yes | .github/ |

## File Specifications

### CONTRIBUTING.md

Key sections to include:
- How to Contribute (fork, branch, PR workflow)
- Development Setup (prerequisites, install steps)
- Code Style (linting, formatting, conventions)
- Reporting Bugs (link to issue template)
- Requesting Features (link to issue template)
- Code of Conduct reference

### CODE_OF_CONDUCT.md

Recommended: **Contributor Covenant v2.1** (most widely adopted).
GitHub provides a template at repo Settings > Code of Conduct.

Key sections: Our Pledge, Our Standards, Enforcement Responsibilities,
Scope, Enforcement, Attribution.

### SECURITY.md

Key sections:
- Supported Versions (table of version → supported status)
- Reporting a Vulnerability (email, NOT public issue)
- What to Expect (acknowledgment timeline, resolution timeline)
- Disclosure Policy (responsible disclosure steps)

### SUPPORT.md

Key sections:
- Getting Help (docs link, Discussions link, Issues for bugs only)
- Reporting Issues (direct to GitHub Issues for bugs)

### CODEOWNERS

Pattern-based ownership assignment for PR reviews:
- `* @username` for global owner
- `*.js @js-team` for language-specific
- `/docs/ @docs-team` for directory-specific

### .github/FUNDING.yml

Supported platforms: github, patreon, open_collective, ko_fi, custom URLs.

## Issue Templates

Use YAML form-based templates (`.github/ISSUE_TEMPLATE/*.yml`) instead of markdown
templates. They provide structured input, required fields, and dropdowns.

Recommended templates:
- **Bug Report** — Description, steps to reproduce, expected behavior, version, OS
- **Feature Request** — Problem statement, proposed solution, alternatives considered

Add a **config.yml** to disable blank issues and link to Discussions for questions.

See `community-templates.md` for full YAML template code.

## Pull Request Template

Place at `.github/PULL_REQUEST_TEMPLATE.md`. Include:
- Summary section
- Type of Change checklist (bug fix, feature, breaking change, docs)
- Testing checklist
- Code review checklist

See `community-templates.md` for the full template.

## Dev Container

A `.devcontainer/devcontainer.json` file enables one-click contributor onboarding
via GitHub Codespaces or VS Code Dev Containers.

Select the base image by language:
| Language | Image |
|----------|-------|
| Node.js | `mcr.microsoft.com/devcontainers/javascript-node` |
| Python | `mcr.microsoft.com/devcontainers/python` |
| Rust | `mcr.microsoft.com/devcontainers/rust` |
| Go | `mcr.microsoft.com/devcontainers/go` |
| Java | `mcr.microsoft.com/devcontainers/java` |
| General | `mcr.microsoft.com/devcontainers/base:ubuntu` |

See `community-templates.md` for the full devcontainer.json template.

## Dependabot

Place at `.github/dependabot.yml`. Detect the package ecosystem from the project:

| File | Ecosystem |
|------|-----------|
| package.json | npm |
| requirements.txt / pyproject.toml | pip |
| Cargo.toml | cargo |
| go.mod | gomod |
| pom.xml | maven |
| build.gradle | gradle |
| Gemfile | bundler |

See `community-templates.md` for the full dependabot.yml template.

## Intent-Based Priority

| Intent | Priority Files |
|--------|---------------|
| Open Source Community | CONTRIBUTING (critical), CoC, issue templates, devcontainer |
| Professional Portfolio | Lightweight community files, focus on polish |
| Business / Brand | SECURITY.md (critical), SUPPORT.md, structured templates |
| Internal to Public | SECURITY.md (critical), CONTRIBUTING (detailed), CODEOWNERS |
| Academic / Research | CONTRIBUTING (methodology), CITATION.cff (separate skill) |
| Hobby / Learning | Minimal — CONTRIBUTING, basic issue template |
