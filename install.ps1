# Legends GitHub - Installation Script (Windows PowerShell)
# Installs the GitHub optimization skill suite for Claude Code

$ErrorActionPreference = "Stop"

Clear-Host
Write-Host ""
Write-Host "    LEGENDS GITHUB" -ForegroundColor Cyan
Write-Host "    Repository Optimization Skills for Claude Code" -ForegroundColor DarkGray

Write-Host "   " -NoNewline
Write-Host "░▒▓" -NoNewline -ForegroundColor Magenta
Write-Host " v1.3 " -NoNewline -ForegroundColor Green
Write-Host "▓▒░" -NoNewline -ForegroundColor Magenta
Write-Host "  Claude Code installer" -ForegroundColor DarkGray
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
    (Join-Path $SkillsDir "github\scripts"),
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

Copy-Item (Join-Path $ScriptDir "requirements-dataforseo.txt") (Join-Path $SkillsDir "github\requirements-dataforseo.txt") -Force
Copy-Item (Join-Path $ScriptDir "github\requirements.txt") (Join-Path $SkillsDir "github\requirements.txt") -Force
Copy-Item (Join-Path $ScriptDir "github\scripts\*.py") (Join-Path $SkillsDir "github\scripts\") -Force
Write-Host "   " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " Headless Runtime    " -NoNewline
Write-Host "deterministic audit and release helpers" -ForegroundColor DarkGray

$skills = @("github-audit", "github-legal", "github-community", "github-release", "github-seo", "github-meta", "github-readme", "github-empire")
foreach ($skill in $skills) {
    Copy-Item (Join-Path $ScriptDir "skills\$skill\SKILL.md") (Join-Path $SkillsDir "$skill\SKILL.md") -Force
}
Write-Host "   " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 8 Sub-Skills        " -NoNewline
Write-Host "audit, legal, community, release, seo, meta, readme, empire" -ForegroundColor DarkGray

$agents = @("github-legal", "github-community", "github-release", "github-seo", "github-meta", "github-readme")
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
Write-Host "   DataForSEO is optional and only needed for requested live keyword research."
Write-Host "   Local repository workflows do not require a paid service."
Write-Host ""

Write-Host "   " -NoNewline
Write-Host "--- Optional ---" -NoNewline -ForegroundColor Magenta
Write-Host " " -NoNewline
Write-Host "DataForSEO" -NoNewline -ForegroundColor White
Write-Host " (live keyword data and SERP evidence)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   This powers real keyword research with actual search volume and"
Write-Host "   difficulty data. Without it, SEO recommendations are best-guess only."
Write-Host ""

$DataForSeoDone = $false
$setupDfs = Read-Host "   Install legends-dataforseo-kit for live research? (y/n)"
if ($setupDfs -match "^[Yy]") {
    & (Join-Path $ScriptDir "extensions\dataforseo\install.ps1")
    $DataForSeoDone = ($LASTEXITCODE -eq 0)
}

Write-Host "   Optional artwork uses supplied local files; no image service is configured." -ForegroundColor DarkGray

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
Write-Host "   DataForSEO [" -NoNewline
Write-Host $dfsStatus -NoNewline -ForegroundColor $dfsColor
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
Write-Host "   Standard Operating Procedure (run in this order):" -ForegroundColor Magenta
Write-Host ""
Write-Host "   Step 0  " -NoNewline -ForegroundColor White
Write-Host "/github audit       " -NoNewline -ForegroundColor Cyan
Write-Host "Diagnose: score 0-100, generates your SOP" -ForegroundColor DarkGray
Write-Host "   Step 1  " -NoNewline -ForegroundColor White
Write-Host "/github legal       " -NoNewline -ForegroundColor Cyan
Write-Host "Foundation: license, SECURITY.md, CITATION.cff" -ForegroundColor DarkGray
Write-Host "   Step 2  " -NoNewline -ForegroundColor White
Write-Host "/github community   " -NoNewline -ForegroundColor Cyan
Write-Host "Infrastructure: templates, CoC, devcontainer" -ForegroundColor DarkGray
Write-Host "   Step 3  " -NoNewline -ForegroundColor White
Write-Host "/github release     " -NoNewline -ForegroundColor Cyan
Write-Host "Versioning: CHANGELOG, badges, releases" -ForegroundColor DarkGray
Write-Host "   Step 4  " -NoNewline -ForegroundColor White
Write-Host "/github seo         " -NoNewline -ForegroundColor Cyan
Write-Host "Research: keyword data for description + README" -ForegroundColor DarkGray
Write-Host "   Step 5  " -NoNewline -ForegroundColor White
Write-Host "/github meta        " -NoNewline -ForegroundColor Cyan
Write-Host "Settings: description, topics, features" -ForegroundColor DarkGray
Write-Host "   Step 6  " -NoNewline -ForegroundColor White
Write-Host "/github readme      " -NoNewline -ForegroundColor Cyan
Write-Host "Capstone: README optimization with SEO keywords" -ForegroundColor DarkGray
Write-Host "   Step 7  " -NoNewline -ForegroundColor White
Write-Host "/github audit       " -NoNewline -ForegroundColor Cyan
Write-Host "Measure: re-audit to verify improvement" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   After all repos are optimized:" -ForegroundColor DarkGray
Write-Host "           " -NoNewline
Write-Host "/github empire      " -NoNewline -ForegroundColor Cyan
Write-Host "Portfolio strategy, profile README, avatar" -ForegroundColor DarkGray
Write-Host ""
