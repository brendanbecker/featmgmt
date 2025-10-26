# Implementation Plan: FEAT-007

## Overview

Add proper status lifecycle tracking to the featmgmt workflow by updating bug-processor-agent to mark items as "in_progress" when starting work, and OVERPROMPT to mark items as "resolved" when archiving.

## Objectives

1. **Primary**: Implement status tracking in bug-processor-agent and OVERPROMPT workflows
2. **Secondary**: Document the complete status lifecycle for all work item types
3. **Tertiary**: Provide foundation for future metrics (time-to-completion, abandonment detection)

## Architecture Changes

### Affected Components

1. **claude-agents/standard/bug-processor-agent.md** - Add Step 0 for status updates
2. **templates/OVERPROMPT-standard.md** - Update Phase 4 archival process
3. **templates/OVERPROMPT-gitops.md** - Update Phase 4 archival process
4. **docs/CUSTOMIZATION.md** - Document status lifecycle
5. **docs/ARCHITECTURE.md** - Document state management design

### Status State Machine

```
┌─────────┐
│   new   │ (work-item-creation-agent creates)
└────┬────┘
     │
     ▼
┌─────────────┐
│ in_progress │ (bug-processor-agent marks)
└──────┬──────┘
       │
       ├──────────┐
       │          │
       ▼          ▼
  ┌──────────┐ ┌────────────┐
  │ resolved │ │ deprecated │ (retrospective-agent)
  └──────────┘ └──────┬─────┘
                      │
                      ▼
                  ┌────────┐
                  │ merged │ (retrospective-agent)
                  └────────┘
```

### New Fields

- **started_date**: Timestamp when bug-processor-agent marks item as in_progress
- Existing fields repurposed:
  - **completed_date**: When item archived (already used by some features)
  - **updated_date**: Last modification (already exists)

## Implementation Approach

### Phase 1: Agent Updates (Section 1)
- Add Step 0 to bug-processor-agent
- Include JSON read, update, write, commit logic
- Minimal changes to existing workflow

### Phase 2: OVERPROMPT Updates (Sections 2-3)
- Update Phase 4 in both OVERPROMPT variants
- Add metadata status update before archival
- Maintain existing commit message formats

### Phase 3: Documentation (Sections 4-5)
- Document complete status lifecycle
- Add state machine diagrams
- Explain date field semantics
- Connect to audit trail and metrics use cases

## Dependencies

None - this is an additive change that doesn't break existing items.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing items lack new fields | Low | Fields are optional, agents handle missing gracefully |
| Concurrent processing race | Low | Status provides basic lock, but not atomic (acceptable for current use) |
| Git conflicts during status update | Medium | Agents already handle push failures, status update follows same pattern |

## Testing Strategy

1. **Manual verification**: Create test bug, verify status transitions
2. **Integration test**: Run OVERPROMPT on test item, check all status changes committed
3. **Documentation review**: Verify docs match implementation
4. **Backward compatibility**: Verify old items without new fields still work

## Success Metrics

- [ ] All status transitions happen at correct workflow points
- [ ] Git history shows status update commits
- [ ] Documentation accurately describes status lifecycle
- [ ] No breaking changes to existing items

## Timeline Estimate

**Total Effort: 2-3 hours**

- Agent updates: 1 hour
- OVERPROMPT updates: 30 minutes
- Documentation: 1 hour
- Testing and verification: 30 minutes
