# Claude GitHub - Installation Script (Windows PowerShell)
# Installs the GitHub optimization skill suite for Claude Code

$ErrorActionPreference = "Stop"

Clear-Host
Write-Host ""
Write-Host @"
    ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗
   ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
   ██║     ██║     ███████║██║   ██║██║  ██║█████╗
   ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝
   ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗
    ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝

    ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗
   ██╔════╝ ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗
   ██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝
   ██║   ██║██║   ██║   ██╔══██║██║   ██║██╔══██╗
   ╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝
    ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝
"@ -ForegroundColor Cyan

Write-Host "   " -NoNewline
Write-Host "░▒▓" -NoNewline -ForegroundColor Magenta
Write-Host " v1.1 " -NoNewline -ForegroundColor Green
Write-Host "▓▒░" -NoNewline -ForegroundColor Magenta
Write-Host "  Repository Optimization Skills for Claude Code" -ForegroundColor DarkGray
Write-Host ""

# Check prerequisites
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "   [!] GitHub CLI (gh) not detected" -ForegroundColor Yellow
    Write-Host "       Required for repo operations. Install: winget install GitHub.cli" -ForegroundColor DarkGray
    Write-Host ""
}

# Determine Claude skills directory
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"
$SkillsDir = Join-Path $ClaudeDir "skills"
$AgentsDir = Join-Path $ClaudeDir "agents"

