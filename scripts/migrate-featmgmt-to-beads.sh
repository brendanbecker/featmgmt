#!/bin/bash
# migrate-featmgmt-to-beads.sh
# Converts featmgmt feature-management directories into Beads
#
# Usage:
#   ./scripts/migrate-featmgmt-to-beads.sh --source /path/to/feature-management [options]
#
# Options:
#   --source DIR       Path to feature-management directory (required)
#   --epic NAME        Epic name for migrated beads (default: "Migration")
#   --dry-run          Preview commands without executing
#   --include-completed Include items from completed/ directory
#   --skip-bugs        Skip bug reports, only migrate features
#   --verbose          Show detailed output
#   --help             Show this help message

# set -e  # Disabled - we handle errors manually

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SOURCE_DIR=""
EPIC_NAME="Migration"
DRY_RUN=false
INCLUDE_COMPLETED=false
SKIP_BUGS=false
VERBOSE=false
SKIP_IDS=""  # Comma-separated list of IDs to skip (already exist as beads)

# Counters
FEATURES_MIGRATED=0
BUGS_MIGRATED=0
DEPS_CREATED=0
SKIPPED=0
ERRORS=0

# ID mapping: featmgmt_id -> bead_id
declare -A ID_MAP

# Usage
usage() {
    grep '^#' "$0" | grep -v '#!/' | sed 's/^# //' | sed 's/^#//'
    exit 0
}

# Logging
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_verbose() { if $VERBOSE; then echo -e "${BLUE}[DEBUG]${NC} $1"; fi; }
log_dry() { echo -e "${YELLOW}[DRY-RUN]${NC} $1"; }

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE_DIR="$2"
            shift 2
            ;;
        --epic)
            EPIC_NAME="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --include-completed)
            INCLUDE_COMPLETED=true
            shift
            ;;
        --skip-bugs)
            SKIP_BUGS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --skip-ids)
            SKIP_IDS="$2"
            shift 2
            ;;
        --map)
            # Format: FEAT-014=fe-89o,FEAT-015=fe-xyz
            # Pre-populate ID_MAP with existing beads
            IFS=',' read -ra MAPS <<< "$2"
            for mapping in "${MAPS[@]}"; do
                IFS='=' read -r old_id new_id <<< "$mapping"
                ID_MAP["$old_id"]="$new_id"
                log_verbose "Pre-mapped: $old_id -> $new_id"
            done
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate source directory
if [[ -z "$SOURCE_DIR" ]]; then
    log_error "Missing required --source argument"
    usage
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
    log_error "Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

if [[ ! -d "$SOURCE_DIR/features" ]]; then
    log_error "No features/ directory found in $SOURCE_DIR"
    exit 1
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed. Install with: sudo apt install jq"
    exit 1
fi

# Check for bd
if ! command -v bd &> /dev/null; then
    log_error "bd (beads) is required but not installed"
    exit 1
fi

log "Starting migration from: $SOURCE_DIR"
log "Epic name: $EPIC_NAME"
$DRY_RUN && log_warn "DRY RUN MODE - no changes will be made"

# Map priority P0-P3 to numeric 0-3
map_priority() {
    local p="$1"
    case "$p" in
        P0|p0) echo "0" ;;
        P1|p1) echo "1" ;;
        P2|p2) echo "2" ;;
        P3|p3) echo "3" ;;
        *) echo "2" ;;  # Default to P2
    esac
}

# Escape content for shell
escape_for_shell() {
    # Use base64 to safely handle any content
    cat | base64 -w 0
}

