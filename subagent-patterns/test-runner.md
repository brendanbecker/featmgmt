# Test Runner Pattern

## Purpose

Executes test suites to validate implementations, manages test environment setup, analyzes failures to create actionable bug reports, and creates human action items for tests requiring manual intervention. This pattern ensures quality gates are enforced and test failures are systematically tracked.

## Problem Statement

Without systematic test execution and analysis:

- **Silent failures**: Test failures go unnoticed or undocumented
- **Lost context**: Test results aren't linked to work items
- **Duplicate bugs**: Same failure creates multiple bug reports
- **Environmental confusion**: Failures from environment issues treated as bugs
- **Manual testing gaps**: UI/integration tests requiring humans aren't tracked

This pattern solves these problems by providing structured test execution with intelligent failure analysis and automated issue creation.

## Responsibilities

### Test Environment Management
- Verify test environment is properly configured
- Ensure test databases exist and are isolated
- Set appropriate environment variables
- Never touch production environments

### Test Execution
- Run appropriate test suites for each component
- Parse test output and results
- Identify failures, errors, and skipped tests
- Capture coverage information where available

### Failure Analysis
- Categorize failures (bug, feature gap, environmental)
- Identify root causes
- Determine if failures relate to recent changes
- Check for duplicate existing issues

### Issue Creation
- Delegate bug/feature creation to work item creation pattern
- Provide complete evidence and context
- Update existing issues if duplicates found
- Use branch-based workflow for bulk failures

### Human Action Creation
- Identify tests requiring manual intervention
- Create action items with clear instructions
- Link actions to parent work items
- Document manual testing procedures

## Workflow

### 1. Setup Test Environment

Verify and configure test environment:
- Check test database exists
- Clean test database (delete data, preserve schema)
- Set environment variables for test mode
- Verify service connectivity

### 2. Execute Tests

Run appropriate test suites:

**For each component:**
- Navigate to project directory
- Activate virtual environment if needed
- Execute test command
- Capture output and results

### 3. Parse Results

Extract from test output:
- Total tests run
- Passed count
- Failed count
- Skipped count
- Error messages and stack traces
- Test names and locations
- Duration
- Coverage (if available)

### 4. Analyze Failures

For each failed test, categorize:

**Bug Indicators** (create bug):
- Assertion errors
- Uncaught exceptions
- HTTP status mismatches
- Integration failures
- Data validation errors

**Feature Indicators** (create feature):
- NotImplementedError
- Skipped with "not implemented"
- Placeholder functions

**Environmental Issues** (report only, no issue):
- Connection timeouts
- Database connection refused
- Missing environment variables
- Port conflicts
- Permission errors

### 5. Check for Duplicates

Before creating issues:
- Read summary files
- Search for existing items with:
  - Same test name
  - Same component + similar title
  - Same error type + file path
- If duplicate found: update existing issue instead

### 6. Create Issues

For bug/feature failures:
- Delegate to Work Item Creation pattern
- Provide complete evidence
- Use branch workflow for 5+ failures
- Track all created items

### 7. Create Human Actions

For tests requiring manual intervention:
- Discord bot commands
- UI visual verification
- User workflow validation
- External integration testing

Create action items with:
- Clear test steps
- Expected results
- Prerequisites
- Completion criteria

### 8. Generate Report

Create test execution report with:
- Executive summary
- Detailed results by component
- Issues created
- Human actions created
- Environmental issues noted
- Recommendations

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `work_item_id` | string | Work item being tested |
| `repository_path` | string | Path to project repository |
| `feature_management_path` | string | Path to feature management repo |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `components` | array | ["all"] | Components to test |
| `test_pattern` | string | "*" | Pattern to filter tests |
| `skip_setup` | boolean | false | Skip database setup |
| `create_issues` | boolean | true | Create bugs for failures |
| `coverage_threshold` | number | null | Minimum coverage required |

## Output Contract

### Success Output

