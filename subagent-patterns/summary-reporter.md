# Summary Reporter Pattern

## Purpose

Generates comprehensive session reports that capture metrics, outcomes, patterns, and insights from work processing sessions. This pattern creates a historical record that enables trend analysis, process improvement, and accountability for autonomous work.

## Problem Statement

Without systematic session reporting:

- **Lost metrics**: Success rates, timing, and efficiency data aren't captured
- **No accountability**: What happened during autonomous sessions is opaque
- **Missed patterns**: Recurring issues and successes go unnoticed
- **Poor planning**: Future sessions can't learn from past performance
- **Stakeholder blindness**: No visibility into autonomous work outcomes

This pattern solves these problems by generating structured reports that capture every aspect of work sessions.

## Responsibilities

### Data Collection
- Gather metrics from all session phases
- Extract outcomes from processing agents
- Collect test results and verification data
- Identify human action items created

### Metric Calculation
- Calculate success/failure rates
- Compute timing statistics
- Aggregate test pass rates
- Track changes per component

### Pattern Analysis
- Identify recurring failure patterns
- Track component-specific trends
- Analyze root causes of failures
- Suggest process improvements

### Report Generation
- Create structured markdown reports
- Include executive summary
- Provide detailed breakdowns
- Add actionable recommendations

### Historical Tracking
- Maintain session history
- Enable trend comparison
- Document lessons learned
- Track improvement over time

## Workflow

### 1. Gather Session Data

Collect information from all sources:
- Session configuration (start time, parameters)
- Work items processed (IDs, titles, components)
- Processing outcomes (completed, failed, skipped)
- Git operations (commits, branches, PRs)
- Test results (pass/fail counts, coverage)
- Human actions created
- Errors encountered

### 2. Calculate Metrics

Compute aggregate statistics:

**Success Rate:**
```
success_rate = completed_items / total_processed_items × 100
```

**Average Time per Item:**
```
avg_time = total_duration / items_processed
```

**Test Pass Rate:**
```
pass_rate = passed_tests / total_tests × 100
```

**Efficiency Metrics:**
- Files modified per item
- Commits per item
- Sections completed

### 3. Analyze Bug Processing

For each processed item:
- Determine final status
- Count sections completed
- List files modified
- Record duration
- Note any issues

### 4. Aggregate Test Results

Combine all test execution data:
- Total runs and tests executed
- Pass/fail/skip counts
- Component breakdown
- Coverage percentages
- Failure patterns

### 5. Track Git Operations

Summarize version control activity:
- Commits created (count and messages)
- Branches created
- Pull requests opened
- Repositories modified

### 6. Generate Report

Create comprehensive markdown report with:
- Executive summary
- Items processed (completed/failed/skipped)
- Git operations summary
- Test results summary
- Human actions created
- Performance metrics
- Failure analysis
- Component health
- Files modified
- Session notes
- Next steps

### 7. Update Index

Add entry to session history index:
- Session date and ID
- Quick summary (items processed, success rate)
- Link to full report

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique identifier for the session |
| `session_start` | timestamp | When the session began |
| `session_end` | timestamp | When the session completed |
| `repository_path` | string | Path to feature management repository |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items_processed` | array | [] | List of work items processed |
| `test_results` | object | null | Aggregated test data |
| `git_operations` | array | [] | List of git commits/operations |
| `human_actions` | array | [] | Human action items created |
| `initial_queue_state` | object | null | Queue state at session start |
| `final_queue_state` | object | null | Queue state at session end |

## Output Contract

### Success Output

```
{
  "success": true,
  "report_path": "agent_runs/session-YYYY-MM-DD-HHMMSS.md",
  "summary": {
    "session_id": "session-YYYY-MM-DD-HHMMSS",
    "duration": "HH:MM:SS",
    "items_processed": number,
    "completed": number,
    "failed": number,
    "skipped": number,
    "success_rate": percentage,
    "human_actions_created": number,
    "commits_created": number,
    "tests_executed": number,
    "test_pass_rate": percentage
  },
  "highlights": ["key achievement 1", "key achievement 2"],
  "concerns": ["issue 1", "issue 2"],
  "next_session_recommendation": {
    "focus_area": "component name",
    "priority_range": "P0-P1",
    "estimated_items": number
  }
}
```

### Error Output

```
{
  "success": false,
  "error": "Insufficient session data",
  "message": "Could not generate report due to missing data",
  "partial_report": "path if partial report generated"
}
```

## Decision Rules

### Report Completeness
- All sections must be populated (use "N/A" or "0" for empty sections)
- Never generate incomplete reports
- If data is missing, note it explicitly

### Success Classification
- **Completed**: All acceptance criteria met, tests pass
- **Failed**: Implementation blocked or tests fail
- **Skipped**: Deprioritized or blocked by external factor

### Health Assessment
| Pass Rate | Status |
|-----------|--------|
| ≥95% | 🟢 Good |
| 80-94% | 🟡 Fair |
| <80% | 🔴 Needs Attention |

### Trend Determination
- **Improving**: Current metrics better than previous 3 sessions average
- **Stable**: Within 5% of previous average
- **Declining**: Current metrics worse than previous average

### Recommendation Priority
- Focus recommendations on:
  1. Components with declining health
  2. High-priority items that failed
  3. Recurring issues identified
  4. Quick wins available

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Scan Prioritize | Initial queue state |
| Bug Processor / Infra Executor | Processing outcomes |
| Test Runner / Verification | Test results |
| Retrospective | Backlog changes and patterns |

### Sends To

| Agent | Information |
|-------|-------------|
| User | Complete session report |
| Git History (indirectly) | Historical record for future queries |

### Coordination Protocol

1. Invoked at end of work session
2. Collects data from all previous phases
3. Generates comprehensive report
4. Saves report to persistent storage
5. Returns summary to orchestrator

## Quality Criteria

### Report Completeness
- [ ] All sections populated
- [ ] All processed items documented
- [ ] All metrics calculated accurately
- [ ] All recommendations actionable

### Data Accuracy
- [ ] Numbers match actual results
- [ ] Timestamps are correct
- [ ] File paths are valid
- [ ] Git hashes are real (if included)

### Insight Quality
- [ ] Pattern analysis is meaningful
- [ ] Recommendations are specific
- [ ] Lessons learned documented
- [ ] Next steps are clear

### Historical Tracking
- [ ] Report saved to correct location
- [ ] Index updated with new entry
- [ ] Format consistent with previous reports

## Implementation Notes

### Report Structure

```markdown
# Work Session Report

**Session ID**: session-YYYY-MM-DD-HHMMSS
**Date**: YYYY-MM-DD HH:MM:SS
**Duration**: HH:MM:SS

---

## Executive Summary
- Total Processed: X
- Completed: X (Y%)
- Failed: X
- Human Actions: X

---

## Items Processed
### Completed
[Details of each completed item]

### Failed
[Details of each failed item with reasons]

---

## Git Operations Summary
[Commits, branches, PRs]

---

## Test Results Summary
[Aggregate test statistics by component]

---

## Human Actions Created
[List with priorities and components]

---

## Performance Metrics
[Time breakdown, efficiency metrics]

---

## Failure Analysis
[Common patterns, root causes, recommendations]

---

## Component Health
[Status per component with trends]

---

## Next Steps
[Immediate actions, recommended focus for next session]

---

## Appendix
[Full item list, commit hashes, detailed statistics]
```

### Extensibility
- Report sections should be modular
- Custom sections can be added per variant
- Metrics should be extensible without format changes

### Performance
- Report generation should complete within 1 minute
- Large data sets should not block completion
- Partial reports acceptable if full generation times out
