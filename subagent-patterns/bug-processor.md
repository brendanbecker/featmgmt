# Bug Processor Pattern

## Purpose

Systematically implements fixes for bugs and features by reading structured instruction documents (PROMPT.md), executing implementation tasks section by section, tracking progress, and preparing changes for version control. This pattern ensures disciplined, incremental progress with clear state management.

## Problem Statement

Without structured bug processing:

- **Scope creep**: Fixes expand beyond the original issue
- **Incomplete work**: Tasks are partially completed or skipped
- **Lost progress**: Work state isn't tracked between sessions
- **Quality gaps**: Testing and verification are inconsistent
- **Poor traceability**: Changes aren't linked to work items
- **Context loss**: Implementation rationale isn't captured

This pattern solves these problems by providing a disciplined, section-by-section approach with explicit progress tracking and quality gates.

## Responsibilities

### Instruction Parsing
- Read and understand PROMPT.md structure
- Read PLAN.md for context and approach
- Read TASKS.md to identify current progress
- Parse sections and acceptance criteria

### Section-by-Section Execution
- Identify the next incomplete section
- Execute ALL tasks within that section
- Test implementations before marking complete
- Never skip or partially complete sections

### Progress Tracking
- Update task status with timestamps
- Add implementation notes
- Document any deviations or issues
- Maintain audit trail

### Change Preparation
- Prepare meaningful commit messages
- Report all modified files
- Verify tests pass before completion

## Workflow

### 0. Mark Item as In Progress

Before any implementation:
- Read current metadata file
- Update status to "in_progress"
- Set started_date if not present
- Commit status change

### 1. Read Current State

Gather all context for the work item:
- Read PROMPT.md for detailed instructions
- Read PLAN.md for objectives and approach
- Read TASKS.md to determine current position

### 2. Detect Next Section

Find the first section without completion markers:
- Completed: marked with success indicator and date
- Failed: marked with failure indicator and date
- Issues: marked with warning indicator and date

The first section without any of these markers is the target.

### 3. Create Implementation Plan

Build a detailed plan for the section:
- List all tasks within the section
- Identify dependencies between tasks
- Plan the execution order
- Note any prerequisites

### 4. Execute Implementation

For each task in the section:

1. **Begin Task**: Mark as in progress
2. **Understand Requirements**: Read acceptance criteria carefully
3. **Locate Code**: Find relevant files and understand existing patterns
4. **Implement**: Make the required changes following existing conventions
5. **Test**: Run tests to verify implementation
6. **Verify**: Check acceptance criteria are met
7. **Complete**: Mark task as done

Continue until all tasks in section are complete.

### 5. Update Progress File

After completing all section tasks:
- Mark each task with completion status and date
- Add implementation notes
- Document any deviations from plan
- Note any discovered issues

Example format:
```
### TASK-001: Create validation logic  [COMPLETED - 2024-01-15]
Status: DONE
Implemented by: bug-processor
Notes: Added input validation with comprehensive edge case handling.
       Used existing ValidationUtils pattern.
```

### 6. Prepare Commit Information

Generate commit message:
- Reference the work item ID
- Summarize section completed
- List tasks accomplished
- Note acceptance criteria status

### 7. Commit Changes

Create atomic commit for section:
- Stage all modified files
- Use prepared commit message
- Push to repository

### 8. Report Completion

Provide structured status report:
- Work item ID and section name
- Overall status (completed, failed, issues)
- Tasks completed with details
- Files modified
- Commit information
- Next steps

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `item_path` | string | Path to the bug/feature directory |
| `repository_path` | string | Path to the codebase to modify |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `section_name` | string | auto-detect | Specific section to work on |
| `skip_tests` | boolean | false | Skip test execution (not recommended) |
| `max_tasks` | number | unlimited | Maximum tasks to complete |

## Output Contract

### Success Output

```
{
  "success": true,
  "item_id": "BUG-XXX",
  "section": "Section 2: Implementation",
  "status": "completed | failed | issues",
  "tasks": [
    {
      "task_id": "TASK-001",
      "title": "Implement validation",
      "status": "completed",
      "notes": "Implementation notes"
    }
  ],
  "files_modified": ["path/to/file.py"],
  "tests": {
    "ran": true,
    "passed": true,
    "details": "All 42 tests passed"
  },
  "commit": {
    "hash": "abc123",
    "message": "commit message preview"
  },
  "next_steps": "Description of what happens next"
}
```

### Error Output

```
{
  "success": false,
  "item_id": "BUG-XXX",
  "section": "Section 2: Implementation",
  "status": "failed",
  "error": "Error description",
  "tasks_completed": ["TASK-001"],
  "tasks_failed": ["TASK-002"],
  "recovery_suggestions": ["suggestions for resolution"]
}
```

## Decision Rules

### Section Selection
- Always work on the FIRST incomplete section
- Never skip ahead to later sections
- Complete or fail current section before moving on

### Task Completion Criteria
- All acceptance criteria explicitly met
- Tests pass (if test execution enabled)
- No obvious regressions introduced
- Code follows existing patterns

### When to Mark Failed
- Acceptance criteria cannot be met
- Required dependencies are missing
- Tests fail and cannot be fixed
- Implementation blocked by external factors

### When to Mark Issues
- Completed but with caveats
- Tests pass but edge cases exist
- Workaround implemented instead of proper fix
- Additional work recommended

### Code Quality Standards
- Follow existing code style and patterns
- Add appropriate comments for complex logic
- Use type hints where language supports them
- Match naming conventions of codebase

### Testing Requirements
- Run existing tests before marking section complete
- New functionality should have tests (if test section exists)
- Manual testing performed for UI/UX changes

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Scan Prioritize | Work item to process, priority context |
| User | Direct request to process specific item |
| Orchestrator | Work item from queue |

### Sends To

| Agent | Information |
|-------|-------------|
| Test Runner | What to test after implementation |
| Summary Reporter | Progress and completion status |
| User | Status updates, commit information |

### Coordination Protocol

1. Receives work item path from orchestrator or user
2. Reads instruction documents, determines next section
3. Executes section tasks, commits changes
4. Reports completion status
5. Control returns to orchestrator for next action

## Quality Criteria

### Implementation Quality
- [ ] Follows existing code patterns
- [ ] No obvious security vulnerabilities introduced
- [ ] Changes are minimal and focused

### Progress Accuracy
- [ ] Progress file accurately reflects completed work
- [ ] Timestamps are correct
- [ ] Notes capture implementation decisions

### Commit Quality
- [ ] Commit message references work item
- [ ] Changes are atomic to section
- [ ] All modified files are staged

### Test Compliance
- [ ] All existing tests still pass
- [ ] No regressions introduced
- [ ] New tests added where appropriate

## Implementation Notes

### Resumability
- All progress is persisted to progress file
- Can resume after interruption by re-reading state
- No in-memory-only state

### Error Recovery
- On failure, document exactly what failed
- Suggest recovery steps when possible
- Leave codebase in consistent state (revert if needed)

### Scope Control
- Only modify files relevant to current section
- Resist temptation to "fix" unrelated issues
- Document discovered issues for separate tracking

### Component Awareness
- Different components may have different conventions
- Read component-specific documentation if available
- Match existing patterns within the component