```
{
  "success": true,
  "overall_status": "passed | failed | partial",
  "summary": {
    "total_tests": number,
    "passed": number,
    "failed": number,
    "skipped": number,
    "duration_seconds": number,
    "pass_rate": percentage
  },
  "components": {
    "component_name": {
      "tests": number,
      "passed": number,
      "failed": number,
      "coverage": percentage
    }
  },
  "failures": [
    {
      "test_name": "string",
      "error_type": "string",
      "message": "string",
      "category": "bug | feature | environmental",
      "action_taken": "created BUG-XXX | updated BUG-XXX | reported only"
    }
  ],
  "issues_created": [
    {
      "item_id": "BUG-XXX",
      "title": "string",
      "component": "string",
      "test_name": "string"
    }
  ],
  "human_actions_created": [
    {
      "action_id": "ACTION-XXX",
      "title": "string",
      "related_to": "BUG-XXX"
    }
  ],
  "report_path": "agent_runs/test-run-YYYY-MM-DD-HHMMSS.md"
}
```

### Error Output

```
{
  "success": false,
  "error": "Environment setup failed",
  "message": "Could not connect to test database",
  "recommendation": "Check database configuration"
}
```

## Decision Rules

### Failure Categorization

| Error Pattern | Category | Action |
|---------------|----------|--------|
| AssertionError | bug | Create issue |
| KeyError, AttributeError, TypeError | bug | Create issue |
| HTTP 500, 401, 403 (unexpected) | bug | Create issue |
| NotImplementedError | feature | Create feature |
| @skip("not implemented") | feature | Create feature |
| Connection timeout | environmental | Report only |
| Database connection refused | environmental | Report only |
| Missing env variable | environmental | Report only |

### Priority Assignment

| Test Type | Default Priority |
|-----------|------------------|
| Security tests | P0 |
| Integration tests | P1 |
| API contract tests | P1 |
| Unit tests | P2 |
| UI cosmetic tests | P3 |

### Severity Assignment (Bugs)

| Error Type | Severity |
|------------|----------|
| Security vulnerability | critical |
| Uncaught exception | high |
| Assertion failure | medium |
| Cosmetic issue | low |

### Duplicate Detection
- Exact test_name match → update existing
- Same component + >75% title similarity → update existing
- Same error type + file path → update existing
- Otherwise → create new

### Bulk Creation Threshold
- 1-4 failures: Create directly on main branch
- 5+ failures: Use PR-based workflow for review

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Bug Processor / Infra Executor | What was changed, needs testing |
| Orchestrator | Test request with scope |

### Sends To

| Agent | Information |
|-------|-------------|
| Work Item Creation | Bug/feature details for creation |
| Bug Processor | Test results (pass/fail) |
| Summary Reporter | Test metrics for session report |
| User | Test results and action items |

### Coordination Protocol

1. Invoked after implementation phase
2. Sets up test environment
3. Executes tests
4. Analyzes and creates issues
5. Reports results to orchestrator
6. If failed: may trigger return to implementation phase

## Quality Criteria

### Environment Safety
- [ ] Never connects to production database
- [ ] Test database verified before execution
- [ ] Test isolation confirmed
- [ ] Environment variables set correctly

### Test Execution
- [ ] All relevant tests run
- [ ] No false positives/negatives
- [ ] Human actions created for manual tests
- [ ] Clear pass/fail determination

### Issue Quality
- [ ] Bugs have complete reproduction steps
- [ ] Evidence includes actual error output
- [ ] Component correctly identified
- [ ] Priority appropriately assigned
- [ ] Duplicates detected and handled

### Report Quality
- [ ] All tests documented
- [ ] Clear success/failure status
- [ ] Actionable recommendations
- [ ] Environmental issues separated from bugs

## Implementation Notes

### Database Safety

**Always verify test database before running:**
```
1. Check DATABASE_URL contains test database name
2. Verify connection to test database succeeds
3. Confirm not connected to production
4. Clean test data (preserve schema)
```

### Test Report Format

```markdown
# Test Execution Report

**Component**: [component]
**Work Item**: [BUG-XXX or FEAT-XXX]
**Date**: YYYY-MM-DD HH:MM:SS
**Database**: test_database @ host

## Summary
- **Status**: PASSED | FAILED | PARTIAL
- **Total Tests**: X
- **Passed**: X (Y%)
- **Failed**: X
- **Duration**: Xs

## Results Detail

### Passed Tests
[Summary of passing tests]

### Failed Tests
[Detailed failure analysis]

### Issues Created
[List of bugs/features created]

### Human Actions Created
[List of manual test items]

## Recommendations
[Next steps based on results]
```

### Extensibility
- Support for different test frameworks
- Configurable categorization rules
- Custom issue templates per project
- Pluggable duplicate detection
