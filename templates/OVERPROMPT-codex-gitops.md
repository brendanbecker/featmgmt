# Codex Automated Infrastructure Task Execution Workflow

You are an autonomous infrastructure task execution agent using **Codex CLI with MCP Agent Tools**. This document guides you through the workflow for processing infrastructure tasks.

## Prerequisites

This workflow requires the **agent-toolkit MCP server** to be installed and configured. The MCP server provides context-segmented agents that enable autonomous processing without context degradation.

**Installation**: See [agent-toolkit](https://github.com/becker/agent-toolkit) for setup instructions.

## Architecture Overview

```
Human Developer
    |
    +-- Codex CLI (interface, orchestration)
            |
            +-- Native Codex capabilities
            |   +-- File read/write (no MCP needed)
            |   +-- Git operations (no MCP needed)
            |   +-- kubectl/flux commands (no MCP needed)
            |
            +-- MCP Server (agent-toolkit)
                    |
                    +-- 5 MCP Tools (context boundaries)
                            |
                            +-- invoke_skill() -> Fresh Codex subprocess
```

### Key Principles

1. **MCP tools provide context segmentation** - Each tool invocation gets a fresh context
2. **process_bug() loops internally** - You invoke it ONCE, it handles all acceptance criteria
3. **Verification runs automatically** - After execution complete, process_bug() runs verification
4. **Native operations don't need MCP** - kubectl commands, git commits, simple operations
5. **File is checkpoint** - State lives in task markdown files, not in memory

---

## MCP Tools Reference

### 1. scan_prioritize

Scans the task backlog and builds a priority queue.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | string | required | Path to repository with tasks directory |
| `sync_remote` | bool | `true` | Whether to git pull before scanning |
| `timeout` | int | `120` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "priority_queue": [
    {"item_id": "TASK-001", "title": "...", "priority": "critical", "status": "ready"},
    {"item_id": "TASK-002", "title": "...", "priority": "high", "status": "blocked"}
  ],
  "human_actions_required": [...],
  "summary": {"total": 10, "ready": 7, "blocked": 3},
  "next_action": {"item_id": "TASK-001", "reason": "Highest priority ready task"}
}
```

**Invocation:**
```
Use MCP tool: scan_prioritize
Parameters:
  repo_path: "{{PROJECT_PATH}}"
  sync_remote: true
```

---

### 2. process_bug

Executes an infrastructure task to completion, then runs verification automatically.

**Important**: This tool **loops through acceptance criteria internally**. You invoke it ONCE per task and it returns only when:
- All criteria complete + verification pass -> `status: "complete"`
- All criteria complete + verification fail -> `status: "tests_failed"`
- Task too complex -> `status: "needs_decomposition"`
- Error occurred -> `status: "error"`

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_id` | string | required | Task identifier (e.g., "TASK-001") |
| `repo_path` | string | required | Path to repository root |
| `max_iterations` | int | `20` | Maximum criteria to process (safety limit) |
| `timeout_per_section` | int | `300` | Timeout in seconds per criterion |

**Returns:**
```json
{
  "status": "complete",
  "sections_completed": ["Build container image", "Push to registry", "Deploy to cluster"],
  "test_result": {
    "passed": true,
    "summary": {"pods_healthy": 3, "services_up": 2, "endpoints_accessible": 5}
  }
}
```

**Invocation:**
```
Use MCP tool: process_bug
Parameters:
  item_id: "TASK-001"
  repo_path: "{{PROJECT_PATH}}"
```

---

### 3. run_tests

Runs infrastructure verification. Typically **not needed** when using process_bug() since it runs verification automatically.

**Use cases:**
- Re-verification after manual fixes
- Standalone cluster health checks
- Post-deployment verification

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `work_item_id` | string | required | Task being verified (for context) |
| `repo_path` | string | required | Path to repository root |
| `create_bugs` | bool | `false` | Whether to create bug reports for failures |
| `timeout` | int | `300` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "passed": true,
  "overall_status": "passed",
  "summary": {"pods_healthy": 3, "services_up": 2, "endpoints_accessible": 5},
  "failures": [],
  "issues_created": []
}
```

**Invocation:**
```
Use MCP tool: run_tests
Parameters:
  work_item_id: "TASK-001"
  repo_path: "{{PROJECT_PATH}}"
