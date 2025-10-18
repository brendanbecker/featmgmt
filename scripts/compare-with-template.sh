#!/bin/bash
# compare-with-template.sh - Compare a project with featmgmt templates
#
# Usage: ./scripts/compare-with-template.sh <target-path> <type>
#
# Arguments:
#   target-path   - Path to feature-management directory
#   type          - Project type: "standard" or "gitops"
#
# Example:
#   ./scripts/compare-with-template.sh /home/becker/projects/triager/feature-management standard

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory (featmgmt repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEATMGMT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: $0 <target-path> <type>"
    echo ""
    echo "Arguments:"
    echo "  target-path   - Path to feature-management directory"
    echo "  type          - Project type: 'standard' or 'gitops'"
    echo ""
    echo "Example:"
    echo "  $0 /home/becker/projects/triager/feature-management standard"
    exit 1
fi

TARGET_PATH="$1"
PROJECT_TYPE="$2"

# Validate inputs
if [[ "$PROJECT_TYPE" != "standard" && "$PROJECT_TYPE" != "gitops" ]]; then
    echo -e "${RED}Error: Project type must be 'standard' or 'gitops'${NC}"
    exit 1
fi

if [ ! -d "$TARGET_PATH" ]; then
    echo -e "${RED}Error: Target path does not exist: $TARGET_PATH${NC}"
    exit 1
fi

# Get project info
PROJECT_NAME="Unknown"
if [ -f "$TARGET_PATH/.featmgmt-config.json" ]; then
    PROJECT_NAME=$(jq -r '.project_name' "$TARGET_PATH/.featmgmt-config.json")
fi

echo -e "${BLUE}Comparison Report: $PROJECT_NAME vs featmgmt $PROJECT_TYPE template${NC}"
echo "========================================================================"
echo ""
echo "Target: $TARGET_PATH"
echo "Template: $PROJECT_TYPE variant"
echo ""

# Function to compare files
compare_file() {
    local filename=$1
    local template_file=$2
    local target_file="$TARGET_PATH/$filename"

    if [ ! -f "$template_file" ]; then
        return
    fi

    if [ ! -f "$target_file" ]; then
        echo -e "${RED}✗ $filename${NC} - MISSING FROM PROJECT"
        return
    fi

    if diff -q "$target_file" "$template_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $filename${NC} - Exact match with template"
    else
        echo -e "${YELLOW}⚠ $filename${NC} - Has local modifications"
        echo "  Differences:"
        diff -u "$template_file" "$target_file" | grep -E "^[\+\-]" | grep -v "^[\+\-][\+\-][\+\-]" | head -10 | sed 's/^/    /'
        local line_count=$(diff "$template_file" "$target_file" | wc -l)
        if [ "$line_count" -gt 20 ]; then
            echo "    ... ($(($line_count - 20)) more lines differ)"
        fi
    fi
    echo ""
}

# Compare key files
echo "=== MATCHES TEMPLATE ==="
echo ""

compare_file "OVERPROMPT.md" "$FEATMGMT_ROOT/templates/OVERPROMPT-${PROJECT_TYPE}.md"
compare_file "agent_actions.md" "$FEATMGMT_ROOT/templates/agent_actions.md"
compare_file ".gitignore" "$FEATMGMT_ROOT/templates/.gitignore"

# Check for extra files
echo "=== EXTRA FILES (not in template) ==="
echo ""

# List project-specific content (expected to be different)
if [ -d "$TARGET_PATH/bugs" ]; then
    BUG_COUNT=$(find "$TARGET_PATH/bugs" -type d -name "BUG-*" | wc -l)
    FEAT_COUNT=$(find "$TARGET_PATH/features" -type d -name "FEAT-*" 2>/dev/null | wc -l || echo 0)
    echo -e "${GREEN}+ bugs/${NC} - $BUG_COUNT bug directories (expected)"
    echo -e "${GREEN}+ features/${NC} - $FEAT_COUNT feature directories (expected)"
fi

if [ -d "$TARGET_PATH/completed" ]; then
    COMPLETED_COUNT=$(find "$TARGET_PATH/completed" -type d -depth 1 | wc -l)
    echo -e "${GREEN}+ completed/${NC} - $COMPLETED_COUNT completed items (expected)"
fi

if [ -d "$TARGET_PATH/agent_runs" ]; then
    RUN_COUNT=$(find "$TARGET_PATH/agent_runs" -type f -name "*.md" 2>/dev/null | wc -l || echo 0)
    echo -e "${GREEN}+ agent_runs/${NC} - $RUN_COUNT session reports (expected)"
fi

# Check for unexpected extra files
for file in "$TARGET_PATH"/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if [[ "$filename" != "OVERPROMPT.md" && "$filename" != "README.md" && "$filename" != "agent_actions.md" ]]; then
            echo -e "${YELLOW}+ $filename${NC} - Additional documentation file"
        fi
    fi
done

echo ""
echo "=== MISSING FROM PROJECT ==="
echo ""

# Check if expected template files exist
MISSING_COUNT=0

if [ ! -f "$TARGET_PATH/OVERPROMPT.md" ]; then
    echo -e "${RED}- OVERPROMPT.md${NC}"
    ((MISSING_COUNT++))
fi

if [ ! -f "$TARGET_PATH/agent_actions.md" ]; then
    echo -e "${RED}- agent_actions.md${NC}"
    ((MISSING_COUNT++))
fi

if [ ! -f "$TARGET_PATH/.gitignore" ]; then
    echo -e "${RED}- .gitignore${NC}"
    ((MISSING_COUNT++))
fi

if [ ! -f "$TARGET_PATH/README.md" ]; then
    echo -e "${YELLOW}- README.md (recommended)${NC}"
fi

if [ $MISSING_COUNT -eq 0 ]; then
    echo -e "${GREEN}None - All template files present${NC}"
fi

echo ""
echo "=== VERSION INFO ==="
echo ""

if [ -f "$TARGET_PATH/.featmgmt-version" ]; then
    CURRENT_VERSION=$(cat "$TARGET_PATH/.featmgmt-version")
    LATEST_VERSION=$(cat "$FEATMGMT_ROOT/VERSION")
    echo "Current version: $CURRENT_VERSION"
    echo "Latest version: $LATEST_VERSION"

    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        echo -e "${GREEN}Status: Up to date${NC}"
    else
        echo -e "${YELLOW}Status: Update available${NC}"
    fi
else
    echo -e "${RED}Not managed by featmgmt (no .featmgmt-version file)${NC}"
fi

echo ""
echo "=== RECOMMENDATION ==="
echo ""

if [ -f "$TARGET_PATH/.featmgmt-version" ]; then
    CURRENT_VERSION=$(cat "$TARGET_PATH/.featmgmt-version")
    LATEST_VERSION=$(cat "$FEATMGMT_ROOT/VERSION")

    if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
        echo -e "${YELLOW}Update recommended${NC}"
        echo "Run: $SCRIPT_DIR/update-project.sh $TARGET_PATH"
    elif [ $MISSING_COUNT -gt 0 ]; then
        echo -e "${YELLOW}Some template files missing${NC}"
        echo "Consider adding missing files manually or re-initialize"
    else
        echo -e "${GREEN}Project is well-maintained with featmgmt pattern${NC}"
        echo "Local customizations documented and preserved."
    fi
else
    echo -e "${YELLOW}To adopt featmgmt pattern:${NC}"
    echo "1. Create .featmgmt-version file"
    echo "2. Create .featmgmt-config.json with project metadata"
    echo "3. Run update-project.sh to synchronize with template"
fi

echo ""
