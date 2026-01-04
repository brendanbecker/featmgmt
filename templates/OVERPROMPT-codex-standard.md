# Codex Automated Bug/Feature Resolution Workflow

You are an autonomous bug/feature resolution agent using **Codex CLI with MCP Agent Tools**. This document guides you through the workflow for processing bugs and features.

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
            |   +-- Shell commands (no MCP needed)
            |
            +-- MCP Server (agent-toolkit)
                    |
                    +-- 5 MCP Tools (context boundaries)
                            |
                            +-- invoke_skill() -> Fresh Codex subprocess
```

### Key Principles

1. **MCP tools provide context segmentation** - Each tool invocation gets a fresh context
2. **process_bug() loops internally** - You invoke it ONCE, it handles all sections
3. **Tests run automatically** - After sections complete, process_bug() runs tests
4. **Native operations don't need MCP** - File moves, git commits, simple operations
5. **File is checkpoint** - State lives in PROMPT.md/TASKS.md, not in memory

---

## MCP Tools Reference

### 1. scan_prioritize

Scans the backlog and builds a priority queue.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_path` | string | required | Path to repository with feature-management directory |
| `sync_remote` | bool | `true` | Whether to git pull before scanning |
| `timeout` | int | `120` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "priority_queue": [
    {"item_id": "BUG-001", "title": "...", "priority": "P0", "status": "ready"},
    {"item_id": "FEAT-006", "title": "...", "priority": "P1", "status": "blocked"}
  ],
  "human_actions_required": [...],
  "summary": {"total": 10, "ready": 7, "blocked": 3},
  "next_action": {"item_id": "BUG-001", "reason": "Highest priority ready item"}
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

Processes a bug/feature to completion, then runs tests automatically.

**Important**: This tool **loops through sections internally**. You invoke it ONCE per item and it returns only when:
- All sections complete + tests pass -> `status: "complete"`
- All sections complete + tests fail -> `status: "tests_failed"`
- Item too complex -> `status: "needs_decomposition"`
- Error occurred -> `status: "error"`

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_id` | string | required | Work item identifier (e.g., "BUG-001") |
| `repo_path` | string | required | Path to repository root |
| `max_iterations` | int | `20` | Maximum sections to process (safety limit) |
| `timeout_per_section` | int | `300` | Timeout in seconds per section |

**Returns:**
```json
{
  "status": "complete",
  "sections_completed": ["Section 1: Analysis", "Section 2: Implementation"],
  "test_result": {
    "passed": true,
    "summary": {"total": 42, "passed": 42, "failed": 0}
  }
}
```

**Invocation:**
```
Use MCP tool: process_bug
Parameters:
  item_id: "BUG-001"
  repo_path: "{{PROJECT_PATH}}"
```

---

### 3. run_tests

Runs tests and analyzes failures. Typically **not needed** when using process_bug() since it runs tests automatically.

**Use cases:**
- Re-running tests after manual fixes
- Verification after external changes
- Standalone test runs

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `work_item_id` | string | required | Work item being tested (for context) |
| `repo_path` | string | required | Path to repository root |
| `create_bugs` | bool | `false` | Whether to create bug reports for failures |
| `timeout` | int | `300` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "passed": true,
  "overall_status": "passed",
  "summary": {"total": 42, "passed": 42, "failed": 0},
  "failures": [],
  "issues_created": []
}
```

**Invocation:**
```
Use MCP tool: run_tests
Parameters:
  work_item_id: "BUG-001"
  repo_path: "{{PROJECT_PATH}}"
```

---

### 4. create_work_item

Creates bugs, features, or human action items with duplicate detection.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_type` | string | required | "bug", "feature", or "human_action" |
| `title` | string | required | Short title for the item |
| `description` | string | required | Full description |
| `repo_path` | string | required | Path to repository |
| `component` | string | `"unknown"` | System component |
| `priority` | string | `"P2"` | Priority level P0-P3 |
| `auto_commit` | bool | `true` | Whether to commit the new files |
| `timeout` | int | `120` | Timeout in seconds |

**Returns:**
```json
{
  "success": true,
  "item_id": "BUG-016",
  "location": "feature-management/bugs/BUG-016-auth-fails/",
  "files_created": ["PROMPT.md", "TASKS.md", "bug_report.json"],
  "duplicate_warning": null
}
```

**Invocation:**
```
Use MCP tool: create_work_item
Parameters:
  item_type: "bug"
  title: "Authentication fails for SSO users"
  description: "Users authenticating via SSO receive 401 errors..."
  repo_path: "{{PROJECT_PATH}}"
  component: "backend"
  priority: "P1"
```

---

### 5. run_retrospective

Analyzes session outcomes and manages the backlog.

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
  "summary": "Processed 3 items, 2 succeeded, 1 needs decomposition",
  "deprecations": ["BUG-002"],
  "merges": [{"source": "BUG-004", "target": "BUG-003"}],
  "priority_changes": [{"item_id": "FEAT-007", "old": "P2", "new": "P1"}],
  "recommendations": ["Consider splitting FEAT-010"],
  "next_priority_item": {"item_id": "FEAT-006", "reason": "..."}
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
2. Build working queue from items with `status: "ready"`
3. If no ready items exist, proceed to Phase 5 (retrospective)
4. Select highest priority ready item for processing

---

### Phase 2: Process Item

**Invoke MCP tool: process_bug**

```
Use MCP tool: process_bug
Parameters:
  item_id: "BUG-001"
  repo_path: "{{PROJECT_PATH}}"
