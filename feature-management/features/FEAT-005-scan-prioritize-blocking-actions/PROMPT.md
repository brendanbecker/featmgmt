# FEAT-005: scan-prioritize-agent detects and recommends blocking human actions

**Priority**: P1
**Component**: agents/shared
**Type**: enhancement
**Estimated Effort**: medium
**Business Value**: high

## Overview

Enhance scan-prioritize-agent to analyze the `human-actions/` directory, detect when human actions are blocking critical bugs or features (P0/P1), and surface these blocking actions in the priority queue with recommendations to the user.

This enables users to unblock automated workflows by addressing human interventions first, preventing wasted agent cycles on items that cannot proceed.

## Problem Statement

Currently, the scan-prioritize-agent only scans `bugs/` and `features/` directories. If a P0 bug requires human intervention (e.g., "Get database credentials from ops team"), the bug might be prioritized high but cannot be processed until the human action is completed.

**Current workflow issues:**
- Agent attempts to process blocked bug
- Fails because human action prerequisite isn't met
- Failure logged, agent moves to next item
- Human action remains invisible in priority queue
- User doesn't know what needs human intervention
- Blocked bugs accumulate without resolution path

**Desired workflow:**
- Agent scans human-actions/ for blocking items
- Identifies which bugs/features are blocked by human actions
- Surfaces human actions in priority queue with context
- User sees: "Complete ACTION-001 first - blocks BUG-003 (P0)"
- User completes human action
- Agent can now successfully process unblocked bug

## Benefits

- **Workflow Efficiency**: Prevent wasted cycles on blocked items
- **User Visibility**: Clear view of what needs human intervention
- **Priority Awareness**: Understand which human actions are most critical
- **Unblocking Path**: Clear roadmap to unblock automated work
- **Reduced Failures**: Fewer agent failures from attempting blocked work

## Proposed Behavior

### 1. Scan human-actions/ Directory

The agent should:
- Read `human-actions/actions.md` summary file
- For each pending human action, read `action_report.json`
- Extract blocking_items field (array of bug/feature IDs)

Example `action_report.json`:
```json
{
  "action_id": "ACTION-001",
  "title": "Get production database credentials from ops team",
  "urgency": "high",
  "status": "pending",
  "blocking_items": ["BUG-003", "FEAT-007"]
}
```

### 2. Analyze Blocking Relationships

For each human action:
- Check if blocking_items array exists and is non-empty
- Look up each blocked item's priority (from bug_report.json or feature_request.json)
- Calculate effective urgency based on highest blocked priority:
  - Blocks P0 item → Urgency: critical
  - Blocks P1 item → Urgency: high
  - Blocks P2 item → Urgency: medium
  - Blocks P3 item → Urgency: low
  - Blocks nothing → Urgency: as specified in action_report.json

### 3. Update Priority Queue Output

Current output format:
```json
{
  "priority_queue": [
    {
      "item_id": "BUG-003",
      "priority": "P0",
      "component": "agents/infrastructure"
    }
  ]
}
```

Enhanced output format:
```json
{
  "priority_queue": [
    {
      "item_id": "BUG-003",
      "priority": "P0",
      "component": "agents/infrastructure",
      "blocked_by": "ACTION-001",
      "status": "blocked"
    }
  ],
  "human_actions_required": [
    {
      "action_id": "ACTION-001",
      "title": "Get production database credentials from ops team",
      "urgency": "critical",
      "reason": "Blocks BUG-003 (P0), BUG-005 (P1)",
      "blocking_items": ["BUG-003", "BUG-005"],
      "location": "human-actions/ACTION-001-get-db-credentials/"
    }
  ],
  "recommendations": [
    "⚠️  Complete ACTION-001 first - blocks 1 P0 bug and 1 P1 bug",
    "Processing blocked items will fail until human actions are resolved"
  ]
}
```

### 4. Provide User Recommendations

The agent should generate clear recommendations:

