<!-- Updated: 2026-03-08 -->
# README Framework -- Structure, SEO Patterns, and Heading Hierarchy

## Overview

The README is the #1 SEO-indexed page for any GitHub repo. Google crawls README content
and uses it for search results. A well-structured README serves three audiences: search
engines, AI systems, and humans.

## README Structure by Repo Type

### Library/Package

```markdown
# Project Name -- One-line description with primary keyword

[![Badge row: CI, coverage, npm/pypi version, license, downloads]]

Brief 2-3 sentence description. What problem does this solve? Primary keyword in first sentence.

## Features
- Feature 1 (keyword-rich)
- Feature 2
- Feature 3

## Installation
[Package manager install commands]

## Quick Start
[Minimal code example that works]

## Usage
[Detailed examples with code blocks]

## API Reference
[Key methods/functions]

## Configuration
[Options and defaults]

## Contributing
[Link to CONTRIBUTING.md]

## License
[License type with link to LICENSE file]
```

### CLI Tool

```markdown
# tool-name -- One-line description

[![Badges]]

## Installation
[Multiple install methods: binary, package manager, from source]

## Quick Start
[The one command that shows the tool's value]

## Commands
[Command reference table]

## Configuration
[Config file format, environment variables]

## Examples
[Real-world usage scenarios]
```

### Application / Framework

```markdown
# Project Name -- One-line description

[![Badges]]

## Why Project Name?
[Problem statement, value proposition]

## Getting Started
[Prerequisites, installation, first run]

## Documentation
[Link to docs site / GitHub Pages]

## Architecture
[High-level overview for contributors]

## Deployment
[How to deploy]

## Contributing
[Link to CONTRIBUTING.md]
```

## SEO Optimization Rules

### Heading Hierarchy (Critical for SEO)
- **H1**: Project name + primary keyword (exactly ONE H1)
- **H2**: Major sections (Features, Installation, Usage, etc.)
- **H3**: Subsections within H2s
- Never skip levels (H1 → H3 without H2)
- Use keywords naturally in headings

### First Paragraph (Most Important for SEO)
- Include primary keyword in the first sentence
- Describe what the project does (not what it is)
- Keep to 2-3 sentences
- This text often becomes the Google search snippet

### Keyword Placement
- H1: Primary keyword
- First paragraph: Primary keyword
- H2 headings: Secondary keywords
- Body: Natural density (1-3%), semantic variations
- Alt text on images: Descriptive with keywords
- Link text: Descriptive (never "click here")

### AI Citability (GEO Optimization)
- Clear, quotable statements with specific facts
- Structured content (tables, lists) that AI systems can extract
- Answer-first formatting for key questions
- Statistics and data points with attribution

## Badge Strategy

### Essential Badges (in this order)
1. **CI/Build status** -- Signals working code
2. **Version** -- Shows latest release
3. **License** -- Quick legal clarity
4. **Downloads/installs** -- Social proof (if significant)

### Optional Badges
- Code coverage (if high)
- Last commit (signals active maintenance)
- Contributors count
- Language/platform badges

### Badge URL Patterns

```markdown
<!-- GitHub Actions -->
![CI](https://github.com/{owner}/{repo}/actions/workflows/{file}/badge.svg)

<!-- Shields.io -->
![Version](https://img.shields.io/github/v/release/{owner}/{repo})
![License](https://img.shields.io/github/license/{owner}/{repo})
![Downloads](https://img.shields.io/npm/dm/{package})
![Stars](https://img.shields.io/github/stars/{owner}/{repo})
![Last Commit](https://img.shields.io/github/last-commit/{owner}/{repo})
```

## Table of Contents

Include a ToC for READMEs longer than 4 sections. Use markdown links:

```markdown
## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
```

## Common Mistakes to Avoid

- No H1 heading (or multiple H1s)
- Missing installation instructions
- No code examples
- "Click here" link text
- Outdated badges pointing to broken CI
- No license mentioned
- Wall of text without structure
- README that describes what the project IS instead of what it DOES
