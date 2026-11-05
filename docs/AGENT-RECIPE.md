# legends-github agent recipe

Complete workflow recipe for `legends-github`. See also [docs/GITHUB-RECIPE.md](GITHUB-RECIPE.md).

## CLI Entrypoint and Global Options

Run all workflows through the portable Python entrypoint from the module root:

```bash
python legends_github.py [--offline] [--artifacts-dir PATH] <workflow> [options]
```

| Workflow | Command | Purpose | Mutation Flags |
| --- | --- | --- | --- |
| Capabilities | `python legends_github.py capabilities` | Emit machine-readable JSON workflow contract | Read-only |
| Readiness | `python legends_github.py verify --path /path/to/repo` | Check local readiness, `git`, `gh`, and optional providers | Read-only |
| Audit | `python legends_github.py audit --path /path/to/repo` | Collect repository evidence and prioritize findings | Read-only |
| SEO | `python legends_github.py seo --path /path/to/repo` | Derive keyword hypotheses from repository evidence | Read-only |
| Research | `python legends_github.py research --path /path/to/repo` | Estimate or collect live DataForSEO search evidence | `--execute` |
| Discover | `python legends_github.py discover --path /path/to/repo` | Plan evidence-backed organic discovery experiments | Read-only |
| Metadata | `python legends_github.py meta --path /path/to/repo` | Plan or apply repository description, homepage, and topics | `--apply` |
| README | `python legends_github.py readme --path /path/to/repo` | Preview or write README improvements and local artwork | `--write`, `--generate-assets` |
| Community | `python legends_github.py community --path /path/to/repo` | Plan or write contributor health files | `--write-files` |
| Legal | `python legends_github.py legal --path /path/to/repo` | Inventory licensing and attribution for review | `--write-files` |
| Release | `python legends_github.py release --path /path/to/repo` | Plan changelog and release preparation | `--write-files`, `--create-release`, `--publish` |
| Social Preview | `python legends_github.py social-preview --repo OWNER/REPO --image PATH --output OUT.json` | Prepare or verify (`--verify`) the 1280x640 social preview | `--verify` |
| Portfolio | `python legends_github.py empire --path /path/to/repo` | Plan portfolio presentation across repositories | `--generate-avatar` |
| Cache Status | `python legends_github.py cache-status --path /path/to/repo` | Inspect saved workflow evidence and cache state | Read-only |

## Standard Execution Sequence

1. **Verify readiness**:

   ```bash
   python legends_github.py verify --path /path/to/repo
   ```

2. **Collect repository evidence**:

   ```bash
   python legends_github.py audit --path /path/to/repo
   ```

3. **Run targeted workflows (preview first)**:

   ```bash
   python legends_github.py readme --path /path/to/repo
   python legends_github.py meta --path /path/to/repo
   python legends_github.py community --path /path/to/repo
   python legends_github.py legal --path /path/to/repo
   python legends_github.py release --path /path/to/repo
   ```

4. **Prepare and verify social preview**:

   ```bash
   python scripts/render_social_preview.py --title repo-slug --subtitle "approved copy" --font "/path/to/Legends-Regular.ttf" --output assets/social-preview.png
   python legends_github.py social-preview --repo OWNER/REPO --image assets/social-preview.png --verify --output /outside/repo/verified.json
   ```

## EDR and Security Guardrails

- Zero browser state or local desktop credential store reads (`Local State`, `Login Data`, `Cookies`, `IndexedDB`, `LevelDB`, DPAPI, Keychain).
- Zero executable shell wrappers (`.ps1`, `.sh`, `.bat`, `.cmd`, `.vbs`, `.wsf`, `.hta`, `.scr`) shipped inside the repository.
- Outbound network traffic is restricted to explicit user-invoked GitHub CLI (`gh`) commands, HTTPS GitHub social-preview image verification, and optional DataForSEO API requests (`--execute`).
- All PNG and WebP assets are stripped of ancillary metadata chunks (`tEXt`, `iTXt`, `zTXt`, `eXIf`, `EXIF`, `XMP`) before commit.
- Read before writing; keep remote changes opt-in (`--apply`, `--create-release`, `--publish`, `--execute`).
- Never fabricate metrics, license provenance, or search volume, and never claim a social preview is live until `--verify` passes.
