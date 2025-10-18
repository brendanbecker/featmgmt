#!/bin/bash
# sync-agents.sh - Sync subagent definitions to project .claude directory
#
# Usage: ./scripts/sync-agents.sh <type> <project-root>
#
# Arguments:
#   type          - Project type: "standard" or "gitops"
#   project-root  - Path to project root directory (parent of .claude/)
#
# Example:
#   ./scripts/sync-agents.sh standard /home/becker/projects/triager
#   ./scripts/sync-agents.sh gitops /home/becker/projects/beckerkube

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory (featmgmt repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEATMGMT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: $0 <type> <project-root>"
    echo ""
    echo "Arguments:"
    echo "  type          - Project type: 'standard' or 'gitops'"
    echo "  project-root  - Path to project root directory (parent of .claude/)"
    echo ""
    echo "Example:"
    echo "  $0 standard /home/becker/projects/triager"
    exit 1
fi

PROJECT_TYPE="$1"
PROJECT_ROOT="$2"

# Validate project type
if [[ "$PROJECT_TYPE" != "standard" && "$PROJECT_TYPE" != "gitops" ]]; then
    echo -e "${RED}Error: Project type must be 'standard' or 'gitops'${NC}"
    exit 1
fi

# Validate project root
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}Error: Project root does not exist: $PROJECT_ROOT${NC}"
    exit 1
fi

# Create .claude/agents directory if it doesn't exist
AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
mkdir -p "$AGENTS_DIR"

echo -e "${GREEN}Syncing $PROJECT_TYPE agents to $PROJECT_ROOT/.claude/agents/${NC}"
echo ""

# Count agents
VARIANT_COUNT=$(ls -1 "$FEATMGMT_ROOT/claude-agents/$PROJECT_TYPE"/*.md 2>/dev/null | wc -l)
SHARED_COUNT=$(ls -1 "$FEATMGMT_ROOT/claude-agents/shared"/*.md 2>/dev/null | wc -l)
TOTAL_COUNT=$((VARIANT_COUNT + SHARED_COUNT))

echo "Agents to sync:"
echo "  - $VARIANT_COUNT $PROJECT_TYPE variant agents"
echo "  - $SHARED_COUNT shared agents"
echo "  - Total: $TOTAL_COUNT agents"
echo ""

# Copy variant-specific agents
if [ -d "$FEATMGMT_ROOT/claude-agents/$PROJECT_TYPE" ]; then
    echo "Copying $PROJECT_TYPE variant agents..."
    for agent in "$FEATMGMT_ROOT/claude-agents/$PROJECT_TYPE"/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            cp "$agent" "$AGENTS_DIR/$agent_name"
            echo -e "  ${GREEN}✓${NC} $agent_name"
        fi
    done
fi

# Copy shared agents
if [ -d "$FEATMGMT_ROOT/claude-agents/shared" ]; then
    echo "Copying shared agents..."
    for agent in "$FEATMGMT_ROOT/claude-agents/shared"/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent")
            cp "$agent" "$AGENTS_DIR/$agent_name"
            echo -e "  ${GREEN}✓${NC} $agent_name"
        fi
    done
fi

echo ""
echo -e "${GREEN}✓ Successfully synced $TOTAL_COUNT agents${NC}"

# Check if .claude/settings.local.json exists
if [ -f "$PROJECT_ROOT/.claude/settings.local.json" ]; then
    echo ""
    echo "Note: .claude/settings.local.json exists."
    echo "You may want to verify agent references in that file."
fi

echo ""
echo "Agents synced to:"
echo "  $AGENTS_DIR"
echo ""
echo "List synced agents:"
echo "  ls -la $AGENTS_DIR"
