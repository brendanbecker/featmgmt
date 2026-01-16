#!/bin/bash
# sync-agents.sh - Sync skills to agent definitions
#
# Usage: ./scripts/sync-agents.sh [--global] <type> [project-root]
#
# Arguments:
#   --global      - Install to global ~/.claude/agents/ (optional)
#   type          - Project type: "standard" or "gitops"
#   project-root  - Path to project root directory (required for local install)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEATMGMT_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$FEATMGMT_ROOT/skills"

# Argument Parsing
GLOBAL=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --global)
      GLOBAL=true
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [ "$GLOBAL" = true ]; then
    if [ "$#" -lt 1 ]; then
        echo -e "${RED}Error: Missing type argument${NC}"
        exit 1
    fi
    PROJECT_TYPE="$1"
    PROJECT_ROOT="$HOME"
    AGENTS_DIR="$HOME/.claude/agents"
else
    if [ "$#" -lt 2 ]; then
        echo -e "${RED}Error: Missing type or project-root argument${NC}"
        exit 1
    fi
    PROJECT_TYPE="$1"
    PROJECT_ROOT="$2"
    AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
fi

mkdir -p "$AGENTS_DIR"
echo -e "${GREEN}Syncing $PROJECT_TYPE skills to $AGENTS_DIR...${NC}"

# Function to copy skill prompt to agent file
sync_skill() {
    local skill_name=$1
    local agent_name=$2
    local src="$SKILLS_DIR/$skill_name/SKILL.md"
    
    if [ -f "$src" ]; then
        # Add frontmatter if missing (basic)
        if ! grep -q "^---" "$src"; then
            echo "---" > "$AGENTS_DIR/$agent_name.md"
            echo "name: $agent_name" >> "$AGENTS_DIR/$agent_name.md"
            echo "description: Agent derived from skill $skill_name" >> "$AGENTS_DIR/$agent_name.md"
            echo "---" >> "$AGENTS_DIR/$agent_name.md"
            cat "$src" >> "$AGENTS_DIR/$agent_name.md"
        else
            cp "$src" "$AGENTS_DIR/$agent_name.md"
        fi
        echo -e "  ${GREEN}✓${NC} $agent_name ($skill_name)"
    else
        echo -e "  ${RED}✗${NC} Skill $skill_name not found"
    fi
}

# Standard Skills
if [ "$PROJECT_TYPE" == "standard" ]; then
    sync_skill "scan-prioritize" "scan-prioritize-agent"
    sync_skill "bug-processor" "bug-processor-agent"
    sync_skill "test-runner" "test-runner-agent"
    sync_skill "retrospective" "retrospective-agent"
    sync_skill "work-item-creation" "work-item-creation-agent"
fi

# GitOps Skills
if [ "$PROJECT_TYPE" == "gitops" ]; then
    sync_skill "gitops-infra" "infra-executor-agent"
    sync_skill "gitops-scanner" "task-scanner-agent"
    sync_skill "gitops-verification" "verification-agent"
    # Shared skills often used in gitops too
    sync_skill "retrospective" "retrospective-agent"
    sync_skill "work-item-creation" "work-item-creation-agent"
fi

echo ""
echo -e "${GREEN}Sync Complete.${NC}"
if [ "$GLOBAL" = true ]; then
    echo -e "${YELLOW}Restart Claude Code to pick up changes.${NC}"
fi