# Create directories
$dirs = @(
    (Join-Path $SkillsDir "github\references"),
    (Join-Path $SkillsDir "github-audit"),
    (Join-Path $SkillsDir "github-readme"),
    (Join-Path $SkillsDir "github-legal"),
    (Join-Path $SkillsDir "github-meta"),
    (Join-Path $SkillsDir "github-seo"),
    (Join-Path $SkillsDir "github-community"),
    (Join-Path $SkillsDir "github-release"),
    (Join-Path $SkillsDir "github-empire"),
    $AgentsDir
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "   " -NoNewline
Write-Host "Installing skills..." -ForegroundColor Cyan
Write-Host ""

Copy-Item (Join-Path $ScriptDir "github\SKILL.md") (Join-Path $SkillsDir "github\SKILL.md") -Force
Write-Host "   " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " Orchestrator        " -NoNewline
Write-Host "routes commands to 8 sub-skills" -ForegroundColor DarkGray

Copy-Item (Join-Path $ScriptDir "github\references\*.md") (Join-Path $SkillsDir "github\references\") -Force
Write-Host "   " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 9 Reference Files   " -NoNewline
Write-Host "SEO, legal, readme, community guides" -ForegroundColor DarkGray

$skills = @("github-audit", "github-readme", "github-legal", "github-meta", "github-seo", "github-community", "github-release", "github-empire")
foreach ($skill in $skills) {
    Copy-Item (Join-Path $ScriptDir "skills\$skill\SKILL.md") (Join-Path $SkillsDir "$skill\SKILL.md") -Force
}
Write-Host "   " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 8 Sub-Skills        " -NoNewline
Write-Host "audit, readme, legal, meta, seo, community, release, empire" -ForegroundColor DarkGray

$agents = @("github-readme", "github-legal", "github-meta", "github-community", "github-release", "github-seo")
foreach ($agent in $agents) {
    Copy-Item (Join-Path $ScriptDir "agents\$agent.md") (Join-Path $AgentsDir "$agent.md") -Force
}
Write-Host "   " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 6 Scoring Agents    " -NoNewline
Write-Host "parallel audit across 6 categories" -ForegroundColor DarkGray

Write-Host ""
Write-Host "   Skills installed." -ForegroundColor Green

# ─────────────────────────────────────────────────
# GUIDED SETUP: DataForSEO
# ─────────────────────────────────────────────────
Write-Host ""
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host "    SERVICE SETUP" -ForegroundColor Yellow
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host ""
Write-Host "   Two services are " -NoNewline
Write-Host "strongly recommended" -NoNewline -ForegroundColor White
Write-Host " to unlock the full suite."
Write-Host "   Setting them up takes about 5 minutes and is well worth it."
Write-Host ""

Write-Host "   " -NoNewline
Write-Host "--- 1/2 ---" -NoNewline -ForegroundColor Magenta
Write-Host " " -NoNewline
Write-Host "DataForSEO" -NoNewline -ForegroundColor White
Write-Host " (live keyword data, SERP rankings, AI visibility)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   This powers real keyword research with actual search volume and"
Write-Host "   difficulty data. Without it, SEO recommendations are best-guess only."
Write-Host ""

$DataForSeoDone = $false
$setupDfs = Read-Host "   Set up DataForSEO now? (y/n)"
Write-Host ""

if ($setupDfs -match "^[Yy]") {
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if (-not $nodeCmd) {
        Write-Host "   [!] Node.js is required for the DataForSEO MCP server." -ForegroundColor Yellow
        Write-Host "       Install it from https://nodejs.org/ and re-run this installer." -ForegroundColor DarkGray
        Write-Host "       Skipping DataForSEO for now." -ForegroundColor DarkGray
    } else {
        $nodeVer = [int](node -v).TrimStart('v').Split('.')[0]
        if ($nodeVer -lt 20) {
            Write-Host "   [!] Node.js 20+ required. You have $(node -v)." -ForegroundColor Yellow
            Write-Host "       Update Node.js and re-run this installer." -ForegroundColor DarkGray
        } else {
            Write-Host "   If you don't have an account yet:" -ForegroundColor DarkGray
            Write-Host "     1. Sign up free at " -NoNewline -ForegroundColor DarkGray
            Write-Host "https://dataforseo.com" -ForegroundColor Cyan
            Write-Host "     2. Find your login + password at " -NoNewline -ForegroundColor DarkGray
            Write-Host "https://app.dataforseo.com/api-access" -ForegroundColor Cyan
            Write-Host ""
            $DfLogin = Read-Host "   DataForSEO Login (email)"
            $DfPassword = Read-Host "   DataForSEO Password" -AsSecureString
            $DfPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($DfPassword))
            Write-Host ""

            if ($DfLogin -and $DfPasswordPlain) {
                # Install DataForSEO skill and agent
                $dfSkillDir = Join-Path $SkillsDir "github-dataforseo"
                if (-not (Test-Path $dfSkillDir)) { New-Item -ItemType Directory -Path $dfSkillDir -Force | Out-Null }
                Copy-Item (Join-Path $ScriptDir "extensions\dataforseo\skills\github-dataforseo\SKILL.md") (Join-Path $dfSkillDir "SKILL.md") -Force
                Copy-Item (Join-Path $ScriptDir "extensions\dataforseo\agents\github-dataforseo.md") (Join-Path $AgentsDir "github-dataforseo.md") -Force

                # Pre-download MCP server
                Write-Host "   Downloading DataForSEO MCP server..." -ForegroundColor DarkGray
                npx -y @anthropic/data-for-seo-mcp --version 2>$null | Out-Null

                # Configure MCP server
                $SettingsFile = Join-Path $ClaudeDir "settings.json"
                try {
                    if (Test-Path $SettingsFile) {
                        $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json -AsHashtable
                    } else {
                        $settings = @{}
                    }
                    if (-not $settings.ContainsKey('mcpServers')) { $settings['mcpServers'] = @{} }
                    $settings['mcpServers']['dataforseo'] = @{
                        command = 'npx'
                        args = @('-y', '@anthropic/data-for-seo-mcp')
                        env = @{
                            DATAFORSEO_LOGIN = $DfLogin
                            DATAFORSEO_PASSWORD = $DfPasswordPlain
                        }
                    }
                    $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
                    Write-Host "   " -NoNewline
                    Write-Host "[+]" -NoNewline -ForegroundColor Green
                    Write-Host " DataForSEO          " -NoNewline
                    Write-Host "MCP server configured" -ForegroundColor DarkGray
                    $DataForSeoDone = $true
                } catch {
                    Write-Host "   [!] Could not auto-configure. You can set it up manually later:" -ForegroundColor Yellow
                    Write-Host "       claude mcp add dataforseo-mcp-server" -ForegroundColor DarkGray
                }
            } else {
                Write-Host "   No credentials entered. Skipping DataForSEO." -ForegroundColor DarkGray
            }
        }
    }
} else {
    Write-Host "   Skipped. You can set it up later:" -ForegroundColor DarkGray
    Write-Host "     powershell -File extensions\dataforseo\install.ps1" -ForegroundColor DarkGray
}

# ─────────────────────────────────────────────────
# GUIDED SETUP: KIE.ai
# ─────────────────────────────────────────────────
Write-Host ""
Write-Host "   " -NoNewline
Write-Host "--- 2/2 ---" -NoNewline -ForegroundColor Magenta
Write-Host " " -NoNewline
Write-Host "KIE.ai" -NoNewline -ForegroundColor White
Write-Host " (AI-generated banners and profile avatars)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   This generates professional banner images for READMEs and"
Write-Host "   AI profile avatars for your GitHub account. About 4 cents per image."
Write-Host "   Without it, image generation is skipped entirely."
Write-Host ""

$EnvFile = Join-Path $SkillsDir "github\.env"
$KieDone = $false
$setupKie = Read-Host "   Set up KIE.ai now? (y/n)"
Write-Host ""

if ($setupKie -match "^[Yy]") {
    Write-Host "   If you don't have an account yet:" -ForegroundColor DarkGray
    Write-Host "     1. Go to " -NoNewline -ForegroundColor DarkGray
    Write-Host "https://kie.ai/api-key" -ForegroundColor Cyan
    Write-Host "     2. Create an account and copy your API key" -ForegroundColor DarkGray
    Write-Host ""
    $KieKey = Read-Host "   KIE.ai API Key"
    Write-Host ""

    if ($KieKey) {
        # Write or update .env
        if ((Test-Path $EnvFile) -and (Select-String -Path $EnvFile -Pattern "^KIE_API_KEY=" -Quiet)) {
            (Get-Content $EnvFile) -replace "^KIE_API_KEY=.*", "KIE_API_KEY=$KieKey" | Set-Content $EnvFile -Encoding UTF8
        } else {
            "KIE_API_KEY=$KieKey" | Add-Content $EnvFile -Encoding UTF8
        }
        Write-Host "   " -NoNewline
        Write-Host "[+]" -NoNewline -ForegroundColor Green
        Write-Host " KIE.ai              " -NoNewline
        Write-Host "API key saved to .env" -ForegroundColor DarkGray
        $KieDone = $true
    } else {
        Write-Host "   No key entered. Skipping KIE.ai." -ForegroundColor DarkGray
    }
} else {
    Write-Host "   Skipped. You can add your key later to:" -ForegroundColor DarkGray
    Write-Host "     ~\.claude\skills\github\.env" -ForegroundColor DarkGray
}

# Create .env template if it doesn't exist yet (user skipped both)
if (-not (Test-Path $EnvFile)) {
    @"
# Claude GitHub - API Credentials
#
# KIE.ai — AI-generated banner images for READMEs
# Get your API key: https://kie.ai/api-key
KIE_API_KEY=
#
# DataForSEO credentials are NOT stored here.
# They are configured via the MCP server installer:
#   powershell -File extensions\dataforseo\install.ps1
# See: https://dataforseo.com (free tier available)
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
}

# ─────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────
Write-Host ""
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host "    SETUP COMPLETE" -ForegroundColor Green
Write-Host "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Magenta
Write-Host ""

$dfsStatus = if ($DataForSeoDone) { "active" } else { "not configured" }
$dfsColor = if ($DataForSeoDone) { "Green" } else { "Yellow" }
$kieStatus = if ($KieDone) { "active" } else { "not configured" }
$kieColor = if ($KieDone) { "Green" } else { "Yellow" }
Write-Host "   DataForSEO [" -NoNewline
Write-Host $dfsStatus -NoNewline -ForegroundColor $dfsColor
Write-Host "]  |  KIE.ai [" -NoNewline
Write-Host $kieStatus -NoNewline -ForegroundColor $kieColor
Write-Host "]"
Write-Host ""

Write-Host "   " -NoNewline
Write-Host "Next step: restart Claude Code so the new skills load." -ForegroundColor White
Write-Host ""
Write-Host "   How to restart:" -ForegroundColor Magenta
Write-Host "   1. " -NoNewline -ForegroundColor Cyan
Write-Host "Type " -NoNewline
Write-Host "/exit" -NoNewline -ForegroundColor White
Write-Host " to quit Claude Code"
Write-Host "   2. " -NoNewline -ForegroundColor Cyan
Write-Host "Run " -NoNewline
Write-Host "claude" -NoNewline -ForegroundColor White
Write-Host " again from your project folder"
Write-Host "   3. " -NoNewline -ForegroundColor Cyan
Write-Host "(optional) " -NoNewline -ForegroundColor DarkGray
Write-Host "Type " -NoNewline
Write-Host "/resume" -NoNewline -ForegroundColor White
Write-Host " to pick up where you left off"
Write-Host ""
Write-Host "   Important:" -NoNewline -ForegroundColor Magenta
Write-Host " Run skills from inside the project you want to optimize."
Write-Host "   The skills read your source code, configs, and git remote to make" -ForegroundColor DarkGray
Write-Host "   informed recommendations. Running from an empty folder won't work well." -ForegroundColor DarkGray
Write-Host ""
Write-Host "   Available commands:" -ForegroundColor Magenta
Write-Host ""
Write-Host "   /github audit           " -NoNewline -ForegroundColor Cyan
Write-Host "Score your repo 0-100 across 6 categories" -ForegroundColor DarkGray
Write-Host "   /github readme          " -NoNewline -ForegroundColor Cyan
Write-Host "Generate a keyword-optimized README" -ForegroundColor DarkGray
Write-Host "   /github legal           " -NoNewline -ForegroundColor Cyan
Write-Host "LICENSE, SECURITY.md, CITATION.cff" -ForegroundColor DarkGray
Write-Host "   /github meta            " -NoNewline -ForegroundColor Cyan
Write-Host "Description, topics, feature toggles" -ForegroundColor DarkGray
Write-Host "   /github seo             " -NoNewline -ForegroundColor Cyan
Write-Host "Live keyword research and SERP analysis" -ForegroundColor DarkGray
Write-Host "   /github community       " -NoNewline -ForegroundColor Cyan
Write-Host "Issue templates, CONTRIBUTING, CODE_OF_CONDUCT" -ForegroundColor DarkGray
Write-Host "   /github release         " -NoNewline -ForegroundColor Cyan
Write-Host "CHANGELOG, versioning, badges" -ForegroundColor DarkGray
Write-Host "   /github empire          " -NoNewline -ForegroundColor Cyan
Write-Host "Portfolio strategy across all repos" -ForegroundColor DarkGray
Write-Host ""
