# FEAT-001: Enable test-runner-agent to Report Encountered Issues

## Description

Extend the test-runner-agent to automatically detect patterns in test failures that indicate bugs or missing features, and create draft bug/feature entries in the feature-management repository with structured issue reports.

## Problem Statement

Currently, when test-runner-agent executes tests and encounters failures, it reports the results but does not capture these as trackable work items. This means:
- Test failures that indicate bugs are not automatically tracked
- Patterns across multiple test failures are not recognized
- Manual intervention is required to create bug entries from test results
- Knowledge about test failures is lost between sessions

## Proposed Solution

Enhance test-runner-agent with issue detection and reporting capabilities:

1. **Failure Pattern Analysis**: Analyze test output to categorize failures
2. **Issue Detection**: Identify when failures indicate bugs vs. features vs. environmental issues
3. **Draft Entry Creation**: Automatically create bug/feature directories with metadata
4. **Context Preservation**: Include test output, stack traces, and failure context
5. **Linking**: Connect generated issues back to the test run that discovered them

## Acceptance Criteria

- [ ] Test-runner-agent can parse test failures and extract relevant information
- [ ] Agent identifies failure patterns that indicate:
  - New bugs (assertion failures, exceptions, unexpected behavior)
  - Missing features (NotImplementedError, missing functionality)
  - Environmental issues (connection errors, setup problems)
- [ ] Agent creates well-structured bug/feature entries in appropriate directories
- [ ] Generated entries include:
  - Proper metadata (bug_report.json or feature_request.json)
  - PROMPT.md with reproduction steps and context
  - Test output snippets and stack traces
  - Component detection from test file paths
  - Priority suggestion based on failure severity
