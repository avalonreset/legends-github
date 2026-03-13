<!-- Updated: 2026-03-08 -->
# Repo Type Templates -- Per-Type Defaults and Recommendations

## Overview

Different repo types have different optimization priorities. This reference provides
defaults for each detected type, covering README structure, recommended files,
badge selection, topic strategy, and SEO focus.

## Library / Package

**Detection signals:** package.json, setup.py, Cargo.toml, go.mod, pyproject.toml,
Gemfile, *.gemspec, pom.xml, build.gradle

**Priority files:**
- README.md (installation + usage examples critical)
- LICENSE (permissive recommended -- MIT or Apache 2.0)
- CONTRIBUTING.md (important for adoption)
- CHANGELOG.md (users need to know what changed)

**README structure:** Installation first, then quick start, then API reference.

**Badge priority:** Version > CI > License > Downloads > Coverage

**Topic strategy:**
- Language: `javascript`, `python`, `rust`, etc.
- Ecosystem: `npm`, `pypi`, `crates-io`
- Domain: what the library does (`state-management`, `http-client`)
- Framework: if library targets a framework (`react`, `vue`, `express`)

**SEO focus keywords:** "[language] [what it does] library", "best [what it does] for [framework]"

---

## CLI Tool

**Detection signals:** bin/, "usage:", commander, yargs, clap, argparse,
cobra, click, "command-line", shebang lines

**Priority files:**
- README.md (command reference critical)
- LICENSE
- CHANGELOG.md (users need to track behavior changes)

**README structure:** Installation (multiple methods), quick start command, full command reference.

**Badge priority:** Version > CI > License > Downloads

**Topic strategy:**
- `cli`, `command-line`, `terminal`
- Language
- Domain: `git-tool`, `devops`, `productivity`

**SEO focus keywords:** "[what it does] cli", "[what it does] command line tool", "[what it does] terminal"

---

## Framework

**Detection signals:** middleware, routing, plugins, "getting started",
createApp, mount, bootstrap, "starter template"

**Priority files:**
- README.md (getting started critical)
- LICENSE
- CONTRIBUTING.md (framework needs contributors)
- docs/ or GitHub Pages (documentation is essential)
- SECURITY.md (frameworks are security-sensitive)

**README structure:** Why this framework, getting started, documentation link, architecture overview.

**Badge priority:** CI > Version > License > Stars > Contributors

**Topic strategy:**
- `framework`, `web-framework`, `library`
- Language and ecosystem
- Paradigm: `functional`, `reactive`, `mvc`

**SEO focus keywords:** "[language] [type] framework", "[language] web framework", "best [language] framework 2026"

---

## API / Service

**Detection signals:** /api, swagger, OpenAPI, endpoints, "REST API",
"GraphQL", routes, controllers

**Priority files:**
- README.md (API overview + authentication)
- LICENSE
- SECURITY.md (critical -- API = attack surface)
- docs/ or GitHub Pages (API docs essential)
- .env.example (environment variables)

**README structure:** What the API does, authentication, endpoints overview, link to full docs.

**Badge priority:** CI > Version > License > Uptime (if available)

**Topic strategy:**
- `api`, `rest-api`, `graphql`
- Domain: `payment-api`, `auth-service`
- Technology: `express`, `fastapi`, `spring-boot`

**SEO focus keywords:** "[domain] api", "[domain] REST API", "open source [domain] API"

---

## Application

**Detection signals:** docker-compose, Dockerfile, deployment configs,
.env, database migrations, CI/CD workflows

**Priority files:**
- README.md (setup + deployment)
- LICENSE
- SECURITY.md
- .env.example
- docker-compose.yml (if containerized)
- CONTRIBUTING.md

**README structure:** What it does, screenshots/demo, setup instructions, deployment guide.

**Badge priority:** CI > License > Last Commit > Contributors

**Topic strategy:**
- Application type: `web-app`, `desktop-app`, `mobile-app`
- Technology stack: `react`, `django`, `electron`
- Domain: `task-manager`, `chat-app`, `dashboard`

**SEO focus keywords:** "open source [type of app]", "[type] app built with [tech]"

---

## Skill / Plugin

**Detection signals:** SKILL.md, AGENTS.md, extension pattern, plugin.json,
"extends", "hooks into"

**Priority files:**
- README.md (what it extends + how to install)
- LICENSE
- SKILL.md or plugin config

**README structure:** What it does, what it extends, installation, configuration, examples.

**Badge priority:** Version > License > CI

**Topic strategy:**
- Parent platform: `claude-code`, `vscode`, `neovim`, `obsidian`
- `plugin`, `extension`, `skill`
- What it does

**SEO focus keywords:** "[platform] [what it does] plugin", "best [platform] extensions"

---

## Documentation

**Detection signals:** mkdocs.yml, docusaurus.config.js, mostly .md files,
_config.yml (Jekyll), book.toml (mdBook)

**Priority files:**
- README.md (overview + navigation)
- LICENSE (often CC-BY-4.0 for docs)
- mkdocs.yml or equivalent config

**README structure:** What documentation covers, how to navigate, how to contribute to docs.

**Badge priority:** CI (docs build) > License > Last Commit

**Topic strategy:**
- `documentation`, `docs`, `tutorial`
- Subject domain
- `markdown`, `static-site`

**SEO focus keywords:** "[subject] documentation", "[subject] tutorial", "[subject] guide"

---

## Default Recommendations (All Types)

| Setting | Recommendation |
|---------|---------------|
| Topics count | 5-20 (never zero) |
| Description | Filled, keyword-rich, under 350 chars |
| Homepage URL | Set if docs site exists |
| License | Present and GitHub-detected |
| Default branch | `main` |
| Issues | Enabled |
| Discussions | Enable for community projects |
| Wiki | Disable (use README or Pages instead) |
