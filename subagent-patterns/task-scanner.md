# Task Scanner Pattern (Infrastructure)

## Purpose

Scans infrastructure task repositories to identify active and backlog tasks, builds a priority-ordered queue, detects blocking relationships with human actions, and produces a work plan for infrastructure operations. This is the GitOps variant of the Scan & Prioritize pattern, specialized for infrastructure management.

## Problem Statement

Without systematic infrastructure task scanning:

- **Unclear priorities**: No single view of what infrastructure work is needed
- **Hidden blockers**: Manual actions blocking infrastructure work aren't visible
- **Dependency chaos**: Task dependencies aren't tracked systematically
- **Stale task data**: Task status becomes inconsistent across repositories
- **Priority violations**: Low-priority tasks executed before critical ones

This pattern solves these problems by providing automated scanning of infrastructure task repositories with dependency and blocking detection.

## Responsibilities

### Repository Scanning
- Synchronize with latest task repository state
- Parse task files in active and backlog directories
- Extract metadata from task frontmatter
- Identify tasks by priority and status

### Human Action Analysis
- Scan human action items
- Identify blocking relationships
- Calculate effective urgency based on blocked tasks
- Detect circular dependencies

### Dependency Tracking
- Parse task dependency sections
- Build dependency graph
- Identify ready vs waiting tasks
- Detect dependency cycles

### Priority Queue Building
- Sort by priority (critical > high > medium > low)
- Separate active from backlog
- Mark blocked vs ready status
- Recommend next task

## Workflow

### 1. Navigate to Task Repository

Locate and access the infrastructure task repository.

### 2. Synchronize State

Pull latest changes from remote:
- If pull fails, proceed with local state
- Note sync status in output

### 3. Read Active Tasks

Scan active tasks directory:
- Parse each task file
- Extract frontmatter metadata:
  - ID, title, status
  - Priority, labels
  - Dependencies

### 4. Read Backlog Tasks

Scan backlog tasks directory:
- Same parsing as active tasks
- Note backlog status

### 5. Scan Human Actions

If human actions directory exists:
- Read action summary file
- For each pending action:
  - Extract metadata
  - Extract blocking_items list
- Build action → blocked tasks mapping

### 6. Analyze Blocking Relationships

For each action with blocking items:
- Look up priority of each blocked task
- Calculate effective urgency:
  - Blocks critical → critical urgency
  - Blocks high → high urgency
  - Blocks medium → medium urgency
  - Blocks low → low urgency

For each task:
- Check if any action blocks it
- Mark as "blocked" or "ready"
- Record blocking action ID

### 7. Analyze Dependencies

For each task:
- Parse Dependencies section
- Check if dependencies are completed
- Mark as "waiting-dependency" if not ready
- Note which dependencies are missing

### 8. Build Priority Queue

Apply sorting algorithm:
1. Group by status (active before backlog)
2. Within status, group by priority
3. Within priority, sort by task number (oldest first)
4. Attach blocking/dependency status

### 9. Generate Human Actions Required List

Filter actions for display:
- Status is pending
- Has non-empty blocking_items
- Effective urgency is critical or high

Sort by effective urgency.

### 10. Generate Output

Produce structured report with:
- Scan metadata
- Human actions requiring attention
- Priority queue by level
- Summary statistics
- Recommended next task
- JSON data for programmatic use
- Warnings and notes

## Input Contract

### Required Inputs

| Field | Type | Description |
|-------|------|-------------|
| `repository_path` | string | Path to infrastructure task repository |

