
#!/usr/bin/env bash
# Create GitHub repo using gh CLI and push current repo as `main`.
# Usage: ./scripts/create_github_repo.sh <user_or_org> <repo-name> [--private]

set -euo pipefail
OWNER="$1"
REPO="$2"
PRIVATE_FLAG="${3:---public}"

# Ensure gh is authenticated
if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install it and run 'gh auth login' first."
  exit 2
fi

echo "Creating repo ${OWNER}/${REPO} (${PRIVATE_FLAG}) ..."
gh repo create "${OWNER}/${REPO}" "${PRIVATE_FLAG}" --source . --remote origin --push
echo "Repo created and pushed to https://github.com/${OWNER}/${REPO}"