# Create a bead from a feature directory
migrate_feature() {
    local dir="$1"
    local json_file="$dir/feature_request.json"
    local prompt_file="$dir/PROMPT.md"

    if [[ ! -f "$json_file" ]]; then
        log_warn "No feature_request.json in $dir, skipping"
        ((SKIPPED++))
        return
    fi

    # Extract metadata from JSON (handle both 'feature_id' and 'id' field names)
    local feat_id=$(jq -r '.feature_id // .id // empty' "$json_file")
    local title=$(jq -r '.title // empty' "$json_file")
    local priority=$(jq -r '.priority // "P2"' "$json_file")
    local component=$(jq -r '.component // empty' "$json_file")
    local status=$(jq -r '.status // "new"' "$json_file")
    local tags=$(jq -r '.tags // [] | join(",")' "$json_file")
    local effort=$(jq -r '.estimated_effort // empty' "$json_file")
    local deps=$(jq -r '.dependencies // [] | join(",")' "$json_file")

    if [[ -z "$feat_id" ]] || [[ -z "$title" ]]; then
        log_warn "Missing feature_id or title in $json_file, skipping"
        ((SKIPPED++))
        return
    fi

    # Skip if in --skip-ids list
    if [[ -n "$SKIP_IDS" ]] && [[ ",$SKIP_IDS," == *",$feat_id,"* ]]; then
        log_verbose "Skipping $feat_id (in --skip-ids list)"
        ((SKIPPED++))
        return
    fi

    # Skip if already in ID_MAP (pre-mapped via --map)
    if [[ -n "${ID_MAP[$feat_id]}" ]]; then
        log_verbose "Skipping $feat_id (already mapped to ${ID_MAP[$feat_id]})"
        ((SKIPPED++))
        return
    fi

    # Skip completed items unless --include-completed
    if [[ "$status" == "completed" ]] || [[ "$status" == "resolved" ]]; then
        if ! $INCLUDE_COMPLETED; then
            log_verbose "Skipping completed feature: $feat_id"
            ((SKIPPED++))
            return
        fi
    fi

    log_verbose "Processing feature: $feat_id - $title"

    # Build labels
    local labels="$priority"
    [[ -n "$component" ]] && labels="$labels,component:$component"
    [[ -n "$effort" ]] && labels="$labels,effort:$effort"
    [[ -n "$tags" ]] && labels="$labels,$tags"

    # Get PROMPT.md content for body
    local body=""
    if [[ -f "$prompt_file" ]]; then
        body=$(cat "$prompt_file")
    else
        body="Migrated from $feat_id. No PROMPT.md found."
    fi

    # Build the bd create command
    local numeric_priority=$(map_priority "$priority")

    if $DRY_RUN; then
        log_dry "bd create \"$feat_id: $title\" --type feature --priority $numeric_priority --label \"$labels\""
        # Store fake ID for dependency tracking in dry run
        ID_MAP["$feat_id"]="fe-dry-$feat_id"
    else
        # Actually create the bead
        local result=$(bd create "$feat_id: $title" \
            --type feature \
            --priority "$numeric_priority" \
            --label "$labels" \
            --body "$body" 2>&1)

        # Extract bead ID from result (format: "✓ Created issue: fe-xxx")
        local bead_id=$(echo "$result" | grep -oP 'fe-[a-z0-9]+' | head -1)

        if [[ -n "$bead_id" ]]; then
            ID_MAP["$feat_id"]="$bead_id"
            log_success "Created $bead_id from $feat_id: $title"
        else
            log_error "Failed to create bead for $feat_id: $result"
            ((ERRORS++))
            return
        fi
    fi

    # Store dependencies for later processing
    if [[ -n "$deps" ]]; then
        echo "$feat_id:$deps" >> /tmp/featmgmt_deps_$$
    fi

    ((FEATURES_MIGRATED++))
}

# Create a bead from a bug directory
migrate_bug() {
    local dir="$1"
    local json_file="$dir/bug_report.json"
    local prompt_file="$dir/PROMPT.md"

    if [[ ! -f "$json_file" ]]; then
        log_warn "No bug_report.json in $dir, skipping"
        ((SKIPPED++))
        return
    fi

    # Extract metadata from JSON
    local bug_id=$(jq -r '.bug_id // empty' "$json_file")
    local title=$(jq -r '.title // empty' "$json_file")
    local priority=$(jq -r '.priority // "P2"' "$json_file")
    local severity=$(jq -r '.severity // empty' "$json_file")
    local component=$(jq -r '.component // empty' "$json_file")
    local status=$(jq -r '.status // "new"' "$json_file")
    local tags=$(jq -r '.tags // [] | join(",")' "$json_file")

    if [[ -z "$bug_id" ]] || [[ -z "$title" ]]; then
        log_warn "Missing bug_id or title in $json_file, skipping"
        ((SKIPPED++))
        return
    fi

    # Skip completed items unless --include-completed
    if [[ "$status" == "completed" ]] || [[ "$status" == "resolved" ]]; then
        if ! $INCLUDE_COMPLETED; then
            log_verbose "Skipping completed bug: $bug_id"
            ((SKIPPED++))
            return
        fi
    fi

    log_verbose "Processing bug: $bug_id - $title"

    # Build labels
    local labels="$priority"
    [[ -n "$severity" ]] && labels="$labels,severity:$severity"
    [[ -n "$component" ]] && labels="$labels,component:$component"
    [[ -n "$tags" ]] && labels="$labels,$tags"

    # Get PROMPT.md content for body
    local body=""
    if [[ -f "$prompt_file" ]]; then
        body=$(cat "$prompt_file")
    else
        body="Migrated from $bug_id. No PROMPT.md found."
    fi

    # Build the bd create command
    local numeric_priority=$(map_priority "$priority")

    if $DRY_RUN; then
        log_dry "bd create \"$bug_id: $title\" --type bug --priority $numeric_priority --label \"$labels\""
        ID_MAP["$bug_id"]="fe-dry-$bug_id"
    else
        local result=$(bd create "$bug_id: $title" \
            --type bug \
            --priority "$numeric_priority" \
            --label "$labels" \
            --body "$body" 2>&1)

        local bead_id=$(echo "$result" | grep -oP 'fe-[a-z0-9]+' | head -1)

        if [[ -n "$bead_id" ]]; then
            ID_MAP["$bug_id"]="$bead_id"
            log_success "Created $bead_id from $bug_id: $title"
        else
            log_error "Failed to create bead for $bug_id: $result"
            ((ERRORS++))
            return
        fi
    fi

    ((BUGS_MIGRATED++))
}

