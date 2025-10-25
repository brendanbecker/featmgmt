#!/bin/bash
# Test validation script for FEAT-004: Early-exit bug/feature creation
# This validates the template files were updated correctly with early-exit handling

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result function
pass_test() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

fail_test() {
    echo -e "${RED}[FAIL]${NC} $1"
    echo "       Details: $2"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

section_header() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
    echo ""
}

# Test 1: File Existence
section_header "Test 1: File Existence"

if [ -f "templates/OVERPROMPT-standard.md" ]; then
    pass_test "OVERPROMPT-standard.md exists"
else
    fail_test "OVERPROMPT-standard.md exists" "File not found"
fi

if [ -f "templates/OVERPROMPT-gitops.md" ]; then
    pass_test "OVERPROMPT-gitops.md exists"
else
    fail_test "OVERPROMPT-gitops.md exists" "File not found"
fi

# Test 2: Early Exit Handling Section Presence
section_header "Test 2: Early Exit Handling Section"

if grep -q "## Early Exit Handling" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md contains 'Early Exit Handling' section"
else
    fail_test "OVERPROMPT-standard.md contains 'Early Exit Handling' section" "Section not found"
fi

if grep -q "## Early Exit Handling" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md contains 'Early Exit Handling' section"
else
    fail_test "OVERPROMPT-gitops.md contains 'Early Exit Handling' section" "Section not found"
fi

# Test 3: Exit Conditions Subsection
section_header "Test 3: Exit Conditions Documentation"

if grep -q "### Exit Conditions" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md contains 'Exit Conditions' subsection"
else
    fail_test "OVERPROMPT-standard.md contains 'Exit Conditions' subsection" "Subsection not found"
fi

if grep -q "### Exit Conditions" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md contains 'Exit Conditions' subsection"
else
    fail_test "OVERPROMPT-gitops.md contains 'Exit Conditions' subsection" "Subsection not found"
fi

# Test 4: 3 Consecutive Failures Detection
section_header "Test 4: 3 Consecutive Failures Detection"

if grep -q "3 Consecutive Failures" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents 3 consecutive failures detection"
else
    fail_test "OVERPROMPT-standard.md documents 3 consecutive failures detection" "Not found"
fi

if grep -q "3 Consecutive Failures" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md documents 3 consecutive failures detection"
else
    fail_test "OVERPROMPT-gitops.md documents 3 consecutive failures detection" "Not found"
fi

# Test 5: Explicit STOP Command Detection
section_header "Test 5: Explicit STOP Command Detection"

if grep -q "Explicit STOP Command" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents STOP command detection"
else
    fail_test "OVERPROMPT-standard.md documents STOP command detection" "Not found"
fi

if grep -q "Explicit STOP Command" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md documents STOP command detection"
else
    fail_test "OVERPROMPT-gitops.md documents STOP command detection" "Not found"
fi

# Test 6: Critical Errors Detection
section_header "Test 6: Critical Errors Detection"

if grep -q "Critical Errors" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents critical errors detection"
else
    fail_test "OVERPROMPT-standard.md documents critical errors detection" "Not found"
fi

if grep -q "Critical Errors" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md documents critical errors detection"
else
    fail_test "OVERPROMPT-gitops.md documents critical errors detection" "Not found"
fi

# Test 7: Early Exit Procedure
section_header "Test 7: Early Exit Procedure Documentation"

if grep -q "### Early Exit Procedure" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md contains Early Exit Procedure"
else
    fail_test "OVERPROMPT-standard.md contains Early Exit Procedure" "Subsection not found"
fi

if grep -q "### Early Exit Procedure" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md contains Early Exit Procedure"
else
    fail_test "OVERPROMPT-gitops.md contains Early Exit Procedure" "Subsection not found"
fi

# Test 8: work-item-creation-agent Invocation
section_header "Test 8: work-item-creation-agent Integration"

if grep -q "work-item-creation-agent" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md references work-item-creation-agent"
else
    fail_test "OVERPROMPT-standard.md references work-item-creation-agent" "Not found"
fi

if grep -q "work-item-creation-agent" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md references work-item-creation-agent"
else
    fail_test "OVERPROMPT-gitops.md references work-item-creation-agent" "Not found"
fi

# Test 9: Specific Cases Documentation
section_header "Test 9: Specific Cases Documentation"

if grep -q "#### Case 1: 3 Consecutive Failures" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents Case 1 (3 consecutive failures)"
else
    fail_test "OVERPROMPT-standard.md documents Case 1" "Not found"
