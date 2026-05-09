# Codex GitHub - Installation Script (Windows PowerShell)
# Installs the GitHub optimization skill suite for Codex.

param(
    [switch]$SkipPythonDeps
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host "   [+] " -NoNewline -ForegroundColor Green
    Write-Host $Message
}

function Invoke-CodexPython {
    param([string[]]$PythonArgs)
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 @PythonArgs
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python @PythonArgs
    } else {
        throw "Python 3.10+ is required for the headless runtime."
    }
}

Clear-Host
Write-Host ""
Write-Host "    CODEX GITHUB" -ForegroundColor Cyan
Write-Host "    GitHub repository optimization skills for Codex" -ForegroundColor DarkGray
Write-Host ""

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "   [!] GitHub CLI (gh) not detected" -ForegroundColor Yellow
    Write-Host "       Required for live repo operations. Install: winget install GitHub.cli" -ForegroundColor DarkGray
    Write-Host ""
}

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$SkillsDir = Join-Path $CodexHome "skills"
$AgentsDir = Join-Path $CodexHome "agents"
$GithubSkillDir = Join-Path $SkillsDir "github"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$dirs = @(
    (Join-Path $GithubSkillDir "references"),
    (Join-Path $GithubSkillDir "scripts"),
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

Copy-Item (Join-Path $ScriptDir "github\SKILL.md") (Join-Path $GithubSkillDir "SKILL.md") -Force
Copy-Item (Join-Path $ScriptDir "github\requirements.txt") (Join-Path $GithubSkillDir "requirements.txt") -Force
Copy-Item (Join-Path $ScriptDir "github\references\*.md") (Join-Path $GithubSkillDir "references\") -Force
Copy-Item (Join-Path $ScriptDir "github\scripts\*.py") (Join-Path $GithubSkillDir "scripts\") -Force
Write-Step "Installed orchestrator, references, and headless runtime"

$skills = @("github-audit", "github-legal", "github-community", "github-release", "github-seo", "github-meta", "github-readme", "github-empire")
foreach ($skill in $skills) {
    Copy-Item (Join-Path $ScriptDir "skills\$skill\SKILL.md") (Join-Path $SkillsDir "$skill\SKILL.md") -Force
}
Write-Step "Installed 8 specialized Codex skills"

$agents = @("github-legal", "github-community", "github-release", "github-seo", "github-meta", "github-readme")
foreach ($agent in $agents) {
    Copy-Item (Join-Path $ScriptDir "agents\$agent.md") (Join-Path $AgentsDir "$agent.md") -Force
}
Write-Step "Installed scoring-agent reference files"

if (-not $SkipPythonDeps) {
    try {
        Invoke-CodexPython @("-m", "pip", "install", "--user", "-r", (Join-Path $GithubSkillDir "requirements.txt"))
        Write-Step "Installed Python runtime dependencies"
    } catch {
        Write-Host "   [!] Python dependency install failed. Run manually:" -ForegroundColor Yellow
        Write-Host "       py -3 -m pip install --user -r `"$GithubSkillDir\requirements.txt`"" -ForegroundColor DarkGray
    }
}

$EnvFile = Join-Path $GithubSkillDir ".env"
if (-not (Test-Path $EnvFile)) {
    @"
# Codex GitHub - API Credentials
#
# KIE.ai -- AI-generated banner images for READMEs
# Get your API key: https://kie.ai/api-key
KIE_API_KEY=
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
}

Write-Host ""
$setupKie = Read-Host "   Set up KIE.ai now for banner/social images? (y/n)"
if ($setupKie -match "^[Yy]") {
    $KieKey = Read-Host "   KIE.ai API Key"
    if ($KieKey) {
        if ((Test-Path $EnvFile) -and (Select-String -Path $EnvFile -Pattern "^KIE_API_KEY=" -Quiet)) {
            (Get-Content $EnvFile) -replace "^KIE_API_KEY=.*", "KIE_API_KEY=$KieKey" | Set-Content $EnvFile -Encoding UTF8
        } else {
            "KIE_API_KEY=$KieKey" | Add-Content $EnvFile -Encoding UTF8
        }
        Write-Step "Saved KIE.ai key to $EnvFile"
    }
}

Write-Host ""
$setupDfs = Read-Host "   Configure DataForSEO MCP for Codex now? (y/n)"
if ($setupDfs -match "^[Yy]") {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host "   [!] Node.js is required for the DataForSEO MCP server." -ForegroundColor Yellow
    } else {
        $DfLogin = Read-Host "   DataForSEO Login"
        $DfPassword = Read-Host "   DataForSEO Password"
        if ($DfLogin -and $DfPassword) {
            Invoke-CodexPython @((Join-Path $GithubSkillDir "scripts\setup_dataforseo.py"), "--login", $DfLogin, "--password", $DfPassword)
            Write-Step "Configured DataForSEO in $CodexHome\config.toml"
        }
    }
}

Write-Host ""
Write-Host "   Setup complete." -ForegroundColor Green
Write-Host "   Restart Codex, then use: github-audit, github-readme, github-meta, github-seo, github-legal, github-community, github-release, github-empire" -ForegroundColor DarkGray
Write-Host "   Headless check: py -3 `"$GithubSkillDir\scripts\run_headless.py`" verify --mode cli --path . --allow-missing-gh-auth" -ForegroundColor DarkGray
