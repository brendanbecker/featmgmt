# FEAT-001 Implementation Plan

## Overview

This feature extends test-runner-agent to automatically create bugs and features based on test failures, enabling autonomous issue tracking and reducing manual overhead.

## Architecture

### Components Modified

1. **test-runner-agent.md**
   - Location: `claude-agents/standard/test-runner-agent.md`
   - New sections: Issue Detection, Failure Analysis, Bug Creation
   - Updated sections: Core Responsibilities, Tools, Workflow

### Data Flow

```
Test Execution
    ↓
Parse Test Output
    ↓
Identify Failure Patterns
    ↓
Categorize (Bug / Feature / Environmental)
    ↓
Check for Duplicates
    ↓
Create Issue Entry (if needed)
    ↓
Update Summary Files
    ↓
Include in Test Report
```

## Implementation Steps

### Step 1: Add Failure Pattern Recognition

**Location**: Section "Test Failure Analysis" in test-runner-agent.md

**Content**:
```markdown
## Test Failure Analysis

### Pattern Recognition

When tests fail, analyze output to categorize:

**Bug Indicators** (create bug entry):
- AssertionError: Expected X, got Y
- Uncaught exceptions (KeyError, AttributeError, TypeError, etc.)
- HTTP status code mismatches (expected 200, got 500)
- Integration test failures
- Regression test failures
- Data validation errors

**Feature Indicators** (create feature entry):
- NotImplementedError or NotImplemented exceptions
- Tests decorated with @pytest.mark.skip("not implemented")
- Tests decorated with @pytest.mark.xfail("planned feature")
- TODO/FIXME comments in failing tests
- Placeholder functions raising NotImplementedError

**Environmental Issues** (report but don't create entry):
- Connection timeout to external services
- Database connection refused
- Import errors for optional dependencies
- Missing environment variables
- Test database not initialized
- Port already in use errors
```

### Step 2: Add Duplicate Detection Logic

**Location**: New section "Duplicate Detection" in test-runner-agent.md

**Content**:
```markdown
## Duplicate Detection

Before creating new bug/feature, check for duplicates:

### Process
1. Read bugs.md and features.md summary files
2. Search for existing items matching:
   - Same test name
   - Same component + similar error message
   - Same file path + similar failure type

### Matching Criteria
**Exact match** (do not create new):
- Existing bug with same test_name field

**Similar match** (add comment instead):
- Same component AND similar title (>75% similarity)
- Same error type AND same file

### Action on Duplicate Found
Instead of creating new bug:
1. Add comment to existing bug's comments.md:
```markdown
## Test Run Update - [YYYY-MM-DD HH:MM:SS]

**Status**: Still failing
**Test Run**: agent_runs/test-run-[timestamp].md
**Error**: [current error message]

This bug was re-encountered during automated testing.
```
2. Update existing bug's updated_date field
3. Note in test report: "Updated existing BUG-XXX instead of creating duplicate"
```

### Step 3: Add Issue Creation Process

**Location**: New section "Automated Issue Creation" in test-runner-agent.md

**Content**:
```markdown
## Automated Issue Creation

### Workflow

When a new bug/feature should be created:

#### 1. Determine Next ID
```bash
# Find highest existing ID
cd /path/to/feature-management
ls -d bugs/BUG-* | sort -V | tail -1
# Extract number, add 1

# Or for features
ls -d features/FEAT-* | sort -V | tail -1
```

#### 2. Generate Slug
Convert test name to slug:
- test_oauth_token_refresh → oauth-token-refresh
- test_api_returns_404 → api-returns-404

#### 3. Create Directory Structure
```bash
mkdir -p bugs/BUG-042-test-oauth-token-refresh
```

#### 4. Write bug_report.json
```json
{
  "bug_id": "BUG-042",
  "title": "Test failure: test_oauth_token_refresh",
  "component": "backend/auth",
  "severity": "high",
  "priority": "P2",
  "status": "new",
  "type": "bug",
  "created_date": "2025-10-19",
  "discovered_by": "test-runner-agent",
  "test_run": "agent_runs/test-run-2025-10-19-143022.md",
  "test_name": "tests/test_auth.py::test_oauth_token_refresh",
  "tags": ["test-failure", "auth", "backend", "auto-generated"]
}
```

**Field Mappings**:
- component: Detect from test file path using .agent-config.json keywords
- severity: Map from failure type (exception → high, assertion → medium)
- priority: Default P2 (can be elevated by retrospective-agent)
- test_name: Full pytest node path or jest test identifier

#### 5. Write PROMPT.md
Template:
```markdown
# BUG-XXX: Test Failure - [test_name]

## Discovered By
**Agent**: test-runner-agent
**Test Run**: [link to test run report]
**Date**: [YYYY-MM-DD]

## Test Information
**Test File**: [file path]
**Test Name**: [full test name]
**Component**: [component]

## Failure Details

### Error Message
```
[error message]
```

### Stack Trace
```
[formatted stack trace]
```

### Expected Behavior
[extracted from assertion or test docstring]