fi

if grep -q "#### Case 2: Explicit STOP Command" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents Case 2 (STOP command)"
else
    fail_test "OVERPROMPT-standard.md documents Case 2" "Not found"
fi

if grep -q "#### Case 3: Critical Error" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents Case 3 (critical error)"
else
    fail_test "OVERPROMPT-standard.md documents Case 3" "Not found"
fi

if grep -q "#### Case 4: Subagent Invocation Failures" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents Case 4 (subagent failures)"
else
    fail_test "OVERPROMPT-standard.md documents Case 4" "Not found"
fi

# Test 10: State Management Schema Updates
section_header "Test 10: State Management Schema Updates"

if grep -q '"failure_count"' templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md includes failure_count field"
else
    fail_test "OVERPROMPT-standard.md includes failure_count field" "Not found"
fi

if grep -q '"last_failures"' templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md includes last_failures field"
else
    fail_test "OVERPROMPT-standard.md includes last_failures field" "Not found"
fi

if grep -q '"early_exit_triggered"' templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md includes early_exit_triggered field"
else
    fail_test "OVERPROMPT-standard.md includes early_exit_triggered field" "Not found"
fi

if grep -q '"early_exit_reason"' templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md includes early_exit_reason field"
else
    fail_test "OVERPROMPT-standard.md includes early_exit_reason field" "Not found"
fi

# Test 11: State Update Logic Documentation
section_header "Test 11: State Update Logic Documentation"

if grep -q "State Update Logic" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents state update logic"
else
    fail_test "OVERPROMPT-standard.md documents state update logic" "Not found"
fi

if grep -q "On Success" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents success case logic"
else
    fail_test "OVERPROMPT-standard.md documents success case logic" "Not found"
fi

if grep -q "On Failure" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents failure case logic"
else
    fail_test "OVERPROMPT-standard.md documents failure case logic" "Not found"
fi

if grep -q "On Early Exit" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents early exit case logic"
else
    fail_test "OVERPROMPT-standard.md documents early exit case logic" "Not found"
fi

# Test 12: Safeguards Section Updates
section_header "Test 12: Safeguards Section Updates"

if grep -q "Early Exit Protection" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md includes Early Exit Protection safeguard"
else
    fail_test "OVERPROMPT-standard.md includes Early Exit Protection safeguard" "Not found"
fi

if grep -q "Failure Tracking" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md mentions failure tracking"
else
    fail_test "OVERPROMPT-standard.md mentions failure tracking" "Not found"
fi

if grep -q "Automatic Bug Creation" templates/OVERPROMPT-standard.md || grep -q "Automatic Task Creation" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md mentions automatic issue creation"
else
    fail_test "OVERPROMPT-standard.md mentions automatic issue creation" "Not found"
fi

if grep -q "Knowledge Preservation" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md mentions knowledge preservation"
else
    fail_test "OVERPROMPT-standard.md mentions knowledge preservation" "Not found"
fi

if grep -q "Graceful Shutdown" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md mentions graceful shutdown"
else
    fail_test "OVERPROMPT-standard.md mentions graceful shutdown" "Not found"
fi

# Test 13: Phase 6 Retrospective Context Updates
section_header "Test 13: Phase 6 Retrospective Context Updates"

if grep -q "early_exit_triggered" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md passes early_exit context to retrospective"
else
    fail_test "OVERPROMPT-standard.md passes early_exit context to retrospective" "Not found"
fi

if grep -q "Note.*Retrospective runs even after early exit" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md notes retrospective runs after early exit"
else
    fail_test "OVERPROMPT-standard.md notes retrospective runs after early exit" "Not found"
fi

# Test 14: GitOps Variant Completeness
section_header "Test 14: GitOps Variant Validation"

if grep -q "failure_count" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md includes failure_count field"
else
    fail_test "OVERPROMPT-gitops.md includes failure_count field" "Not found"
fi

if grep -q "early_exit_triggered" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md includes early_exit_triggered field"
else
    fail_test "OVERPROMPT-gitops.md includes early_exit_triggered field" "Not found"
fi

if grep -q "Early Exit Protection" templates/OVERPROMPT-gitops.md; then
    pass_test "OVERPROMPT-gitops.md includes Early Exit Protection safeguard"
else
    fail_test "OVERPROMPT-gitops.md includes Early Exit Protection safeguard" "Not found"
fi