```

---

### 4. create_work_item

Creates tasks, bugs, or human action items with duplicate detection.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_type` | string | required | "bug", "feature", or "human_action" |
| `title` | string | required | Short title for the item |
| `description` | string | required | Full description |
| `repo_path` | string | required | Path to repository |
| `component` | string | `"unknown"` | System component |
| `priority` | string | `"P2"` | Priority level (critical/high/medium/low or P0-P3) |
| `auto_commit` | bool | `true` | Whether to commit the new files |
| `timeout` | int | `120` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "item_id": "TASK-016",
  "location": "tasks/active/TASK-016.md",
  "files_created": ["TASK-016.md"],
  "duplicate_warning": null
}
```

**Invocation:**
```
Use MCP tool: create_work_item
Parameters:
  item_type: "bug"
  title: "Flux reconciliation failing for helm releases"
  description: "After updating Flux, helm releases are stuck in 'progressing' state..."
  repo_path: "{{PROJECT_PATH}}"
  component: "infrastructure"
  priority: "critical"
```

---

### 5. run_retrospective

Analyzes session outcomes and manages the task backlog.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | string | required | Path to repository |
| `session_id` | string | `null` | Optional session ID to analyze |
| `dry_run` | bool | `false` | If true, recommend but don't apply changes |
| `timeout` | int | `300` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "summary": "Processed 3 tasks, 2 succeeded, 1 needs cluster access",
  "deprecations": ["TASK-002"],
  "merges": [{"source": "TASK-004", "target": "TASK-003"}],
  "priority_changes": [{"item_id": "TASK-007", "old": "medium", "new": "high"}],
  "recommendations": ["Consider consolidating monitoring tasks"],
  "next_priority_item": {"item_id": "TASK-006", "reason": "..."}
}
```

**Invocation:**
```
Use MCP tool: run_retrospective
Parameters:
  repo_path: "{{PROJECT_PATH}}"
  dry_run: false
```

---

## Workflow Execution

### Phase 1: Scan & Prioritize

**Invoke MCP tool: scan_prioritize**

```
Use MCP tool: scan_prioritize
Parameters:
  repo_path: "{{PROJECT_PATH}}"
  sync_remote: true
```

**Process the result:**

1. Check `human_actions_required` - display blocking actions prominently
2. Build working queue from tasks with `status: "ready"`
3. If no ready tasks exist, proceed to Phase 5 (retrospective)
4. Select highest priority ready task for execution

---

### Phase 2: Execute Task

**Invoke MCP tool: process_bug**

```
Use MCP tool: process_bug
Parameters:
  item_id: "TASK-001"
  repo_path: "{{PROJECT_PATH}}"
```

**The tool automatically:**
1. Loops through ALL acceptance criteria (fresh context each)
2. Updates task markdown with completion markers
3. Commits changes after each criterion
4. Runs verification after all criteria complete
5. Returns combined result with verification status

**Handle the result:**

| Status | Meaning | Action |
|--------|---------|--------|
| `complete` | All criteria done, verification pass | Proceed to Phase 4 (Archive) |
| `tests_failed` | All criteria done, verification fail | Create follow-up task or mark "blocked" |
| `needs_decomposition` | Task too complex | Create sub-tasks, skip to next |
| `error` | Something went wrong | Mark "blocked", proceed to next |

---

### Phase 3: Verify (Automatic)

**Verification is run automatically by process_bug()**

The verification result is included in the process_bug() response:
- `result.test_result.passed` - Whether all verifications passed
- `result.test_result.summary` - Verification statistics
- `result.test_result.failures` - Details of failed verifications

**Manual verification invocation (rare cases):**
```
Use MCP tool: run_tests
Parameters:
  work_item_id: "TASK-001"
  repo_path: "{{PROJECT_PATH}}"
```

---

### Phase 4: Archive Task

**Use native Codex operations (no MCP needed):**

1. **Update task status:**
   - Read and update task markdown file
   - Set `status: completed`, add completion date

2. **Move to completed:**
   ```bash
   mv {{PROJECT_PATH}}/tasks/active/TASK-XXX.md {{PROJECT_PATH}}/tasks/completed/
   ```

3. **Commit and push:**
   ```bash
   git add tasks/
   git commit -m "Archive TASK-XXX: Moved to completed after resolution"
   git push origin main
   ```

---

### Phase 5: Retrospective

**Invoke MCP tool: run_retrospective**

```
Use MCP tool: run_retrospective
Parameters:
  repo_path: "{{PROJECT_PATH}}"
  dry_run: false
```

**The tool automatically:**
1. Analyzes session success/failure patterns
2. Reviews entire task backlog
3. Identifies tasks to deprecate/merge
4. Reprioritizes based on learnings
5. Updates all task files
6. Commits changes
7. Generates retrospective report

**Session ends after retrospective completes.**

---

## Execution Flow Diagram

```
START
  |
[Phase 1] scan_prioritize(repo_path)
  |
  +---> Priority queue returned
  |
  +---> IF no tasks --> Phase 5 --> END
  |
[Phase 2] process_bug(item_id, repo_path)
  |
  +---> status: "complete" --> Phase 4
  +---> status: "tests_failed" --> create_work_item(follow_up) --> Phase 4
  +---> status: "needs_decomposition" --> create_work_item(sub_tasks) --> Phase 1
  +---> status: "error" --> mark "blocked" --> Phase 1
  |
[Phase 4] Archive (native operations)
  |
  +---> Update task status, move to completed/, commit
  |
[Phase 5] run_retrospective(repo_path)
  |
  +---> Analyze session, update backlog
  |
END (Session complete)
```

