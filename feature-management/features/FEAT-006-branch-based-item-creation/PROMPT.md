# FEAT-006: Branch-based Work Item Creation with Human-in-the-Loop PR Review

**Status**: New
**Priority**: P1
**Component**: agents/shared
**Estimated Effort**: Medium (3-4 hours)

---

## Problem Statement

Currently, agents (test-runner-agent, retrospective-agent, early-exit handling) create work items directly on the master branch. This means:

- ❌ No quality control before items enter backlog
- ❌ Duplicate items waste processing cycles
- ❌ Multiple items that share a root cause aren't consolidated
- ❌ Poorly-specified items cause agent failures
- ❌ No human checkpoint to reject false positives

**Example scenario**: retrospective-agent detects a pattern and creates 5 bugs. Upon review, a human realizes these are all symptoms of one root cause. But they're already in the master backlog, so the next OVERPROMPT session will process all 5 wastefully.

## Proposed Solution

Create an **intelligent checkpoint at work item creation** where humans can review, consolidate, refine, or reject auto-created items before they enter the master backlog.

### Workflow

```
Agent detects issue(s)
    ↓
Agent creates branch: "auto-items-YYYY-MM-DD-HHMMSS"
    ↓
Invoke work-item-creation-agent multiple times (items created on branch)
    ↓
Agent commits all items with descriptive message
    ↓
Agent pushes branch to origin
    ↓
Agent creates PR using `gh pr create`
    ↓
Human reviews PR:
  - Consolidates duplicates
  - Improves descriptions
  - Rejects false positives
  - Approves valid items
    ↓
Merge PR → Items enter master backlog
    ↓
Next OVERPROMPT session processes approved items
```

### Benefits

1. **Quality Control**: Catch agent mistakes before they waste cycles
2. **Pattern Recognition**: "These 5 bugs are symptoms of one root cause"
3. **Batch Review**: Review all auto-created items from a session at once
4. **Easy Rejection**: Close PR to discard all items if agent misbehaved
5. **Preserves Autonomy**: Processing is still autonomous, just gated at input
6. **Audit Trail**: PR shows what was created and why

---

## Implementation Plan

### Section 1: Enhance work-item-creation-agent with Optional Branching

**File**: `/home/becker/projects/featmgmt/claude-agents/shared/work-item-creation-agent.md`

**Changes needed**:

1. Add optional `branch_name` parameter to input schema:
   ```json
   {
     "item_type": "bug|feature|human-action",
     "title": "...",
     "branch_name": "auto-items-2025-10-24",  // NEW: Optional
     ...
   }
   ```

2. Update workflow to handle branching:
   - If `branch_name` provided: Create/checkout branch before creating files
   - If `branch_name` not provided: Work on current branch (backward compatible)

3. Update output format to include branch info:
   ```json
   {
     "success": true,
     "item_id": "BUG-XXX",
     "branch_name": "auto-items-2025-10-24",  // NEW
     ...
   }
   ```

4. Document branching behavior in "Processing Steps" section

**Acceptance Criteria**:
- [ ] work-item-creation-agent accepts optional `branch_name` parameter
- [ ] Agent creates/checks out branch if `branch_name` provided
- [ ] Agent works on current branch if `branch_name` not provided (backward compatible)
- [ ] Output includes `branch_name` when used

---

### Section 2: Update Agents to Own PR Creation

**Rationale**: Each agent creating items knows the context for the PR better than a separate git-ops-agent. The agent owns the work item creation workflow, so it should own the PR creation that completes that workflow.

**Agents affected**: retrospective-agent, test-runner-agent, any agent creating multiple work items

---

#### 2.1: Update retrospective-agent for PR Creation

**File**: `/home/becker/projects/featmgmt/claude-agents/shared/retrospective-agent.md`

**When creating bulk/speculative items (3+)**:

1. **Generate branch name**: `auto-items-[timestamp]`
   ```bash
   BRANCH_NAME="auto-items-$(date +%Y-%m-%d-%H%M%S)"
   git checkout -b "$BRANCH_NAME"
   ```

