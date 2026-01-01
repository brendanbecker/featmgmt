# Retrospective Pattern

## Purpose

Conducts comprehensive analysis of work sessions, identifies patterns across the backlog, reprioritizes items based on learnings, and maintains backlog health through deprecation, merging, and proactive issue creation. This pattern acts as a "scrum master" that ensures the backlog reflects reality and the team learns from every session.

## Problem Statement

Without systematic retrospective analysis:

- **Priority drift**: Items remain at stale priorities that no longer reflect reality
- **Backlog bloat**: Duplicate, obsolete, and superseded items accumulate
- **Pattern blindness**: Recurring issues aren't recognized or addressed systematically
- **Lost learnings**: Insights from sessions aren't captured or acted upon
- **Dependency hidden**: Blocking relationships between items aren't visible
- **Component neglect**: Struggling components don't receive appropriate attention

This pattern solves these problems by providing structured session analysis, pattern recognition, and active backlog management.

## Responsibilities

### Session Analysis
- Review completed session outcomes and patterns
- Analyze success/failure rates and root causes
- Identify component health trends
- Assess priority accuracy and velocity
- Detect dependency chains and blockers

### Backlog Reprioritization
- Review ALL bugs and features in repository
- Adjust priorities based on session learnings
- Identify items to deprecate or merge
- Update metadata files and summary indexes
- Commit all changes atomically

### Pattern Recognition
- Identify recurring issues across sessions
- Detect priority misalignments
- Find duplicate or overlapping work items
- Recognize dependency patterns
- Track component-specific trends

### Proactive Issue Creation
- Analyze patterns to identify missing work items
- Delegate bug creation for recurring failures
- Delegate feature creation for automation opportunities
- Use branch-based workflow for batch creation

### Continuous Improvement
- Generate actionable recommendations
- Suggest process improvements
- Document lessons learned
- Update backlog health metrics

## Workflow

### 1. Gather Session Context

Collect data about the session being analyzed:
- Read session state/configuration
- Read latest session reports
- Review recent version control history
- Load current bug and feature summaries

### 2. Analyze Session Outcomes

Evaluate what happened during the session:

**Success/Failure Patterns:**
- Which items were completed vs failed
- Common failure root causes
- Components with issues
- Success rates by priority level

**Priority Accuracy:**
- Were high-priority items truly critical?
- Did any items reveal hidden dependencies?
- Were priorities correctly calibrated?

**Component Health:**
- Bugs fixed vs failed per component
- Test pass rates
- Resolution complexity patterns
- Outstanding bug counts

**Dependencies:**
- Items that blocked other work
- Feature dependencies on bug fixes
- Circular dependencies
- Dependency chain mapping

### 3. Scan Entire Backlog

Review all active work items:
- Enumerate all bug and feature directories
- For each item, extract metadata:
  - Current priority, status, component
  - Creation date and age
  - Tags and categorization
- Identify relationships between items

### 4. Identify Items for Action

**Deprecation Candidates:**
- Superseded by completed work
- No longer relevant to project goals
- Blocked indefinitely with no path forward
- Duplicate of another item
- Component no longer exists

**Merge Candidates:**
- Address same root cause
- Significant scope overlap (>70%)
- Would be more efficient as single item
- Share acceptance criteria
- Target same functionality

**Priority Adjustments:**
- Revealed dependencies → higher priority
- Component health declining → higher priority
- Session revealed harder than expected → adjust
- Business value reassessment
- Security implications discovered

### 5. Pattern Analysis for New Issues

Analyze patterns that warrant new work items:

**Bug Creation Triggers:**
- Same test fails 3+ times within 2 weeks
- Component test pass rate declining >15%
- 3+ bugs in same component with related causes
- Repeated environmental failures

**Feature Creation Triggers:**
- Same human action type created 3+ times
- Workflow phase consistently slow
- Multiple bugs in areas without test coverage
- Clear tooling gaps identified

**Thresholds:**
- Bugs: 2+ occurrences OR 1 critical issue
- Features: 3+ occurrences OR clear high-impact opportunity
- Time window: Last 5 sessions

### 6. Execute Backlog Changes

**Deprecate Items:**
- Update metadata with deprecation info
- Update summary file status
- Move to deprecated directory
- Add deprecation note to comments

**Merge Items:**
- Update primary item with consolidated scope
- Mark merged-from items with merge info
- Move merged-from items to completed
- Update summary files

**Reprioritize Items:**
- Update metadata with new priority and reason
- Add priority change comment
- Re-sort summary files if needed

### 7. Create New Issues from Patterns

When patterns warrant new items:
- Generate branch name for batch operations
- Delegate to Work Item Creation pattern
- Process each pattern-detected issue
- Track all created items

### 8. Update Summary Files

Ensure all index files reflect current state:
- Update statistics sections
- Add entries for new items
- Remove entries for deprecated/moved items
- Add recent changes section

### 9. Commit Changes

