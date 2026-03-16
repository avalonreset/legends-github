# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2026-03-16

### Added
- Standard Operating Procedure (SOP) across all skills: audit generates a numbered remediation plan, each skill hands off to the next logical step, re-audit closes the loop
- Two-phase workflow: Phase 1 (per-repo optimization) and Phase 2 (portfolio optimization via /github empire)
- Canonical skill order: legal -> community -> release -> seo -> meta -> readme
- Clickable image link rules: all generated images output both local file:// and raw GitHub URLs for immediate terminal access
- Social preview generation guidance with download + upload links in github-meta skill

### Changed
- Avatar pipeline simplified to JPEG-only (GitHub rejects WebP, PNGs often exceed 1MB)
- Lossless PNG originals preserved in assets/originals/ for user reference
- Contact email updated to benjamin@rankenstein.pro
- All em dashes removed from skill suite (replaced with regular hyphens)

### Fixed
- Social preview format policy enforced: JPEG only, under 1MB for GitHub upload
- WebP input handling for banner recomposition via KIE.ai

## [1.1.0] - 2026-03-13

### Added
- Empire skill redesign: empire builder mode with profile completeness checks and AI avatar generation
- WebP image pipeline with metadata stripping across all conversion scripts
- Getting Started guide, install screenshot, FAQ, and Best Practices sections in README
- Restart guide and project-folder reminder in installers
- Mascot and BEN branding images
- Skill Forge attribution in README

### Changed
- All images converted from PNG/JPG to WebP for smaller file sizes
- Installer splash screen updated to v1.1 with stronger service messaging
- README optimized for secondary keyword opportunities
- Banner generation reference updated for WebP delivery

### Fixed
- DataForSEO cost gate and competitor search field name
- Avatar detection method for image format rubric
- Markdownlint CI failures with config and rule adjustments
- Empty badge link in README

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

[Unreleased]: https://github.com/avalonreset-pro/claude-github/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/avalonreset-pro/claude-github/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/avalonreset-pro/claude-github/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/avalonreset-pro/claude-github/releases/tag/v1.0.0