**When blocking human actions exist:**
```
⚠️  HUMAN ACTIONS REQUIRED BEFORE PROCESSING

The following human actions are blocking high-priority work items:

1. ACTION-001: Get production database credentials (CRITICAL)
   - Blocks: BUG-003 (P0), BUG-005 (P1)
   - Location: human-actions/ACTION-001-get-db-credentials/INSTRUCTIONS.md

2. ACTION-002: Review security policy changes (HIGH)
   - Blocks: FEAT-003 (P1)
   - Location: human-actions/ACTION-002-security-review/INSTRUCTIONS.md

RECOMMENDATION: Complete these human actions before running OVERPROMPT workflow
to avoid failures on blocked items.
```

**When no blocking actions:**
```
✓ No blocking human actions detected. All queued items can be processed.
```

## Implementation Tasks

### Task 1: Update scan-prioritize-agent.md

**File**: `claude-agents/shared/scan-prioritize-agent.md`

#### Add Human Actions Scanning

Add new section after feature scanning logic:

```markdown
## Phase 3: Scan Human Actions

### Read Human Actions Summary

Read `human-actions/actions.md` to get list of pending actions.

### For Each Pending Human Action

1. Read `action_report.json` from action directory
2. Extract metadata:
   - action_id
   - title
   - urgency (original)
   - status
   - blocking_items (array of bug/feature IDs)
3. Store in actions_list array

### Analyze Blocking Relationships

For each action in actions_list:

1. If blocking_items is empty or null, skip blocking analysis
2. For each blocked item ID:
   - Locate item in bugs/ or features/
   - Read priority from bug_report.json or feature_request.json
   - Track highest blocked priority
3. Calculate effective urgency:
   - If blocks P0 → urgency: "critical"
   - If blocks P1 → urgency: "high"
   - If blocks P2 → urgency: "medium"
   - If blocks P3 → urgency: "low"
   - Otherwise → use original urgency from action_report.json
4. Update action entry with:
   - effective_urgency
   - blocking_items (with priorities)
```

#### Update Priority Queue Generation

```markdown
## Phase 4: Build Priority Queue (Updated)

### Mark Blocked Items

For each item in priority_queue:

1. Check if any human action's blocking_items contains this item_id
2. If blocked:
   - Add "blocked_by": "{action_id}"
   - Add "status": "blocked"
3. If not blocked:
   - Add "status": "ready"

### Create human_actions_required Array

Filter actions_list for:
- status == "pending"
- effective_urgency in ["critical", "high"]
- blocking_items is non-empty

Sort by effective_urgency (critical > high > medium > low).

Format:
```json
{
  "action_id": "ACTION-001",
  "title": "...",
  "urgency": "critical",
  "reason": "Blocks BUG-003 (P0), BUG-005 (P1)",
  "blocking_items": ["BUG-003", "BUG-005"],
  "location": "human-actions/ACTION-001-slug/"
}
```

### Generate Recommendations

If human_actions_required is non-empty:

```
⚠️  HUMAN ACTIONS REQUIRED BEFORE PROCESSING

{for each action in human_actions_required}:
{index}. {action_id}: {title} ({urgency})
   - Blocks: {blocking_items with priorities}
   - Location: {location}/INSTRUCTIONS.md

RECOMMENDATION: Complete these human actions before running OVERPROMPT workflow
to avoid failures on blocked items.
```

If human_actions_required is empty:

```
✓ No blocking human actions detected. All queued items can be processed.
```
```

#### Update Output Schema

```markdown
## Output Format

```json
{
  "priority_queue": [
    {
      "item_id": "string",
      "priority": "P0|P1|P2|P3",
      "component": "string",
      "title": "string",
      "status": "ready|blocked",
      "blocked_by": "ACTION-XXX (optional, only if blocked)"
    }
  ],
  "human_actions_required": [
    {
      "action_id": "ACTION-XXX",
      "title": "string",
      "urgency": "critical|high|medium|low",
      "reason": "string (which items are blocked)",
      "blocking_items": ["item_id", ...],
      "location": "human-actions/ACTION-XXX-slug/"
    }
  ],
  "recommendations": [
    "string (user-facing recommendations)"
  ],
  "summary": {
    "total_bugs": number,
    "total_features": number,
    "total_human_actions": number,
    "blocking_actions": number,
    "blocked_items": number
  }
}
```
```

### Task 2: Create Human Actions Summary File Template

