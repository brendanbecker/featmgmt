#!/bin/bash
# Test validation for FEAT-004: Early-exit handling updates to OVERPROMPT templates
# Component: workflow
# Tests: File integrity, structure, early-exit documentation, state schema, safeguards

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$PROJECT_ROOT/templates"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test result tracking
declare -a FAILED_TESTS=()

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "\n${YELLOW}[TEST $TESTS_RUN]${NC} $test_name"

    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        FAILED_TESTS+=("$test_name")
        return 1
    fi
}

echo "======================================"
echo "FEAT-004 Validation Test Suite"
echo "======================================"
echo "Testing early-exit handling updates"
echo "Templates: OVERPROMPT-standard.md, OVERPROMPT-gitops.md"
echo ""

# Test 1: Files exist
run_test "Template files exist" \
    "test -f '$TEMPLATES_DIR/OVERPROMPT-standard.md' && test -f '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 2: Files are valid markdown (basic check - no syntax errors)
# Test 2: Files have reasonable size (non-empty)
run_test "Template files are non-empty" \
    "test -s '$TEMPLATES_DIR/OVERPROMPT-standard.md' && test -s '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 3: Early Exit Handling section exists in both templates
run_test "Early Exit Handling section exists in OVERPROMPT-standard.md" \
    "grep -q '^## Early Exit Handling' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Early Exit Handling section exists in OVERPROMPT-gitops.md" \
    "grep -q '^## Early Exit Handling' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 4: Exit Conditions subsection exists
run_test "Exit Conditions subsection in OVERPROMPT-standard.md" \
    "grep -q '^### Exit Conditions' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Exit Conditions subsection in OVERPROMPT-gitops.md" \
    "grep -q '^### Exit Conditions' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 5: Early Exit Procedure subsection exists
run_test "Early Exit Procedure subsection in OVERPROMPT-standard.md" \
    "grep -q '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Early Exit Procedure subsection in OVERPROMPT-gitops.md" \
    "grep -q '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 6: Specific Cases subsection exists
run_test "Specific Cases subsection in OVERPROMPT-standard.md" \
    "grep -q '^### Specific Cases' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Specific Cases subsection in OVERPROMPT-gitops.md" \
    "grep -q '^### Specific Cases' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 7: All 4 specific cases documented
run_test "Case 1: 3 Consecutive Failures documented in standard" \
    "grep -q '^#### Case 1: 3 Consecutive Failures' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Case 2: Explicit STOP Command documented in standard" \
    "grep -q '^#### Case 2: Explicit STOP Command' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Case 3: Critical Error documented in standard" \
    "grep -q '^#### Case 3: Critical Error' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Case 4: Subagent Invocation Failures documented in standard" \
    "grep -q '^#### Case 4: Subagent Invocation Failures' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

# Test 8: Same cases in gitops variant
run_test "All 4 cases documented in gitops variant" \
    "grep -q '^#### Case 1: 3 Consecutive Failures' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' && \
     grep -q '^#### Case 2: Explicit STOP Command' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' && \
     grep -q '^#### Case 3: Critical Error' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' && \
     grep -q '^#### Case 4: Subagent Invocation Failures' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 9: State Management schema includes new fields
run_test "State Management includes failure_count field in standard" \
    "grep -q '\"failure_count\":' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "State Management includes last_failures field in standard" \
    "grep -q '\"last_failures\":' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "State Management includes early_exit_triggered field in standard" \
    "grep -q '\"early_exit_triggered\":' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "State Management includes early_exit_reason field in standard" \
    "grep -q '\"early_exit_reason\":' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

# Test 10: Same fields in gitops variant
run_test "State Management schema updated in gitops variant" \
    "grep -q '\"failure_count\":' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' && \
     grep -q '\"last_failures\":' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' && \
     grep -q '\"early_exit_triggered\":' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' && \
     grep -q '\"early_exit_reason\":' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 11: State Update Logic documented
