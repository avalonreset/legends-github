#!/usr/bin/env bash
# Bulk invite community members to the GitHub organization
#
# Usage:
#   bash scripts/invite-members.sh <org-name> <team-slug> <emails-file>
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

set -euo pipefail

ORG="${1:?Usage: $0 <org-name> <team-slug> <emails-file>}"
TEAM="${2:?Usage: $0 <org-name> <team-slug> <emails-file>}"
EMAILS_FILE="${3:?Usage: $0 <org-name> <team-slug> <emails-file>}"

if [[ ! -f "$EMAILS_FILE" ]]; then
  echo "Error: File not found: $EMAILS_FILE"
  exit 1
fi

# Get team ID
TEAM_ID=$(gh api "orgs/$ORG/teams/$TEAM" --jq '.id' 2>/dev/null) || {
  echo "Error: Team '$TEAM' not found in org '$ORG'"
  echo "Create it first: gh api --method POST orgs/$ORG/teams -f name='$TEAM' -f permission=pull"
  exit 1
}

echo "Organization: $ORG"
echo "Team: $TEAM (ID: $TEAM_ID)"
echo ""

SUCCESS=0
FAILED=0
SKIPPED=0

while IFS= read -r email || [[ -n "$email" ]]; do
  # Skip empty lines and comments
  email=$(echo "$email" | xargs)
  [[ -z "$email" || "$email" == \#* ]] && continue

  echo -n "Inviting $email ... "

  RESPONSE=$(gh api --method POST "orgs/$ORG/invitations" \
    -f "email=$email" \
    -f "role=direct_member" \
    -F "team_ids[]=$TEAM_ID" \
    2>&1) && {
    echo "OK"
    ((SUCCESS++))
  } || {
    if echo "$RESPONSE" | grep -q "already a member"; then
      echo "SKIPPED (already a member)"
      ((SKIPPED++))
    elif echo "$RESPONSE" | grep -q "already been invited"; then
      echo "SKIPPED (already invited)"
      ((SKIPPED++))
    else
      echo "FAILED: $RESPONSE"
      ((FAILED++))
    fi
  }
done < "$EMAILS_FILE"

echo ""
echo "Done. Invited: $SUCCESS | Skipped: $SKIPPED | Failed: $FAILED"