2. **Invoke work-item-creation-agent multiple times** (items created on branch):
   - Set `auto_commit: false` for each item
   - Items are created but not committed individually

3. **Stage all created items**:
   ```bash
   git add bugs/ features/
   ```

4. **Create comprehensive commit**:
   ```bash
   git commit -m "Auto-created items from retrospective-agent - $(date +%Y-%m-%d)

   Created by: retrospective-agent
   Session: retrospective-$(date +%Y-%m-%d-%H%M%S)
   Context: Pattern detection during retrospective analysis

   Items created:
   - BUG-010: Test failures in authentication module (P1)
   - FEAT-007: Consolidate duplicate detection logic (P2)

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

5. **Push branch to origin**:
   ```bash
   git push -u origin "$BRANCH_NAME"
   ```

6. **Create PR using `gh pr create`**:
   ```bash
   gh pr create \
     --title "Auto-created items from retrospective-agent - $(date +%Y-%m-%d)" \
     --body "$(cat <<'EOF'
   ## Auto-Created Work Items

   **Created by**: retrospective-agent
   **Session**: $(date +%Y-%m-%d\ %H:%M:%S)
   **Context**: Pattern detection during retrospective analysis

   ## Items Created

   - **BUG-010**: Test failures in authentication module
     - Location: `bugs/BUG-010-auth-test-failures/`
     - Priority: P1
     - [View PROMPT.md](bugs/BUG-010-auth-test-failures/PROMPT.md)

   - **FEAT-007**: Consolidate duplicate detection logic
     - Location: `features/FEAT-007-consolidate-duplicate-detection/`
     - Priority: P2
     - [View PROMPT.md](features/FEAT-007-consolidate-duplicate-detection/PROMPT.md)

   ## Review Guidelines

   - ✅ Check for duplicates with existing items
   - ✅ Verify descriptions are clear and actionable
   - ✅ Consolidate items that share a root cause
   - ✅ Reject items that are false positives
   - ✅ Improve acceptance criteria if needed

   ## Next Steps

   - **Merge**: Items will enter the master backlog and be processed by next OVERPROMPT session
   - **Close**: Items will be discarded without entering backlog

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )" \
     --base master \
     --label "auto-created"
   ```

7. **Return PR URL to user**:
   ```
   ✅ Created 2 items on branch auto-items-2025-10-24-153045
   ✅ PR created: https://github.com/user/repo/pull/123
   📋 Review and merge to add items to backlog
   ```

**Acceptance Criteria**:
- [ ] retrospective-agent creates branch for bulk items (3+)
- [ ] Invokes work-item-creation-agent with `auto_commit: false`
- [ ] Commits all items together with descriptive message
- [ ] Pushes branch to origin
- [ ] Creates PR using `gh pr create`
- [ ] Returns PR URL to user
- [ ] Single items still use `auto_commit: true` (no PR needed)

---

#### 2.2: Update test-runner-agent for PR Creation

**File**: `/home/becker/projects/featmgmt/claude-agents/standard/test-runner-agent.md`

**When creating bulk test failure bugs (5+)**:

Same workflow as retrospective-agent, but:
- PR title: `Auto-created bugs from test failures - [date]`
- PR body includes test failure context and links to test run reports
- Threshold: 5+ test failures trigger PR workflow (fewer go direct to master with `auto_commit: true`)

**Acceptance Criteria**:
- [ ] test-runner-agent creates branch for bulk failures (5+)
- [ ] PR includes test failure context and evidence
- [ ] Single/few failures still commit directly to master

6. **Return PR URL**:
   ```json
   {
     "success": true,
     "operation": "create-items-pr",
     "branch_name": "auto-items-2025-10-24-153045",
     "pr_url": "https://github.com/owner/repo/pull/123",
     "pr_number": 123,
     "items_count": 2,
     "message": "PR created successfully. Review at: https://github.com/owner/repo/pull/123"
   }
   ```

**Acceptance Criteria**:
- [ ] git-ops-agent supports `create-items-pr` operation
- [ ] Branch is created/checked out
- [ ] All items are staged and committed with descriptive message
- [ ] Branch is pushed to remote
- [ ] PR is created with summary of all items
- [ ] PR includes links to each item's PROMPT.md/INSTRUCTIONS.md
- [ ] PR is labeled "auto-created"
- [ ] PR URL is returned to caller

---

### Section 3: Update retrospective-agent to Use Branching (Optional)

**File**: `/home/becker/projects/featmgmt/claude-agents/shared/retrospective-agent.md`

**Add branching workflow option** to the bug/feature creation sections:

**Current workflow** (direct to master):
```markdown
1. Invoke work-item-creation-agent for each bug/feature
2. Each item committed immediately to master
3. Items appear in backlog immediately
```

**New branching workflow** (for batch/speculative items):
```markdown
1. Generate branch name: "auto-items-[timestamp]"
2. For each bug/feature:
   - Invoke work-item-creation-agent with branch_name parameter