# Process dependencies after all beads are created
process_dependencies() {
    local deps_file="/tmp/featmgmt_deps_$$"

    if [[ ! -f "$deps_file" ]]; then
        log_verbose "No dependencies to process"
        return
    fi

    log "Processing dependencies..."

    while IFS=: read -r child_featmgmt_id deps_list; do
        local child_bead_id="${ID_MAP[$child_featmgmt_id]}"

        if [[ -z "$child_bead_id" ]]; then
            log_warn "No bead found for $child_featmgmt_id, skipping dependencies"
            continue
        fi

        # Split deps_list by comma
        IFS=',' read -ra DEPS <<< "$deps_list"
        for parent_featmgmt_id in "${DEPS[@]}"; do
            # Clean up whitespace
            parent_featmgmt_id=$(echo "$parent_featmgmt_id" | xargs)

            if [[ -z "$parent_featmgmt_id" ]]; then
                continue
            fi

            local parent_bead_id="${ID_MAP[$parent_featmgmt_id]}"

            if [[ -z "$parent_bead_id" ]]; then
                log_warn "No bead found for dependency $parent_featmgmt_id (from $child_featmgmt_id)"
                continue
            fi

            if $DRY_RUN; then
                log_dry "bd dep add $child_bead_id $parent_bead_id"
            else
                bd dep add "$child_bead_id" "$parent_bead_id" 2>/dev/null && \
                    log_success "Added dependency: $child_bead_id depends on $parent_bead_id" || \
                    log_warn "Failed to add dependency: $child_bead_id -> $parent_bead_id"
            fi

            ((DEPS_CREATED++))
        done
    done < "$deps_file"

    rm -f "$deps_file"
}

# Main migration
echo ""
echo "=========================================="
echo "  featmgmt to Beads Migration"
echo "=========================================="
echo ""

# Process features directory
log "Scanning features directory..."
if [[ -d "$SOURCE_DIR/features" ]]; then
    for dir in "$SOURCE_DIR/features"/*/; do
        if [[ -d "$dir" ]]; then
            migrate_feature "$dir"
        fi
    done
fi

# Process bugs directory
if ! $SKIP_BUGS && [[ -d "$SOURCE_DIR/bugs" ]]; then
    log "Scanning bugs directory..."
    for dir in "$SOURCE_DIR/bugs"/*/; do
        if [[ -d "$dir" ]]; then
            migrate_bug "$dir"
        fi
    done
fi

# Process completed directory if requested
if $INCLUDE_COMPLETED && [[ -d "$SOURCE_DIR/completed" ]]; then
    log "Scanning completed directory..."
    for dir in "$SOURCE_DIR/completed"/*/; do
        if [[ -d "$dir" ]]; then
            # Check if it's a feature or bug
            if [[ -f "$dir/feature_request.json" ]]; then
                migrate_feature "$dir"
            elif [[ -f "$dir/bug_report.json" ]]; then
                migrate_bug "$dir"
            fi
        fi
    done
fi

# Process dependencies
process_dependencies

# Print summary
echo ""
echo "=========================================="
echo "  Migration Summary"
echo "=========================================="
echo ""
echo "  Features migrated: $FEATURES_MIGRATED"
echo "  Bugs migrated:     $BUGS_MIGRATED"
echo "  Dependencies:      $DEPS_CREATED"
echo "  Skipped:           $SKIPPED"
echo "  Errors:            $ERRORS"
echo ""

if $DRY_RUN; then
    echo -e "${YELLOW}This was a dry run. No beads were created.${NC}"
    echo "Run without --dry-run to execute the migration."
fi

if [[ $ERRORS -gt 0 ]]; then
    exit 1
fi

exit 0