If `human-actions/actions.md` doesn't exist in projects, create template.

**File**: `templates/actions.md.template`

```markdown
# Human Actions Required

**Project**: {project_name}
**Last Updated**: {date}

## Summary Statistics
- Total Actions: 0
- Pending: 0
- Completed: 0

## Action List

| ID | Title | Urgency | Status | Blocking Items | Location |
|----|-------|---------|--------|----------------|----------|

## Recent Activity

### {date}
- No actions yet
```

### Task 3: Update action_report.json Schema

Ensure `blocking_items` field is documented and used consistently.

**File**: Documentation update in `docs/CUSTOMIZATION.md` or similar

```json
{
  "action_id": "ACTION-001",
  "title": "string",
  "component": "string",
  "urgency": "critical|high|medium|low",
  "status": "pending|in_progress|completed",
  "created_date": "YYYY-MM-DD",
  "updated_date": "YYYY-MM-DD",
  "assigned_to": "string|null",
  "tags": ["array"],
  "required_expertise": "string",
  "estimated_time": "string",
  "description": "string",
  "reason": "why human intervention is needed",
  "blocking_items": ["BUG-XXX", "FEAT-YYY"],  // IMPORTANT: IDs of blocked work items
  "evidence": {}
}
```

### Task 4: Update OVERPROMPT.md to Use Enhanced Output

**Files**:
- `templates/OVERPROMPT-standard.md`
- `templates/OVERPROMPT-gitops.md`

#### Phase 1 Update

After invoking scan-prioritize-agent, check for blocking human actions:

```markdown
## Phase 1: Scan & Prioritize

Invoke scan-prioritize-agent...

**Process scan-prioritize-agent output:**

1. **Check for blocking human actions:**
   - If `human_actions_required` is non-empty:
     - Display recommendations to user
     - Log blocking actions in session state
     - User decides: complete actions first, or skip blocked items

2. **Build priority queue:**
   - Include blocked_by and status fields
   - Filter out blocked items (optional, based on user preference)

3. **Proceed to Phase 2:**
   - If queue has ready items → Process next ready item
   - If queue only has blocked items → Exit to Phase 6 (retrospective)
   - If queue is empty → Exit to Phase 6
```

### Task 5: Update work-item-creation-agent (FEAT-003)

When creating human actions via work-item-creation-agent, ensure:

1. `blocking_items` field is included in input schema
2. action_report.json template includes `blocking_items: []`
3. Documentation explains how to populate blocking_items

**File**: `claude-agents/shared/work-item-creation-agent.md` (when implemented)

Add to human action creation:

```markdown
### Human Action Input Fields

```json
{
  "item_type": "human_action",
  "title": "string",
  "component": "string",
  "urgency": "critical|high|medium|low",
  "blocking_items": ["BUG-003", "FEAT-007"],  // Optional: IDs this action blocks
  "metadata": {
    "required_expertise": "string",
    "estimated_time": "string",
    "description": "string",
    "reason": "why human intervention is needed"
  }
}
```
```

## Acceptance Criteria

- [ ] scan-prioritize-agent scans `human-actions/` directory
- [ ] Agent reads `actions.md` and `action_report.json` files
- [ ] Agent analyzes `blocking_items` field for dependency relationships
- [ ] Effective urgency calculated based on highest blocked priority
- [ ] Priority queue items marked with `blocked_by` and `status` fields
- [ ] `human_actions_required` array includes blocking actions with context
- [ ] Recommendations generated for user when blocking actions exist
- [ ] Output includes summary statistics (blocking_actions, blocked_items counts)
- [ ] OVERPROMPT.md updated to display blocking action warnings
- [ ] User can see which human actions block which bugs/features
- [ ] Documentation updated for `blocking_items` field usage

## Testing Strategy

### Test Case 1: No Human Actions

**Setup:**
- Empty `human-actions/` directory or no pending actions

**Expected:**
- `human_actions_required`: []
- All items in priority_queue have `status: "ready"`
- Recommendation: "✓ No blocking human actions detected"

### Test Case 2: Human Action Blocking P0 Bug

