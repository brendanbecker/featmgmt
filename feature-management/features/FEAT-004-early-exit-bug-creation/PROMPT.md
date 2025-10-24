# FEAT-004: Early-exit bug/feature creation on session failures

**Priority**: P2
**Component**: workflow
**Type**: enhancement
**Estimated Effort**: small
**Business Value**: medium
**Dependencies**: FEAT-003 (work-item-creation-agent)

## Overview

When OVERPROMPT encounters early exit conditions (3 consecutive failures, explicit STOP, errors), valuable context about what went wrong is lost. The workflow should automatically create a bug or feature capturing:

- What was being attempted
- Why it failed
- How many attempts were made
- Session state at failure
- Recommended next steps

This ensures failures become trackable work items rather than lost knowledge.

## Proposed Behavior

### Early Exit Triggers

The workflow should detect these conditions and create issues:

1. **3 consecutive item failures**
2. **Explicit STOP command** in comments.md
3. **Critical error** in workflow execution
4. **Subagent invocation failures** (after retries)

### On Early Exit

When an early exit is triggered:

1. **Invoke work-item-creation-agent** (FEAT-003)
2. **Create bug** with:
   - Title: "Session failure: [reason]"
   - Component: affected component or "workflow"
   - Priority: P1 (session-blocking issues are important)
   - Evidence: .agent-state.json, session logs, error output
   - PROMPT.md with debugging context
3. **Include in retrospective report**
4. **Allow retrospective-agent to run** despite early exit

### Item Type Decision

- **Failures/Errors**: Create bug
- **STOP with requested work**: Create feature (user is asking for something)
- **Blocked operations**: Create human action

## Implementation Tasks

### Task 1: Update OVERPROMPT.md - Add Early Exit Detection

**Files**:
- `templates/OVERPROMPT-standard.md`
- `templates/OVERPROMPT-gitops.md`

Add new section after Phase 7 logic:

```markdown
## Early Exit Handling

### Exit Conditions

Monitor for these conditions throughout execution:

1. **3 Consecutive Failures**:
   - Track failure count in .agent-state.json
   - If 3 items fail in a row, trigger early exit

2. **Explicit STOP Command**:
   - Check comments.md for "STOP" marker
   - If found, trigger early exit

3. **Critical Errors**:
   - Subagent invocation failures (after 3 retries)
   - File system errors
   - Git operation failures
   - Trigger early exit

### Early Exit Procedure

When early exit is triggered:

1. **Capture Session State**:
   - Current item being processed
   - Failure count and error messages
   - Agent outputs (if any)
   - Git status (uncommitted changes)

2. **Create Issue via work-item-creation-agent**:

   Invoke work-item-creation-agent with:

   ```json
   {
     "item_type": "bug",  // or "feature" if STOP with request
     "title": "Session failure: {reason}",
     "component": "{affected_component | workflow}",
     "priority": "P1",
     "evidence": [
       {
         "type": "file",
         "location": ".agent-state.json",
         "description": "Session state at failure"
       },
       {
         "type": "log",
         "location": "agent_runs/{timestamp}/",
         "description": "Session logs"
       },
       {
         "type": "output",
         "location": "error output text",
         "description": "Error messages"
       }
     ],
     "description": "OVERPROMPT session exited early due to: {reason}. This issue captures the context for debugging and resolution.",
     "metadata": {
       "severity": "high",
       "reproducibility": "{always | intermittent}",
       "steps_to_reproduce": [
         "Attempted to process item: {item_id}",
         "Failure occurred at phase: {phase}",
         "{specific_error_details}"
       ],
       "expected_behavior": "Session should complete successfully",
       "actual_behavior": "{what_happened}",
       "impact": "Blocked autonomous workflow execution"
     }
   }
   ```

3. **Proceed to Phase 6**: Run retrospective-agent despite early exit
4. **Proceed to Phase 7**: Run summary-reporter-agent
5. **Exit gracefully**

### Specific Cases

#### Case 1: 3 Consecutive Failures

```markdown
**Title**: "Session failure: 3 consecutive item processing failures"
**Component**: {last_item_component | workflow}
**Evidence**:
- All 3 failed items' directories
- Error outputs from bug-processor-agent or test-runner-agent
- .agent-state.json showing failure count
```

#### Case 2: Explicit STOP Command

```markdown
**Title**: "User-requested work: {work_description_from_comments}"
**Type**: feature (usually)
**Component**: {requested_component}
**Evidence**:
- comments.md with STOP marker and request details
```

#### Case 3: Critical Error

```markdown
**Title**: "Session failure: Critical error in {phase}"
**Component**: workflow
**Evidence**:
- Stack trace or error message
- Phase where error occurred
- Agent outputs if available
```

#### Case 4: Subagent Invocation Failures

```markdown
**Title**: "Session failure: Unable to invoke {agent_name}"
**Component**: agents/infrastructure
**Evidence**:
- Agent invocation attempts and errors
- Agent directory listing (.claude/agents/ or ~/.claude/agents/)
- Related to BUG-003
```
```

