#!/bin/bash
# init-project.sh - Initialize a new feature-management submodule from featmgmt templates
#
# Usage: ./scripts/init-project.sh <type> <target-path> <project-name> [components...]
#
# Arguments:
#   type          - Project type: "standard" or "gitops"
#   target-path   - Absolute path where to create feature-management directory
#   project-name  - Name of the project (e.g., "triager", "beckerkube")
#   components    - Optional: Comma-separated list of components
#
# Example:
#   ./scripts/init-project.sh standard /home/becker/projects/myapp/feature-management myapp "backend,frontend,api"
#   ./scripts/init-project.sh gitops /home/becker/projects/beckerkube/feature-management beckerkube "infrastructure,builds,deployments"

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory (featmgmt repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEATMGMT_ROOT="$(dirname "$SCRIPT_DIR")"
FEATMGMT_VERSION=$(cat "$FEATMGMT_ROOT/VERSION")

# Parse arguments
if [ "$#" -lt 3 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: $0 <type> <target-path> <project-name> [components...]"
    echo ""
    echo "Arguments:"
    echo "  type          - Project type: 'standard' or 'gitops'"
    echo "  target-path   - Absolute path where to create feature-management directory"
    echo "  project-name  - Name of the project (e.g., 'triager', 'beckerkube')"
    echo "  components    - Optional: Comma-separated list of components"
    echo ""
    echo "Example:"
    echo "  $0 standard ../myapp/feature-management myapp backend,frontend,api"
    exit 1
fi

PROJECT_TYPE="$1"
TARGET_PATH="$2"
PROJECT_NAME="$3"
COMPONENTS="${4:-}"

# Validate project type
if [[ "$PROJECT_TYPE" != "standard" && "$PROJECT_TYPE" != "gitops" ]]; then
    echo -e "${RED}Error: Project type must be 'standard' or 'gitops'${NC}"
    exit 1
fi

# Check if target path already exists
if [ -d "$TARGET_PATH" ]; then
    echo -e "${YELLOW}Warning: Target path already exists: $TARGET_PATH${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    rm -rf "$TARGET_PATH"
fi

echo -e "${GREEN}Initializing $PROJECT_TYPE feature-management for $PROJECT_NAME${NC}"
echo "Target: $TARGET_PATH"
echo "Version: $FEATMGMT_VERSION"
echo ""

# Create target directory
mkdir -p "$TARGET_PATH"

# Copy template files
echo "Copying template files..."
cp "$FEATMGMT_ROOT/templates/OVERPROMPT-${PROJECT_TYPE}.md" "$TARGET_PATH/OVERPROMPT.md"
cp "$FEATMGMT_ROOT/templates/agent_actions.md" "$TARGET_PATH/agent_actions.md"
cp "$FEATMGMT_ROOT/templates/.gitignore" "$TARGET_PATH/.gitignore"

# Create README from template
cp "$FEATMGMT_ROOT/templates/README.md.template" "$TARGET_PATH/README.md"
sed -i "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$TARGET_PATH/README.md"
sed -i "s/{{PROJECT_TYPE}}/$PROJECT_TYPE/g" "$TARGET_PATH/README.md"
sed -i "s/{{FEATMGMT_VERSION}}/$FEATMGMT_VERSION/g" "$TARGET_PATH/README.md"

# Create directory structure
echo "Creating directory structure..."
mkdir -p "$TARGET_PATH/bugs"
mkdir -p "$TARGET_PATH/features"
mkdir -p "$TARGET_PATH/completed"
mkdir -p "$TARGET_PATH/deprecated"
mkdir -p "$TARGET_PATH/human-actions"
mkdir -p "$TARGET_PATH/agent_runs"

# Create summary files
echo "Creating summary files..."
cat > "$TARGET_PATH/bugs/bugs.md" << EOF
# Bug Reports

**Project**: $PROJECT_NAME
**Last Updated**: $(date +%Y-%m-%d)

## Summary Statistics
- Total Bugs: 0
- New: 0
- In Progress: 0
- Resolved: 0

## Bug List

| ID | Title | Priority | Status | Component | Location |
|----|-------|----------|--------|-----------|----------|

EOF

cat > "$TARGET_PATH/features/features.md" << EOF
# Feature Requests

**Project**: $PROJECT_NAME
**Last Updated**: $(date +%Y-%m-%d)

## Summary Statistics
- Total Features: 0
- New: 0
- In Progress: 0
- Implemented: 0

## Feature List

| ID | Title | Priority | Status | Component | Location |
|----|-------|----------|--------|-----------|----------|

EOF

# Create .agent-config.json based on project type and components
echo "Creating .agent-config.json..."

if [ "$PROJECT_TYPE" = "standard" ]; then
    # Standard project tags
    if [ -z "$COMPONENTS" ]; then
        COMPONENTS="backend,frontend,api,database"
    fi

    # Convert components to JSON array
    IFS=',' read -ra COMP_ARRAY <<< "$COMPONENTS"
    TAG_JSON=$(printf ',\n    "%s"' "${COMP_ARRAY[@]}")
    TAG_JSON="${TAG_JSON:1}"  # Remove leading comma

    # Build component keywords
    KEYWORD_JSON=""
    for comp in "${COMP_ARRAY[@]}"; do
        KEYWORD_JSON+=",\n    \"$comp\": [\"$comp\"]"
    done
    KEYWORD_JSON="${KEYWORD_JSON:2}"  # Remove leading comma and newline

    cat > "$TARGET_PATH/.agent-config.json" << EOF
{
  "version": "1.0.0",
  "project_name": "$PROJECT_NAME",
  "project_type": "standard",
  "duplicate_similarity_threshold": 0.75,
  "available_tags": [
    $TAG_JSON,
    "infrastructure",
    "database",
    "api",
    "performance",
    "security",
    "deployment",
    "documentation",
    "crash",
    "bug",
    "enhancement",
    "feature-request"
  ],
  "component_detection_keywords": {
    $KEYWORD_JSON
  },
  "severity_keywords": {
    "critical": ["crash", "data loss", "security", "down", "broken", "unavailable"],
    "high": ["error", "broken", "not working", "fails"],
    "medium": ["issue", "problem", "incorrect"],
    "low": ["typo", "cosmetic", "minor", "suggestion"]
  }
}
EOF
else
    # GitOps project tags
    if [ -z "$COMPONENTS" ]; then
        COMPONENTS="infrastructure,builds,deployments,configs"
    fi

    # Convert components to JSON array
    IFS=',' read -ra COMP_ARRAY <<< "$COMPONENTS"
    TAG_JSON=$(printf ',\n    "%s"' "${COMP_ARRAY[@]}")
    TAG_JSON="${TAG_JSON:1}"  # Remove leading comma

    # Build component keywords
    KEYWORD_JSON=""
    for comp in "${COMP_ARRAY[@]}"; do
        KEYWORD_JSON+=",\n    \"$comp\": [\"$comp\"]"
    done
    KEYWORD_JSON="${KEYWORD_JSON:2}"  # Remove leading comma and newline

    cat > "$TARGET_PATH/.agent-config.json" << EOF
{
  "version": "1.0.0",
  "project_name": "$PROJECT_NAME",
  "project_type": "gitops",
  "duplicate_similarity_threshold": 0.75,
  "available_tags": [
    $TAG_JSON,
    "kubernetes",
    "helm",
    "flux",
    "docker",
    "networking",
    "security",
    "monitoring",
    "deployment",
    "documentation",
    "crash",
    "bug",
    "enhancement",
    "feature-request"
  ],
  "component_detection_keywords": {
    $KEYWORD_JSON
  },
  "severity_keywords": {
    "critical": ["crash", "data loss", "security", "down", "broken", "unavailable"],
    "high": ["error", "broken", "not working", "fails"],
    "medium": ["issue", "problem", "incorrect"],
    "low": ["typo", "cosmetic", "minor", "suggestion"]
  }
}
EOF
fi

# Create .featmgmt-config.json for tracking customizations
echo "Creating .featmgmt-config.json..."

# Build components JSON array
COMPONENTS_JSON=""
for comp in "${COMP_ARRAY[@]}"; do
  if [ -z "$COMPONENTS_JSON" ]; then
    COMPONENTS_JSON="\"$comp\""
  else
    COMPONENTS_JSON="$COMPONENTS_JSON, \"$comp\""
  fi
done

cat > "$TARGET_PATH/.featmgmt-config.json" << EOF
{
  "project_name": "$PROJECT_NAME",
  "project_type": "$PROJECT_TYPE",
  "featmgmt_version": "$FEATMGMT_VERSION",
  "initialized_at": "$(date -Iseconds)",
  "components": [$COMPONENTS_JSON],
  "customizations": {
    "description": "Track any local customizations to preserve during updates"
  }
}
EOF

# Create version file
echo "$FEATMGMT_VERSION" > "$TARGET_PATH/.featmgmt-version"

# Initialize git repository
echo "Initializing git repository..."
cd "$TARGET_PATH"
git init
git add .
git commit -m "Initialize feature-management from featmgmt v$FEATMGMT_VERSION ($PROJECT_TYPE variant)"

echo ""
echo -e "${GREEN}✓ Successfully initialized feature-management for $PROJECT_NAME${NC}"
echo ""
echo "Next steps:"
echo "  1. Review OVERPROMPT.md and customize if needed"
echo "  2. Update .agent-config.json with project-specific tags"
echo "  3. Sync agents to parent project: ../sync-agents.sh $PROJECT_TYPE <parent-project-path>"
echo "  4. Add as submodule to parent project (if applicable)"
echo ""
echo "To add as submodule:"
echo "  cd <parent-project-directory>"
echo "  git submodule add <git-url> feature-management"
