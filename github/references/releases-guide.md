<!-- Updated: 2026-03-08 -->
# Releases Guide — Semver, Changelog, Badges, and Release Automation

## Overview

Releases signal active maintenance, provide download counts (social proof), and are
indexed by Google. A proper release strategy increases trust and discoverability.

## Semantic Versioning (semver)

Format: `MAJOR.MINOR.PATCH`

| Component | When to Increment | Example |
|-----------|------------------|---------|
| MAJOR | Breaking changes (incompatible API changes) | 1.0.0 → 2.0.0 |
| MINOR | New features (backwards compatible) | 1.0.0 → 1.1.0 |
| PATCH | Bug fixes (backwards compatible) | 1.0.0 → 1.0.1 |

### Pre-release Tags
- Alpha: `1.0.0-alpha.1` (unstable, in development)
- Beta: `1.0.0-beta.1` (feature-complete, testing)
- RC: `1.0.0-rc.1` (release candidate, final testing)

### First Release
- Use `0.1.0` for initial development (API may change)
- Use `1.0.0` when the public API is stable

## CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.0] - 2026-03-08
### Added
- New feature X
- Support for Y

### Changed
- Improved performance of Z

### Fixed
- Bug where A happened when B

## [1.0.0] - 2026-02-01
### Added
- Initial release
```

### Change Categories
- **Added** — New features
- **Changed** — Changes to existing functionality
- **Deprecated** — Features that will be removed
- **Removed** — Features that were removed
- **Fixed** — Bug fixes
- **Security** — Vulnerability fixes

## GitHub Releases

### Creating a Release

```bash
# Create a tag and release
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes here"

# With auto-generated notes from merged PRs
gh release create v1.0.0 --generate-notes

# Pre-release
gh release create v1.0.0-beta.1 --prerelease --generate-notes

# With binary assets
gh release create v1.0.0 ./dist/binary-linux ./dist/binary-macos ./dist/binary-windows
```

### Auto-Generated Release Notes Config

```yaml
# .github/release.yml
changelog:
  exclude:
    labels:
      - ignore-for-release
    authors:
      - dependabot
  categories:
    - title: "Breaking Changes"
      labels:
        - breaking
    - title: "New Features"
      labels:
        - enhancement
        - feature
    - title: "Bug Fixes"
      labels:
        - bug
        - fix
    - title: "Documentation"
      labels:
        - documentation
    - title: "Other Changes"
      labels:
        - "*"
```

## Badge Reference

### Shields.io URL Patterns

| Badge | URL | When to Use |
|-------|-----|-------------|
| CI Status | `https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow}` | Always — signals working code |
| Version | `https://img.shields.io/github/v/release/{owner}/{repo}` | When releases exist |
| License | `https://img.shields.io/github/license/{owner}/{repo}` | Always |
| npm Version | `https://img.shields.io/npm/v/{package}` | For npm packages |
| PyPI Version | `https://img.shields.io/pypi/v/{package}` | For Python packages |
| Downloads (npm) | `https://img.shields.io/npm/dm/{package}` | When download count is impressive |
| Downloads (GitHub) | `https://img.shields.io/github/downloads/{owner}/{repo}/total` | For binary releases |
| Stars | `https://img.shields.io/github/stars/{owner}/{repo}` | When star count is impressive |
| Last Commit | `https://img.shields.io/github/last-commit/{owner}/{repo}` | Signals active maintenance |
| Code Coverage | `https://img.shields.io/codecov/c/github/{owner}/{repo}` | When using Codecov |
| Contributors | `https://img.shields.io/github/contributors/{owner}/{repo}` | For community projects |

### Native GitHub Actions Badge

```markdown
![CI](https://github.com/{owner}/{repo}/actions/workflows/{file}.yml/badge.svg)
```

### Badge Styling Options

```markdown
<!-- Flat (default) -->
![Badge](https://img.shields.io/badge/label-message-color)

<!-- Flat-square -->
![Badge](https://img.shields.io/badge/label-message-color?style=flat-square)

<!-- For-the-badge (larger) -->
![Badge](https://img.shields.io/badge/label-message-color?style=for-the-badge)
```

## Release Automation

### semantic-release

Fully automated version management from conventional commits:

```bash
npm install --save-dev semantic-release
```

Commit format drives versioning:
- `fix: description` → PATCH release
- `feat: description` → MINOR release
- `feat!: description` or `BREAKING CHANGE:` → MAJOR release

### GitHub Actions Release Workflow

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
```

## Intent-Based Release Strategy

| Intent | Strategy |
|--------|---------|
| Open Source Community | Regular releases, detailed changelogs, pre-releases for testing |
| Professional Portfolio | Clean release history, semver, meaningful release notes |
| Business / Brand | Frequent releases signal momentum, auto-generated notes |
| Academic / Research | Versioned releases tied to paper submissions, DOI integration |
| Hobby / Learning | Informal releases when ready, focus on CHANGELOG |
