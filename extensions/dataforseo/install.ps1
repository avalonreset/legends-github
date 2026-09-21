# Compatibility installer: provider package only, no host configuration changes.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
python -m pip install -r (Join-Path $root 'requirements-dataforseo.txt')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Installed legends-dataforseo-kit. Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in your environment.'
Write-Host 'See docs/SEO-RESEARCH.md. No MCP server or credential file was configured.'