3. After all items created:
   - Invoke git-ops-agent operation="create-items-pr"
4. Return PR URL for human review
```

**When to use branching**:
- ✅ Creating 3+ items in single session (batch review valuable)
- ✅ Pattern-based detection (speculative, may need refinement)
- ✅ Multiple items that might share root cause
- ❌ Single critical bug (direct to master is fine)
- ❌ Human explicitly requested item (already approved)

**Acceptance Criteria**:
- [ ] retrospective-agent can use branching workflow for bulk item creation
- [ ] Agent chooses workflow based on item count and confidence
- [ ] Documentation includes examples of both workflows
- [ ] Agent returns PR URL when using branching workflow

---

### Section 4: Update test-runner-agent to Use Branching (Optional)

**File**: `/home/becker/projects/featmgmt/claude-agents/standard/test-runner-agent.md`

**Add branching workflow option** for bulk test failures:

**When to use branching**:
- ✅ 5+ test failures detected (likely related, consolidation possible)
- ✅ Same failure pattern across multiple tests
- ❌ 1-2 test failures (direct to master is fine)

**Acceptance Criteria**:
- [ ] test-runner-agent can use branching workflow for bulk failures
- [ ] Agent chooses workflow based on failure count and patterns
- [ ] Documentation includes examples of both workflows

---

### Section 5: Update Documentation

**Files to update**:
- `/home/becker/projects/featmgmt/docs/CUSTOMIZATION.md`
- `/home/becker/projects/featmgmt/templates/OVERPROMPT-standard.md`

**Add section**: "Human-in-the-Loop Workflow with PR Review"

**Content**:
```markdown
## Human-in-the-Loop Workflow

Agents can create work items on a separate branch for human review before entering the master backlog.

### Benefits
- Quality control checkpoint
- Batch review and consolidation
- Easy rejection of false positives
- Audit trail via PRs

### Workflow
1. Agent creates items on branch using work-item-creation-agent
2. Agent invokes git-ops-agent to create PR
3. Human reviews PR and consolidates/refines items
4. Merge PR → items enter backlog
5. Next OVERPROMPT session processes approved items

### Example Usage

**retrospective-agent creates 5 pattern-based bugs**:
```
[Agent invokes work-item-creation-agent 5 times with branch_name]
[Agent invokes git-ops-agent operation="create-items-pr"]
[Returns PR URL to user]
```

**Human reviews PR**:
- Realizes bugs #1-3 share root cause
- Consolidates into single bug
- Improves description
- Merges PR

