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
"@ -ForegroundColor Cyan

Write-Host "             +----------------------------+" -ForegroundColor Green
Write-Host "             |    G I T H U B   v1.0      |" -ForegroundColor Green
Write-Host "             +----------------------------+" -ForegroundColor Green
Write-Host ""
Write-Host "  Repository Optimization Skills for Claude Code" -ForegroundColor DarkGray
Write-Host ""

# Check prerequisites
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "  [!] GitHub CLI (gh) not detected" -ForegroundColor Yellow
    Write-Host "      Required for repo operations. Install: winget install GitHub.cli" -ForegroundColor DarkGray
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

# Install with progress
Write-Host "  Installing skill suite..." -ForegroundColor Cyan
Write-Host ""

Copy-Item (Join-Path $ScriptDir "github\SKILL.md") (Join-Path $SkillsDir "github\SKILL.md") -Force
Write-Host "  " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " Orchestrator          " -NoNewline
Write-Host "routes commands to 8 sub-skills" -ForegroundColor DarkGray

Copy-Item (Join-Path $ScriptDir "github\references\*.md") (Join-Path $SkillsDir "github\references\") -Force
Write-Host "  " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 9 Reference Files     " -NoNewline
Write-Host "SEO, legal, readme, community guides" -ForegroundColor DarkGray

$skills = @("github-audit", "github-readme", "github-legal", "github-meta", "github-seo", "github-community", "github-release", "github-empire")
foreach ($skill in $skills) {
    Copy-Item (Join-Path $ScriptDir "skills\$skill\SKILL.md") (Join-Path $SkillsDir "$skill\SKILL.md") -Force
}
Write-Host "  " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 8 Sub-Skills          " -NoNewline
Write-Host "audit, readme, legal, meta, seo, community, releases, empire" -ForegroundColor DarkGray

$agents = @("github-readme", "github-legal", "github-meta", "github-community", "github-release", "github-seo")
foreach ($agent in $agents) {
    Copy-Item (Join-Path $ScriptDir "agents\$agent.md") (Join-Path $AgentsDir "$agent.md") -Force
}
Write-Host "  " -NoNewline
Write-Host "[+]" -NoNewline -ForegroundColor Green
Write-Host " 6 Scoring Agents      " -NoNewline
Write-Host "parallel audit across 6 categories" -ForegroundColor DarkGray

Write-Host ""
Write-Host "  ===============================================" -ForegroundColor Green
Write-Host "    INSTALL COMPLETE" -ForegroundColor Green
Write-Host "  ===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Restart Claude Code" -NoNewline -ForegroundColor White
Write-Host ", then try:"
Write-Host ""
Write-Host "    /github audit          " -NoNewline -ForegroundColor Cyan
Write-Host "Score your repo 0-100 across 6 categories" -ForegroundColor DarkGray
Write-Host "    /github readme         " -NoNewline -ForegroundColor Cyan
Write-Host "Generate a keyword-optimized README" -ForegroundColor DarkGray
Write-Host "    /github legal          " -NoNewline -ForegroundColor Cyan
Write-Host "LICENSE, SECURITY.md, CITATION.cff" -ForegroundColor DarkGray
Write-Host "    /github meta           " -NoNewline -ForegroundColor Cyan
Write-Host "Description, topics, feature toggles" -ForegroundColor DarkGray
Write-Host "    /github seo            " -NoNewline -ForegroundColor Cyan
Write-Host "Live keyword research and SERP analysis" -ForegroundColor DarkGray
Write-Host "    /github community      " -NoNewline -ForegroundColor Cyan
Write-Host "Issue templates, CONTRIBUTING, CODE_OF_CONDUCT" -ForegroundColor DarkGray
Write-Host "    /github release       " -NoNewline -ForegroundColor Cyan
Write-Host "CHANGELOG, versioning, badges" -ForegroundColor DarkGray
Write-Host "    /github empire          " -NoNewline -ForegroundColor Cyan
Write-Host "Portfolio strategy across all repos" -ForegroundColor DarkGray

Write-Host ""
Write-Host "  ===============================================" -ForegroundColor Green
Write-Host "    RECOMMENDED: DataForSEO + KIE.ai" -ForegroundColor Yellow
Write-Host "  ===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  DataForSEO " -NoNewline -ForegroundColor White
Write-Host "(live keyword data, SERP rankings, AI visibility)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "    1. Sign up at " -NoNewline
Write-Host "https://dataforseo.com" -ForegroundColor Cyan
Write-Host "       Free tier includes credits for hundreds of analyses." -ForegroundColor DarkGray
Write-Host ""
Write-Host "    2. Run the DataForSEO installer:"
Write-Host ""
Write-Host "       powershell -File extensions\dataforseo\install.ps1" -ForegroundColor White
Write-Host ""
Write-Host "    3. Add your credentials to " -NoNewline
Write-Host "~\.claude\skills\github\.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "       DATAFORSEO_LOGIN=your_email@example.com" -ForegroundColor White
Write-Host "       DATAFORSEO_PASSWORD=your_api_password" -ForegroundColor White
Write-Host ""
Write-Host "  KIE.ai " -NoNewline -ForegroundColor White
Write-Host "(AI-generated banner images for READMEs)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "    1. Get a key at " -NoNewline
Write-Host "https://kie.ai/api-key" -ForegroundColor Cyan
Write-Host ""
Write-Host "    2. Add to the same " -NoNewline
Write-Host ".env" -NoNewline -ForegroundColor Cyan
Write-Host " file:"
Write-Host ""
Write-Host "       KIE_API_KEY=your_key_here" -ForegroundColor White
Write-Host ""
Write-Host "  Both services make the suite dramatically more powerful." -ForegroundColor DarkGray
Write-Host "  Without them, skills still work but rely on codebase analysis only." -ForegroundColor DarkGray
Write-Host ""