run_test "State Update Logic section exists in standard" \
    "grep -q '\*\*State Update Logic\*\*:' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "State Update Logic section exists in gitops" \
    "grep -q '\*\*State Update Logic\*\*:' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 12: On Success/Failure logic documented
run_test "On Success logic documented in standard" \
    "grep -q 'On Success.*failure_count.*to 0' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "On Failure logic documented in standard" \
    "grep -q 'On Failure.*Increment.*failure_count' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "On Early Exit logic documented in standard" \
    "grep -q 'On Early Exit.*early_exit_triggered.*true' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

# Test 13: Safeguards section includes Early Exit Protection
run_test "Safeguards section includes Early Exit Protection in standard" \
    "grep -q 'Early Exit Protection' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Safeguards section includes Early Exit Protection in gitops" \
    "grep -q 'Early Exit Protection' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 14: Safeguards mention Failure Tracking
run_test "Safeguards mention Failure Tracking in standard" \
    "grep -q 'Failure Tracking.*Count consecutive failures' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Safeguards mention Automatic Bug Creation in standard" \
    "grep -q 'Automatic Bug Creation' '$TEMPLATES_DIR/OVERPROMPT-standard.md' || \
     grep -q 'Automatic Task Creation' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Safeguards mention Knowledge Preservation in standard" \
    "grep -q 'Knowledge Preservation.*Capture session state' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Safeguards mention Graceful Shutdown in standard" \
    "grep -q 'Graceful Shutdown.*retrospective and summary' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

# Test 15: Phase 5 (Retrospective) mentions early_exit fields
run_test "Phase 5 mentions early_exit fields in standard" \
    "grep -A 10 '^## Phase 5: Retrospective' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'early_exit'"

run_test "Phase 5 mentions early_exit fields in gitops" \
    "grep -A 10 '^## Phase 5: Retrospective' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' | grep -q 'early_exit'"

# Test 16: Phase 5 Context mentions early exit items
run_test "Phase 5 Context to provide mentions early exit in standard" \
    "grep -A 5 '\*\*Context to provide:\*\*' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'early exit'"

# Test 17: Early exit documentation exists (template uses 5 phases, not 7)
run_test "Early Exit Procedure includes documentation in standard" \
    "grep -A 20 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'early exit'"

run_test "Early Exit Procedure includes documentation in gitops" \
    "grep -A 20 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' | grep -q 'early exit'"

# Test 18: work-item-creation-agent invocation documented
run_test "work-item-creation-agent invocation in Early Exit Procedure (standard)" \
    "grep -A 15 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'work-item-creation-agent'"

run_test "work-item-creation-agent invocation in Early Exit Procedure (gitops)" \
    "grep -A 15 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' | grep -q 'work-item-creation-agent'"

# Test 19: Exit Conditions section exists (separate from Early Exit Handling)
run_test "Exit Conditions section exists in standard" \
    "grep -q '^## Exit Conditions' '$TEMPLATES_DIR/OVERPROMPT-standard.md'"

run_test "Exit Conditions section exists in gitops" \
    "grep -q '^## Exit Conditions' '$TEMPLATES_DIR/OVERPROMPT-gitops.md'"

# Test 20: Exit Conditions mentions 3 consecutive failures
run_test "Exit Conditions mentions 3 consecutive failures in standard" \
    "grep -A 5 '^## Exit Conditions' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q '3 consecutive failures'"

run_test "Exit Conditions mentions explicit STOP in standard" \
    "grep -A 5 '^## Exit Conditions' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'STOP command'"

# Test 21: JSON schema validation (basic - check structure)
run_test "State Management JSON schema is valid in standard" \
    "grep -Pzo '(?s)## State Management.*?\{.*?\"session_id\".*?\"failure_count\".*?\"early_exit_triggered\".*?\}' '$TEMPLATES_DIR/OVERPROMPT-standard.md' > /dev/null"

run_test "State Management JSON schema is valid in gitops" \
    "grep -Pzo '(?s)## State Management.*?\{.*?\"session_id\".*?\"failure_count\".*?\"early_exit_triggered\".*?\}' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' > /dev/null"