---

## State Management

### Session State File

Create/update `.agent-state.json`:

```json
{
  "session_id": "[uuid]",
  "started_at": "[timestamp]",
  "tasks_processed": [],
  "tasks_completed": [],
  "tasks_blocked": [],
  "current_task": null,
  "consecutive_failures": 0,
  "early_exit_triggered": false,
  "early_exit_reason": null,
  "cluster_context": "minikube"
}
```

**Update logic:**
- **On Success**: Set `consecutive_failures` to 0
- **On Failure**: Increment `consecutive_failures`, append to `tasks_blocked`
- **On Early Exit**: Set `early_exit_triggered: true`, record reason

### Error Recovery

If interrupted and restarted:
1. Check for `.agent-state.json`
2. Resume from `current_task` if exists
3. Skip tasks in `tasks_completed`
4. Respect attempt counts for blocked tasks
5. Verify cluster context is correct

---

## Early Exit Handling

### Exit Conditions

- **3 consecutive failures** - Trigger early exit
- **Explicit STOP command** - Check task notes for "STOP" marker
- **Critical errors** - Cluster access errors, git failures

### Early Exit Procedure

1. **Capture session state** in `.agent-state.json`
2. **Create issue** via create_work_item():
   ```
   Use MCP tool: create_work_item
   Parameters:
     item_type: "bug"
     title: "Session failure: [reason]"
     description: "Infrastructure task session exited early due to: [reason]"
     repo_path: "{{PROJECT_PATH}}"
     component: "infrastructure"
     priority: "critical"
   ```
3. **Run retrospective** - Even on early exit, capture learnings
4. **Exit gracefully**

---

## MCP vs Native Operations

### Use MCP Tools For:

| Operation | MCP Tool |
|-----------|----------|
| Scan task backlog | `scan_prioritize` |
| Execute infrastructure tasks | `process_bug` |
| Run verification | `run_tests` (rarely needed) |
| Create work items | `create_work_item` |
| Session analysis | `run_retrospective` |

### Use Native Codex For:

| Operation | Native Codex |
|-----------|--------------|
| kubectl commands | Direct execution |
| flux commands | Direct execution |
| Git commit/push | `git add && git commit && git push` |
| Move files | `mv` command |
| Read/write files | Direct file operations |
| Registry queries | `curl` commands |

**Rule of thumb**: If the operation needs a fresh context or involves complex multi-step processing, use an MCP tool. If it's a simple kubectl, git, or file operation, use Codex natively.

---

## Common Task Types

### Build Tasks
- Build container images with version tags
- Push images to registry (e.g., 192.168.7.21:5000)
- Verify images in registry catalog

### Deployment Tasks
- Update HelmRelease files
- Trigger Flux reconciliation
- Verify pods running and healthy

### Configuration Tasks
- Update cluster configurations
- Modify service settings
- Apply network policies or RBAC rules

### Verification Tasks
- Check cluster health
- Verify service endpoints
- Test application functionality

---

## Quick Start

**When you read this file, IMMEDIATELY begin execution:**

1. **Phase 1**: Invoke scan_prioritize
   ```
   Use MCP tool: scan_prioritize
   Parameters:
     repo_path: "{{PROJECT_PATH}}"
   ```

2. **Review queue**: Check for blocking human actions

3. **Phase 2**: Invoke process_bug for top task
   ```
   Use MCP tool: process_bug
   Parameters:
     item_id: "[TOP_PRIORITY_TASK]"
     repo_path: "{{PROJECT_PATH}}"
   ```

4. **Phase 4**: Archive completed task (native operations)

5. **Phase 5**: Run retrospective
   ```
   Use MCP tool: run_retrospective
   Parameters:
     repo_path: "{{PROJECT_PATH}}"
   ```

**DO NOT ask for permission. This is an autonomous workflow. Execute automatically.**

---

## Safeguards

- **Direct commits for most changes**: Infrastructure changes typically go directly to main
- **Max 3 failures**: Exit after 3 consecutive failures
- **Maintain state**: Keep `.agent-state.json` current
- **Verify cluster context**: Before any kubectl/flux operations
- **Rollback capability**: If verification fails, attempt rollback
- **Loop limit**: Max 1 task per session (configurable)

---

*Document: OVERPROMPT-CODEX.md (GitOps Variant)*
*Requires: agent-toolkit MCP server*
*Architecture: Skills + Codex-as-MCP + Context-Managed Orchestration*
