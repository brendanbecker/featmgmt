# BUG-005: Remove git-ops-agent - Over-abstraction Fragmenting Agent Responsibilities

**Status**: New
**Priority**: P2
**Severity**: Medium
**Component**: agents/shared
**Type**: Architectural cleanup

---

## Problem Statement

The git-ops-agent creates unnecessary abstraction by separating git operations from the agents that own the work. This is architectural over-engineering that:

- ❌ Fragments atomic operations (e.g., "create item" is incomplete without committing it)
- ❌ Adds coordination overhead (extra agent invocations)
- ❌ Obscures agent responsibilities (who's really doing the work?)
- ❌ Creates artificial boundaries in natural workflows
- ❌ Violates single responsibility principle (commit belongs to the agent that made the change)

### The "Python Code Writing Agent" Problem

This would be like bug-processor-agent delegating to a "python-code-writing-agent" every time it needs to write code. Git operations are **intrinsic** to each agent's work, not a separate concern.

## Why This Happened

During initial design, we correctly identified that git-ops-agent should be **shared** (used by both standard and gitops variants). However, we incorrectly applied the delegation pattern that worked for work-item-creation-agent:

**work-item-creation-agent** ✅ Good delegation:
- Complex, reusable logic (duplicate detection, ID generation)
- Multiple agents doing EXACTLY the same thing
- Distinct operation: "create a work item"
- Business logic worth centralizing

**git-ops-agent** ❌ Bad delegation:
- Simple operations (git add, git commit, git push)
- Each agent has DIFFERENT commit contexts
- Not a distinct operation - it's the **completion** of work
- No business logic - just infrastructure

## Correct Architecture

Git operations should be **performed by the agent that did the work**:

```
bug-processor-agent:
  1. Process PROMPT.md
  2. Make code changes
  3. Commit changes with context-specific message ← Agent's responsibility

retrospective-agent:
  1. Analyze session patterns
  2. Update backlog files
  3. Commit changes with retrospective context ← Agent's responsibility

work-item-creation-agent:
  1. Create item files
  2. Update summary files
  3. (Optional) Commit created item ← Agent's responsibility
```

Each agent **owns** the git commit because the commit message reflects what **that agent** accomplished.

---

## Implementation Plan

### Section 1: Delete git-ops-agent

**Files to delete**:
- `/home/becker/projects/featmgmt/claude-agents/shared/git-ops-agent.md`

**Acceptance Criteria**:
- [ ] git-ops-agent.md deleted from repository
- [ ] Commit message explains architectural reasoning

---

### Section 2: Update retrospective-agent to Own Its Git Operations

**File**: `/home/becker/projects/featmgmt/claude-agents/shared/retrospective-agent.md`

**Current state**: Already does its own git operations (lines 657-693)

**Changes needed**:
1. **Keep existing git operations** (they're already correct!)
2. **Remove any references** to delegating to git-ops-agent (if any exist)
3. **Clarify in documentation** that retrospective-agent owns its commits

**Git operations to preserve**:
```bash
# Stage all changes
git add bugs/ features/ completed/ deprecated/ ...

# Create detailed commit message
git commit -m "$(cat <<'EOF'
chore: Retrospective backlog reprioritization - session-YYYY-MM-DD
...
EOF
)"

# Push to origin
git push origin master
```

**Acceptance Criteria**:
- [ ] retrospective-agent performs its own git operations
- [ ] Documentation clarifies agent owns its commits
- [ ] No references to git-ops-agent delegation

---

### Section 3: Update work-item-creation-agent Git Handling

**File**: `/home/becker/projects/featmgmt/claude-agents/shared/work-item-creation-agent.md`

**Current state**: Step 11 (optional) - git add and commit

**Changes needed**:
1. **Keep optional git operations** (caller decides if items are committed)
2. **Clarify when to use**:
   - `commit_changes: true` - When creating single items that should be immediately committed
   - `commit_changes: false` - When creating multiple items that will be committed together
3. **Update documentation** to explain this is the agent's responsibility, not delegated

**Rationale for keeping optional commit**:
- Creating a work item and committing it is often atomic
- Caller knows whether to commit immediately or batch multiple items
- No need for separate agent invocation

**Acceptance Criteria**:
- [ ] work-item-creation-agent keeps optional git commit parameter
- [ ] Documentation clarifies when to use commit_changes: true/false
- [ ] No references to delegating to git-ops-agent

---

### Section 4: Update OVERPROMPT Templates

**Files**:
- `/home/becker/projects/featmgmt/templates/OVERPROMPT-standard.md`
- `/home/becker/projects/featmgmt/templates/OVERPROMPT-gitops.md`

**Changes needed**:

1. **Remove Phase 4**: "Git Operations → INVOKE git-ops-agent"
   - This phase becomes part of Phase 2 (bug-processor-agent commits its own changes)

2. **Update Phase 5**: "Archive"
   - Currently invokes git-ops-agent to archive and commit
   - Change to: Execute archive operations directly (move directory, update summary, commit)

3. **Update agent list** in introduction:
   - Remove git-ops-agent from available subagents list

4. **Update workflow diagram**:
   - Remove separate git-ops-agent phase
   - Show commits as part of each agent's work

**New Phase 4 (Archive & Update Summary)**:
```markdown
## Phase 4: Archive & Update Summary

After bug-processor-agent completes implementation and commits changes:

1. Update item status in bugs/bugs.md or features/features.md to "resolved"
2. Update summary statistics
3. Move {bugs|features}/{ITEM-ID}-[slug] to completed/
4. Commit with message 'Archive {ITEM-ID}: Moved to completed after resolution'
5. Push to origin master

Execute directly or delegate to bug-processor-agent as final step.
```

**Acceptance Criteria**:
- [ ] OVERPROMPT-standard.md updated to remove git-ops-agent
- [ ] OVERPROMPT-gitops.md updated to remove git-ops-agent
- [ ] Available agents list updated
- [ ] Workflow simplified with fewer phases
- [ ] Archive operations clearly documented

---

### Section 5: Update FEAT-006 Design

**File**: `/home/becker/projects/featmgmt/feature-management/features/FEAT-006-branch-based-item-creation/PROMPT.md`

**Changes needed**:

**Remove Section 2**: "Add create-items-pr Mode to git-ops-agent"

**Replace with Section 2**: "Update calling agents to handle PR creation"

**New approach**: Each agent that creates items on a branch is responsible for creating the PR:

```markdown
## Section 2: Update Calling Agents with PR Creation Logic

### retrospective-agent creates items on branch and PR

When creating bulk/speculative items (3+):

1. Generate branch name: "auto-items-[timestamp]"
2. Create and checkout branch
3. Invoke work-item-creation-agent multiple times (items created on branch)
4. Commit all items with descriptive message
5. Push branch to origin
6. Create PR using `gh pr create`:
   ```bash
   gh pr create \
     --title "Auto-created items from retrospective-agent - [date]" \
     --body "[summary of items with links]" \
     --base master \
     --label "auto-created"
   ```
7. Return PR URL to user

### test-runner-agent creates items on branch and PR

When encountering bulk test failures (5+):

1. Same workflow as retrospective-agent
2. PR title: "Auto-created bugs from test failures - [date]"
3. PR body includes test failure context
```

**Rationale**:
- The agent creating the items knows the context for the PR
- PR creation is the natural completion of "create items for review"
- No artificial handoff to another agent
- Simpler coordination

**Acceptance Criteria**:
- [ ] FEAT-006 updated to remove git-ops-agent dependency
- [ ] New design shows agents creating their own PRs
- [ ] PR creation is part of agent's workflow, not delegated

---

### Section 6: Update Documentation

**Files to update**:
- `/home/becker/projects/featmgmt/docs/CUSTOMIZATION.md`
- `/home/becker/projects/featmgmt/docs/ARCHITECTURE.md` (if exists)
- `/home/becker/projects/featmgmt/README.md`

**Changes needed**:

1. **Remove git-ops-agent references**:
   - Remove from agent list
   - Remove from workflow diagrams
   - Remove from examples

2. **Document git operations philosophy**:
   ```markdown
   ## Git Operations Philosophy

   Each agent is responsible for committing its own work. Git operations are
   intrinsic to an agent's responsibilities, not a separate concern.

   **Examples**:
   - bug-processor-agent commits code changes after implementation
   - retrospective-agent commits backlog updates after analysis
   - work-item-creation-agent optionally commits created items

   **Why not centralized git operations?**
   Git commits reflect the work of a specific agent. The commit message,
   context, and staging decisions are tightly coupled to what the agent
   accomplished. Delegating this fragments atomic operations and obscures
   responsibility.
   ```

3. **Update agent list**:
   - Standard agents: scan-prioritize-agent, bug-processor-agent, test-runner-agent
   - GitOps agents: task-scanner-agent, infra-executor-agent, verification-agent
   - Shared agents: ~~git-ops-agent~~, retrospective-agent, summary-reporter-agent, work-item-creation-agent

**Acceptance Criteria**:
- [ ] All git-ops-agent references removed from documentation
- [ ] Git operations philosophy documented
- [ ] Agent lists updated
- [ ] Examples show agents doing their own commits

---

### Section 7: Sync Changes to Consuming Projects

After all changes complete:

1. **Bump version** to 1.2.0 (minor version for architectural change)
2. **Sync agents** to consuming projects:
   ```bash
   ./scripts/sync-agents.sh --global standard
   # Or for each project:
   ./scripts/sync-agents.sh standard /path/to/project
   ```
3. **Update OVERPROMPT** in consuming projects:
   ```bash
   ./scripts/update-project.sh /path/to/triager/feature-management
   ./scripts/update-project.sh /path/to/ccbot/feature-management
   ./scripts/update-project.sh /path/to/midwestmtg/feature-management
   ```

**Acceptance Criteria**:
- [ ] Version bumped to 1.2.0
- [ ] Agents synced to all 4 projects (featmgmt, triager, ccbot, midwestmtg)
- [ ] OVERPROMPT templates updated in all projects
- [ ] No git-ops-agent.md files remain in any .claude/agents/ directory

---

## Testing Strategy

**Test 1: retrospective-agent commits its changes**
- Run retrospective-agent
- Verify it creates commit with appropriate message
- Verify changes pushed to remote

**Test 2: work-item-creation-agent with commit_changes: true**
- Create single bug with commit_changes: true
- Verify bug created and committed in single operation

**Test 3: work-item-creation-agent with commit_changes: false**
- Create 3 bugs with commit_changes: false
- Verify bugs created but not committed
- Manually commit all 3 together

**Test 4: OVERPROMPT workflow without git-ops-agent**
- Run full OVERPROMPT session
- Verify bug-processor-agent commits its changes
- Verify archive operations work without git-ops-agent
- Verify retrospective commits its changes

**Test 5: No git-ops-agent references remain**
- Search entire codebase for "git-ops-agent"
- Verify only historical references in completed/, session reports, etc.
- Verify no active workflow references exist

---

## Acceptance Criteria Summary

All sections complete when:

- [ ] git-ops-agent.md deleted
- [ ] retrospective-agent owns its git operations
- [ ] work-item-creation-agent keeps optional commit
- [ ] OVERPROMPT templates updated (removed git-ops-agent phases)
- [ ] FEAT-006 updated (removed git-ops-agent dependency)
- [ ] Documentation updated (philosophy and agent lists)
- [ ] Version bumped to 1.2.0
- [ ] Changes synced to all consuming projects
- [ ] All tests pass
- [ ] No active references to git-ops-agent remain

---

## Migration Notes

**Backward Compatibility**: None needed - git-ops-agent was only invoked by OVERPROMPT templates, which are being updated in the same release.

**Rollback Plan**:
- Restore git-ops-agent.md from git history
- Revert OVERPROMPT templates to previous version
- Update consuming projects back to 1.1.0

---

## Related Items

- **FEAT-003**: work-item-creation-agent (good delegation pattern - keep)
- **FEAT-006**: Branch-based PR workflow (needs update to remove git-ops-agent)

---

## Architectural Lessons

### Good Delegation (work-item-creation-agent)
✅ Complex, reusable business logic
✅ Multiple agents doing identical operations
✅ Clear, distinct responsibility
✅ Meaningful centralization

### Bad Delegation (git-ops-agent)
❌ Simple infrastructure operations
❌ Each agent has different context
❌ Fragments atomic operations
❌ Obscures responsibility

**Guideline**: Delegate when centralizing **business logic** that's truly identical across callers. Don't delegate when separating **completion steps** that are intrinsic to the operation.

---

## Implementation Checklist

### Pre-implementation
- [ ] Read entire PROMPT.md
- [ ] Understand architectural reasoning
- [ ] Review git-ops-agent current usage

### Implementation
- [ ] Section 1: Delete git-ops-agent.md
- [ ] Section 2: Update retrospective-agent
- [ ] Section 3: Update work-item-creation-agent
- [ ] Section 4: Update OVERPROMPT templates
- [ ] Section 5: Update FEAT-006 design
- [ ] Section 6: Update documentation
- [ ] Section 7: Sync to consuming projects

### Testing
- [ ] Test 1: retrospective-agent commits
- [ ] Test 2: work-item-creation with commit
- [ ] Test 3: work-item-creation without commit
- [ ] Test 4: Full OVERPROMPT workflow
- [ ] Test 5: No git-ops-agent references

### Post-implementation
- [ ] Mark BUG-005 as resolved
- [ ] Archive to completed/
- [ ] Create session report
- [ ] Celebrate cleaner architecture! 🎉
