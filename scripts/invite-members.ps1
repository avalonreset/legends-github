# Bulk invite community members to the GitHub organization
#
# Usage:
#   .\scripts\invite-members.ps1 -Org <org-name> -Team <team-slug> -EmailsFile <path>
#
# The emails file should have one email address per line.
# Members receive an invitation email and must accept to gain access.
#
# Prerequisites:
#   - gh CLI authenticated with admin:org scope
#   - You must be an owner of the organization
#
# To add the required scope:
#   gh auth refresh -s admin:org

param(
    [Parameter(Mandatory=$true)][string]$Org,
    [Parameter(Mandatory=$true)][string]$Team,
    [Parameter(Mandatory=$true)][string]$EmailsFile
)

if (-not (Test-Path $EmailsFile)) {
    Write-Error "File not found: $EmailsFile"
    exit 1
}

# Get team ID
try {
    $teamData = gh api "orgs/$Org/teams/$Team" --jq '.id' 2>&1
    $TeamId = $teamData.Trim()
    if (-not $TeamId -or $TeamId -match 'Not Found') {
        throw "Team not found"
    }
} catch {
    Write-Error "Team '$Team' not found in org '$Org'"
    Write-Host "Create it first: gh api --method POST orgs/$Org/teams -f name='$Team' -f permission=pull"
    exit 1
}

Write-Host "Organization: $Org"
Write-Host "Team: $Team (ID: $TeamId)"
Write-Host ""

$success = 0
$failed = 0
$skipped = 0

Get-Content $EmailsFile | ForEach-Object {
    $email = $_.Trim()
    if (-not $email -or $email.StartsWith('#')) { return }

    Write-Host -NoNewline "Inviting $email ... "

    try {
        $response = gh api --method POST "orgs/$Org/invitations" `
            -f "email=$email" `
            -f "role=direct_member" `
            -F "team_ids[]=$TeamId" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK"
            $success++
        } else {
            if ($response -match 'already a member|already been invited') {
                Write-Host "SKIPPED (already invited/member)"
                $skipped++
            } else {
                Write-Host "FAILED: $response"
                $failed++
            }
        }
    } catch {
        Write-Host "FAILED: $_"
        $failed++
    }
}

Write-Host ""
Write-Host "Done. Invited: $success | Skipped: $skipped | Failed: $failed"
