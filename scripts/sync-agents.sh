#!/bin/bash
# sync-agents.sh - Sync subagent definitions to global or project .claude directory
#
# Usage: ./scripts/sync-agents.sh [--global] <type> [project-root]
#
# Arguments:
#   --global      - Install to global ~/.claude/agents/ (optional)
#   type          - Project type: "standard" or "gitops"
#   project-root  - Path to project root directory (required for local install)
#
# Examples:
#   ./scripts/sync-agents.sh --global standard
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
    # Global mode: only needs project type
    if [ "$#" -lt 1 ]; then
        echo -e "${RED}Error: Missing required argument${NC}"
        echo "Usage: $0 [--global] <type> [project-root]"
        echo ""
        echo "Arguments:"
        echo "  --global      - Install to global ~/.claude/agents/ (optional)"
        echo "  type          - Project type: 'standard' or 'gitops'"
        echo "  project-root  - Path to project root (required for local install)"
        echo ""
        echo "Examples:"
        echo "  $0 --global standard"
        echo "  $0 standard /home/becker/projects/triager"
        exit 1
    fi
    PROJECT_TYPE="$1"
    PROJECT_ROOT="$HOME"
else
    # Local mode: needs both type and project root
    if [ "$#" -lt 2 ]; then
        echo -e "${RED}Error: Missing required arguments${NC}"
        echo "Usage: $0 [--global] <type> [project-root]"
        echo ""
        echo "Arguments:"
        echo "  --global      - Install to global ~/.claude/agents/ (optional)"
        echo "  type          - Project type: 'standard' or 'gitops'"
        echo "  project-root  - Path to project root (required for local install)"
        echo ""
        echo "Examples:"
        echo "  $0 --global standard"
        echo "  $0 standard /home/becker/projects/triager"
        exit 1
    fi
    PROJECT_TYPE="$1"
    PROJECT_ROOT="$2"
fi

# Validate project type
if [[ "$PROJECT_TYPE" != "standard" && "$PROJECT_TYPE" != "gitops" ]]; then
    echo -e "${RED}Error: Project type must be 'standard' or 'gitops'${NC}"
    exit 1
fi

# Validate project root (skip for global mode since $HOME always exists)
if [ "$GLOBAL" = false ] && [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}Error: Project root does not exist: $PROJECT_ROOT${NC}"
    exit 1
fi

# Create .claude/agents directory if it doesn't exist
if [ "$GLOBAL" = true ]; then
    AGENTS_DIR="$HOME/.claude/agents"
else
    AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
fi
mkdir -p "$AGENTS_DIR"

if [ "$GLOBAL" = true ]; then
    echo -e "${GREEN}Syncing $PROJECT_TYPE agents to global ~/.claude/agents/${NC}"
else
    echo -e "${GREEN}Syncing $PROJECT_TYPE agents to $PROJECT_ROOT/.claude/agents/${NC}"
fi
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

# Check if .claude/settings.local.json exists (only for local mode)
if [ "$GLOBAL" = false ] && [ -f "$PROJECT_ROOT/.claude/settings.local.json" ]; then
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
echo ""
if [ "$GLOBAL" = true ]; then
    echo -e "${YELLOW}⚠️  IMPORTANT: Restart your Claude Code session for agents to be discovered.${NC}"
else
    echo -e "${YELLOW}⚠️  IMPORTANT: Restart your Claude Code session for agents to be discovered.${NC}"
fi
