# FEAT-006 Implementation Tasks

## Section 1: Enhance work-item-creation-agent with Optional Branching  ✅ COMPLETED - 2025-10-24

### TASK-001: Add branch_name parameter to input schema  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added optional `branch_name` parameter to input schema. Parameter is fully backward compatible - works without branch_name (continues on current branch).

### TASK-002: Update workflow to handle branching  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added step 6.5 "Handle Branch Creation" that creates/checks out branch if branch_name provided. Falls through to current branch if not provided. Output includes `branch_name` field in JSON response.

### TASK-003: Document branching behavior  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added comprehensive documentation:
- "When to Use branch_name" section with use cases and workflow
- Processing Steps section includes branch handling logic
- Clear examples of when to use vs not use branch_name
- Documented that branch_name should be paired with auto_commit: false

---

## Section 2: Update Agents to Own PR Creation  ✅ COMPLETED - 2025-10-24

### Section 2.1: Update retrospective-agent for PR Creation  ✅ COMPLETED - 2025-10-24

### TASK-004: Add PR creation workflow to retrospective-agent  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added comprehensive "Branching Workflow for Bulk Item Creation" section to retrospective-agent.md:
- Creates branch with timestamp naming convention
- Invokes work-item-creation-agent with branch_name and auto_commit: false
- Stages all items and creates detailed commit message
- Pushes branch and creates PR using gh pr create
- PR includes item links, review guidelines, and next steps
- Returns PR URL to user

### TASK-005: Add threshold logic for PR vs direct commit  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Documented clear thresholds:
- 3+ items → PR workflow (bulk review valuable)
- 1-2 items → Direct commit to master (auto_commit: true)
- Pattern-based detection → PR workflow
- Human-requested items → Direct commit

### Section 2.2: Update test-runner-agent for PR Creation  ✅ COMPLETED - 2025-10-24

### TASK-006: Add PR creation workflow to test-runner-agent  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added "Branching Workflow for Bulk Test Failures" section to test-runner-agent.md:
- Creates branch for 5+ test failures
- Invokes work-item-creation-agent with branch_name and auto_commit: false
- PR includes test failure details, test run statistics, review guidelines
- PR labeled with both "auto-created" and "test-failure"
- 1-4 failures still commit directly to master
- Threshold: 5+ failures triggers PR workflow

---

## Section 3: Update retrospective-agent to Use Branching (Optional)

**Status:** SKIPPED - Covered in Section 2.1
**Reason:** Section 2.1 already implements the branching workflow for retrospective-agent

---

## Section 4: Update test-runner-agent to Use Branching (Optional)

**Status:** SKIPPED - Covered in Section 2.2
**Reason:** Section 2.2 already implements the branching workflow for test-runner-agent

---

## Section 5: Update Documentation  ✅ COMPLETED - 2025-10-24

### TASK-007: Update CUSTOMIZATION.md  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added comprehensive "Human-in-the-Loop Workflow with PR Review" section to CUSTOMIZATION.md:
- Benefits section explaining quality control, pattern recognition, batch review
- Workflow diagram showing full process
- When to use guidance (thresholds for different agents)
- Detailed examples for retrospective-agent and test-runner-agent
- Agent support documentation
- Technical details including branch naming and PR creation
- Customization options for thresholds and templates

### TASK-008: Update OVERPROMPT-standard.md  ✅ COMPLETED - 2025-10-24
**Status:** DONE
**Implemented by:** bug-processor-agent
**Notes:** Added "PR-Based Work Item Creation (Optional)" section to OVERPROMPT-standard.md:
- Overview of PR-based workflow
- When agents use PR workflow (thresholds documented)
- Benefits clearly explained
- Human review workflow steps
- Concrete example with consolidation scenario
- Requirements (GitHub CLI) documented

---

## Section 6: Testing  ⚠️ READY FOR RUNTIME TESTING - 2025-10-24

### TASK-009: Test branching workflow with work-item-creation-agent  📝 DOCUMENTED - 2025-10-24
**Status:** READY FOR TESTING
**Implemented by:** bug-processor-agent
**Notes:** Implementation complete. Testing requires runtime execution:
- Agent documentation includes branching logic in step 6.5
- Branch creation/checkout code documented
- Output includes branch_name field
- **Testing**: Requires invoking work-item-creation-agent with branch_name parameter in real scenario

**Test Plan:**
```
1. Invoke work-item-creation-agent with branch_name="test-branch-001"
2. Verify: git branch shows test-branch-001 created and checked out
3. Verify: Bug files created on branch
4. Verify: git checkout master; ls bugs/ shows no new bug (branch isolated)
5. Verify: Output JSON includes "branch_name": "test-branch-001"
```

