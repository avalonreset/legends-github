<!-- Created: 2026-03-08 -->
# Shared Data Cache — Cross-Skill Data Persistence

## Overview

Skills in the GitHub suite produce data that other skills need. Rather than forcing
a rigid execution order, each skill **caches its output** and **checks for cached
data** before gathering dependencies from scratch.

**Directory:** `.github-audit/` in the repo root (add to `.gitignore`).

**Principle:** Check cache first → use if fresh → gather yourself if missing.

## Cache Files

| File | Written By | Contains |
|------|-----------|----------|
| `repo-context.json` | github (orchestrator) | Repo type, intent, owner, language, metadata |
| `seo-data.json` | github-seo | Keywords, PAA, topics, description, AI visibility |
| `legal-data.json` | github-legal | License type, SECURITY.md status, CITATION.cff status, compliance |
| `audit-data.json` | github-audit | Per-category scores, action items, file existence map |
| `community-data.json` | github-community | Files created, scorecard, placeholders |
| `readme-data.json` | github-readme | Score before/after, banner status, keyword integration |
| `meta-data.json` | github-meta | Description, topics, settings applied |
| `releases-data.json` | github-release | CHANGELOG status, badges, version, release.yml status |
| `empire-data.json` | github-empire | Portfolio scores, topic authority, pinned repos, cross-linking |

## Dependency Map

Which cache files each skill should CHECK before gathering:

| Skill | Required Cache | Optional Cache |
|-------|---------------|----------------|
| github-readme | — | `seo-data.json` (strongly recommended), `repo-context.json`, `legal-data.json`, `audit-data.json` |
| github-meta | — | `seo-data.json` (strongly recommended), `repo-context.json` |
| github-audit | — | `repo-context.json`, `audit-data.json` (offers reuse if fresh) |
| github-community | — | `repo-context.json`, `legal-data.json` |
| github-legal | — | `repo-context.json` |
| github-release | — | `repo-context.json` |
| github-audit | — | `repo-context.json` |
| github-empire | `audit-data.json` | `seo-data.json`, `repo-context.json` |

**"Required" means:** The skill cannot function without this data and will invoke
the dependency skill to generate it if missing.

**"Strongly recommended" means:** Output quality degrades significantly without this
data. If missing, the skill will attempt to gather it inline (adding cost/time).
If that also fails, the skill proceeds with best-effort guesses marked "unverified."

**"Optional" means:** If available, use it to improve output. If missing, proceed without.

## JSON Schemas

### repo-context.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "owner": "avalonreset",
  "repo": "claude-knife",
  "repo_type": "Skill/Plugin",
  "intent": "Open Source Community",
  "primary_language": "Python",
  "description": "Current repo description",
  "stars": 12,
  "forks": 3,
  "has_discussions": false,
  "has_wiki": true,
  "has_issues": true,
  "default_branch": "main",
  "is_fork": false
}
```

### seo-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "mode": "quick",
  "primary_keyword": {
    "keyword": "knife design software",
    "volume": 40,
    "difficulty": 8,
    "category": "Sweet Spot (niche)",
    "intent": "transactional"
  },
  "secondary_keywords": [
    {
      "keyword": "cadquery knife",
      "volume": 20,
      "difficulty": 5,
      "category": "Worth It"
    }
  ],
  "skip_keywords": ["butterfly knife", "knife sharpening"],
  "recommended_description": "AI-powered knife design software...",
  "recommended_topics": ["knife-design", "cadquery", "parametric-cad"],
  "paa_questions": [
    "What tools are used in knife design?",
    "Is CadQuery free to use?"
  ],
  "ai_visibility": {
    "cited": false,
    "competitors_cited": ["knifeprint", "bladesmiths-forum"]
  },
  "serp_verified": true,
  "github_in_serp": true,
  "github_serp_position": 9
}
```

### legal-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "license_type": "MIT",
  "license_file_exists": true,
  "license_file_path": "LICENSE",
  "security_md_exists": false,
  "security_md_path": null,
  "citation_cff_exists": false,
  "notice_file_exists": false,
  "is_fork": false,
  "fork_compliant": null,
  "dependency_conflicts": []
}
```

### audit-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "overall_score": 48,
  "scores": {
    "readme": 14,
    "meta": 12,
    "legal": 8,
    "community": 5,
    "releases": 4,
    "seo": 5
  },
  "action_items": [
    {
      "priority": "critical",
      "category": "readme",
      "action": "Add Table of Contents"
    }
  ],
  "file_existence": {
    "readme": true,
    "license": true,
    "contributing": false,
    "code_of_conduct": false,
    "security_md": false,
    "support_md": false,
    "codeowners": false,
    "funding_yml": false,
    "issue_templates": false,
    "pr_template": false,
    "changelog": false,
    "citation_cff": false
  }
}
```

