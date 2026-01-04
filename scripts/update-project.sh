#!/bin/bash
# update-project.sh - Update an existing feature-management submodule from featmgmt templates
#
# Usage: ./scripts/update-project.sh [--dry-run] <target-path>
#
# Arguments:
#   --dry-run     - Optional: Show what would change without making changes
#   target-path   - Path to existing feature-management directory
#
# Example:
#   ./scripts/update-project.sh --dry-run /home/becker/projects/triager/feature-management
#   ./scripts/update-project.sh /home/becker/projects/triager/feature-management

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
FEATMGMT_VERSION=$(cat "$FEATMGMT_ROOT/VERSION")

# Parse arguments
DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    shift
fi

if [ "$#" -lt 1 ]; then
    echo -e "${RED}Error: Missing target path${NC}"
    echo "Usage: $0 [--dry-run] <target-path>"
    exit 1
fi

TARGET_PATH="$1"

# Validate target path
if [ ! -d "$TARGET_PATH" ]; then
    echo -e "${RED}Error: Target path does not exist: $TARGET_PATH${NC}"
    exit 1
fi

if [ ! -f "$TARGET_PATH/.featmgmt-version" ]; then
    echo -e "${RED}Error: Not a featmgmt-managed project (missing .featmgmt-version)${NC}"
    echo "To adopt featmgmt pattern, manually create .featmgmt-version and .featmgmt-config.json"
    exit 1
fi

# Read current configuration
CURRENT_VERSION=$(cat "$TARGET_PATH/.featmgmt-version")
PROJECT_TYPE=$(jq -r '.project_type' "$TARGET_PATH/.featmgmt-config.json" 2>/dev/null || echo "unknown")

if [ "$PROJECT_TYPE" = "unknown" ] || [ "$PROJECT_TYPE" = "null" ]; then
    echo -e "${RED}Error: Cannot determine project type from .featmgmt-config.json${NC}"
    exit 1
fi

echo -e "${BLUE}Checking for updates...${NC}"
echo "Project: $(jq -r '.project_name' "$TARGET_PATH/.featmgmt-config.json")"
echo "Type: $PROJECT_TYPE"
echo "Current version: $CURRENT_VERSION"
echo "Latest version: $FEATMGMT_VERSION"
echo ""