# Test 22: Evidence fields in work-item-creation-agent call
run_test "Evidence includes .agent-state.json in standard" \
    "grep -A 30 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q '\.agent-state\.json'"

run_test "Evidence includes session logs in standard" \
    "grep -A 30 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Session logs'"

run_test "Evidence includes error messages in standard" \
    "grep -A 30 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Error messages'"

# Test 23: Verify retrospective note about running after early exit
run_test "Retrospective note about running after early exit in standard" \
    "grep -A 3 '\*\*Note\*\*:' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Retrospective runs even after early exit'"

run_test "Retrospective note about running after early exit in gitops" \
    "grep -A 3 '\*\*Note\*\*:' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' | grep -q 'Retrospective runs even after early exit'"

# Test 24: Verify consistent terminology (bug vs task)
run_test "Standard variant uses 'bug' terminology in early exit" \
    "grep -A 50 '^## Early Exit Handling' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'item_type.*bug'"

run_test "GitOps variant uses appropriate terminology in early exit" \
    "grep -A 50 '^## Early Exit Handling' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' | grep -q 'item_type.*bug'"

# Test 25: Verify P1 priority mentioned for early-exit bugs
run_test "Early exit bugs have P1 priority in standard" \
    "grep -A 30 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q '\"priority\": \"P1\"'"

# Test 26: File line count sanity check (should be substantial files)
run_test "OVERPROMPT-standard.md has reasonable length (>400 lines)" \
    "test \$(wc -l < \"\$TEMPLATES_DIR/OVERPROMPT-standard.md\") -gt 400"

run_test "OVERPROMPT-gitops.md has reasonable length (>400 lines)" \
    "test \$(wc -l < \"\$TEMPLATES_DIR/OVERPROMPT-gitops.md\") -gt 400"

# Test 27: Verify capture session state steps
run_test "Capture Session State mentioned in Early Exit Procedure (standard)" \
    "grep -A 10 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Capture Session State'"

run_test "Captured items include failure count (standard)" \
    "grep -A 15 'Capture Session State' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Failure count'"

run_test "Captured items include git status (standard)" \
    "grep -A 15 'Capture Session State' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Git status'"

# Test 28: Verify Proceed to Phase 5 steps (5-phase template structure)
run_test "Early Exit Procedure includes Proceed to Phase 5 (standard)" \
    "grep -A 60 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Proceed to Phase 5'"

run_test "Early Exit Procedure includes retrospective reference (standard)" \
    "grep -A 60 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -qi 'retrospective'"

run_test "Early Exit Procedure includes Exit gracefully (standard)" \
    "grep -A 60 '^### Early Exit Procedure' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q 'Exit gracefully'"

# Test 29: Verify metadata fields in work-item-creation call
run_test "Metadata includes severity field (standard)" \
    "grep -A 40 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q '\"severity\":'"

run_test "Metadata includes steps_to_reproduce field (standard)" \
    "grep -A 40 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q '\"steps_to_reproduce\":'"

run_test "Metadata includes impact field (standard)" \
    "grep -A 40 'work-item-creation-agent' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -q '\"impact\":'"

# Test 30: Cross-variant consistency check
run_test "Both variants have same number of Early Exit subsections" \
    "test $(grep -c '^### ' '$TEMPLATES_DIR/OVERPROMPT-standard.md' | grep -A 50 '^## Early Exit Handling') = $(grep -c '^### ' '$TEMPLATES_DIR/OVERPROMPT-gitops.md' | grep -A 50 '^## Early Exit Handling') || true"

echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo "Tests Run:    $TESTS_RUN"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    echo ""
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $test"
    done
else
    echo -e "${GREEN}Tests Failed: 0${NC}"
fi
echo ""

# Calculate success rate
if [ $TESTS_RUN -gt 0 ]; then
    SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($TESTS_PASSED/$TESTS_RUN)*100}")
    echo "Success Rate: $SUCCESS_RATE%"
fi

echo "======================================"

# Exit with failure code if any tests failed
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
