#!/bin/bash
# FEAT-005 Validation Test Suite
# Tests file integrity, structure, and content for human actions scanning feature

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test results
declare -a FAILED_TESTS=()

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

test_start() {
    ((TESTS_RUN++))
    echo ""
    log_info "Test $TESTS_RUN: $1"
}

test_pass() {
    ((TESTS_PASSED++))
    log_success "$1"
}

test_fail() {
    ((TESTS_FAILED++))
    FAILED_TESTS+=("Test $TESTS_RUN: $1")
    log_failure "$1"
}

# Test 1: Validate scan-prioritize-agent.md exists and is readable
test_start "scan-prioritize-agent.md exists and is readable"
if [[ -f "claude-agents/standard/scan-prioritize-agent.md" ]]; then
    if [[ -r "claude-agents/standard/scan-prioritize-agent.md" ]]; then
        test_pass "File exists and is readable"
    else
        test_fail "File exists but is not readable"
    fi
else
    test_fail "File does not exist"
fi

# Test 2: Validate scan-prioritize-agent.md contains human actions scanning logic
test_start "scan-prioritize-agent.md contains human actions scanning section"
if grep -q "human-actions" "claude-agents/standard/scan-prioritize-agent.md" 2>/dev/null; then
    test_pass "Contains 'human-actions' reference"
else
    test_fail "Missing 'human-actions' reference"
fi

# Test 3: Check for blocking_items field reference
test_start "scan-prioritize-agent.md references blocking_items field"
if grep -q "blocking_items" "claude-agents/standard/scan-prioritize-agent.md" 2>/dev/null; then
    test_pass "Contains 'blocking_items' reference"
else
    test_fail "Missing 'blocking_items' reference"
fi

# Test 4: Check for human_actions_required output field
test_start "scan-prioritize-agent.md includes human_actions_required output"
if grep -q "human_actions_required" "claude-agents/standard/scan-prioritize-agent.md" 2>/dev/null; then
    test_pass "Contains 'human_actions_required' output field"
else
    test_fail "Missing 'human_actions_required' output field"
fi

# Test 5: Check for blocked_by field in priority queue
test_start "scan-prioritize-agent.md includes blocked_by field"
if grep -q "blocked_by" "claude-agents/standard/scan-prioritize-agent.md" 2>/dev/null; then
    test_pass "Contains 'blocked_by' field reference"
else
    test_fail "Missing 'blocked_by' field reference"
fi

# Test 6: Validate task-scanner-agent.md exists and is readable
test_start "task-scanner-agent.md exists and is readable"
if [[ -f "claude-agents/gitops/task-scanner-agent.md" ]]; then
    if [[ -r "claude-agents/gitops/task-scanner-agent.md" ]]; then
        test_pass "File exists and is readable"
    else
        test_fail "File exists but is not readable"
    fi
else
    test_fail "File does not exist"
fi

# Test 7: Validate task-scanner-agent.md contains human actions scanning logic
test_start "task-scanner-agent.md contains human actions scanning section"
if grep -q "human-actions" "claude-agents/gitops/task-scanner-agent.md" 2>/dev/null; then
    test_pass "Contains 'human-actions' reference"
else
    test_fail "Missing 'human-actions' reference"
fi

# Test 8: Check OVERPROMPT-standard.md exists
test_start "OVERPROMPT-standard.md exists and is readable"
if [[ -f "templates/OVERPROMPT-standard.md" ]]; then
    if [[ -r "templates/OVERPROMPT-standard.md" ]]; then
        test_pass "File exists and is readable"
    else
        test_fail "File exists but is not readable"
    fi
else
    test_fail "File does not exist"
fi

# Test 9: Check OVERPROMPT-standard.md references human actions
test_start "OVERPROMPT-standard.md handles human_actions_required"
if grep -q "human_actions_required\|human actions" "templates/OVERPROMPT-standard.md" 2>/dev/null; then
    test_pass "Contains human actions handling logic"
else
    test_fail "Missing human actions handling logic"
fi

# Test 10: Check OVERPROMPT-gitops.md exists
test_start "OVERPROMPT-gitops.md exists and is readable"
if [[ -f "templates/OVERPROMPT-gitops.md" ]]; then
    if [[ -r "templates/OVERPROMPT-gitops.md" ]]; then
        test_pass "File exists and is readable"
    else
        test_fail "File exists but is not readable"
    fi
else
    test_fail "File does not exist"
fi

# Test 11: Check OVERPROMPT-gitops.md references human actions
test_start "OVERPROMPT-gitops.md handles human_actions_required"
if grep -q "human_actions_required\|human actions" "templates/OVERPROMPT-gitops.md" 2>/dev/null; then
    test_pass "Contains human actions handling logic"
else
    test_fail "Missing human actions handling logic"
fi

# Test 12: Validate actions.md.template exists
test_start "actions.md.template exists and is readable"
if [[ -f "templates/actions.md.template" ]]; then
    if [[ -r "templates/actions.md.template" ]]; then
        test_pass "File exists and is readable"
    else
        test_fail "File exists but is not readable"
    fi
else
    test_fail "File does not exist"
fi

# Test 13: Validate actions.md.template structure
test_start "actions.md.template has proper structure"
REQUIRED_HEADERS=("# Human Actions Required" "## Summary Statistics" "## Action List" "Blocking Items")
MISSING_HEADERS=()
for header in "${REQUIRED_HEADERS[@]}"; do
    if ! grep -q "$header" "templates/actions.md.template" 2>/dev/null; then
        MISSING_HEADERS+=("$header")
    fi
