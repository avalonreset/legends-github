# Claude GitHub -- DataForSEO Extension Installer (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=== Claude GitHub -- DataForSEO Extension ===" -ForegroundColor Cyan
Write-Host ""

# Check that base skill is installed
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"
$SkillsDir = Join-Path $ClaudeDir "skills"
$AgentsDir = Join-Path $ClaudeDir "agents"

if (-not (Test-Path (Join-Path $SkillsDir "github\SKILL.md"))) {
    Write-Host "ERROR: Claude GitHub base skill not found." -ForegroundColor Red
    Write-Host "Please install the base skill first: .\install.ps1"
    exit 1
}

# Check for Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is required for the DataForSEO MCP server." -ForegroundColor Red
    Write-Host "Install: https://nodejs.org/"
    exit 1
}

# Get API credentials
Write-Host "DataForSEO API credentials required."
Write-Host "Sign up at: https://app.dataforseo.com/"
Write-Host ""
$DfLogin = Read-Host "DataForSEO API Login"
$DfPassword = Read-Host "DataForSEO API Password" -AsSecureString
$DfPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DfPassword)
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Copy extension skill and agent
$ExtSkillDir = Join-Path $SkillsDir "github-dataforseo"
if (-not (Test-Path $ExtSkillDir)) {
    New-Item -ItemType Directory -Path $ExtSkillDir -Force | Out-Null
}
Copy-Item (Join-Path $ScriptDir "skills\github-dataforseo\SKILL.md") (Join-Path $ExtSkillDir "SKILL.md") -Force
Write-Host "[+] Installed: github-dataforseo skill" -ForegroundColor Green

Copy-Item (Join-Path $ScriptDir "agents\github-dataforseo.md") (Join-Path $AgentsDir "github-dataforseo.md") -Force
Write-Host "[+] Installed: github-dataforseo agent" -ForegroundColor Green

# Copy field config
$FieldConfigPath = Join-Path $SkillsDir "seo\dataforseo-field-config.json"
$FieldConfigDir = Split-Path -Parent $FieldConfigPath
if (-not (Test-Path $FieldConfigDir)) {
    New-Item -ItemType Directory -Path $FieldConfigDir -Force | Out-Null
}
if (Test-Path (Join-Path $ScriptDir "field-config.json")) {
    Copy-Item (Join-Path $ScriptDir "field-config.json") $FieldConfigPath -Force
    Write-Host "[+] Installed: field config" -ForegroundColor Green
}

# Pre-download MCP server
Write-Host "[*] Pre-downloading DataForSEO MCP server..."
npx -y dataforseo-mcp-server --help 2>$null

# Register MCP server via Claude CLI (preferred method)
$cliRegistered = $false
if (Get-Command claude -ErrorAction SilentlyContinue) {
    try {
        claude mcp add `
            -e "DATAFORSEO_USERNAME=$DfLogin" `
            -e "DATAFORSEO_PASSWORD=$DfPasswordPlain" `
            -e "ENABLED_MODULES=SERP,KEYWORDS_DATA,ONPAGE,DATAFORSEO_LABS,BACKLINKS,DOMAIN_ANALYTICS,BUSINESS_DATA,CONTENT_ANALYSIS,AI_OPTIMIZATION" `
            -e "FIELD_CONFIG_PATH=$FieldConfigPath" `
            -s user `
            dataforseo -- npx -y dataforseo-mcp-server 2>$null
        $cliRegistered = $true
        Write-Host "[+] Registered MCP server via Claude CLI" -ForegroundColor Green
    } catch {
        Write-Host "[*] Claude CLI registration failed, falling back to settings.json" -ForegroundColor Yellow
    }
}

# Fallback: merge MCP config into settings.json (Daniel's method)
if (-not $cliRegistered) {
    $SettingsFile = Join-Path $ClaudeDir "settings.json"
    if (Test-Path $SettingsFile) {
        $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json
    } else {
        $settings = @{}
    }

    if (-not $settings.mcpServers) {
        $settings | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{}
    }

    $settings.mcpServers | Add-Member -NotePropertyName "dataforseo" -NotePropertyValue @{
        command = "npx"
        args = @("-y", "dataforseo-mcp-server")
        env = @{
            DATAFORSEO_USERNAME = $DfLogin
            DATAFORSEO_PASSWORD = $DfPasswordPlain
            ENABLED_MODULES = "SERP,KEYWORDS_DATA,ONPAGE,DATAFORSEO_LABS,BACKLINKS,DOMAIN_ANALYTICS,BUSINESS_DATA,CONTENT_ANALYSIS,AI_OPTIMIZATION"
            FIELD_CONFIG_PATH = $FieldConfigPath
        }
    } -Force

    $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile
    Write-Host "[+] Configured MCP server in settings.json" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== DataForSEO Extension Installed ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usage: /github dataforseo keywords 'react state management'"