### Task 2: Update .agent-state.json Schema

Add fields to track failures:

```json
{
  "current_phase": "phase_2",
  "current_item": "BUG-003",
  "iteration_count": 1,
  "failure_count": 0,  // NEW: Track consecutive failures
  "last_failures": [],  // NEW: Array of last failed items
  "early_exit_triggered": false,  // NEW: Early exit flag
  "early_exit_reason": null  // NEW: Why we exited early
}
```

Update after each item:
- Success: Reset failure_count to 0
- Failure: Increment failure_count, append to last_failures

### Task 3: Update Safeguards Section

**Files**:
- `templates/OVERPROMPT-standard.md`
- `templates/OVERPROMPT-gitops.md`

Add to safeguards:

```markdown
### Early Exit Protection

- **Failure Tracking**: Count consecutive failures
- **Automatic Bug Creation**: Create bugs for unresolved failures
- **Knowledge Preservation**: Capture session state before exit
- **Graceful Shutdown**: Allow retrospective and summary even on early exit
```

### Task 4: Update Phase 6 (Retrospective)

Ensure retrospective-agent receives early exit context:

```markdown
## Phase 6: Retrospective Analysis

Invoke retrospective-agent with:

**Context to provide:**
- Session summary (successful items, failed items)
- .agent-state.json (including early_exit_* fields if applicable)
- Created issues from early exit (if any)
- Overall patterns observed

**Expected output:**
- Session analysis
- Pattern identification
- New bugs/features created from patterns
- Updated priority queue
- Recommendations for next session
```

### Task 5: Update Phase 7 (Summary Report)

Ensure summary includes early exit items:

```markdown
## Phase 7: Session Summary Report

Invoke summary-reporter-agent with:

**Context to provide:**
- All processed items (successful and failed)
- Issues created during session (including early-exit bugs)
- Retrospective findings
- Updated backlog state

**Expected output:**
- Formatted session report
- Saved to agent_runs/{timestamp}/session_report.md
- Includes early-exit items in "Issues Created" section
```

## Acceptance Criteria

- [ ] OVERPROMPT.md detects 3 consecutive failures and triggers early exit
- [ ] OVERPROMPT.md detects explicit STOP command and creates feature
- [ ] OVERPROMPT.md detects critical errors and creates bug
- [ ] Created items include full session state and debugging info
- [ ] .agent-state.json tracks failure_count and early_exit fields
- [ ] Retrospective still runs after early exit
- [ ] Summary report includes early-exit items created
- [ ] All early-exit bugs have P1 priority
- [ ] Evidence includes .agent-state.json and session logs
- [ ] PROMPT.md for created bugs includes debugging context

## Testing Strategy

### Test Case 1: 3 Consecutive Failures

1. Create 3 intentionally failing bugs (e.g., invalid file references)
2. Run OVERPROMPT.md
3. Verify failure_count increments to 3
4. Verify early exit is triggered
5. Verify bug is created: "Session failure: 3 consecutive item processing failures"
6. Verify retrospective and summary still run

### Test Case 2: Explicit STOP Command

1. Add STOP marker to a bug's comments.md with feature request
2. Run OVERPROMPT.md
3. Verify early exit on STOP detection
4. Verify feature is created with requested work
5. Verify retrospective and summary still run

### Test Case 3: Critical Error

1. Simulate critical error (e.g., corrupt .agent-state.json)
2. Run OVERPROMPT.md
3. Verify error is caught
4. Verify bug is created: "Session failure: Critical error in {phase}"
5. Verify graceful shutdown

### Test Case 4: Subagent Invocation Failure

1. Remove an agent from .claude/agents/
2. Run OVERPROMPT.md
3. Verify agent invocation fails after retries
4. Verify bug is created: "Session failure: Unable to invoke {agent}"
5. Verify graceful shutdown

## Notes

This feature is **defensive programming** - it ensures no knowledge is lost when sessions fail. By automatically creating bugs for failures, we build a self-documenting system that tracks its own problems.

## Dependencies

**FEAT-003** (work-item-creation-agent) must be implemented first, as this feature relies on programmatic issue creation.

## Integration with Existing Workflow

This feature enhances the existing OVERPROMPT workflow by adding safety nets:

- **Normal operation**: No changes to happy path
- **Failure scenarios**: Automatic issue creation and graceful degradation
- **Knowledge preservation**: Failed sessions become actionable bugs
- **Self-improvement**: System tracks its own failures for future fixes