### TASK-010: Test backward compatibility  📝 DOCUMENTED - 2025-10-24
**Status:** READY FOR TESTING
**Implemented by:** bug-processor-agent
**Notes:** Implementation complete. Backward compatibility ensured by design:
- branch_name parameter is optional
- Agent continues on current branch if branch_name not provided
- No changes to existing workflow when branch_name omitted

**Test Plan:**
```
1. Invoke work-item-creation-agent without branch_name parameter (existing usage)
2. Verify: Bug created on current branch (same as before)
3. Verify: Output does not include branch_name or is null
4. Verify: No breaking changes to existing callers
```

### TASK-011: Test retrospective-agent integration  📝 DOCUMENTED - 2025-10-24
**Status:** READY FOR TESTING
**Implemented by:** bug-processor-agent
**Notes:** Implementation complete. Workflow documented in retrospective-agent.md:
- Branching workflow for 3+ items documented
- PR creation with gh pr create documented
- Threshold logic clear (3+ → PR, 1-2 → direct commit)

**Test Plan:**
```
1. Trigger retrospective that creates 5 bugs from pattern analysis
2. Verify: Branch created with auto-items-YYYY-MM-DD-HHMMSS naming
3. Verify: All 5 items invoked with branch_name and auto_commit: false
4. Verify: Single commit contains all items
5. Verify: Branch pushed to origin
6. Verify: PR created with gh pr create
7. Verify: PR includes links to all PROMPT.md files and review guidelines
8. Verify: PR labeled "auto-created"
```

### TASK-012: Test test-runner-agent integration  📝 DOCUMENTED - 2025-10-24
**Status:** READY FOR TESTING
**Implemented by:** bug-processor-agent
**Notes:** Implementation complete. Workflow documented in test-runner-agent.md:
- Branching workflow for 5+ failures documented
- PR creation with test context documented
- Threshold logic clear (5+ → PR, 1-4 → direct commit)

**Test Plan:**
```
1. Run test suite with 7 failures
2. Verify: test-runner-agent detects 7 ≥ 5, triggers PR workflow
3. Verify: Branch created with auto-items-YYYY-MM-DD-HHMMSS naming
4. Verify: All 7 bugs created with branch_name and auto_commit: false
5. Verify: PR includes test run statistics and failure details
6. Verify: PR labeled "auto-created" and "test-failure"
7. Test opposite: Run with 3 failures, verify direct commit (no PR)
```

---

## Progress Summary

**Total Tasks**: 12
**Completed**: 8 (Sections 1, 2, and 5 fully implemented)
**Ready for Testing**: 4 (Section 6 test plans documented)
**Not Started**: 0
**Skipped**: 2 (Sections 3 & 4 redundant with Section 2)

**Implementation Status**: ✅ **COMPLETE** - All code and documentation implemented
**Testing Status**: ⚠️ **READY FOR RUNTIME TESTING** - Requires actual agent invocations to validate

**Last Updated**: 2025-10-24
**Implemented By**: bug-processor-agent

### Sections Completed:
- ✅ Section 1: work-item-creation-agent enhanced with optional branching
- ✅ Section 2: retrospective-agent and test-runner-agent own PR creation
- 🔄 Section 3: SKIPPED (covered in Section 2.1)
- 🔄 Section 4: SKIPPED (covered in Section 2.2)
- ✅ Section 5: Documentation updated (CUSTOMIZATION.md and OVERPROMPT-standard.md)
- ⚠️ Section 6: Test plans documented, ready for runtime testing

### Files Modified:
1. `/home/becker/projects/featmgmt/claude-agents/shared/work-item-creation-agent.md`
   - Added optional `branch_name` parameter to input schema
   - Added step 6.5 for branch creation/checkout
   - Updated output format to include `branch_name`
   - Documented when to use branch_name

2. `/home/becker/projects/featmgmt/claude-agents/shared/retrospective-agent.md`
   - Added "Branching Workflow for Bulk Item Creation" section
   - Documented PR creation process with gh pr create
   - Threshold: 3+ items → PR, 1-2 items → direct commit

3. `/home/becker/projects/featmgmt/claude-agents/standard/test-runner-agent.md`
   - Added "Branching Workflow for Bulk Test Failures" section
   - Documented PR creation with test failure context
   - Threshold: 5+ failures → PR, 1-4 failures → direct commit

4. `/home/becker/projects/featmgmt/docs/CUSTOMIZATION.md`
   - Added "Human-in-the-Loop Workflow with PR Review" section
   - Benefits, workflow, examples, and customization options

5. `/home/becker/projects/featmgmt/templates/OVERPROMPT-standard.md`
   - Added "PR-Based Work Item Creation (Optional)" section
   - Documented when agents use PR workflow and requirements
