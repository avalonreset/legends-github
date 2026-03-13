# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-03-13

### Added
- Orchestrator skill (`/github`) with intent detection, repo type classification, and DataForSEO integration
- 8 sub-skills: audit, readme, legal, meta, seo, community, release, empire
- 6 parallel scoring agents for repository health audit (0-100 scoring across README, metadata, legal, community, releases, SEO)
- 9 reference guides (banner generation, community files, community templates, license guide, readme framework, releases guide, repo type templates, SEO guide, shared data cache)
- DataForSEO MCP server integration for live keyword research, SERP analysis, and AI visibility tracking
- KIE.ai banner generation with one-shot Nano Banana 2 image generation
- Cross-platform installers (Bash for macOS/Linux, PowerShell for Windows)
- Shared data cache system (`.github-audit/` directory) for inter-skill communication
- Portfolio audit mode (`/github audit username`) with parallel multi-repo analysis
- GARE pattern (Gather, Analyze, Recommend, Execute) across all skills with confirmation gates
- SEO-optimized README with professional banner, keyword-integrated headings, and FAQ
- Proprietary license for community distribution
- SECURITY.md with credential handling scope and vulnerability reporting policy
- Full community health suite: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SUPPORT.md, CODEOWNERS, issue templates (YAML forms), PR template, devcontainer, dependabot
- Member invitation scripts for GitHub organization management

[Unreleased]: https://github.com/avalonreset-pro/claude-github/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/avalonreset-pro/claude-github/releases/tag/v1.0.0