**Setup:**
```
human-actions/ACTION-001-get-db-creds/
  action_report.json: { blocking_items: ["BUG-003"], urgency: "medium" }

bugs/BUG-003-subagents-not-available/
  bug_report.json: { priority: "P0" }
```

**Expected:**
- ACTION-001 effective_urgency: "critical" (blocks P0)
- BUG-003 in priority_queue: `blocked_by: "ACTION-001", status: "blocked"`
- `human_actions_required`: [ACTION-001 with urgency="critical"]
- Recommendation: "⚠️ Complete ACTION-001 first - blocks BUG-003 (P0)"

### Test Case 3: Multiple Blocking Actions

**Setup:**
```
ACTION-001: blocks BUG-003 (P0)
ACTION-002: blocks FEAT-004 (P2)
ACTION-003: blocks nothing
```

**Expected:**
- `human_actions_required`: [ACTION-001 (critical), ACTION-002 (medium)]
- ACTION-003 not included (doesn't block anything high priority)
- Recommendations sorted by urgency

### Test Case 4: One Action Blocks Multiple Items

**Setup:**
```
ACTION-001: blocks BUG-003 (P0), BUG-004 (P1), FEAT-002 (P2)
```

**Expected:**
- ACTION-001 urgency: "critical" (highest is P0)
- Reason: "Blocks BUG-003 (P0), BUG-004 (P1), FEAT-002 (P2)"
- All 3 items marked as `blocked_by: "ACTION-001"`

### Integration Test: Full OVERPROMPT Workflow

1. Create blocking human action
2. Run OVERPROMPT.md Phase 1
3. Verify blocking warnings displayed
4. Verify blocked items are not processed (or fail gracefully)
5. Complete human action (move to completed/)
6. Re-run Phase 1
7. Verify items are now unblocked and processed successfully

## Edge Cases

### Case 1: Blocked Item Doesn't Exist

If `blocking_items: ["BUG-999"]` but BUG-999 doesn't exist:
- Log warning: "ACTION-001 references non-existent item BUG-999"
- Continue processing other blocking_items
- Include in agent output warnings section

### Case 2: Circular Blocking

If BUG-003 creates ACTION-001, which blocks BUG-003:
- Detect circular dependency
- Log error: "Circular blocking detected: BUG-003 → ACTION-001 → BUG-003"
- Mark both as blocked
- User must resolve manually

### Case 3: Action Completed But Still in Pending

If `status: "completed"` but still in `human-actions/`:
- Don't include in `human_actions_required`
- Log info: "ACTION-001 completed but not archived"
- Suggest moving to completed/ directory

## User Experience Flow

### Before Enhancement

```
User runs OVERPROMPT.md
→ Phase 1: Scan shows BUG-003 (P0)
→ Phase 2: Attempt to process BUG-003
→ Fails: "Cannot proceed without database credentials"
→ User confused: "What do I need to do?"
```

### After Enhancement

```
User runs OVERPROMPT.md
→ Phase 1: Scan shows:
   ⚠️  HUMAN ACTIONS REQUIRED

   1. ACTION-001: Get production database credentials (CRITICAL)
      - Blocks: BUG-003 (P0)
      - Location: human-actions/ACTION-001-get-db-creds/INSTRUCTIONS.md

   RECOMMENDATION: Complete this action before processing BUG-003

→ User opens INSTRUCTIONS.md
→ User completes action
→ User marks ACTION-001 as completed
→ User re-runs OVERPROMPT.md
→ Phase 1: ✓ No blocking actions
→ Phase 2: Process BUG-003 (succeeds!)
```

## Notes

This feature is **critical for workflow efficiency**. Without it, users waste time running OVERPROMPT on blocked items, leading to failures and frustration.

By surfacing blocking human actions proactively, we:
- Save agent processing time
- Improve user experience
- Provide clear unblocking paths
- Enable truly autonomous workflows (once human prerequisites are met)

## Dependencies

None - this is an enhancement to existing scan-prioritize-agent functionality.

## Related Work Items

- **BUG-003**: Subagents not available - may require human action to install agents
- **FEAT-003**: work-item-creation-agent - should support creating human actions with blocking_items
- **FEAT-004**: Early-exit bug creation - should create human actions when agent blocked