# Test 15: Markdown Syntax Validation
section_header "Test 15: Markdown Syntax Validation"

# Check for common markdown issues
if ! grep -P '\t' templates/OVERPROMPT-standard.md > /dev/null 2>&1; then
    pass_test "OVERPROMPT-standard.md has no tab characters (uses spaces)"
else
    fail_test "OVERPROMPT-standard.md has no tab characters" "Contains tabs"
fi

if ! grep -P '\t' templates/OVERPROMPT-gitops.md > /dev/null 2>&1; then
    pass_test "OVERPROMPT-gitops.md has no tab characters (uses spaces)"
else
    fail_test "OVERPROMPT-gitops.md has no tab characters" "Contains tabs"
fi

# Check for proper header hierarchy (no skipped levels)
python3 -c "
import sys
import re

def check_header_hierarchy(filename):
    with open(filename, 'r') as f:
        content = f.read()

    headers = re.findall(r'^(#{1,6}) ', content, re.MULTILINE)
    prev_level = 0

    for header in headers:
        level = len(header)
        if level > prev_level + 1 and prev_level != 0:
            return False
        prev_level = level

    return True

if check_header_hierarchy('templates/OVERPROMPT-standard.md'):
    print('PASS')
    sys.exit(0)
else:
    print('FAIL')
    sys.exit(1)
" && pass_test "OVERPROMPT-standard.md has valid header hierarchy" || fail_test "OVERPROMPT-standard.md has valid header hierarchy" "Skipped header levels detected"

# Test 16: JSON Schema Validation in State Management
section_header "Test 16: JSON Schema Validation"

# Extract JSON block and validate it
python3 -c "
import json
import sys
import re

def extract_and_validate_json(filename, pattern_start):
    with open(filename, 'r') as f:
        content = f.read()

    # Find JSON block after State Management
    match = re.search(r'State Management.*?```json\n(.*?)```', content, re.DOTALL)

    if not match:
        print('No JSON block found')
        return False

    json_str = match.group(1)

    try:
        data = json.loads(json_str)

        # Check for required fields
        required_fields = ['failure_count', 'last_failures', 'early_exit_triggered', 'early_exit_reason']

        for field in required_fields:
            if field not in data:
                print(f'Missing required field: {field}')
                return False

        return True
    except json.JSONDecodeError as e:
        print(f'JSON parse error: {e}')
        return False

if extract_and_validate_json('templates/OVERPROMPT-standard.md', 'State Management'):
    print('PASS')
    sys.exit(0)
else:
    print('FAIL')
    sys.exit(1)
" && pass_test "OVERPROMPT-standard.md has valid .agent-state.json schema" || fail_test "OVERPROMPT-standard.md has valid .agent-state.json schema" "Schema validation failed"

# Test 17: Cross-reference Consistency
section_header "Test 17: Cross-reference Consistency"

# Check that both variants mention the same core concepts
CORE_CONCEPTS=("early_exit_triggered" "failure_count" "work-item-creation-agent" "Graceful Shutdown")

for concept in "${CORE_CONCEPTS[@]}"; do
    standard_count=$(grep -c "$concept" templates/OVERPROMPT-standard.md || echo 0)
    gitops_count=$(grep -c "$concept" templates/OVERPROMPT-gitops.md || echo 0)

    if [ "$standard_count" -gt 0 ] && [ "$gitops_count" -gt 0 ]; then
        pass_test "Both variants reference '$concept'"
    else
        fail_test "Both variants reference '$concept'" "Standard: $standard_count, GitOps: $gitops_count"
    fi
done

# Test 18: Evidence Collection Documentation
section_header "Test 18: Evidence Collection Documentation"

if grep -q "Capture Session State" templates/OVERPROMPT-standard.md; then
    pass_test "OVERPROMPT-standard.md documents session state capture"
else
    fail_test "OVERPROMPT-standard.md documents session state capture" "Not found"
fi

if grep -q ".agent-state.json" templates/OVERPROMPT-standard.md | grep -q "Session state at failure"; then
    pass_test "OVERPROMPT-standard.md mentions .agent-state.json as evidence"
else
    # Fallback check
    if grep -q ".agent-state.json" templates/OVERPROMPT-standard.md; then
        pass_test "OVERPROMPT-standard.md mentions .agent-state.json"
    else
        fail_test "OVERPROMPT-standard.md mentions .agent-state.json as evidence" "Not found"
    fi
fi

# Final Summary
section_header "Test Summary"

echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
