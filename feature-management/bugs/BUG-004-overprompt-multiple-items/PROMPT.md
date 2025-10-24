# BUG-004: OVERPROMPT processes multiple items per session (should be 1)

**Priority**: P1
**Component**: templates
**Severity**: medium
**Status**: new

## Problem Statement

OVERPROMPT.md currently allows "max 5 items per session" (lines 295, 301), but this is problematic:

- Without specialized agents, manual execution of 5 items is risky
- Creates large, hard-to-review git commits
- Violates single-responsibility principle
- Makes rollback difficult

The loop should **exit after exactly 1 iteration**, not 5. This should not be variable/configurable.

## Changes Required

### Files to Update

Both OVERPROMPT variants need this change:
1. `templates/OVERPROMPT-standard.md`
2. `templates/OVERPROMPT-gitops.md`

### Specific Edits

#### Edit 1: Line 295 - Session Limit Description

**Find:**
```markdown
(max 5 items per session)
```

**Replace with:**
```markdown
(max 1 item per session - exits after first item)
```

#### Edit 2: Line 301 - Session Limit Reference

**Find:**
```markdown
(5 items per session)
```

**Replace with:**
```markdown
(1 item per session)
```

#### Edit 3: Phase 7 Logic - Enforce Single Item

Locate the Phase 7 loop logic (around lines 456-481). Update to ensure exit after first item:

**Find:**
```markdown
### Iteration Control

Check iteration count:
- IF iteration < max_iterations (5):
  - Return to Phase 1 if queue has more items
```

**Replace with:**
```markdown
### Iteration Control

**ALWAYS exit after completing 1 item:**
- Do NOT return to Phase 1
- Proceed directly to Phase 6 (Retrospective)
- User can re-run OVERPROMPT.md manually for next item
```

#### Edit 4: Execution Flow Diagram (Lines 227-276)

Update the workflow diagram to show single-item processing:

**Find:**
```
Phase 7: Report
    ↓
IF queue not empty AND iteration < 5
    ↓
[Back to Phase 1] ← Loop
```

**Replace with:**
```
Phase 7: Report
    ↓
EXIT (session complete)
    ↓
User re-runs OVERPROMPT.md for next item
```

#### Edit 5: Safeguards Section

Locate the "Safeguards" section. Update to clarify 1-item limit:

**Find:**
```markdown
- Process items one at a time
- Maximum 5 items per session
```

**Replace with:**
```markdown
- Process exactly ONE item per session, then exit to Phase 6/7
- User manually re-runs OVERPROMPT.md to process next item
- Ensures focused commits and easier review
```

## Implementation Steps

1. **Update OVERPROMPT-standard.md:**
   - Apply all 5 edits above
   - Search for any other references to "5 items" or "max_iterations"
   - Ensure loop logic exits after 1 item

2. **Update OVERPROMPT-gitops.md:**
   - Apply same 5 edits (line numbers may differ slightly)
   - Search for any other references to "5 items" or "max_iterations"
   - Ensure loop logic exits after 1 item

3. **Verify No Remaining References:**
   ```bash
   grep -n "5 items" templates/OVERPROMPT-*.md
   grep -n "max_iterations" templates/OVERPROMPT-*.md
   ```
   Should return no results.

4. **Test Execution Flow:**
   - Open OVERPROMPT.md in a test project
   - Process 1 item
   - Verify workflow exits to Phase 6/7 (does not loop back)

## Acceptance Criteria

- [ ] OVERPROMPT-standard.md updated to process exactly 1 item per session
- [ ] OVERPROMPT-gitops.md updated to process exactly 1 item per session
- [ ] Execution flow diagram reflects single-item behavior
- [ ] Safeguards section clarifies 1-item limit
- [ ] No references to "5 items" remain in either template
- [ ] No loop-back logic after Phase 7 (session always exits)
- [ ] Test with actual OVERPROMPT execution - should stop after 1 item
- [ ] Documentation explains users must re-run OVERPROMPT.md for next item

## Rationale

**Why exactly 1 item, not configurable?**

1. **Focused Commits**: Each item gets its own atomic commit
2. **Easier Review**: Reviewers see one logical change at a time
3. **Safer Rollback**: If item fails, only that item needs reverting
4. **Error Isolation**: Problem in item 3 doesn't affect items 1-2
5. **Agent Compatibility**: Works with or without specialized agents
6. **User Control**: User decides when to process next item

**Why not make it configurable?**

Configuration adds complexity without clear benefit. The 1-item pattern is always the safer, more maintainable choice.

## Notes

This change enforces best practices learned from practical usage. Batch processing (5 items) sounded good in theory but created operational problems in practice.
