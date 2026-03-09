<!-- Extracted from community-files-guide.md — YAML templates and code templates -->
# Community File Templates

## Issue Templates

### Bug Report (YAML form — recommended)

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: Report a bug or unexpected behavior
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: "Thanks for reporting! Please fill in the details below."
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: What happened?
      placeholder: Describe the bug...
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: How can we reproduce this?
      value: |
        1.
        2.
        3.
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should have happened?
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: Version
      placeholder: e.g., 1.0.0
  - type: dropdown
    id: os
    attributes:
      label: Operating System
      options:
        - Windows
        - macOS
        - Linux
        - Other
```

### Feature Request (YAML form)

```yaml
# .github/ISSUE_TEMPLATE/feature_request.yml
name: Feature Request
description: Suggest a new feature or improvement
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem Statement
      description: What problem does this solve?
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: How should this work?
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Other approaches you've thought about
```

### Template Chooser Config

```yaml
# .github/ISSUE_TEMPLATE/config.yml
blank_issues_enabled: false
contact_links:
  - name: Questions & Help
    url: https://github.com/{owner}/{repo}/discussions
    about: Use Discussions for questions and help
```

## Pull Request Template

```markdown
<!-- .github/PULL_REQUEST_TEMPLATE.md -->
## Summary

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tests pass locally
- [ ] New tests added for changes

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-reviewed my code
- [ ] Updated documentation if needed
```

## Dev Container (Contributor Onboarding)

```json
// .devcontainer/devcontainer.json
{
  "name": "Project Name",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {},
  "postCreateCommand": "npm install",
  "customizations": {
    "vscode": {
      "extensions": []
    }
  }
}
```

Adapt the image and commands to the project's tech stack.

## Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

Adapt `package-ecosystem` to the project: npm, pip, cargo, gomod, maven, gradle, etc.