- [ ] Agent links generated issues to the test run report
- [ ] Agent updates bugs.md / features.md summary files
- [ ] Only creates issues for genuine failures (not flaky tests or known issues)
- [ ] Handles duplicate detection (doesn't create duplicate bugs)

## Implementation Plan

### Phase 1: Failure Analysis Enhancement
**Location**: `claude-agents/standard/test-runner-agent.md`

Add new section: "Test Failure Analysis"
- Parse test framework output (pytest, jest, etc.)
- Extract failure type, message, stack trace, test file
- Categorize failures by pattern
- Identify root cause indicators

### Phase 2: Issue Detection Logic
**Location**: `claude-agents/standard/test-runner-agent.md`

Add new section: "Issue Detection Criteria"
- Define rules for when to create bugs vs. features
- Implement duplicate detection logic
- Check against existing bugs/features
- Filter out environmental/setup issues

### Phase 3: Draft Entry Creation
**Location**: `claude-agents/standard/test-runner-agent.md`

Add new section: "Automated Issue Creation"
- Create directory structure (bugs/BUG-XXX-slug or features/FEAT-XXX-slug)
- Generate bug_report.json / feature_request.json with metadata
- Create PROMPT.md with reproduction steps
- Include test output and stack traces
- Detect component from test file path
- Suggest priority based on severity

### Phase 4: Summary File Updates
**Location**: `claude-agents/standard/test-runner-agent.md`

Add new responsibility: "Update Summary Files"
- Add entries to bugs.md or features.md
- Link back to test run report
- Include "discovered-by: test-runner" tag

### Phase 5: Report Integration
**Location**: `claude-agents/standard/test-runner-agent.md`

Update "Report Format" section:
- Include list of issues created from test failures
- Show issue IDs and titles
- Provide links to created directories

## Technical Design

### New Capabilities for test-runner-agent

```markdown
## Issue Detection and Reporting

### Failure Pattern Recognition

Analyze test output to identify:

**Bug Indicators**:
- AssertionError with unexpected values
- Unhandled exceptions (KeyError, AttributeError, etc.)
- Failed integration tests
- Data validation failures
- API contract violations

**Feature Indicators**:
- NotImplementedError exceptions
- Tests marked as skip/xfail for missing functionality
- Comments in test code about future features
- Placeholder functions/methods

**Environmental Indicators** (do NOT create bugs):
- Connection timeouts to external services
- Missing test database setup
- Import errors for optional dependencies
- Configuration file not found

### Issue Creation Process

When a bug-worthy failure is detected:

1. **Generate Bug ID**: Find next available BUG-XXX number
2. **Create Directory**: `bugs/BUG-XXX-test-failure-description/`
3. **Write Metadata**: bug_report.json
4. **Write PROMPT.md**: Include:
   - Test name and file
   - Failure message and stack trace
   - Expected vs actual behavior
   - Reproduction steps
   - Component (detected from test path)
   - Link to test run report

5. **Update Summary**: Add to bugs.md
6. **Tag Appropriately**: "test-failure", "auto-generated", component tags

### Duplicate Detection

Before creating new bug:
- Read existing bugs.md
- Check for similar titles/components
- Look for existing bugs with same test name
- If duplicate found, add comment to existing bug instead

### Example bug_report.json

```json
{
  "bug_id": "BUG-042",
  "title": "Test failure: test_oauth_token_refresh fails with KeyError",
  "component": "backend/auth",
  "severity": "high",
  "priority": "P1",
  "status": "new",
  "type": "bug",
  "created_date": "2025-10-19",
  "discovered_by": "test-runner-agent",
  "test_run": "agent_runs/test-run-2025-10-19-143022.md",
  "test_name": "tests/test_auth.py::test_oauth_token_refresh",
  "tags": ["test-failure", "auth", "backend", "auto-generated"]
}
```

### Example PROMPT.md

```markdown
# BUG-042: Test Failure - test_oauth_token_refresh

## Discovered By
**Agent**: test-runner-agent
**Test Run**: agent_runs/test-run-2025-10-19-143022.md
**Date**: 2025-10-19

## Test Information
**Test File**: tests/test_auth.py
**Test Name**: test_oauth_token_refresh
**Component**: backend/auth

## Failure Details

### Error Message
```
KeyError: 'refresh_token'
```

### Stack Trace
```
tests/test_auth.py:145: in test_oauth_token_refresh
    token = auth_service.refresh_token(user_id)
app/services/auth.py:89: in refresh_token
    refresh = self.token_cache[user_id]['refresh_token']
E   KeyError: 'refresh_token'
```

### Expected Behavior
The test expects the auth service to retrieve a refresh token from the cache and return a new access token.

### Actual Behavior
The code raises a KeyError because the 'refresh_token' key is missing from the cached token data.

## Reproduction Steps
1. Run: `pytest tests/test_auth.py::test_oauth_token_refresh -v`
2. Observe KeyError

## Analysis
The token cache structure may be incomplete or the refresh_token is not being stored properly when tokens are initially cached.

## Acceptance Criteria
- [ ] Test passes successfully
- [ ] Token cache includes refresh_token
- [ ] Error handling for missing refresh_token added
- [ ] Related tests still pass

## Related Tests
- tests/test_auth.py::test_oauth_login (passed)
- tests/test_auth.py::test_token_cache (passed)
```
```

## Testing This Feature

### Test Scenarios

1. **Bug Creation from Test Failure**
   - Run test suite with known failing test
   - Verify test-runner-agent creates bug entry
   - Check metadata is correct
   - Verify bugs.md is updated

2. **Duplicate Detection**
   - Create existing bug manually
   - Run same failing test
   - Verify no duplicate bug created
   - Verify comment added to existing bug

3. **Environmental Failure Filtering**
   - Simulate database connection failure
   - Verify no bug created (environmental issue)
   - Verify failure noted in test report

4. **Multiple Failures**
   - Run suite with 3 different failing tests
   - Verify 3 distinct bugs created
   - Check each has proper context

## Integration Points

### Modified Files
- `claude-agents/standard/test-runner-agent.md`

### New Sections to Add
1. "Issue Detection and Reporting"
2. "Failure Pattern Recognition"
3. "Issue Creation Process"
4. "Duplicate Detection"

### Updated Sections
- "Report Format" - add created issues list
- "Core Responsibilities" - add issue reporting
- "Tools Available" - may need Write tool
- "Workflow Steps" - add Step 6: Create Issues

## Dependencies

- Requires Write tool access for test-runner-agent
- Needs access to bugs.md / features.md for duplicate detection
- Should respect .agent-config.json for component detection

## Priority and Component

**Priority**: P1 (High) - Enhances autonomous bug tracking
**Component**: agents/standard
**Estimated Effort**: Medium (2-3 hours implementation)

## Success Metrics

- Test-runner-agent automatically creates bugs from test failures
- Bugs have sufficient context for developers to understand and fix
- Duplicate detection prevents clutter
- Integration with existing workflow is seamless
- Summary files stay up-to-date automatically