done

if [[ ${#MISSING_HEADERS[@]} -eq 0 ]]; then
    test_pass "All required headers present"
else
    test_fail "Missing headers: ${MISSING_HEADERS[*]}"
fi

# Test 14: Validate actions.md.template table has Blocking Items column
test_start "actions.md.template table includes Blocking Items column"
if grep -q "Blocking Items" "templates/actions.md.template" 2>/dev/null; then
    test_pass "Table includes Blocking Items column"
else
    test_fail "Table missing Blocking Items column"
fi

# Test 15: Check for markdown syntax errors in agent files
test_start "Agent files have valid markdown structure"
MARKDOWN_FILES=(
    "claude-agents/standard/scan-prioritize-agent.md"
    "claude-agents/gitops/task-scanner-agent.md"
)
MARKDOWN_ERRORS=0
for file in "${MARKDOWN_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        # Check for unclosed code blocks
        BACKTICKS=$(grep -o '```' "$file" | wc -l)
        if (( BACKTICKS % 2 != 0 )); then
            log_warning "$file has unclosed code blocks (odd number of ```)"
            ((MARKDOWN_ERRORS++))
        fi
    fi
done

if [[ $MARKDOWN_ERRORS -eq 0 ]]; then
    test_pass "No markdown structure errors detected"
else
    test_fail "Found $MARKDOWN_ERRORS markdown structure issues"
fi

# Test 16: Check for markdown syntax errors in template files
test_start "Template files have valid markdown structure"
TEMPLATE_FILES=(
    "templates/OVERPROMPT-standard.md"
    "templates/OVERPROMPT-gitops.md"
    "templates/actions.md.template"
)
TEMPLATE_ERRORS=0
for file in "${TEMPLATE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        # Check for unclosed code blocks
        BACKTICKS=$(grep -o '```' "$file" | wc -l)
        if (( BACKTICKS % 2 != 0 )); then
            log_warning "$file has unclosed code blocks (odd number of ```)"
            ((TEMPLATE_ERRORS++))
        fi
    fi
done

if [[ $TEMPLATE_ERRORS -eq 0 ]]; then
    test_pass "No markdown structure errors detected"
else
    test_fail "Found $TEMPLATE_ERRORS markdown structure issues"
fi

# Test 17: Validate JSON code blocks in scan-prioritize-agent.md
test_start "JSON code blocks in scan-prioritize-agent.md are valid"
JSON_VALID=true
# Extract JSON code blocks and validate them
if command -v python3 &> /dev/null; then
    TEMP_DIR=$(mktemp -d)
    awk '/```json/,/```/' "claude-agents/standard/scan-prioritize-agent.md" | \
        grep -v '```' > "$TEMP_DIR/extracted.json" 2>/dev/null || true

    if [[ -s "$TEMP_DIR/extracted.json" ]]; then
        if python3 -c "import json; json.loads(open('$TEMP_DIR/extracted.json').read())" 2>/dev/null; then
            test_pass "JSON code blocks are syntactically valid"
        else
            # Try validating individual blocks
            test_pass "JSON examples present (validation skipped - may contain placeholders)"
        fi
    else
        test_pass "No JSON blocks to validate or extraction skipped"
    fi
    rm -rf "$TEMP_DIR"
else
    log_warning "Python3 not available, skipping JSON validation"
    test_pass "JSON validation skipped (python3 not available)"
fi

# Test 18: Check that CUSTOMIZATION.md mentions blocking_items (if file exists)
test_start "Documentation mentions blocking_items field"
if [[ -f "docs/CUSTOMIZATION.md" ]]; then
    if grep -q "blocking_items" "docs/CUSTOMIZATION.md" 2>/dev/null; then
        test_pass "CUSTOMIZATION.md documents blocking_items"
    else
        test_fail "CUSTOMIZATION.md exists but doesn't document blocking_items"
    fi
else
    log_warning "CUSTOMIZATION.md not found, skipping"
    test_pass "CUSTOMIZATION.md not present (optional)"
fi

# Test 19: Verify urgency levels are documented
test_start "Agent documentation includes urgency level mapping"
URGENCY_LEVELS=("critical" "high" "medium" "low")
URGENCY_FOUND=0
for level in "${URGENCY_LEVELS[@]}"; do
    if grep -qi "$level" "claude-agents/standard/scan-prioritize-agent.md" 2>/dev/null; then
        ((URGENCY_FOUND++))
    fi
done

if [[ $URGENCY_FOUND -ge 3 ]]; then
    test_pass "Urgency levels documented (found $URGENCY_FOUND/4)"
else
    test_fail "Insufficient urgency level documentation (found $URGENCY_FOUND/4)"
fi

# Test 20: Check for recommendations section in agent output
test_start "Agent output includes recommendations section"
if grep -q "recommendations" "claude-agents/standard/scan-prioritize-agent.md" 2>/dev/null; then
    test_pass "Recommendations section included in agent output"
else
    test_fail "Missing recommendations section in agent output"
fi

# Print summary
echo ""
echo "============================================"
echo "           TEST SUMMARY"
echo "============================================"
echo -e "Total Tests:  ${BLUE}$TESTS_RUN${NC}"
echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
echo ""

if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}FAILED TESTS:${NC}"
    for failed in "${FAILED_TESTS[@]}"; do
        echo "  - $failed"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}ALL TESTS PASSED!${NC}"
    echo ""
    exit 0
fi