### Optional Inputs

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sync_remote` | boolean | true | Pull latest before scanning |
| `include_blocked` | boolean | true | Include blocked tasks in queue |
| `include_backlog` | boolean | true | Include backlog tasks |

## Output Contract

### Success Output

```
{
  "success": true,
  "scan_date": "ISO timestamp",
  "priority_queue": [
    {
      "task_id": "TASK-001",
      "priority": "critical",
      "status": "ready | blocked | waiting-dependency",
      "labels": ["infrastructure", "builds"],
      "dependencies": ["TASK-000"],
      "blocked_by": "ACTION-001 (if blocked)",
      "location": "tasks/active/TASK-001.md"
    }
  ],
  "human_actions_required": [
    {
      "action_id": "ACTION-001",
      "title": "Configure production credentials",
      "urgency": "critical",
      "reason": "Blocks TASK-001 (critical)",
      "blocking_items": ["TASK-001"],
      "location": "human-actions/ACTION-001-slug/"
    }
  ],
  "summary": {
    "total_tasks": number,
    "active_tasks": number,
    "backlog_tasks": number,
    "ready_tasks": number,
    "blocked_tasks": number,
    "waiting_dependency_tasks": number,
    "blocking_actions": number,
    "by_priority": {"critical": n, "high": n, "medium": n, "low": n}
  },
  "recommendations": ["actionable recommendations"],
  "warnings": ["any issues detected"],
  "next_action": {
    "task_id": "TASK-001 | ACTION-001",
    "type": "task | human_action",
    "title": "string",
    "recommendation": "Process this task first | Complete this action first"
  }
}
```

### Empty Queue Output

```
{
  "success": true,
  "scan_date": "ISO timestamp",
  "priority_queue": [],
  "human_actions_required": [],
  "summary": {
    "total_tasks": 0,
    "completed_tasks": number,
    "blocked_tasks": number
  },
  "recommendations": ["All tasks completed or blocked"],
  "next_action": null
}
```

## Decision Rules

### Priority Order

| Priority | Order | Description |
|----------|-------|-------------|
| critical | 0 | Security, data loss, system-wide impact |
| high | 1 | Core infrastructure, blocking other work |
| medium | 2 | Standard tasks, improvements |
| low | 3 | Nice-to-have, cleanup |

### Status Priority
- Active tasks before backlog
- Ready before blocked
- Blocked before waiting-dependency

### Task Readiness

| Condition | Status |
|-----------|--------|
| No blockers, no dependencies | ready |
| No blockers, dependencies met | ready |
| Blocked by human action | blocked |
| Dependencies not met | waiting-dependency |

### Next Action Selection
1. If human actions block critical/high tasks → recommend action first
2. Otherwise → recommend first ready task in queue
3. If all tasks blocked → recommend completing blocking actions

### Error Handling
- Git pull fails → continue with local state, add warning
- Task file parse error → skip task, log error, continue
- Missing directory → not an error if optional (human-actions)

## Integration Pattern

### Receives From

| Agent | Information |
|-------|-------------|
| Orchestrator | Request to scan tasks |
| User | Manual scan request |

### Sends To

| Agent | Information |
|-------|-------------|
| Infra Executor | Next task to process |
| Summary Reporter | Queue statistics |
| Orchestrator | Priority queue and recommendations |

### Coordination Protocol

1. Invoked at start of infrastructure session
2. Produces prioritized task queue
3. Orchestrator uses queue to dispatch work
4. Re-invoked as needed for updated queue

## Quality Criteria

### Scan Accuracy
- [ ] All task files parsed correctly
- [ ] Priority extracted from frontmatter
- [ ] Labels and dependencies captured
- [ ] Status correctly determined

### Blocking Detection
- [ ] All blocking relationships identified
- [ ] Effective urgency correctly calculated
- [ ] Circular dependencies detected
- [ ] Missing blocked items handled

### Priority Correctness
- [ ] Critical tasks always first
- [ ] Active before backlog
- [ ] Oldest tasks first within priority
- [ ] Blocked status correctly shown

### Output Quality
- [ ] Human-readable report is clear
- [ ] JSON structure is valid
- [ ] Recommendations are actionable
- [ ] Next action is correct

## Implementation Notes

### Task File Format

Expected frontmatter:
```yaml
---
id: TASK-001
title: Task Title
status: active | backlog | completed | blocked
priority: critical | high | medium | low
labels: [infrastructure, builds, registry]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Expected sections:
- Description
- Acceptance Criteria
- Dependencies (optional)
- Progress Log

### Performance
- Scan should complete in < 5 seconds
- If taking longer, report progress
- Handle large repositories gracefully

### Extensibility
- Support custom priority levels
- Configurable task directories
- Custom label filtering
