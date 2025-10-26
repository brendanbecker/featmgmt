# FEAT-007: Add in_progress Status Tracking to Workflow

## Objective

Add proper status lifecycle management to bug-processor-agent and OVERPROMPT workflow so that work items transition through clear states: `new` → `in_progress` → `resolved` (or `deprecated`/`merged`).

## Background

Currently, the status field in bug_report.json/feature_request.json remains "new" throughout the entire implementation process. Only human-actions use the 3-state model (pending/in_progress/completed). This creates:

- **Visibility gaps**: Can't tell which items are actively being worked on
- **Incomplete audit trail**: No record of when work actually started
- **Inconsistency**: Different status models for bugs/features vs actions
- **Risk of concurrent processing**: No lock mechanism if multiple agents run
- **No abandonment detection**: Can't identify items started but never completed

## Implementation Plan

### Section 1: Update bug-processor-agent

**File**: `claude-agents/standard/bug-processor-agent.md`

**Changes**:
1. Add new Step 0 before current Step 1 (around line 37)
2. Insert status update logic

**New Step 0 content**:
```markdown
### Step 0: Mark Item as In Progress

Before beginning implementation work:

1. **Read current metadata**:
   - Read `bug_report.json` or `feature_request.json` from the item directory

2. **Update status fields**:
   - Set `"status": "in_progress"`
   - Update `"updated_date": "YYYY-MM-DD"` (current date)
   - Add `"started_date": "YYYY-MM-DD"` (current date) if field doesn't exist

3. **Write updated JSON**:
   - Use Edit tool to update the JSON file

4. **Commit status change**:
   ```bash
   cd {feature-management-path}
   git add {bugs|features}/{ITEM-ID}-*/bug_report.json
   git commit -m "chore({ITEM-ID}): Mark as in_progress"
   git push origin master
   ```

**Important**: This status update should happen BEFORE any implementation work begins, creating a clear audit trail of when work started.
```

3. Update the "Workflow Steps" section header to reflect new step numbering (Step 1 becomes Step 1, etc.)

### Section 2: Update OVERPROMPT-standard.md

**File**: `templates/OVERPROMPT-standard.md`

**Changes**:
1. Update Phase 4 (Archive & Update Summary) around line 136
2. Add metadata status update before moving to completed

**Updated Phase 4 Step 1**:
```markdown
1. **Update metadata status**:
   - Read bug_report.json or feature_request.json from item directory
   - Update fields:
     - `"status": "resolved"`
     - `"completed_date": "YYYY-MM-DD"` (current date)
     - `"updated_date": "YYYY-MM-DD"` (current date)
   - Write updated JSON back to file

2. **Update summary status**:
   - Update status in `bugs/bugs.md` or `features/features.md` to "resolved"
   - Update summary statistics at the bottom of the file
```

### Section 3: Update OVERPROMPT-gitops.md

**File**: `templates/OVERPROMPT-gitops.md`

**Changes**: Same as Section 2, but for GitOps variant (around line 360-380 in Phase 4)

### Section 4: Document Status Lifecycle

**File**: `docs/CUSTOMIZATION.md`

**Changes**: Add new section after line 233 (after action_report.json schema)

**New section**:
```markdown
### Work Item Status Lifecycle

All work items (bugs and features) follow a consistent status lifecycle:

**Status Values:**
- `"new"` - Created by work-item-creation-agent, not yet started
- `"in_progress"` - bug-processor-agent has begun implementation
- `"resolved"` - Implementation completed and item archived
- `"deprecated"` - retrospective-agent marked as obsolete
- `"merged"` - retrospective-agent merged into another item

**Lifecycle Flow:**
```
new → in_progress → resolved → [archived to completed/]
  ↓         ↓
deprecated  deprecated
  ↓         ↓
merged    merged
```

**Date Tracking:**
- `created_date`: When work-item-creation-agent created the item
- `started_date`: When bug-processor-agent marked it in_progress (new field)
- `updated_date`: Last modification timestamp
- `completed_date`: When OVERPROMPT archived to completed/
- `deprecated_date`: When retrospective-agent deprecated it
- `merged_date`: When retrospective-agent merged it

**Consistency with Human Actions:**

Human actions use a similar 3-state model:
- `"pending"` → `"in_progress"` → `"completed"`

This alignment ensures consistent status semantics across all work item types.
```

**File**: `docs/ARCHITECTURE.md`

**Changes**: Add subsection under "Component Architecture" around line 150

**New subsection**:
```markdown
### Status and State Management

**Status Lifecycle**: All work items follow consistent status transitions:

| Status | Set By | Meaning |
|--------|--------|---------|
| `new` | work-item-creation-agent | Created but not started |
| `in_progress` | bug-processor-agent | Currently being implemented |
| `resolved` | OVERPROMPT Phase 4 | Completed successfully |
| `deprecated` | retrospective-agent | Obsolete/superseded |
| `merged` | retrospective-agent | Consolidated into another item |

**Audit Trail**: The combination of `created_date`, `started_date`, `updated_date`, and `completed_date` provides complete timeline tracking for metrics and analysis.

**Concurrent Safety**: The `in_progress` status acts as a basic lock mechanism, preventing multiple agents from starting the same item simultaneously.
```

### Section 5: Update Templates README

**File**: `templates/README.md.template`

**Changes**: Update usage documentation to mention status tracking (if README mentions workflow)

**Add note** (if workflow section exists):
```markdown
Status tracking: Work items automatically transition through states (new → in_progress → resolved) as the workflow processes them, providing visibility and audit trail.
```

## Acceptance Criteria

### Section 1: bug-processor-agent
- [ ] Step 0 added before current Step 1
- [ ] Status update logic correctly reads JSON, updates fields, writes back
- [ ] Commit step included with correct message format
- [ ] Subsequent step numbers remain consistent

### Section 2: OVERPROMPT-standard.md
- [ ] Phase 4 Step 1 adds metadata status update
- [ ] All three status fields updated (status, completed_date, updated_date)
- [ ] Logic placed before summary file update

### Section 3: OVERPROMPT-gitops.md
- [ ] Same changes as Section 2 applied to GitOps variant
- [ ] Maintains consistency with standard variant

### Section 4: Documentation Updates
- [ ] CUSTOMIZATION.md has new status lifecycle section
- [ ] Status values clearly documented
- [ ] Lifecycle flow diagram included
- [ ] Date field meanings explained
- [ ] ARCHITECTURE.md has status management subsection
- [ ] Status table included
- [ ] Audit trail and concurrent safety benefits documented

### Section 5: README Updates
- [ ] Template README mentions status tracking (if applicable)

## Testing Plan

1. **Unit Test**: Create test bug, verify bug-processor-agent sets in_progress
2. **Integration Test**: Run full OVERPROMPT workflow, verify status transitions
3. **Verify Commits**: Check git log shows status update commits
4. **Documentation Review**: Ensure docs accurately describe behavior

## Notes

- This is an additive change - no breaking changes to existing items
- Existing items with status="new" will transition to "in_progress" when processed
- The `started_date` field is new but optional (won't break existing items)
- retrospective-agent already updates status to "deprecated"/"merged", no changes needed there