Create comprehensive commit:
- Stage all modified files
- Generate detailed commit message
- Push to repository

### 10. Generate Retrospective Report

Create detailed analysis document:
- Executive summary
- Session performance metrics
- Priority accuracy assessment
- Component health analysis
- Dependency mapping
- Actions taken (deprecated, merged, reprioritized, created)
- Recommendations for next session
- Lessons learned

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `repository_path` | string | Path to feature management repository |
| `session_id` | string | Identifier for session being analyzed |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `session_report_path` | string | auto-detect | Path to session report |
| `auto_create_issues` | boolean | true | Create issues from pattern analysis |
| `dry_run` | boolean | false | Analyze without making changes |
| `lookback_sessions` | number | 5 | Number of sessions for pattern analysis |

## Output Contract

### Success Output

```
{
  "success": true,
  "report_path": "path to generated retrospective report",
  "commit_hash": "abc123",
  "summary": {
    "items_reviewed": number,
    "items_deprecated": number,
    "items_merged": number,
    "items_reprioritized": number,
    "items_created": number,
    "backlog_health": "improved | stable | needs_attention"
  },
  "changes": {
    "deprecations": [{"item_id", "reason"}],
    "merges": [{"primary_id", "merged_ids", "reason"}],
    "priority_changes": [{"item_id", "old_priority", "new_priority", "reason"}],
    "created_items": [{"item_id", "pattern", "location"}]
  },
  "recommendations": ["list of actionable recommendations"],
  "next_priority_item": {
    "item_id": "BUG-XXX",
    "title": "string",
    "reason": "why this is now top priority"
  }
}
```

### Error Output

```
{
  "success": false,
  "error": "Error category",
  "message": "Human-readable description",
  "partial_results": {
    "analysis_completed": true,
    "changes_applied": false
  }
}
```

## Decision Rules

### Deprecation Criteria
- **Deprecate**: Superseded, obsolete, blocked indefinitely, duplicate
- **Do NOT deprecate**: Just difficult, low priority, temporarily blocked

### Merge Criteria
- **Merge**: Same root cause, >70% overlap, same component + similar acceptance criteria
- **Do NOT merge**: Different components, different root causes, would be too complex

### Priority Increase Triggers
- Blocks multiple other items
- Security vulnerability discovered
- Production impact worse than assessed
- Component health declining
- User impact higher than expected

### Priority Decrease Triggers
- Dependency not yet ready
- Workaround implemented
- User impact lower than expected
- Technical debt acceptable for now

### Issue Creation Thresholds

| Pattern Type | Minimum Occurrences | Default Priority |
|--------------|---------------------|------------------|
| Recurring test failure | 3 | P2 |
| Component degradation | 3 sessions | P1 |
| Technical debt cluster | 3 related bugs | P1 |
| Flaky test | 2 pass/fail cycles | P2 |
| Automation opportunity | 3 manual actions | P2 |
| Missing test coverage | 2 bugs + low coverage | P1 |

### Bulk Creation Workflow
- 3+ items: Use branch-based PR workflow
- 1-2 items: Commit directly to main
- Pattern-detected items: Always use PR for review

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Bug Processor | Implementation outcomes |
| Test Runner | Test results, component health |
| Summary Reporter | Session statistics |
| Scan Prioritize | Original priority queue |

### Sends To

| Agent | Information |
|-------|-------------|
| Work Item Creation | New bugs/features from pattern analysis |
| Summary Reporter | Updated backlog state |
| Scan Prioritize | Reprioritized queue for next session |

### Coordination Protocol

1. Executes after work processing phase completes
2. Analyzes session outcomes and full backlog
3. Delegates issue creation as needed
4. Commits all changes atomically
5. Generates report for summary phase

## Quality Criteria

### Analysis Completeness
- [ ] All active bugs and features reviewed
- [ ] Priority accuracy assessed for each item
- [ ] Dependencies mapped comprehensively
- [ ] Component health evaluated

### Action Quality
- [ ] Deprecations have clear justification
- [ ] Merges are truly redundant/overlapping
- [ ] Priority changes based on evidence, not intuition
- [ ] All changes documented in comments

### Report Quality
- [ ] Actionable recommendations provided
- [ ] Data-driven insights
- [ ] Clear trend analysis
- [ ] Specific next steps

### Pattern Detection
- [ ] No obvious patterns missed
- [ ] Created items are actionable
- [ ] Thresholds applied consistently

## Implementation Notes

### State Management
- Track original state before modifications
- Support dry-run mode for preview
- Log all changes for audit trail

### Conflict Resolution
- If item modified since scan started, re-read before updating
- Prefer conservative action on conflicts
- Flag conflicts in report

### Report Generation
- Use template for consistency
- Include all data even if sections are empty
- Provide both executive summary and detailed analysis

### Extensibility
- Pattern detection rules should be configurable
- Thresholds should be adjustable per repository
- Custom report sections can be added