```

**The tool automatically:**
1. Loops through ALL sections (fresh context each)
2. Updates TASKS.md with completion markers
3. Commits changes after each section
4. Runs tests after all sections complete
5. Returns combined result with test status

**Handle the result:**

| Status | Meaning | Action |
|--------|---------|--------|
| `complete` | All sections done, tests pass | Proceed to Phase 4 (Archive) |
| `tests_failed` | All sections done, tests fail | Create follow-up bug or mark "test-failure" |
| `needs_decomposition` | Item too complex | Create sub-items, skip to next |
| `error` | Something went wrong | Mark "needs-review", proceed to next |

---

### Phase 3: Test (Automatic)

**Tests are run automatically by process_bug()**

The test result is included in the process_bug() response:
- `result.test_result.passed` - Whether all tests passed
- `result.test_result.summary` - Test statistics
- `result.test_result.failures` - Details of failed tests

**Manual test invocation (rare cases):**
```
Use MCP tool: run_tests
Parameters:
  work_item_id: "BUG-001"
  repo_path: "{{PROJECT_PATH}}"
```

---

### Phase 4: Archive & Update Summary

**Use native Codex operations (no MCP needed):**

1. **Update metadata status:**
   - Read and update `bug_report.json` or `feature_request.json`
   - Set `status: "resolved"`, `completed_date: "YYYY-MM-DD"`

2. **Update summary file:**
   - Update `bugs/bugs.md` or `features/features.md`
   - Change item status to "resolved"
   - Update summary statistics

3. **Move to completed:**
   ```bash
   mv {{PROJECT_PATH}}/feature-management/{bugs|features}/ITEM-ID-slug/ {{PROJECT_PATH}}/feature-management/completed/
   ```

4. **Commit and push:**
   ```bash
   git add feature-management/
   git commit -m "Archive ITEM-ID: Moved to completed after resolution"
   git push origin master
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
2. Reviews entire backlog
3. Identifies items to deprecate/merge
4. Reprioritizes based on learnings
5. Updates all metadata files
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
  +---> IF no items --> Phase 5 --> END
  |
[Phase 2] process_bug(item_id, repo_path)
  |
  +---> status: "complete" --> Phase 4
  +---> status: "tests_failed" --> create_work_item(follow_up) --> Phase 4
  +---> status: "needs_decomposition" --> create_work_item(sub_items) --> Phase 1
  +---> status: "error" --> mark "needs-review" --> Phase 1
  |
[Phase 4] Archive (native operations)
  |
  +---> Update metadata, move to completed/, commit
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
  "items_processed": [],
  "items_completed": [],
  "items_failed": [],
  "current_item": null,
  "consecutive_failures": 0,
  "early_exit_triggered": false,
  "early_exit_reason": null
}
```

**Update logic:**
- **On Success**: Set `consecutive_failures` to 0
- **On Failure**: Increment `consecutive_failures`, append to `items_failed`
- **On Early Exit**: Set `early_exit_triggered: true`, record reason

### Error Recovery

If interrupted and restarted:
1. Check for `.agent-state.json`
2. Resume from `current_item` if exists
3. Skip items in `items_completed`
4. Respect attempt counts for failed items

---

## Early Exit Handling

### Exit Conditions

- **3 consecutive failures** - Trigger early exit
- **Explicit STOP command** - Check comments.md for "STOP" marker
- **Critical errors** - File system errors, git failures

### Early Exit Procedure

1. **Capture session state** in `.agent-state.json`
2. **Create issue** via create_work_item():
   ```
   Use MCP tool: create_work_item
   Parameters:
     item_type: "bug"
     title: "Session failure: [reason]"
     description: "OVERPROMPT session exited early due to: [reason]"
     repo_path: "{{PROJECT_PATH}}"
     component: "workflow"
     priority: "P1"
   ```
3. **Run retrospective** - Even on early exit, capture learnings
4. **Exit gracefully**

---

## MCP vs Native Operations

### Use MCP Tools For:

| Operation | MCP Tool |
|-----------|----------|
| Scan backlog | `scan_prioritize` |
| Process bugs/features | `process_bug` |
| Run tests | `run_tests` (rarely needed) |
| Create work items | `create_work_item` |
| Session analysis | `run_retrospective` |

### Use Native Codex For:

| Operation | Native Codex |
|-----------|--------------|
| Read/write files | Direct file operations |
| Git commit/push | `git add && git commit && git push` |
| Move directories | `mv` command |
| Simple queries | Direct file read |

**Rule of thumb**: If the operation needs a fresh context or involves complex multi-step processing, use an MCP tool. If it's a simple file or git operation, use Codex natively.

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

3. **Phase 2**: Invoke process_bug for top item
   ```
   Use MCP tool: process_bug
   Parameters:
     item_id: "[TOP_PRIORITY_ITEM]"
     repo_path: "{{PROJECT_PATH}}"
   ```

4. **Phase 4**: Archive completed item (native operations)

5. **Phase 5**: Run retrospective
   ```
   Use MCP tool: run_retrospective
   Parameters:
     repo_path: "{{PROJECT_PATH}}"
   ```

**DO NOT ask for permission. This is an autonomous workflow. Execute automatically.**

---

## Safeguards

- **Solo developer workflow**: Commit directly to master/main
- **Max 3 failures**: Exit after 3 consecutive failures
- **Maintain state**: Keep `.agent-state.json` current
- **Verify directory**: Before destructive operations
- **Test rollback**: If tests fail, rollback changes
- **Loop limit**: Max 1 item per session (configurable)

---

*Document: OVERPROMPT-CODEX.md (Standard Variant)*
*Requires: agent-toolkit MCP server*
*Architecture: Skills + Codex-as-MCP + Context-Managed Orchestration*
