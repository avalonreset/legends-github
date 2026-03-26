# Support

## Getting Help

If you need help with Claude GitHub, here are your options:

### Questions and Discussion

For "how do I..." questions, troubleshooting, and general discussion:

**[GitHub Discussions](https://github.com/avalonreset/claude-github/discussions)**

This is the best place to ask questions, share tips, and connect with other community members.

### Bug Reports

If something is broken or not working as expected:

**[Open a Bug Report](https://github.com/avalonreset/claude-github/issues/new?template=bug_report.yml)**

Please include the skill name, what happened, and your OS/Claude Code version.

### Feature Requests

Have an idea for a new feature or improvement?

**[Open a Feature Request](https://github.com/avalonreset/claude-github/issues/new?template=feature_request.yml)**

### Security Issues

Found a security vulnerability? **Do not open a public issue.** Email benjamin@rankenstein.pro directly. See [SECURITY.md](SECURITY.md) for details.

## Common Issues

**Skills not appearing after installation:**
Restart Claude Code. Skills register on startup, not dynamically.

**DataForSEO returning errors:**
Check your MCP configuration in `~/.claude/settings.json`. Verify your credentials are correct and your account has credits.

**Banner generation failing:**
Ensure `KIE_API_KEY` is set in `~/.claude/skills/github/.env`. Check your KIE.ai account balance at https://kie.ai.

**Audit scores seem inconsistent:**
Run the audit again. Scores should be within 2-3 points across runs. If variance is larger, open a bug report with both outputs.