# Check if already up to date
if [ "$CURRENT_VERSION" = "$FEATMGMT_VERSION" ]; then
    echo -e "${GREEN}Already at latest version!${NC}"
    exit 0
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Create backup (unless dry run)
if [ "$DRY_RUN" = false ]; then
    BACKUP_DIR="${TARGET_PATH}/.featmgmt-backup-$(date +%Y%m%d-%H%M%S)"
    echo "Creating backup at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$TARGET_PATH"/* "$BACKUP_DIR/" 2>/dev/null || true
    cp "$TARGET_PATH"/.* "$BACKUP_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ Backup created${NC}"
    echo ""
fi

# Compare and update files
echo "Comparing files with template..."
echo ""

# Function to show diff
show_diff() {
    local file=$1
    local template=$2
    local label=$3

    if diff -q "$file" "$template" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $label: No changes${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ $label: Changes detected${NC}"
        if [ "$DRY_RUN" = true ]; then
            echo "  Preview of changes:"
            diff -u "$file" "$template" | head -20 || true
            echo ""
        fi
        return 1
    fi
}

# Check OVERPROMPT.md (Claude Code version)
TEMPLATE_OVERPROMPT="$FEATMGMT_ROOT/templates/OVERPROMPT-${PROJECT_TYPE}.md"
OVERPROMPT_CHANGED=0
if [ -f "$TARGET_PATH/OVERPROMPT.md" ]; then
    show_diff "$TARGET_PATH/OVERPROMPT.md" "$TEMPLATE_OVERPROMPT" "OVERPROMPT.md" || OVERPROMPT_CHANGED=$?
else
    echo -e "${YELLOW}⚠ OVERPROMPT.md: Missing (will be created)${NC}"
    OVERPROMPT_CHANGED=1
fi

# Check OVERPROMPT-CODEX.md (Codex CLI version)
TEMPLATE_OVERPROMPT_CODEX="$FEATMGMT_ROOT/templates/OVERPROMPT-codex-${PROJECT_TYPE}.md"
OVERPROMPT_CODEX_CHANGED=0
if [ -f "$TARGET_PATH/OVERPROMPT-CODEX.md" ]; then
    show_diff "$TARGET_PATH/OVERPROMPT-CODEX.md" "$TEMPLATE_OVERPROMPT_CODEX" "OVERPROMPT-CODEX.md" || OVERPROMPT_CODEX_CHANGED=$?
else
    echo -e "${YELLOW}⚠ OVERPROMPT-CODEX.md: Missing (will be created)${NC}"
    OVERPROMPT_CODEX_CHANGED=1
fi

# Check agent_actions.md
if [ -f "$TARGET_PATH/agent_actions.md" ]; then
    show_diff "$TARGET_PATH/agent_actions.md" "$FEATMGMT_ROOT/templates/agent_actions.md" "agent_actions.md" || true
fi

# Check .gitignore
if [ -f "$TARGET_PATH/.gitignore" ]; then
    show_diff "$TARGET_PATH/.gitignore" "$FEATMGMT_ROOT/templates/.gitignore" ".gitignore" || true
fi

# Check schemas directory
echo ""
echo "Checking schemas..."
SCHEMAS_SOURCE="$FEATMGMT_ROOT/feature-management/schemas"
SCHEMAS_TARGET="$TARGET_PATH/schemas"

if [ -d "$SCHEMAS_SOURCE" ]; then
    if [ ! -d "$SCHEMAS_TARGET" ]; then
        echo -e "${YELLOW}⚠ schemas/: Missing (will be created)${NC}"
    else
        # Check each schema file
        for schema_file in "$SCHEMAS_SOURCE"/*.json "$SCHEMAS_SOURCE"/*.md; do
            if [ -f "$schema_file" ]; then
                filename=$(basename "$schema_file")
                if [ -f "$SCHEMAS_TARGET/$filename" ]; then
                    show_diff "$SCHEMAS_TARGET/$filename" "$schema_file" "schemas/$filename" || true
                else
                    echo -e "${YELLOW}⚠ schemas/$filename: Missing (will be created)${NC}"
                fi
            fi
        done
    fi
fi

echo ""

# If dry run, exit here
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Dry run complete. Run without --dry-run to apply updates.${NC}"
    exit 0
fi

# Apply updates
echo "Applying updates..."

# Update OVERPROMPT.md
# Extract current PROJECT_PATH to preserve customizations
if [ $OVERPROMPT_CHANGED -ne 0 ]; then
    echo "Updating OVERPROMPT.md..."

    # Extract current project path from existing OVERPROMPT.md
    CURRENT_PROJECT_PATH=""
    if [ -f "$TARGET_PATH/OVERPROMPT.md" ]; then
        # Look for .claude/agents/ path and extract parent directory
        CURRENT_PROJECT_PATH=$(grep -m1 "\.claude/agents/" "$TARGET_PATH/OVERPROMPT.md" | sed -E 's|.*`(.*)/.claude/agents/`.*|\1|' || echo "")
    fi

    # If we couldn't extract path, calculate from target path
    if [ -z "$CURRENT_PROJECT_PATH" ]; then
        echo -e "${YELLOW}⚠ Could not extract current project path, calculating from target path...${NC}"
        TARGET_PATH_ABS="$(cd "$(dirname "$TARGET_PATH")" 2>/dev/null && pwd)/$(basename "$TARGET_PATH")" || TARGET_PATH_ABS="$TARGET_PATH"
        CURRENT_PROJECT_PATH="$(dirname "$TARGET_PATH_ABS")"
    fi

    # Copy new template
    cp "$TEMPLATE_OVERPROMPT" "$TARGET_PATH/OVERPROMPT.md"

    # Substitute variables to preserve project-specific paths
    sed -i "s|{{PROJECT_PATH}}|$CURRENT_PROJECT_PATH|g" "$TARGET_PATH/OVERPROMPT.md"

    # Get project name and type from config
    PROJECT_NAME=$(jq -r '.project_name' "$TARGET_PATH/.featmgmt-config.json")
    sed -i "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$TARGET_PATH/OVERPROMPT.md"
    sed -i "s|{{PROJECT_TYPE}}|$PROJECT_TYPE|g" "$TARGET_PATH/OVERPROMPT.md"

    echo -e "${GREEN}✓ OVERPROMPT.md updated (project path preserved: $CURRENT_PROJECT_PATH)${NC}"
fi

# Update OVERPROMPT-CODEX.md (Codex CLI version)
if [ $OVERPROMPT_CODEX_CHANGED -ne 0 ]; then
    echo "Updating OVERPROMPT-CODEX.md..."

    # Extract current project path from existing OVERPROMPT-CODEX.md or reuse from above
    if [ -z "$CURRENT_PROJECT_PATH" ]; then
        if [ -f "$TARGET_PATH/OVERPROMPT-CODEX.md" ]; then
            CURRENT_PROJECT_PATH=$(grep -m1 "repo_path:" "$TARGET_PATH/OVERPROMPT-CODEX.md" | sed -E 's|.*repo_path: "(.*)"|\\1|' || echo "")
        fi
        # If still empty, calculate from target path
        if [ -z "$CURRENT_PROJECT_PATH" ]; then
            TARGET_PATH_ABS="$(cd "$(dirname "$TARGET_PATH")" 2>/dev/null && pwd)/$(basename "$TARGET_PATH")" || TARGET_PATH_ABS="$TARGET_PATH"
            CURRENT_PROJECT_PATH="$(dirname "$TARGET_PATH_ABS")"
        fi
    fi

    # Copy new template
    cp "$TEMPLATE_OVERPROMPT_CODEX" "$TARGET_PATH/OVERPROMPT-CODEX.md"

    # Substitute variables to preserve project-specific paths
    sed -i "s|{{PROJECT_PATH}}|$CURRENT_PROJECT_PATH|g" "$TARGET_PATH/OVERPROMPT-CODEX.md"

    # Get project name and type from config
    PROJECT_NAME=$(jq -r '.project_name' "$TARGET_PATH/.featmgmt-config.json")
    sed -i "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$TARGET_PATH/OVERPROMPT-CODEX.md"
    sed -i "s|{{PROJECT_TYPE}}|$PROJECT_TYPE|g" "$TARGET_PATH/OVERPROMPT-CODEX.md"

    echo -e "${GREEN}✓ OVERPROMPT-CODEX.md updated (project path preserved: $CURRENT_PROJECT_PATH)${NC}"
fi

# Update agent_actions.md
if [ -f "$FEATMGMT_ROOT/templates/agent_actions.md" ]; then
    cp "$FEATMGMT_ROOT/templates/agent_actions.md" "$TARGET_PATH/agent_actions.md"
    echo -e "${GREEN}✓ agent_actions.md updated${NC}"
fi

# Update .gitignore
if [ -f "$FEATMGMT_ROOT/templates/.gitignore" ]; then
    cp "$FEATMGMT_ROOT/templates/.gitignore" "$TARGET_PATH/.gitignore"
    echo -e "${GREEN}✓ .gitignore updated${NC}"
fi

# Update schemas directory
if [ -d "$SCHEMAS_SOURCE" ]; then
    mkdir -p "$SCHEMAS_TARGET"
    cp -r "$SCHEMAS_SOURCE"/* "$SCHEMAS_TARGET/"
    echo -e "${GREEN}✓ schemas/ updated${NC}"
fi

# Update version file
echo "$FEATMGMT_VERSION" > "$TARGET_PATH/.featmgmt-version"

# Update .featmgmt-config.json
jq ".featmgmt_version = \"$FEATMGMT_VERSION\" | .updated_at = \"$(date -Iseconds)\"" \
    "$TARGET_PATH/.featmgmt-config.json" > "$TARGET_PATH/.featmgmt-config.json.tmp"
mv "$TARGET_PATH/.featmgmt-config.json.tmp" "$TARGET_PATH/.featmgmt-config.json"

# Log changes
echo ""
echo "Logging changes..."
cat >> "$TARGET_PATH/UPDATE_LOG.md" << EOF

## Update $(date +%Y-%m-%d %H:%M:%S)

Updated from featmgmt v$CURRENT_VERSION → v$FEATMGMT_VERSION

### Files Updated
- OVERPROMPT.md (Claude Code workflow)
- OVERPROMPT-CODEX.md (Codex CLI workflow)
- agent_actions.md
- .gitignore
- schemas/ (work item validation schemas)
- .featmgmt-version
- .featmgmt-config.json

### Backup Location
Backup created at: .featmgmt-backup-$(date +%Y%m%d-%H%M%S)

EOF

echo -e "${GREEN}✓ Changes logged to UPDATE_LOG.md${NC}"

# Commit changes
echo ""
echo "Committing changes..."
cd "$TARGET_PATH"
git add .
git commit -m "Update from featmgmt v$CURRENT_VERSION → v$FEATMGMT_VERSION

- Updated OVERPROMPT.md with latest Claude Code workflow
- Updated OVERPROMPT-CODEX.md with latest Codex CLI workflow
- Updated common files (agent_actions.md, .gitignore)
- Updated schemas/ for work item validation
- Backup created before update"

echo ""
echo -e "${GREEN}✓ Successfully updated to featmgmt v$FEATMGMT_VERSION${NC}"
echo ""
echo "Review changes:"
echo "  git log -1 -p"
echo ""
echo "Rollback if needed:"
echo "  git reset --hard HEAD~1"
echo "  Or restore from backup: .featmgmt-backup-*/"