### Actual Behavior
[extracted from error]

## Reproduction Steps
1. Run: `pytest [test_path] -v`
2. Observe [error type]

## Acceptance Criteria
- [ ] Test passes successfully
- [ ] Root cause identified and fixed
- [ ] Related tests still pass
```

#### 6. Update Summary File
Add row to bugs.md:
```markdown
| BUG-042 | Test failure: test_oauth_token_refresh | backend/auth | high | P2 | new | bugs/BUG-042-test-oauth-token-refresh |
```

Update statistics:
- Total Bugs: +1
- By Priority: P2 +1
- By Status: New +1
```

### Step 4: Update Tool Requirements

**Location**: Section "Tools Available" in test-runner-agent.md

**Change**:
```markdown
## Tools Available
- `Bash`: Execute test commands, database operations, kubectl
- `Read`: Read test configuration, pytest.ini, package.json, summary files
- `Grep`: Search test output for specific patterns
- `Write`: Create human action item files, bug/feature entries
```

### Step 5: Update Core Responsibilities

**Location**: Section "Core Responsibilities" in test-runner-agent.md

**Add**:
```markdown
### Issue Detection and Reporting
- Analyze test failures to identify bugs vs. features vs. environmental issues
- Check for duplicate issues before creating new entries
- Create bug/feature directories with proper metadata
- Update summary files (bugs.md, features.md)
- Link created issues to test run reports
```

### Step 6: Update Report Format

**Location**: Section "Report Format" in test-runner-agent.md

**Add new section**:
```markdown
### 🐛 Issues Created from Test Failures
**Total Issues**: [count] ([bugs] bugs, [features] features)

#### New Bugs
- **BUG-042**: Test failure: test_oauth_token_refresh
  - Component: backend/auth
  - Severity: high
  - Location: `bugs/BUG-042-test-oauth-token-refresh/`

#### New Features
- **FEAT-015**: Implement missing pagination endpoint
  - Component: backend/api
  - Priority: P2
  - Location: `features/FEAT-015-pagination-endpoint/`

#### Updated Existing Issues
- **BUG-038**: Added test failure update (still failing)
```

## Component Detection Strategy

Use .agent-config.json component_detection_keywords to map test file paths:

```
tests/backend/auth/ → component: "backend/auth"
tests/api/loans/ → component: "api/loans"
website/src/components/__tests__/ → component: "frontend/components"
```

Fallback: Use directory name before "tests/" or extract from test file path.

## Priority Assignment Logic

**P0 (Critical)**:
- Security test failures
- Data loss test failures
- Tests tagged with @pytest.mark.critical

**P1 (High)**:
- Integration test failures
- API contract violations
- Core functionality tests

**P2 (Medium)**: (Default)
- Unit test failures
- Most assertion errors

**P3 (Low)**:
- UI cosmetic tests
- Performance tests (unless severe degradation)

## Error Handling

### Invalid Test Output
If test output cannot be parsed:
- Log warning in test report
- Do not create bug entry
- Include raw output in report for manual review

### Missing Metadata
If component cannot be detected:
- Use "unknown" component
- Add tag "needs-component-classification"
- Flag in test report

### File System Errors
If bug directory creation fails:
- Log error in test report
- Continue with rest of test execution
- Report issue creation failure

## Testing This Implementation

### Manual Test Cases

1. **Create bug from failing pytest test**
   - Add a failing assertion to existing test
   - Run test-runner-agent
   - Verify bug entry created with correct metadata

2. **Duplicate detection**
   - Create bug manually for specific test
   - Run failing test again
   - Verify no duplicate, existing bug updated

3. **Feature detection from NotImplementedError**
   - Add test that expects unimplemented feature
   - Run test-runner-agent
   - Verify feature entry created (not bug)

4. **Environmental failure ignored**
   - Simulate database connection error
   - Verify no bug created
   - Verify failure logged in test report

### Validation Checklist

- [ ] Bug entries have all required fields
- [ ] PROMPT.md includes reproduction steps
- [ ] Component detected correctly
- [ ] Priority assigned reasonably
- [ ] Duplicate detection works
- [ ] Summary files updated
- [ ] Test report includes issue creation summary

## Rollout Plan

### Phase 1: Implementation
- Update test-runner-agent.md with new sections
- Add all logic and examples

### Phase 2: Documentation
- Update CLAUDE.md to mention auto-issue-creation
- Add examples to README.md

### Phase 3: Testing
- Test with real failing tests in triager project
- Verify bugs created correctly
- Check duplicate detection

### Phase 4: Refinement
- Adjust component detection based on results
- Tune priority assignment logic
- Improve duplicate matching

## Success Criteria

- Test-runner-agent creates well-formed bug entries from test failures
- Duplicate detection prevents noise
- Created bugs provide enough context for fixing
- Integration with existing workflow is seamless
- Zero manual intervention needed for issue creation

## Future Enhancements

- Flaky test detection (same test passes and fails)
- Pattern analysis across multiple test runs
- Automatic priority escalation for recurring failures
- Integration with git blame to suggest assignees