**Result**: 3 bugs instead of 5, better specified
```

**Acceptance Criteria**:
- [ ] Documentation explains branching workflow
- [ ] Examples show both direct-to-master and PR-based workflows
- [ ] Benefits and use cases clearly documented

---

### Section 6: Testing

**Test Cases**:

1. **Test branching workflow with work-item-creation-agent**
   - Create bug with `branch_name` parameter
   - Verify branch created/checked out
   - Verify files created on branch
   - Verify master branch unaffected

2. **Test create-items-pr with git-ops-agent**
   - Create 3 test items on branch
   - Invoke git-ops-agent operation="create-items-pr"
   - Verify PR created with correct summary
   - Verify PR labeled "auto-created"
   - Verify PR includes links to all items

3. **Test backward compatibility**
   - Create item without `branch_name` parameter
   - Verify works on current branch (existing behavior)
   - Verify no breaking changes

4. **Test retrospective-agent integration**
   - Trigger pattern detection that creates 5 items
   - Verify branching workflow used
   - Verify PR created
   - Review and merge PR
   - Verify items appear in master backlog

5. **Test PR rejection workflow**
   - Create items on branch
   - Create PR
   - Close PR without merging
   - Verify items don't enter master backlog

**Acceptance Criteria**:
- [ ] All test cases pass
- [ ] Both workflows (direct and PR-based) work correctly
- [ ] Backward compatibility maintained
- [ ] PR workflow tested end-to-end

---

## Acceptance Criteria Summary

All sections complete when:

- [ ] work-item-creation-agent supports optional branching
- [ ] git-ops-agent supports create-items-pr operation
- [ ] retrospective-agent can use branching workflow
- [ ] test-runner-agent can use branching workflow (optional)
- [ ] Documentation updated with examples
- [ ] All test cases pass
- [ ] Backward compatibility maintained
- [ ] Changes committed and synced to consuming projects

---

## Related Items

- **FEAT-003**: work-item-creation-agent (dependency - must exist first)
- **FEAT-004**: Early-exit bug creation (could benefit from branching)
- **FEAT-005**: Blocking action detection (already implemented)

---

## Technical Notes

### Implementation Approach

**Option 2 Selected**: Keep work-item-creation-agent simple (just accept branch_name), put branching orchestration in git-ops-agent.

**Rationale**:
- work-item-creation-agent stays focused: create files
- git-ops-agent handles all git operations: branching, committing, PRs
- Clear separation of concerns
- Easier to test and maintain

### Affected Agents

1. **work-item-creation-agent**: Add optional `branch_name` parameter
2. **git-ops-agent**: Add `create-items-pr` operation
3. **retrospective-agent**: Optional use of branching for bulk items
4. **test-runner-agent**: Optional use of branching for bulk failures

### Git Operations

Branch naming convention: `auto-items-YYYY-MM-DD-HHMMSS`

Example: `auto-items-2025-10-24-153045`

### GitHub CLI Requirement

This feature requires `gh` (GitHub CLI) to be installed for PR creation. Fallback if not available: provide git commands for manual PR creation.

---

## Business Value

**High**: This feature creates an intelligent quality gate that:
- Reduces wasted processing cycles on poor-quality items
- Enables human pattern recognition and consolidation
- Preserves agent autonomy while adding quality control
- Provides audit trail of auto-created items
- Easy opt-out via PR closure

**ROI**: Every consolidated or rejected false-positive item saves an entire bug-processor-agent + test-runner-agent + git-ops-agent cycle.

---

## Implementation Checklist

### Pre-implementation
- [ ] Read and understand all sections
- [ ] Verify FEAT-003 (work-item-creation-agent) exists
- [ ] Verify gh CLI installed (`gh --version`)

### Implementation
- [ ] Section 1: Enhance work-item-creation-agent
- [ ] Section 2: Add create-items-pr to git-ops-agent
- [ ] Section 3: Update retrospective-agent (optional)
- [ ] Section 4: Update test-runner-agent (optional)
- [ ] Section 5: Update documentation
- [ ] Section 6: Run all tests

### Post-implementation
- [ ] Sync agents to consuming projects
- [ ] Update OVERPROMPT templates if needed
- [ ] Create usage examples
- [ ] Update this FEAT-006 status to completed
