#!/bin/bash
# create_bulk_pr.sh
# Creates a PR for bulk test failures

BRANCH_NAME="auto-items-$(date +%Y-%m-%d-%H%M%S)"
echo "Creating branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Note: This script assumes bugs have already been created in file system
git add bugs/ features/

COMMIT_MSG="Auto-created bugs from test failures - $(date +%Y-%m-%d)

Created by: test-runner-skill
Test Run: test-run-$(date +%Y-%m-%d-%H%M%S)
Context: Bulk test failures detected

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "$COMMIT_MSG"
git push -u origin "$BRANCH_NAME"

echo "Branch pushed. Please run 'gh pr create' manually or use the gh CLI if authenticated."