### community-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "files_created": [
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml"
  ],
  "files_skipped": {
    "SECURITY.md": "Handled by /github legal"
  },
  "scorecard_before": 3,
  "scorecard_after": 8,
  "placeholders": [
    {
      "file": "CODE_OF_CONDUCT.md",
      "line": 65,
      "placeholder": "[REPLACE: your-email@example.com]",
      "description": "enforcement contact email"
    }
  ]
}
```

### readme-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "score_before": 43,
  "score_after": 94,
  "banner_generated": true,
  "banner_path": "assets/banner.jpg",
  "keywords_integrated": {
    "primary_in_h1": true,
    "primary_in_first_paragraph": true,
    "secondary_in_h2": ["Installation", "Quick Start"]
  },
  "sections": ["Features", "Installation", "Quick Start", "Usage", "Architecture", "FAQ", "Contributing", "License"]
}
```

### meta-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "description_set": "AI-powered knife design software...",
  "topics_set": ["knife-design", "cadquery", "parametric-cad"],
  "homepage_url": "https://github.com/avalonreset/claude-knife",
  "features_toggled": {
    "discussions": false,
    "wiki": true,
    "issues": true
  },
  "gitattributes_created": false,
  "social_preview_set": false
}
```

### releases-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "changelog_created": true,
  "release_yml_created": true,
  "latest_version": "v1.0.0",
  "badges": [
    "[![GitHub Release](https://img.shields.io/github/v/release/owner/repo)](releases)"
  ],
  "versioning_scheme": "semver"
}
```

### empire-data.json
```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "portfolio_size": 12,
  "average_score": 48,
  "per_repo_scores": {
    "claude-knife": 39,
    "gemini-seo": 63
  },
  "topic_authority": [
    {
      "cluster": "seo-tools",
      "repos": 3,
      "strength": "Strong"
    }
  ],
  "pinned_repos_recommended": ["gemini-seo", "claude-knife", "BenjaminTerm"],
  "cross_linking": [
    {
      "from": "gemini-seo",
      "to": "codex-seo",
      "reason": "Related SEO ports"
    }
  ],
  "branding_consistency": "inconsistent"
}
```

## Freshness Rules

- Cache files are valid for the **current calendar day (UTC)**.
- If the `timestamp` date (UTC) differs from today's date (UTC), treat as stale — re-gather.
- If the user explicitly asks to "re-run" or "refresh" a skill, ignore cache.

## Error Handling

- If `.github-audit/` cannot be created (permissions, read-only filesystem), **skip
  cache writing silently** and continue. The skill's output is unaffected — caching is
  a performance optimization, not a requirement.
- If a cache JSON file is corrupt or unparseable, treat it as missing — re-gather.
- If `.gitignore` doesn't exist, the `grep || echo` pattern creates it automatically.
  If `.gitignore` is read-only, the append fails silently — acceptable.

## Implementation Pattern

### Reading Cache (in Gather step)

```markdown
**Check shared data cache:**
1. Look for `.github-audit/` directory in the repo root
2. For each dependency, check if the JSON file exists and is from today
3. If found and fresh: parse and use the data (skip re-gathering that data)
4. If missing or stale:
   - For REQUIRED dependencies: gather the data yourself (lightweight)
   - For OPTIONAL dependencies: proceed without it
```

### Writing Cache (in Execute step)

```markdown
**Write to shared data cache:**
After completing all work, write results to `.github-audit/{skill}-data.json`.
```json
{
  "timestamp": "[current ISO timestamp]",
  ... skill-specific fields per schema above ...
}
```
Create the `.github-audit/` directory if it doesn't exist.
Add `.github-audit/` to `.gitignore` if not already present.
```

### Lightweight Dependency Gathering

When a required cache file is missing, don't run the full dependency skill.
Instead, gather just the data you need:

| Missing Cache | Lightweight Fallback |
|--------------|---------------------|
| `seo-data.json` | Skip SEO optimization, use codebase-derived keywords (repo name, description words) |
| `legal-data.json` | Check `LICENSE` file exists + read first line for type, check `SECURITY.md` exists |
| `repo-context.json` | Run `gh repo view --json name,description,primaryLanguage,...` yourself |
| `audit-data.json` | Skip audit-informed decisions, use defaults for repo type |

**Never block on missing optional cache.** Degrade gracefully.
